"""Unit tests for ExplanationAgent."""

from adaptive_automata.agents import ExplanationAgent


def test_explanation_agent_grounded_text():
    agent = ExplanationAgent()
    res = agent.run_investigation({
        "session_id": "exp_sess_10",
        "symbol": "CAPABILITIES",
        "model_version": "v1.0.0",
        "severity": "LOW",
    })

    assert res.event_type == "EXPLANATION_GENERATION"
    assert "CAPABILITIES" in res.explanation
    assert "v1.0.0" in res.explanation
