"""Unit tests for Agent Safety Boundaries & Step Budget Enforcement."""

import pytest
from adaptive_automata.agents import AgentConfig, ProtocolAnalystAgent, StepBudgetExceededError, ToolRegistry


def test_agent_step_budget_enforcement():
    config = AgentConfig(max_steps=1)
    agent = ProtocolAnalystAgent(config)
    agent.step_count = 1

    with pytest.raises(StepBudgetExceededError) as exc_info:
        agent.check_step_budget()

    assert "exceeded maximum allowed step budget" in str(exc_info.value)


def test_agent_tool_registry_has_no_mutating_tools_by_default():
    agent = ProtocolAnalystAgent()
    tools = agent.tools.list_tools()

    mutating = [t for t in tools if t["permission"] == "MUTATING"]
    assert len(mutating) == 0  # Zero mutating tools exposed to agent!
