"""
Agent Tool System and Permission Boundary.

Provides controlled, typed tool abstractions wrapping underlying Phase 1-6 formal components.
Enforces explicit tool permissions (READ_ONLY, PROPOSAL, MUTATING) to prevent unauthorized mutations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class ToolPermissionError(Exception):
    """Raised when an agent attempts to execute a tool exceeding its permission level."""
    pass


class ToolPermission(str, Enum):
    """Permission level assigned to agent tools."""
    READ_ONLY = "READ_ONLY"
    PROPOSAL = "PROPOSAL"
    MUTATING = "MUTATING"


@dataclass(slots=True)
class AgentTool:
    """
    Controlled tool wrapper wrapping a system function.
    """
    name: str
    description: str
    permission: ToolPermission
    func: Callable[..., Any]
    input_schema: dict[str, str] = field(default_factory=dict)
    output_schema: dict[str, str] = field(default_factory=dict)

    def execute(self, **kwargs: Any) -> Any:
        """Execute the underlying function with supplied keyword arguments."""
        return self.func(**kwargs)


class ToolRegistry:
    """
    Registry container managing tools and enforcing permission boundaries.
    """

    def __init__(self, allow_mutating_tools: bool = False) -> None:
        self.allow_mutating_tools = allow_mutating_tools
        self._tools: dict[str, AgentTool] = {}

    def register_tool(self, tool: AgentTool) -> None:
        """Register an AgentTool in the registry."""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> AgentTool:
        """Retrieve tool by name."""
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found in registry.")
        return self._tools[name]

    def execute_tool(self, name: str, **kwargs: Any) -> Any:
        """
        Execute tool after verifying permission boundaries.
        Raises ToolPermissionError if a MUTATING tool is invoked when prohibited.
        """
        tool = self.get_tool(name)

        if tool.permission == ToolPermission.MUTATING and not self.allow_mutating_tools:
            raise ToolPermissionError(
                f"Unauthorized tool invocation: '{name}' is a MUTATING tool. "
                "AI agents are strictly prohibited from executing model mutation tools."
            )

        return tool.execute(**kwargs)

    def list_tools(self) -> list[dict[str, str]]:
        """List registered tools and descriptions."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "permission": t.permission.value,
            }
            for t in self._tools.values()
        ]
