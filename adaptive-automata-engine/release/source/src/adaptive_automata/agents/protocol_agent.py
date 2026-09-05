"""
Protocol Analyst Agent component.

Investigates protocol behavior, sequence traces, formal analysis levels (DFA/PDA/CFG), state transitions,
and structural validity. Formal analysis results are treated as authoritative facts.
"""

from typing import Any

from .agent import BaseAgent
from .config import AgentConfig
from .llm import LLMProvider
from .schemas import AgentHypothesis, AgentObservation, InvestigationResult
from .state import AgentState, AgentStateTracker
from .tools import ToolRegistry


class ProtocolAnalystAgent(BaseAgent):
    """
    Specialized agent investigating protocol behavior and sequence traces.
    """

    def __init__(
        self,
        config: AgentConfig | None = None,
        llm_provider: LLMProvider | None = None,
        tools: ToolRegistry | None = None,
    ) -> None:
        super().__init__("ProtocolAnalystAgent", config, llm_provider, tools)

    def run_investigation(self, event_context: dict[str, Any]) -> InvestigationResult:
        """Execute bounded investigation of protocol trace/event."""
        self.reset_counters()
        sess_id = event_context.get("session_id", "sess_unknown")

        state_tracker = AgentStateTracker(f"INV-{sess_id}")

        state_tracker.transition_to(AgentState.RECEIVED_EVENT)
        state_tracker.transition_to(AgentState.PLANNING)
        self.step_count += 1

        state_tracker.transition_to(AgentState.INVESTIGATING)
        self.step_count += 1

        # Step 1: Collect Facts from Formal System
        facts: list[AgentObservation] = []
        symbol = event_context.get("symbol", "UNKNOWN_SYMBOL")
        level = event_context.get("level_used", "DFA_MEALY")

        facts.append(
            AgentObservation(
                fact_id="fact_formal_level",
                source_tool="run_hierarchical_analysis",
                description=f"Formal analysis processed trace at level '{level}'.",
                details={"level": level, "symbol": symbol},
            )
        )

        state_tracker.transition_to(AgentState.EVIDENCE_COLLECTION)
        self.step_count += 1

        # Step 2: Formulate AI Hypotheses (Grounded in Facts)
        state_tracker.transition_to(AgentState.REASONING)
        self.step_count += 1

        is_evolution = event_context.get("is_evolution_candidate", False)
        hypotheses = [
            AgentHypothesis(
                hypothesis_id="hyp_proto_1",
                statement="Observed sequence represents legitimate protocol evolution." if is_evolution else "Observed sequence represents unexpected transition deviation.",
                confidence=0.85 if is_evolution else 0.40,
                supporting_fact_ids=["fact_formal_level"],
                reasoning=[f"Symbol '{symbol}' evaluated at level '{level}'."],
            )
        ]

        state_tracker.transition_to(AgentState.COMPLETED)

        return InvestigationResult(
            investigation_id=f"INV-{sess_id}",
            event_type="PROTOCOL_BEHAVIOR_INVESTIGATION",
            classification="NOVEL_PROTOCOL_BEHAVIOR" if is_evolution else "PROTOCOL_DEVIATION",
            observed_facts=facts,
            ai_hypotheses=hypotheses,
            severity_recommendation="LOW" if is_evolution else "MEDIUM",
            action_recommendation="REVIEW_FOR_MODEL_EVOLUTION" if is_evolution else "COLLECT_ADDITIONAL_TRACE_DATA",
            explanation=f"Protocol Analyst Agent investigated session '{sess_id}'. Formal level used: {level}.",
            steps_executed=self.step_count,
            tools_used=["run_hierarchical_analysis"],
        )
