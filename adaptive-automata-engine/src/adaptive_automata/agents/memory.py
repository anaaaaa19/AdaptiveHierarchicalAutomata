"""
Controlled Agent Memory Abstraction.

Provides bounded, structured memory storage for agent observations, tool execution results,
and investigation records. Arbitrary sensitive raw payloads are excluded.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .schemas import AgentHypothesis, AgentObservation, CandidateModelProposal, InvestigationResult


@dataclass(slots=True)
class InvestigationRecord:
    """
    Structured investigation memory record.
    """
    investigation_id: str
    event_id: str
    model_version: str
    observations: list[AgentObservation] = field(default_factory=list)
    hypotheses: list[AgentHypothesis] = field(default_factory=list)
    proposal: CandidateModelProposal | None = None
    final_result: InvestigationResult | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AgentMemory:
    """
    Controlled memory container mapping investigation_id to InvestigationRecord.
    """

    def __init__(self) -> None:
        self._records: dict[str, InvestigationRecord] = {}

    def get_or_create_record(self, investigation_id: str, event_id: str = "evt_0", model_version: str = "v1.0.0") -> InvestigationRecord:
        """Retrieve existing InvestigationRecord or create a new one."""
        if investigation_id not in self._records:
            self._records[investigation_id] = InvestigationRecord(
                investigation_id=investigation_id,
                event_id=event_id,
                model_version=model_version,
            )
        return self._records[investigation_id]

    def store_result(self, result: InvestigationResult) -> None:
        """Store completed InvestigationResult into memory."""
        rec = self.get_or_create_record(result.investigation_id)
        rec.final_result = result
        rec.observations.extend(result.observed_facts)
        rec.hypotheses.extend(result.ai_hypotheses)
        rec.proposal = result.proposal

    def clear(self) -> None:
        """Clear memory contents."""
        self._records.clear()
