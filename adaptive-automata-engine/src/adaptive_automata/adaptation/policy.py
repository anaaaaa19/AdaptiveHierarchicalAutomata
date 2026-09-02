"""
Adaptation Policy and Poisoning-Resistant Defense component.

Decides whether accumulated behavioral evidence is sufficient to propose and evaluate a candidate model update.

CRITICAL SAFETY PRINCIPLE:
Frequency alone MUST NEVER BE SUFFICIENT for a model update.
Requires multi-dimensional evidence: frequency + session diversity + successful protocol follow-ups + structural validity.
"""

from enum import Enum
from .evidence import BehaviorEvidence


class EvidenceStrength(str, Enum):
    """Classification of evidence strength."""
    LOW = "LOW"         # Monitor only (insufficient evidence)
    MEDIUM = "MEDIUM"   # Propose candidate for review
    HIGH = "HIGH"       # Propose candidate + trigger formal validation


class AdaptationPolicy:
    """
    Poisoning-resistant multi-dimensional adaptation policy.
    """

    def __init__(
        self,
        min_observations: int = 5,
        min_unique_sessions: int = 3,
        min_successful_followups: int = 2,
        require_structural_validation: bool = True,
    ) -> None:
        self.min_observations = min_observations
        self.min_unique_sessions = min_unique_sessions
        self.min_successful_followups = min_successful_followups
        self.require_structural_validation = require_structural_validation

    def evaluate_evidence_strength(self, evidence: BehaviorEvidence) -> EvidenceStrength:
        """
        Evaluate overall evidence strength across multiple dimensions.
        """
        score = evidence.calculate_evidence_score()

        if (
            evidence.observation_count >= self.min_observations
            and evidence.unique_session_count >= self.min_unique_sessions
            and evidence.successful_followup_count >= self.min_successful_followups
        ):
            return EvidenceStrength.HIGH
        elif evidence.observation_count >= 3 and evidence.unique_session_count >= 2:
            return EvidenceStrength.MEDIUM
        else:
            return EvidenceStrength.LOW

    def should_propose_candidate(self, evidence: BehaviorEvidence) -> tuple[bool, str]:
        """
        Evaluate whether evidence satisfies multi-dimensional criteria to propose a CandidateModel.

        Returns:
            Tuple of (should_propose: bool, explanation_reason: str).
        """
        # Dimension 1: Frequency
        if evidence.observation_count < self.min_observations:
            return False, f"Insufficient observation count: N={evidence.observation_count} < {self.min_observations}."

        # Dimension 2: Session Diversity (Poisoning Defense!)
        if evidence.unique_session_count < self.min_unique_sessions:
            return (
                False,
                f"Poisoning Defense Triggered: Insufficient session diversity "
                f"(observed in {evidence.unique_session_count} sessions, required {self.min_unique_sessions}). "
                f"High-frequency single-session behavior is blocked as potential poisoning."
            )

        # Dimension 3: Successful Protocol Follow-up
        if evidence.successful_followup_count < self.min_successful_followups:
            return (
                False,
                f"Insufficient successful protocol follow-ups "
                f"({evidence.successful_followup_count} < {self.min_successful_followups})."
            )

        # Dimension 4: Structural Validation
        if self.require_structural_validation and evidence.structural_validation_count == 0:
            return False, "Behavior lacks formal structural validation (PDA/CFG)."

        return True, "Multi-dimensional evidence criteria satisfied cleanly."
