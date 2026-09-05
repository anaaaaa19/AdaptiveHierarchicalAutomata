"""
Behavioral Evidence Store.

Accumulates observational evidence for novel protocol behaviors over time across multiple dimensions:
observation count, unique session diversity, successful protocol follow-ups, and structural validity.

CRITICAL PRINCIPLE:
Empirical evidence scores measure observational support. They do NOT constitute formal mathematical
proof of correctness.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import time
from typing import Mapping


@dataclass(slots=True)
class BehaviorEvidence:
    """
    Accumulated empirical evidence container for a specific novel protocol transition.

    Attributes:
        behavior_id: Canonical behavior identifier (e.g. 'q2:RENEW_TOKEN').
        source_state: Origin state label.
        input_symbol: Input trigger symbol.
        target_state: Hypothesized target state label.
        output_symbol: Transduction output symbol.
        session_ids: Set of distinct session IDs where behavior was observed.
        first_seen: ISO 8601 timestamp of first observation.
        last_seen: ISO 8601 timestamp of most recent observation.
        observation_count: Total raw observation count (N).
        unique_session_count: Count of distinct sessions observing behavior.
        successful_followup_count: Count of sessions successfully completing after behavior.
        structural_validation_count: Count of formal PDA/CFG structural validations.
        model_version: Baseline model version when evidence collection began.
        timestamps: Chronological epoch timestamps of observations.
    """
    behavior_id: str
    source_state: str
    input_symbol: str
    target_state: str | None = None
    output_symbol: str | None = None
    session_ids: set[str] = field(default_factory=set)
    first_seen: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    observation_count: int = 0
    unique_session_count: int = 0
    successful_followup_count: int = 0
    structural_validation_count: int = 0
    model_version: str = "v1.0.0"
    timestamps: list[float] = field(default_factory=list)

    def calculate_evidence_score(self) -> float:
        """
        Calculate multi-dimensional empirical evidence score in [0.0, 1.0].

        Note: Empirical evidence strength is an observational heuristic, NOT formal mathematical correctness.
        """
        if self.observation_count == 0:
            return 0.0

        # Frequency component (capped log scaling)
        freq_factor = min(1.0, self.observation_count / 10.0)
        # Session diversity component
        sess_factor = min(1.0, self.unique_session_count / 5.0)
        # Followup success ratio
        followup_ratio = self.successful_followup_count / self.observation_count if self.observation_count > 0 else 0.0

        score = (0.3 * freq_factor) + (0.4 * sess_factor) + (0.3 * followup_ratio)
        return round(score, 3)

    def __repr__(self) -> str:
        return (
            f"BehaviorEvidence(id='{self.behavior_id}', N={self.observation_count}, "
            f"sessions={self.unique_session_count}, followups={self.successful_followup_count}, "
            f"score={self.calculate_evidence_score():.3f})"
        )


class EvidenceStore:
    """
    In-memory evidence aggregation store.
    """

    def __init__(self) -> None:
        self._store: dict[str, BehaviorEvidence] = {}

    def record_observation(
        self,
        session_id: str,
        source_state: str,
        input_symbol: str,
        target_state: str | None = None,
        output_symbol: str | None = None,
        model_version: str = "v1.0.0",
        follows_up_successfully: bool = False,
        structurally_valid: bool = False,
    ) -> BehaviorEvidence:
        """
        Record a new behavioral observation and update aggregated evidence counters.
        """
        behavior_id = f"{source_state}:{input_symbol}"
        now_str = datetime.now(timezone.utc).isoformat()
        now_ts = time()

        if behavior_id not in self._store:
            self._store[behavior_id] = BehaviorEvidence(
                behavior_id=behavior_id,
                source_state=source_state,
                input_symbol=input_symbol,
                target_state=target_state,
                output_symbol=output_symbol,
                session_ids={session_id},
                first_seen=now_str,
                last_seen=now_str,
                observation_count=1,
                unique_session_count=1,
                successful_followup_count=1 if follows_up_successfully else 0,
                structural_validation_count=1 if structurally_valid else 0,
                model_version=model_version,
                timestamps=[now_ts],
            )
        else:
            ev = self._store[behavior_id]
            ev.session_ids.add(session_id)
            ev.last_seen = now_str
            ev.observation_count += 1
            ev.unique_session_count = len(ev.session_ids)
            if follows_up_successfully:
                ev.successful_followup_count += 1
            if structurally_valid:
                ev.structural_validation_count += 1
            ev.timestamps.append(now_ts)
            if target_state:
                ev.target_state = target_state
            if output_symbol:
                ev.output_symbol = output_symbol

        return self._store[behavior_id]

    def get_evidence(self, behavior_id: str) -> BehaviorEvidence | None:
        """Retrieve aggregated evidence for a behavior identifier."""
        return self._store.get(behavior_id)

    def list_all_evidence(self) -> list[BehaviorEvidence]:
        """List all collected behavior evidence records."""
        return list(self._store.values())
