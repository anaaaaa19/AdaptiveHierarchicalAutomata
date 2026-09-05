"""
Security Investigation Agent component.

Investigates Phase 6 security alerts, multi-stage session context, severity reason codes, and anomaly patterns.
The Phase 6 SecurityAssessment remains authoritative; AI classification serves as an advisory investigation.
"""

from typing import Any

from .agent import BaseAgent
from .config import AgentConfig
from .llm import LLMProvider
from .schemas import AgentHypothesis, AgentObservation, InvestigationResult
from .state import AgentState, AgentStateTracker
from .tools import ToolRegistry


class SecurityInvestigationAgent(BaseAgent):
    """
    Specialized agent investigating security alerts and suspicious protocol behavior.
    """

    def __init__(
        self,
        config: AgentConfig | None = None,
        llm_provider: LLMProvider | None = None,
        tools: ToolRegistry | None = None,
    ) -> None:
        super().__init__("SecurityInvestigationAgent", config, llm_provider, tools)

    def run_investigation(self, event_context: dict[str, Any]) -> InvestigationResult:
        """Execute bounded security investigation."""
        self.reset_counters()
        sess_id = event_context.get("session_id", "sec_unknown")

        state_tracker = AgentStateTracker(f"SEC-INV-{sess_id}")

        state_tracker.transition_to(AgentState.RECEIVED_EVENT)
        state_tracker.transition_to(AgentState.PLANNING)
        self.step_count += 1

        state_tracker.transition_to(AgentState.INVESTIGATING)
        self.step_count += 1

        # Facts from Phase 6 Security System
        reasons = event_context.get("reason_codes", ["UNKNOWN_TRANSITION"])
        severity = event_context.get("severity", "MEDIUM")
        facts = [
            AgentObservation(
                fact_id="fact_sec_assessment",
                source_tool="retrieve_security_assessment",
                description=f"Phase 6 security assessment issued severity '{severity}' with reasons: {reasons}.",
                details={"severity": severity, "reasons": reasons},
            )
        ]

        state_tracker.transition_to(AgentState.EVIDENCE_COLLECTION)
        self.step_count += 1

        state_tracker.transition_to(AgentState.REASONING)
        self.step_count += 1

        hypotheses = [
            AgentHypothesis(
                hypothesis_id="hyp_sec_1",
                statement="Deviations indicate suspicious state manipulation attack." if severity in ("HIGH", "CRITICAL") else "Deviations indicate rare protocol edge case.",
                confidence=0.80 if severity in ("HIGH", "CRITICAL") else 0.50,
                supporting_fact_ids=["fact_sec_assessment"],
                reasoning=[f"Reason codes: {reasons}"],
            )
        ]

        state_tracker.transition_to(AgentState.COMPLETED)

        return InvestigationResult(
            investigation_id=f"SEC-INV-{sess_id}",
            event_type="SECURITY_ALERT_INVESTIGATION",
            classification="SUSPICIOUS_PROTOCOL_BEHAVIOR" if severity in ("HIGH", "CRITICAL") else "BENIGN_PROTOCOL_ANOMALY",
            observed_facts=facts,
            ai_hypotheses=hypotheses,
            severity_recommendation=severity,
            action_recommendation="ISOLATE_SESSION_AND_ALERT_OPERATOR" if severity in ("HIGH", "CRITICAL") else "LOG_AND_MONITOR",
            explanation=f"Security Investigation Agent evaluated alert for session '{sess_id}'. Authoritative Severity: {severity}.",
            steps_executed=self.step_count,
            tools_used=["retrieve_security_assessment"],
        )
