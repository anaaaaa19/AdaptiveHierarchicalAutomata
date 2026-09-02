"""Unit tests for Grounding & Hallucination Prevention."""

from adaptive_automata.agents import ProtocolAnalystAgent, SecurityInvestigationAgent


def test_agent_hypotheses_explicitly_separated_from_facts():
    agent = SecurityInvestigationAgent()
    res = agent.run_investigation({
        "session_id": "hallucination_test_sess",
        "reason_codes": ["UNKNOWN_TRANSITION"],
        "severity": "MEDIUM",
    })

    # Facts MUST come from tools / formal system
    assert len(res.observed_facts) >= 1
    assert res.observed_facts[0].source_tool == "retrieve_security_assessment"

    # Hypotheses MUST be marked explicitly as AI speculation
    assert len(res.ai_hypotheses) >= 1
    assert res.ai_hypotheses[0].hypothesis_id == "hyp_sec_1"
