"""
Security Assessment Data Container.

Represents behavioral security classifications, explainable reason codes, severity levels,
and comprehensive risk evidence produced by the Phase 6 Cybersecurity Layer.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from adaptive_automata.analysis.escalation import AnalysisStatus
from adaptive_automata.adaptation.novelty import NoveltyStatus


class SeverityLevel(str, Enum):
    """Explaining cybersecurity severity levels."""
    BENIGN = "BENIGN"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class BehavioralClassification(str, Enum):
    """Formal behavioral cybersecurity classification tags."""
    KNOWN = "KNOWN"
    NOVEL = "NOVEL"
    PROTOCOL_VIOLATION = "PROTOCOL_VIOLATION"
    SUSPICIOUS = "SUSPICIOUS"
    POTENTIAL_ATTACK = "POTENTIAL_ATTACK"
    UNKNOWN = "UNKNOWN"


class ReasonCode(str, Enum):
    """Explicit, explainable reason codes for security assessments and alerts."""
    UNKNOWN_TRANSITION = "UNKNOWN_TRANSITION"
    INVALID_STATE_SEQUENCE = "INVALID_STATE_SEQUENCE"
    STRUCTURAL_VIOLATION = "STRUCTURAL_VIOLATION"
    UNEXPECTED_MESSAGE = "UNEXPECTED_MESSAGE"
    UNEXPECTED_NESTING = "UNEXPECTED_NESTING"
    INVALID_PROTOCOL_ORDER = "INVALID_PROTOCOL_ORDER"
    RARE_BEHAVIOR = "RARE_BEHAVIOR"
    SUSTAINED_NOVEL_BEHAVIOR = "SUSTAINED_NOVEL_BEHAVIOR"
    MODEL_DRIFT = "MODEL_DRIFT"
    MULTI_STAGE_DEVIATION = "MULTI_STAGE_DEVIATION"
    FAILED_VALIDATION = "FAILED_VALIDATION"
    POISONING_SUSPECTED = "POISONING_SUSPECTED"


@dataclass(slots=True)
class SecurityAssessment:
    """
    Complete security evaluation result sitting above Phase 4 AnalysisResult and Phase 5 Novelty.

    Attributes:
        session_id: Target session identifier.
        model_version: Active protocol model version during evaluation.
        analysis_status: Underlying Phase 4 formal analysis status.
        novelty_status: Underlying Phase 5 model-level novelty status.
        structural_status: Description of PDA/CFG structural validity.
        behavioral_classification: Cybersecurity classification tag.
        severity: Assigned SeverityLevel.
        risk_score: Calculated risk score in [0.0, 1.0].
        reason_codes: List of explicit ReasonCode triggers explaining the verdict.
        evidence_details: Supporting metrics and context trace data.
        timestamp: ISO 8601 evaluation timestamp.
    """
    session_id: str
    model_version: str
    analysis_status: AnalysisStatus
    novelty_status: NoveltyStatus
    structural_status: str
    behavioral_classification: BehavioralClassification
    severity: SeverityLevel
    risk_score: float
    reason_codes: list[ReasonCode] = field(default_factory=list)
    evidence_details: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __repr__(self) -> str:
        return (
            f"SecurityAssessment(session='{self.session_id}', class={self.behavioral_classification.value}, "
            f"severity={self.severity.value}, score={self.risk_score:.3f}, reasons={[r.value for r in self.reason_codes]})"
        )
