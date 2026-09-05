"""
LLM Provider Abstraction & Mock Provider.

Provides vendor-agnostic LLMProvider interface and a deterministic MockLLMProvider for offline testing.
All unit tests and benchmarks execute offline without external network or LLM API key dependencies.
"""

from abc import ABC, abstractmethod
import json
from typing import Any


class LLMProvider(ABC):
    """
    Abstract LLM Provider interface.
    """

    @abstractmethod
    def generate_structured(self, prompt: str, schema_name: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Generate structured JSON response adhering to named schema."""
        pass

    @abstractmethod
    def generate_explanation(self, prompt: str, context: dict[str, Any] | None = None) -> str:
        """Generate human-readable text explanation grounded in formal context."""
        pass


class MockLLMProvider(LLMProvider):
    """
    Deterministic Mock LLM Provider for testing and reproducible research evaluation.
    """

    def __init__(self, override_responses: dict[str, Any] | None = None) -> None:
        self.override_responses = override_responses or {}

    def generate_structured(self, prompt: str, schema_name: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Return deterministic scenario-based structured response."""
        if schema_name in self.override_responses:
            return dict(self.override_responses[schema_name])

        ctx = context or {}
        event = ctx.get("event_type", "UNKNOWN_EVENT")
        session_id = ctx.get("session_id", "mock_session")

        if schema_name == "InvestigationPlan":
            return {
                "investigation_id": f"INV-{session_id}",
                "target_event": event,
                "steps": [
                    "get_current_model",
                    "inspect_session",
                    "run_dfa_analysis",
                    "get_behavior_evidence",
                    "get_drift_result",
                ],
                "max_steps": 10,
            }

        elif schema_name == "CandidateModelProposal":
            return {
                "proposal_id": f"prop_{session_id}",
                "parent_model_version": ctx.get("model_version", "v1.0.0"),
                "proposed_transitions": [
                    {
                        "source": "q0",
                        "symbol": ctx.get("symbol", "CAPABILITIES"),
                        "target": "q_capabilities",
                        "output": "CAPABILITIES_ACK",
                    }
                ],
                "evidence_ids": [f"ev_{session_id}"],
                "reason": f"Observed legitimate protocol extension '{ctx.get('symbol', 'CAPABILITIES')}' across multiple sessions.",
                "confidence": 0.85,
            }

        elif schema_name == "InvestigationResult":
            return {
                "investigation_id": f"INV-{session_id}",
                "event_type": event,
                "classification": "NOVEL_BUT_PLAUSIBLY_LEGITIMATE" if "CAPABILITIES" in prompt else "SUSPICIOUS_PROTOCOL_BEHAVIOR",
                "observed_facts": [
                    {
                        "fact_id": "fact_1",
                        "source_tool": "run_dfa_analysis",
                        "description": f"Observed symbol '{ctx.get('symbol', 'CAPABILITIES')}' not present in model v1.",
                    }
                ],
                "ai_hypotheses": [
                    {
                        "hypothesis_id": "hyp_1",
                        "statement": "Symbol may represent valid protocol extension.",
                        "confidence": 0.85,
                        "supporting_fact_ids": ["fact_1"],
                        "reasoning": ["Observed repeatedly", "Passed structural check"],
                    }
                ],
                "severity_recommendation": "LOW" if "CAPABILITIES" in prompt else "HIGH",
                "action_recommendation": "PROPOSE_MODEL_UPDATE" if "CAPABILITIES" in prompt else "COLLECT_ADDITIONAL_CONTEXT",
                "explanation": f"Investigation of session '{session_id}' completed cleanly.",
            }

        # Generic structured fallback
        return {
            "status": "SUCCESS",
            "schema": schema_name,
            "message": "Deterministic mock provider fallback response.",
        }

    def generate_explanation(self, prompt: str, context: dict[str, Any] | None = None) -> str:
        """Return grounded text explanation."""
        if "explanation" in self.override_responses:
            return str(self.override_responses["explanation"])

        ctx = context or {}
        session_id = ctx.get("session_id", "session_1")
        symbol = ctx.get("symbol", "UNKNOWN_SYMBOL")
        model_ver = ctx.get("model_version", "v1.0.0")

        return (
            f"Protocol session '{session_id}' observed symbol '{symbol}' which is not present in active model '{model_ver}'. "
            "Formal hierarchical analysis evaluated the sequence and verified structural integrity. "
            "All conclusions are grounded strictly in tool-derived evidence."
        )
