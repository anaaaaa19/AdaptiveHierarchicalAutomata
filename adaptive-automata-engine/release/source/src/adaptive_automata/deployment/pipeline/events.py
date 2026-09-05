"""
Unified Event Data Structures for Phase 8 Real-Time Pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import time
from typing import Any

from adaptive_automata.analysis.escalation import AnalysisResult
from adaptive_automata.security.assessment import SecurityAssessment


@dataclass(slots=True)
class RawPacket:
    """
    Metadata representation of captured network packet.
    Payload is kept trimmed to avoid memory leaks.
    """
    packet_id: str
    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    protocol: str
    timestamp: float
    payload: bytes
    length: int

    @property
    def flow_key(self) -> tuple[str, int, str, int, str]:
        """5-tuple flow direction key."""
        return (self.src_ip, self.src_port, self.dst_ip, self.dst_port, self.protocol)

    @property
    def bidirectional_flow_key(self) -> tuple[frozenset[tuple[str, int]], str]:
        """Canonical bidirectional flow key."""
        endpoint_a = (self.src_ip, self.src_port)
        endpoint_b = (self.dst_ip, self.dst_port)
        return (frozenset([endpoint_a, endpoint_b]), self.protocol)


@dataclass
class ProtocolEvent:
    """
    Unified Event Representation containing full provenance of formal state,
    security analysis, and model versioning.
    """
    event_id: str
    session_id: str
    protocol: str
    direction: str
    symbol: str
    formal_state: str
    model_version: str
    analysis_result: AnalysisResult
    security_assessment: SecurityAssessment
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    processing_latency_ms: float = 0.0
    raw_payload_snippet: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize event to structured dict for API and WebSocket clients."""
        return {
            "event_id": self.event_id,
            "session_id": self.session_id,
            "protocol": self.protocol,
            "direction": self.direction,
            "symbol": self.symbol,
            "formal_state": self.formal_state,
            "model_version": self.model_version,
            "timestamp": self.timestamp,
            "processing_latency_ms": round(self.processing_latency_ms, 4),
            "raw_payload_snippet": self.raw_payload_snippet,
            "analysis": {
                "status": self.analysis_result.status.value if hasattr(self.analysis_result.status, "value") else str(self.analysis_result.status),
                "level_used": self.analysis_result.level_used.value if hasattr(self.analysis_result.level_used, "value") else str(self.analysis_result.level_used),
                "reason": self.analysis_result.reason,
                "confidence_score": self.analysis_result.confidence_score,
            },
            "security": {
                "classification": self.security_assessment.behavioral_classification.value if hasattr(self.security_assessment.behavioral_classification, "value") else str(self.security_assessment.behavioral_classification),
                "severity": self.security_assessment.severity.value if hasattr(self.security_assessment.severity, "value") else str(self.security_assessment.severity),
                "risk_score": self.security_assessment.risk_score,
                "reason_codes": [r.value if hasattr(r, "value") else str(r) for r in self.security_assessment.reason_codes],
            },
        }
