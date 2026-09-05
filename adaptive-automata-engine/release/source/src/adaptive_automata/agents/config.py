"""
Agentic AI Orchestration Layer Configuration.

Provides AgentConfig and AgentMode abstractions to configure agent behavior, step limits,
permission boundaries, human-in-the-loop approvals, and provider modes.
"""

from dataclasses import dataclass, field
from enum import Enum


class AgentMode(str, Enum):
    """
    Operation modes for the Agentic AI Orchestration Layer.

    DISABLED: Agent layer completely bypassed (Formal Phases 1-6 operate normally).
    ADVISORY: AI can investigate, summarize evidence, and explain alerts. No proposals.
    ASSISTED: AI can investigate, summarize, and generate validated proposals requiring human approval.
    CONTROLLED_AUTOMATION: AI can generate validated proposals passing all policy and formal guards.
    """
    DISABLED = "DISABLED"
    ADVISORY = "ADVISORY"
    ASSISTED = "ASSISTED"
    CONTROLLED_AUTOMATION = "CONTROLLED_AUTOMATION"


@dataclass(slots=True)
class AgentConfig:
    """
    Configuration parameters for the Phase 7 Agentic AI Orchestration Layer.
    """
    enabled: bool = True
    mode: AgentMode = AgentMode.ASSISTED
    max_steps: int = 10
    max_tool_calls: int = 20
    max_agent_depth: int = 2
    timeout_seconds: float = 60.0
    human_approval_required: bool = True
    allow_model_proposals: bool = True
    allow_automation: bool = False
    provider_name: str = "mock"
    temperature: float = 0.0

    def __repr__(self) -> str:
        return (
            f"AgentConfig(mode={self.mode.value}, max_steps={self.max_steps}, "
            f"max_tools={self.max_tool_calls}, human_approval={self.human_approval_required})"
        )
