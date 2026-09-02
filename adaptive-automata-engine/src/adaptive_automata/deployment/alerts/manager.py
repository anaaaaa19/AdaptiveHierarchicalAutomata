"""
Alert Manager Component with State Lifecycle and Deduplication.
"""

from enum import Enum
import threading
import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from adaptive_automata.deployment.storage.base import EventStore
from adaptive_automata.security.alerts import SecurityAlert
from adaptive_automata.security.assessment import SecurityAssessment, SeverityLevel


class AlertState(str, Enum):
    """Lifecycle status of a SecurityAlert."""
    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class AlertManager:
    """
    Alert Manager handling real-time alert generation, time-window deduplication,
    status lifecycle transitions, and persistence.
    """

    def __init__(
        self,
        event_store: EventStore | None = None,
        dedup_window_sec: float = 60.0,
    ) -> None:
        self.event_store = event_store
        self.dedup_window_sec = dedup_window_sec
        self._lock = threading.Lock()
        self._alerts_by_id: dict[str, SecurityAlert] = {}
        self._alert_status: dict[str, AlertState] = {}
        self._dedup_keys: dict[tuple[str, str, str, str], SecurityAlert] = {}
        self._dedup_last_seen: dict[tuple[str, str, str, str], float] = {}

    def process_security_assessment(
        self,
        assessment: SecurityAssessment,
        symbol: str = "",
        state: str = "",
    ) -> SecurityAlert | None:
        """
        Evaluate a SecurityAssessment and produce a deduplicated SecurityAlert if severity >= MEDIUM.
        """
        if assessment.severity in (SeverityLevel.BENIGN, SeverityLevel.LOW):
            return None

        with self._lock:
            reasons_str = "_".join(sorted(r.value if hasattr(r, "value") else str(r) for r in assessment.reason_codes))
            dedup_key = (
                assessment.session_id,
                assessment.model_version,
                state,
                reasons_str,
            )

            now = time.time()
            last_seen = self._dedup_last_seen.get(dedup_key, 0.0)

            # Deduplication window check
            if now - last_seen < self.dedup_window_sec and dedup_key in self._dedup_keys:
                existing_alert = self._dedup_keys[dedup_key]
                existing_alert.evidence["count"] = existing_alert.evidence.get("count", 1) + 1
                existing_alert.evidence["last_seen"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
                self._dedup_last_seen[dedup_key] = now
                if self.event_store:
                    self.event_store.store_alert(existing_alert)
                return existing_alert

            # Create new SecurityAlert
            alert_id = f"ALT-{assessment.session_id}-{int(now * 1000)}"
            alert = SecurityAlert.from_assessment(
                assessment=assessment,
                alert_id=alert_id,
                state=state,
                symbol=symbol,
            )
            alert.evidence["count"] = 1

            self._alerts_by_id[alert_id] = alert
            self._alert_status[alert_id] = AlertState.NEW
            self._dedup_keys[dedup_key] = alert
            self._dedup_last_seen[dedup_key] = now

            if self.event_store:
                self.event_store.store_alert(alert)

            return alert

    def update_alert_status(self, alert_id: str, new_status: AlertState) -> SecurityAlert:
        """Update the lifecycle status of an alert."""
        with self._lock:
            if alert_id not in self._alerts_by_id:
                raise KeyError(f"SecurityAlert '{alert_id}' not found.")
            self._alert_status[alert_id] = new_status
            alert = self._alerts_by_id[alert_id]
            if self.event_store:
                self.event_store.store_alert(alert)
            return alert

    def get_alert_status(self, alert_id: str) -> AlertState:
        with self._lock:
            return self._alert_status.get(alert_id, AlertState.NEW)

    def list_alerts(
        self,
        severity: str | None = None,
        status: AlertState | None = None,
    ) -> list[dict[str, Any]]:
        """List active alerts formatted with status."""
        with self._lock:
            res = []
            for alt_id, alt in self._alerts_by_id.items():
                st = self._alert_status.get(alt_id, AlertState.NEW)
                if status and st != status:
                    continue
                sev_val = alt.severity.value if hasattr(alt.severity, "value") else str(alt.severity)
                if severity and sev_val != severity:
                    continue
                
                d = {
                    "alert_id": alt.alert_id,
                    "session_id": alt.session_id,
                    "severity": sev_val,
                    "classification": alt.classification.value if hasattr(alt.classification, "value") else str(alt.classification),
                    "model_version": alt.model_version,
                    "state": alt.current_state,
                    "representative_symbol": alt.triggering_symbol,
                    "reason_codes": [r.value if hasattr(r, "value") else str(r) for r in alt.reason_codes],
                    "status": st.value,
                    "count": alt.evidence.get("count", 1),
                    "timestamp": alt.timestamp,
                    "evidence": alt.evidence,
                }
                res.append(d)
            return res
