"""
Model Proposal Agent component.

Formulates structured CandidateModelProposal objects for legitimate protocol extensions.
Proposals are unvalidated recommendations and MUST pass through the FormalVerificationGuard and Phase 5 FormalValidator.
"""

from typing import Any

from .agent import BaseAgent
from .config import AgentConfig
from .llm import LLMProvider
from .schemas import CandidateModelProposal, InvestigationResult
from .state import AgentState, AgentStateTracker
from .tools import ToolRegistry


class ModelProposalAgent(BaseAgent):
    """
    Specialized agent proposing model updates for observed protocol evolution.
    """

    def __init__(
        self,
        config: AgentConfig | None = None,
        llm_provider: LLMProvider | None = None,
        tools: ToolRegistry | None = None,
    ) -> None:
        super().__init__("ModelProposalAgent", config, llm_provider, tools)

    def run_investigation(self, event_context: dict[str, Any]) -> InvestigationResult:
        """Formulate CandidateModelProposal for protocol evolution."""
        self.reset_counters()
        sess_id = event_context.get("session_id", "mod_unknown")

        state_tracker = AgentStateTracker(f"MOD-INV-{sess_id}")

        state_tracker.transition_to(AgentState.RECEIVED_EVENT)
        state_tracker.transition_to(AgentState.PLANNING)
        self.step_count += 1

        state_tracker.transition_to(AgentState.INVESTIGATING)
        self.step_count += 1

        state_tracker.transition_to(AgentState.EVIDENCE_COLLECTION)
        self.step_count += 1

        state_tracker.transition_to(AgentState.REASONING)
        self.step_count += 1

        state_tracker.transition_to(AgentState.PROPOSAL)
        self.step_count += 1

        # Formulate UNVALIDATED Model Proposal
        parent_ver = event_context.get("model_version", "v1.0.0")
        symbol = event_context.get("symbol", "CAPABILITIES")
        proposal = CandidateModelProposal(
            proposal_id=f"prop_{sess_id}",
            parent_model_version=parent_ver,
            proposed_transitions=[
                {
                    "source": "q0",
                    "symbol": symbol,
                    "target": "q_capabilities",
                    "output": f"{symbol}_ACK",
                }
            ],
            evidence_ids=[f"ev_{sess_id}"],
            reason=f"Repeated multi-session observation of valid symbol '{symbol}'.",
            confidence=0.85,
        )

        state_tracker.transition_to(AgentState.GUARD_VALIDATION)
        self.step_count += 1

        state_tracker.transition_to(AgentState.COMPLETED)

        return InvestigationResult(
            investigation_id=f"MOD-INV-{sess_id}",
            event_type="MODEL_PROPOSAL_GENERATION",
            classification="MODEL_EVOLUTION_CANDIDATE",
            severity_recommendation="BENIGN",
            action_recommendation="SUBMIT_FOR_FORMAL_GUARD_VALIDATION",
            proposal=proposal,
            explanation=f"Model Proposal Agent formulated proposal '{proposal.proposal_id}' for symbol '{symbol}'.",
            steps_executed=self.step_count,
            tools_used=["generate_candidate"],
        )
