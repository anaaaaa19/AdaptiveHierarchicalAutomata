"""
Investigation Planner component.

Generates explicit, step-bounded investigation plans (InvestigationPlan) to guide agent execution workflows
without entering runaway loops.
"""

from typing import Any
from .config import AgentConfig
from .schemas import InvestigationPlan


class InvestigationPlanner:
    """
    Planner generating bounded investigation plans.
    """

    def __init__(self, config: AgentConfig | None = None) -> None:
        self.config = config or AgentConfig()

    def create_plan(self, event_type: str, session_id: str, context: dict[str, Any] | None = None) -> InvestigationPlan:
        """
        Generate explicit, bounded InvestigationPlan based on target event type.
        """
        inv_id = f"INV-{session_id}"
        ctx = context or {}

        if event_type == "SECURITY_ALERT":
            steps = [
                "retrieve_security_alert",
                "retrieve_security_assessment",
                "inspect_session",
                "get_behavior_evidence",
            ]
        elif event_type == "MODEL_EVOLUTION":
            steps = [
                "get_current_model",
                "inspect_session",
                "run_dfa_analysis",
                "get_behavior_evidence",
                "generate_candidate",
                "validate_candidate",
            ]
        else:
            steps = [
                "get_current_model",
                "inspect_session",
                "run_dfa_analysis",
            ]

        return InvestigationPlan(
            investigation_id=inv_id,
            target_event=event_type,
            steps=steps[: self.config.max_steps],
            max_steps=self.config.max_steps,
        )
