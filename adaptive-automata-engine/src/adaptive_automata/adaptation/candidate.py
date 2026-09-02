"""
Candidate Model update representation and Adaptation Audit Events.

Represents proposed modifications to active protocol models and structured explainable
adaptation audit log events.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .evidence import BehaviorEvidence
from .lifecycle import AdaptationState


@dataclass(slots=True)
class AdaptationEvent:
    """
    Structured explainable audit event for tracking every model adaptation decision.
    """
    event_id: str
    timestamp: str
    session_id: str
    event_type: str
    state_from: str
    state_to: str
    explanation: str
    evidence_summary: dict[str, Any] = field(default_factory=dict)
    drift_score: float | None = None
    validation_errors: list[str] = field(default_factory=list)
    model_version: str = "v1.0.0"

    def __repr__(self) -> str:
        return (
            f"AdaptationEvent(id='{self.event_id}', type='{self.event_type}', "
            f"state='{self.state_from}'->'{self.state_to}', explanation='{self.explanation}')"
        )


@dataclass(slots=True)
class CandidateModel:
    """
    Proposed candidate model change container.

    Attributes:
        candidate_id: Unique candidate label.
        parent_version: Parent active model version (e.g. 'v1.0.0').
        proposed_transitions: List of (source_state, input_symbol, target_state, output_symbol) tuples.
        supporting_evidence: BehaviorEvidence record supporting this proposal.
        created_at: ISO 8601 creation timestamp.
        lifecycle_state: Current AdaptationState in lifecycle state machine.
        validation_notes: Audit messages generated during review.
    """
    candidate_id: str
    parent_version: str
    proposed_transitions: list[tuple[str, str, str, str]]
    supporting_evidence: BehaviorEvidence
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    lifecycle_state: AdaptationState = AdaptationState.CANDIDATE
    validation_notes: list[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"CandidateModel(id='{self.candidate_id}', parent='{self.parent_version}', "
            f"transitions={len(self.proposed_transitions)}, state={self.lifecycle_state.value})"
        )
