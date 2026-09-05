"""
Security Alert object.

Provides explainable, human-readable SecurityAlert containers for high-risk security events.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .assessment import BehavioralClassification, ReasonCode, SecurityAssessment, SeverityLevel


@dataclass(slots=True)
class SecurityAlert:
    """
    Human-readable, explainable security alert container generated for suspicious or malicious behavior.

    Attributes:
        alert_id: Unique alert identifier.
        session_id: Target protocol session ID.
        timestamp: ISO 8601 creation timestamp.
        severity: SeverityLevel assigned to alert.
        classification: BehavioralClassification tag.
        model_version: Active model version tag.
        current_state: Automaton state where deviation occurred.
        triggering_symbol: Input symbol triggering alert.
        reason_codes: List of explicit ReasonCode triggers explaining why alert fired.
        evidence: Dictionary of supporting formal and context evidence.
        trace_position: Symbol index within session.
        analysis_level: Phase 4 formal analysis level used (DFA, PDA, CFG).
    """
    alert_id: str
    session_id: str
    severity: SeverityLevel
    classification: BehavioralClassification
    model_version: str
    current_state: str
    triggering_symbol: str
    reason_codes: list[ReasonCode] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)
    trace_position: int = 0
    analysis_level: str = "DFA_MEALY"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def count(self) -> int:
        return self.evidence.get("count", 1)

    @classmethod
    def from_assessment(cls, assessment: SecurityAssessment, alert_id: str, state: str, symbol: str, position: int = 0, level: str = "DFA_MEALY") -> "SecurityAlert":
        """Construct a human-readable SecurityAlert from a SecurityAssessment."""
        return cls(
            alert_id=alert_id,
            session_id=assessment.session_id,
            severity=assessment.severity,
            classification=assessment.behavioral_classification,
            model_version=assessment.model_version,
            current_state=state,
            triggering_symbol=symbol,
            reason_codes=list(assessment.reason_codes),
            evidence=dict(assessment.evidence_details),
            trace_position=position,
            analysis_level=level,
        )

    def to_explainable_text(self) -> str:
        """Format human-readable explainable security alert report."""
        reasons_str = ", ".join([r.value for r in self.reason_codes]) if self.reason_codes else "NONE"
        return (
            f"[ALERT {self.alert_id}] {self.severity.value} Severity ({self.classification.value}) "
            f"on session '{self.session_id}' at symbol '{self.triggering_symbol}' (state: '{self.current_state}'). "
            f"Reasons: [{reasons_str}]. Active Model: '{self.model_version}' (Level: {self.analysis_level})."
        )

    def __repr__(self) -> str:
        return f"SecurityAlert(id='{self.alert_id}', severity={self.severity.value}, class={self.classification.value})"
