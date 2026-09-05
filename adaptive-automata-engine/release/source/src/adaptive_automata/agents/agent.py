"""
Base Agent Component.

Provides base execution lifecycle, step budget management, prompt injection sanitization,
and controlled tool invocation for all specialized agents.
"""

from abc import ABC, abstractmethod
import re
from typing import Any

from .config import AgentConfig
from .llm import LLMProvider, MockLLMProvider
from .schemas import AgentObservation, InvestigationResult
from .state import AgentState, AgentStateTracker
from .tools import ToolRegistry


class StepBudgetExceededError(Exception):
    """Raised when an agent exceeds its maximum configured step or tool call budget."""
    pass


class BaseAgent(ABC):
    """
    Abstract Base Class for specialized orchestration agents.
    """

    def __init__(
        self,
        name: str,
        config: AgentConfig | None = None,
        llm_provider: LLMProvider | None = None,
        tools: ToolRegistry | None = None,
    ) -> None:
        self.name = name
        self.config = config or AgentConfig()
        self.llm_provider = llm_provider or MockLLMProvider()
        self.tools = tools or ToolRegistry(allow_mutating_tools=False)
        self.step_count = 0
        self.tool_call_count = 0

    def reset_counters(self) -> None:
        """Reset step and tool counters for a new investigation."""
        self.step_count = 0
        self.tool_call_count = 0


    def check_step_budget(self) -> None:
        """
        Verify that agent step budget has not been exceeded.
        Raises StepBudgetExceededError if limit is reached.
        """
        if self.step_count >= self.config.max_steps:
            raise StepBudgetExceededError(
                f"Agent '{self.name}' exceeded maximum allowed step budget ({self.config.max_steps} steps)."
            )
        if self.tool_call_count >= self.config.max_tool_calls:
            raise StepBudgetExceededError(
                f"Agent '{self.name}' exceeded maximum allowed tool call budget ({self.config.max_tool_calls} tool calls)."
            )

    @staticmethod
    def sanitize_protocol_payload(payload: str) -> str:
        """
        Sanitize untrusted protocol payload data to defend against prompt injection.
        Wraps raw content in explicit XML-style delimiters and neutralizes system instruction overrides.
        """
        clean_text = re.sub(r"(?i)(ignore previous instructions|system command|eval|exec|delete model)", "[NEUTRALIZED_TEXT]", payload)
        return f"<untrusted_protocol_payload>\n{clean_text}\n</untrusted_protocol_payload>"

    def execute_tool(self, name: str, **kwargs: Any) -> Any:
        """Execute a controlled tool and update tool call counter."""
        self.check_step_budget()
        self.tool_call_count += 1
        return self.tools.execute_tool(name, **kwargs)

    @abstractmethod
    def run_investigation(self, event_context: dict[str, Any]) -> InvestigationResult:
        """Run bounded investigation workflow and return structured InvestigationResult."""
        pass
