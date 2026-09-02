"""Unit tests for ProtocolAnalystAgent."""

from adaptive_automata.agents import ProtocolAnalystAgent


def test_protocol_analyst_agent_investigation():
    agent = ProtocolAnalystAgent()
    res = agent.run_investigation({
        "session_id": "proto_sess_1",
        "symbol": "CAPABILITIES",
        "level_used": "PDA",
        "is_evolution_candidate": True,
    })

    assert res.event_type == "PROTOCOL_BEHAVIOR_INVESTIGATION"
    assert res.classification == "NOVEL_PROTOCOL_BEHAVIOR"
    assert len(res.observed_facts) == 1
    assert len(res.ai_hypotheses) == 1
    assert res.ai_hypotheses[0].confidence == 0.85
