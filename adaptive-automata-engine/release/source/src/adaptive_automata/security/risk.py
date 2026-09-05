"""
Session Risk Aggregator.

Aggregates multi-stage behavioral evidence and deviation events across complete protocol sessions
to detect sustained, multi-step attacks.
"""

from typing import Any
from .config import SecurityConfig
from .context import SessionBehaviorContext


class SessionRiskAggregator:
    """
    Session-level risk aggregator evaluating multi-stage protocol behavior.
    """

    def __init__(self, config: SecurityConfig | None = None) -> None:
        self.config = config or SecurityConfig()
        self._contexts: dict[str, SessionBehaviorContext] = {}

    def get_or_create_context(self, session_id: str, model_version: str = "v1.0.0") -> SessionBehaviorContext:
        """Retrieve existing SessionBehaviorContext or create a new one."""
        if session_id not in self._contexts:
            self._contexts[session_id] = SessionBehaviorContext(session_id=session_id, model_version=model_version)
        return self._contexts[session_id]

    def compute_aggregated_session_risk(self, ctx: SessionBehaviorContext) -> tuple[float, list[str]]:
        """
        Compute aggregated session risk score and trigger reasons.

        Returns:
            Tuple of (aggregated_risk_score: float, risk_factors: list[str]).
        """
        score = 0.0
        factors: list[str] = []

        w = self.config.risk_weights

        # Risk Factor 1: Formal Deviation Count
        if ctx.deviations_count > 0:
            dev_score = min(0.5, ctx.deviations_count * w.get("unknown_transition", 0.2))
            score += dev_score
            factors.append(f"Formal deviations encountered (N={ctx.deviations_count})")

        # Risk Factor 2: Repeated Deviations Threshold
        if ctx.deviations_count >= self.config.repetition_threshold:
            score += w.get("repeated_deviation", 0.25)
            factors.append(f"Sustained repeated deviations (N >= {self.config.repetition_threshold})")

        # Risk Factor 3: Unanswered Requests (DoS / Anomalous State Skipping)
        if ctx.unanswered_requests_count > 3:
            score += 0.2
            factors.append(f"Excessive unanswered client requests (N={ctx.unanswered_requests_count})")

        # Risk Factor 4: Abrupt Session Termination without FIN/LOGOUT
        if not ctx.protocol_completed and len(ctx.symbols_history) > 5:
            score += 0.1
            factors.append("Session ended abruptly without formal protocol termination")

        return round(min(1.0, score), 3), factors

    def clear_context(self, session_id: str) -> None:
        """Clear context for completed or closed sessions."""
        self._contexts.pop(session_id, None)
