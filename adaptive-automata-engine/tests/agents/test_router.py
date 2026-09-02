"""Unit tests for AgentRouter and fallback execution mode."""

import pytest
from adaptive_automata.agents import AgentConfig, AgentMode, AgentRouter, MaxAgentDepthExceededError


def test_agent_router_routing():
    router = AgentRouter()
    res = router.route_and_execute("SECURITY_ALERT", {"session_id": "sess_sec_10", "severity": "HIGH"})

    assert res.event_type == "SECURITY_ALERT_INVESTIGATION"
    assert res.classification == "SUSPICIOUS_PROTOCOL_BEHAVIOR"


def test_agent_router_fallback_mode_when_disabled():
    config = AgentConfig(enabled=False, mode=AgentMode.DISABLED)
    router = AgentRouter(config)

    res = router.route_and_execute("SECURITY_ALERT", {"session_id": "sess_dis_1"})

    assert res.classification == "FORMAL_ONLY_FALLBACK"
    assert "Agent layer is DISABLED" in res.explanation


def test_agent_router_recursion_limit():
    config = AgentConfig(max_agent_depth=2)
    router = AgentRouter(config)

    with pytest.raises(MaxAgentDepthExceededError):
        router.route_and_execute("SECURITY_ALERT", {"session_id": "sess_rec"}, depth=3)
