"""
Candidate Model update representation.

Represents a proposed modification to an active protocol model before formal validation
and immutable registration.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Sequence

from .evidence import BehaviorEvidence
from .lifecycle import AdaptationState


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
