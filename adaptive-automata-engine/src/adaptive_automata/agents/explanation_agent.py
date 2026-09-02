"""
Explanation Agent component.

Converts structured formal analysis evidence, security assessment metrics, and investigation findings
into clear, human-readable narrative reports grounded strictly in empirical facts.
"""

from typing import Any

from .agent import BaseAgent
from .config import AgentConfig
from .llm import LLMProvider
from .schemas import InvestigationResult
from .state import AgentState, AgentStateTracker
from .tools import ToolRegistry


class ExplanationAgent(BaseAgent):
    """
    Specialized agent providing human-readable explanations grounded in formal evidence.
    """

    def __init__(
        self,
        config: AgentConfig | None = None,
        llm_provider: LLMProvider | None = None,
        tools: ToolRegistry | None = None,
    ) -> None:
        super().__init__("ExplanationAgent", config, llm_provider, tools)

    def run_investigation(self, event_context: dict[str, Any]) -> InvestigationResult:
        """Generate human-readable explanation report for an investigation result."""
        self.reset_counters()
        sess_id = event_context.get("session_id", "exp_unknown")

        state_tracker = AgentStateTracker(f"EXP-{sess_id}")

        state_tracker.transition_to(AgentState.RECEIVED_EVENT)
        state_tracker.transition_to(AgentState.PLANNING)
        self.step_count += 1

        state_tracker.transition_to(AgentState.INVESTIGATING)
        self.step_count += 1

        state_tracker.transition_to(AgentState.EVIDENCE_COLLECTION)
        self.step_count += 1

        state_tracker.transition_to(AgentState.REASONING)
        self.step_count += 1

        exp_text = self.llm_provider.generate_explanation(
            prompt=f"Explain investigation findings for session {sess_id}.",
            context=event_context,
        )

        state_tracker.transition_to(AgentState.COMPLETED)

        return InvestigationResult(
            investigation_id=f"EXP-{sess_id}",
            event_type="EXPLANATION_GENERATION",
            classification="EXPLANATION_REPORT",
            severity_recommendation=event_context.get("severity", "BENIGN"),
            action_recommendation="PRESENT_TO_OPERATOR",
            explanation=exp_text,
            steps_executed=self.step_count,
            tools_used=["generate_explanation"],
        )
