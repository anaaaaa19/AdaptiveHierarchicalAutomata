"""
SQLite and In-Memory Event Store Implementations.
"""

import json
import sqlite3
import threading
from typing import Any

from adaptive_automata.deployment.pipeline.events import ProtocolEvent
from adaptive_automata.deployment.storage.base import EventStore
from adaptive_automata.security.alerts import SecurityAlert
from adaptive_automata.analysis.escalation import AnalysisLevel, AnalysisResult, AnalysisStatus
from adaptive_automata.security.assessment import BehavioralClassification, ReasonCode, SecurityAssessment, SeverityLevel


class SQLiteEventStore(EventStore):
    """
    SQLite-backed Event Store supporting WAL mode, thread concurrency locks,
    and structured JSON serialization.
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        with self._lock:
            cur = self._conn.cursor()
            if self.db_path != ":memory:":
                cur.execute("PRAGMA journal_mode=WAL;")
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    protocol TEXT,
                    direction TEXT,
                    symbol TEXT,
                    formal_state TEXT,
                    model_version TEXT,
                    analysis_status TEXT,
                    analysis_level TEXT,
                    risk_score REAL,
                    severity TEXT,
                    timestamp TEXT,
                    latency_ms REAL,
                    payload_snippet TEXT,
                    raw_json TEXT
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    model_version TEXT,
                    severity TEXT,
                    classification TEXT,
                    status TEXT,
                    risk_score REAL,
                    timestamp TEXT,
                    raw_json TEXT
                );
            """)

            cur.execute("CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_events_version ON events(model_version);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);")
            self._conn.commit()

    def store_event(self, event: ProtocolEvent) -> None:
        with self._lock:
            data = event.to_dict()
            cur = self._conn.cursor()
            cur.execute(
                """
                INSERT OR REPLACE INTO events (
                    event_id, session_id, protocol, direction, symbol, formal_state,
                    model_version, analysis_status, analysis_level, risk_score, severity,
                    timestamp, latency_ms, payload_snippet, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.session_id,
                    event.protocol,
                    event.direction,
                    event.symbol,
                    event.formal_state,
                    event.model_version,
                    data["analysis"]["status"],
                    data["analysis"]["level_used"],
                    data["security"]["risk_score"],
                    data["security"]["severity"],
                    event.timestamp,
                    event.processing_latency_ms,
                    event.raw_payload_snippet,
                    json.dumps(data),
                ),
            )
            self._conn.commit()

    def store_alert(self, alert: SecurityAlert) -> None:
        with self._lock:
            data = {
                "alert_id": alert.alert_id,
                "session_id": alert.session_id,
                "severity": alert.severity.value if hasattr(alert.severity, "value") else str(alert.severity),
                "classification": alert.classification.value if hasattr(alert.classification, "value") else str(alert.classification),
                "model_version": alert.model_version,
                "current_state": alert.current_state,
                "triggering_symbol": alert.triggering_symbol,
                "reason_codes": [r.value if hasattr(r, "value") else str(r) for r in alert.reason_codes],
                "timestamp": alert.timestamp,
                "evidence": alert.evidence,
            }
            cur = self._conn.cursor()
            cur.execute(
                """
                INSERT OR REPLACE INTO alerts (
                    alert_id, session_id, model_version, severity, classification,
                    status, risk_score, timestamp, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    alert.alert_id,
                    alert.session_id,
                    alert.model_version,
                    data["severity"],
                    data["classification"],
                    "NEW",
                    0.8,
                    alert.timestamp,
                    json.dumps(data),
                ),
            )
            self._conn.commit()

    def get_event(self, event_id: str) -> ProtocolEvent | None:
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("SELECT raw_json FROM events WHERE event_id = ?", (event_id,))
            row = cur.fetchone()
            if not row:
                return None
            return self._deserialize_event(json.loads(row["raw_json"]))

    def get_alert(self, alert_id: str) -> SecurityAlert | None:
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("SELECT raw_json FROM alerts WHERE alert_id = ?", (alert_id,))
            row = cur.fetchone()
            if not row:
                return None
            return self._deserialize_alert(json.loads(row["raw_json"]))

    def list_events(
        self,
        session_id: str | None = None,
        model_version: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ProtocolEvent]:
        with self._lock:
            cur = self._conn.cursor()
            query = "SELECT raw_json FROM events WHERE 1=1"
            params: list[Any] = []
            if session_id:
                query += " AND session_id = ?"
                params.append(session_id)
            if model_version:
                query += " AND model_version = ?"
                params.append(model_version)
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cur.execute(query, params)
            rows = cur.fetchall()
            return [self._deserialize_event(json.loads(row["raw_json"])) for row in rows]

    def list_alerts(
        self,
        severity: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SecurityAlert]:
        with self._lock:
            cur = self._conn.cursor()
            query = "SELECT raw_json FROM alerts WHERE 1=1"
            params: list[Any] = []
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            if status:
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cur.execute(query, params)
            rows = cur.fetchall()
            return [self._deserialize_alert(json.loads(row["raw_json"])) for row in rows]

    def get_event_count(self) -> int:
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("SELECT COUNT(*) FROM events")
            return cur.fetchone()[0]

    def get_alert_count(self) -> int:
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("SELECT COUNT(*) FROM alerts")
            return cur.fetchone()[0]

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def _deserialize_event(self, d: dict[str, Any]) -> ProtocolEvent:
        status_enum = AnalysisStatus(d["analysis"]["status"])
        level_enum = AnalysisLevel(d["analysis"]["level_used"])
        an_res = AnalysisResult(
            status=status_enum,
            level_used=level_enum,
            reason=d["analysis"]["reason"],
            state=d.get("formal_state", "q0"),
            symbol=d.get("symbol", ""),
            confidence_score=d["analysis"]["confidence_score"],
            model_version=d["model_version"],
        )
        
        beh_class = BehavioralClassification(d["security"]["classification"])
        sev = SeverityLevel(d["security"]["severity"])
        reasons = [ReasonCode(r) for r in d["security"]["reason_codes"]]

        sec_assess = SecurityAssessment(
            session_id=d["session_id"],
            model_version=d["model_version"],
            analysis_status=status_enum,
            novelty_status="KNOWN" if status_enum == AnalysisStatus.KNOWN else "NOVEL",
            structural_status="VALID",
            behavioral_classification=beh_class,
            severity=sev,
            risk_score=d["security"]["risk_score"],
            reason_codes=reasons,
        )

        return ProtocolEvent(
            event_id=d["event_id"],
            session_id=d["session_id"],
            protocol=d["protocol"],
            direction=d["direction"],
            symbol=d["symbol"],
            formal_state=d["formal_state"],
            model_version=d["model_version"],
            analysis_result=an_res,
            security_assessment=sec_assess,
            timestamp=d["timestamp"],
            processing_latency_ms=d.get("processing_latency_ms", 0.0),
            raw_payload_snippet=d.get("raw_payload_snippet", ""),
        )

    def _deserialize_alert(self, d: dict[str, Any]) -> SecurityAlert:
        sev = SeverityLevel(d.get("severity", "HIGH"))
        cls = BehavioralClassification(d.get("classification", "POTENTIAL_ATTACK"))
        reasons = [ReasonCode(r) for r in d.get("reason_codes", [])]
        return SecurityAlert(
            alert_id=d["alert_id"],
            session_id=d["session_id"],
            severity=sev,
            classification=cls,
            model_version=d.get("model_version", "v1.0.0"),
            current_state=d.get("current_state", "q0"),
            triggering_symbol=d.get("triggering_symbol", ""),
            reason_codes=reasons,
            evidence=d.get("evidence", {}),
            timestamp=d.get("timestamp", ""),
        )


class InMemoryEventStore(SQLiteEventStore):
    """Convenience subclass for in-memory event storage."""
    def __init__(self) -> None:
        super().__init__(db_path=":memory:")
