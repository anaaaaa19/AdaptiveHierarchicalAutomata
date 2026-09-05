"""
Agent Router component.

Determines which specialized agent (ProtocolAnalystAgent, SecurityInvestigationAgent, ModelProposalAgent, ExplanationAgent)
should investigate an event. Prevents uncontrolled agent recursion by enforcing max_agent_depth limit.
"""

from typing import Any

from .agent import BaseAgent
from .config import AgentConfig, AgentMode
from .explanation_agent import ExplanationAgent
from .model_agent import ModelProposalAgent
from .protocol_agent import ProtocolAnalystAgent
from .schemas import InvestigationResult
from .security_agent import SecurityInvestigationAgent


class MaxAgentDepthExceededError(Exception):
    """Raised when agent routing exceeds maximum allowed call depth."""
    pass


class AgentRouter:
    """
    Deterministic router mapping events to specialized agents.
    """

    def __init__(
        self,
        config: AgentConfig | None = None,
        protocol_agent: ProtocolAnalystAgent | None = None,
        security_agent: SecurityInvestigationAgent | None = None,
        model_agent: ModelProposalAgent | None = None,
        explanation_agent: ExplanationAgent | None = None,
    ) -> None:
        self.config = config or AgentConfig()
        self.protocol_agent = protocol_agent or ProtocolAnalystAgent(self.config)
        self.security_agent = security_agent or SecurityInvestigationAgent(self.config)
        self.model_agent = model_agent or ModelProposalAgent(self.config)
        self.explanation_agent = explanation_agent or ExplanationAgent(self.config)

    def route_and_execute(self, event_type: str, event_context: dict[str, Any], depth: int = 1) -> InvestigationResult:
        """
        Route event to appropriate specialized agent and return InvestigationResult.
        Raises MaxAgentDepthExceededError if depth > max_agent_depth.
        """
        if depth > self.config.max_agent_depth:
            raise MaxAgentDepthExceededError(
                f"Agent routing recursion exceeded maximum depth limit ({self.config.max_agent_depth})."
            )

        # Handle Fallback Mode when Agent Layer is DISABLED
        if not self.config.enabled or self.config.mode == AgentMode.DISABLED:
            sess_id = event_context.get("session_id", "fallback_session")
            return InvestigationResult(
                investigation_id=f"FALLBACK-{sess_id}",
                event_type=event_type,
                classification="FORMAL_ONLY_FALLBACK",
                severity_recommendation=event_context.get("severity", "LOW"),
                action_recommendation="FORMAL_PIPELINE_EXECUTION",
                explanation="Agent layer is DISABLED. Formal methods pipeline operating in non-AI fallback mode.",
                steps_executed=0,
                tools_used=[],
            )

        # Route by Event Type
        if event_type in ("SECURITY_ALERT", "SECURITY_ASSESSMENT", "POISONING_SUSPECTED"):
            return self.security_agent.run_investigation(event_context)
        elif event_type in ("MODEL_EVOLUTION_REQUEST", "PROpose_MODEL_UPDATE"):
            return self.model_agent.run_investigation(event_context)
        elif event_type in ("EXPLANATION_REQUEST", "GENERATE_SUMMARY"):
            return self.explanation_agent.run_investigation(event_context)
        else:
            return self.protocol_agent.run_investigation(event_context)
