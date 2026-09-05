"""
Session Behavior Context.

Maintains light-weight, deterministic sequence context across multi-step protocol sessions,
enabling context-aware behavioral evaluation rather than single-symbol inspection.
"""

from dataclasses import dataclass, field
import time
from typing import Any


@dataclass(slots=True)
class SessionBehaviorContext:
    """
    State container tracking progress and deviation history for an ongoing protocol session.

    Attributes:
        session_id: Unique session label.
        model_version: Version tag of model active during session.
        symbols_history: Sequential list of processed input symbols.
        current_formal_state: Active formal automaton state label.
        deviations_count: Count of formal deviations encountered in session.
        recent_deviations: Chronological list of deviation details.
        timestamps: Timestamps of symbol observations.
        protocol_completed: Flag indicating clean protocol completion (e.g. FIN/LOGOUT).
        unanswered_requests_count: Count of client requests awaiting server responses.
    """
    session_id: str
    model_version: str = "v1.0.0"
    symbols_history: list[str] = field(default_factory=list)
    current_formal_state: str = "q0"
    deviations_count: int = 0
    recent_deviations: list[dict[str, Any]] = field(default_factory=list)
    timestamps: list[float] = field(default_factory=list)
    protocol_completed: bool = False
    unanswered_requests_count: int = 0

    def record_step(
        self,
        symbol: str,
        target_state: str | None = None,
        is_deviation: bool = False,
        deviation_details: dict[str, Any] | None = None,
        is_request: bool = False,
        is_response: bool = False,
        is_terminal: bool = False,
    ) -> None:
        """Record an observed symbol and update session context."""
        self.symbols_history.append(symbol)
        self.timestamps.append(time.time())

        if target_state:
            self.current_formal_state = target_state

        if is_deviation:
            self.deviations_count += 1
            details = deviation_details or {}
            details["symbol"] = symbol
            details["position"] = len(self.symbols_history) - 1
            self.recent_deviations.append(details)

        if is_request:
            self.unanswered_requests_count += 1
        elif is_response and self.unanswered_requests_count > 0:
            self.unanswered_requests_count -= 1

        if is_terminal:
            self.protocol_completed = True

    def __repr__(self) -> str:
        return (
            f"SessionBehaviorContext(id='{self.session_id}', len={len(self.symbols_history)}, "
            f"state='{self.current_formal_state}', deviations={self.deviations_count})"
        )
