"""Unit tests for AgentTool, ToolRegistry, and permission boundary enforcement."""

import pytest
from adaptive_automata.agents import AgentTool, ToolPermission, ToolPermissionError, ToolRegistry


def test_tool_registry_read_only_execution():
    registry = ToolRegistry(allow_mutating_tools=False)
    tool = AgentTool(
        name="read_model",
        description="Reads model info",
        permission=ToolPermission.READ_ONLY,
        func=lambda: "model_v1_info",
    )
    registry.register_tool(tool)

    res = registry.execute_tool("read_model")
    assert res == "model_v1_info"


def test_tool_registry_mutating_tool_blocked_for_agents():
    registry = ToolRegistry(allow_mutating_tools=False)
    mutating_tool = AgentTool(
        name="activate_model",
        description="Mutates live protocol model",
        permission=ToolPermission.MUTATING,
        func=lambda: "ACTIVATED",
    )
    registry.register_tool(mutating_tool)

    with pytest.raises(ToolPermissionError) as exc_info:
        registry.execute_tool("activate_model")

    assert "Unauthorized tool invocation" in str(exc_info.value)
    assert "MUTATING tool" in str(exc_info.value)
