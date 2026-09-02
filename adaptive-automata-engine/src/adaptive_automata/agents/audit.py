"""
Agent Audit Logger component.

Provides structured, immutable AgentAuditLogger audit event logging for all AI agent investigations,
tool invocations, hypothesis generation, and formal guard verification decisions.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class AgentAuditEvent:
    """
    Structured audit event record.
    """
    audit_id: str
    investigation_id: str
    timestamp: str
    agent_name: str
    action_type: str
    tool_name: str | None = None
    input_summary: dict[str, Any] = field(default_factory=dict)
    output_summary: dict[str, Any] = field(default_factory=dict)
    decision: str = ""
    error: str | None = None


class AgentAuditLogger:
    """
    Audit logger recording agent actions and decisions for research traceability and debugging.
    """

    def __init__(self) -> None:
        self._events: list[AgentAuditEvent] = []

    @property
    def events(self) -> list[AgentAuditEvent]:
        return list(self._events)

    def log_event(
        self,
        investigation_id: str,
        agent_name: str,
        action_type: str,
        tool_name: str | None = None,
        input_summary: dict[str, Any] | None = None,
        output_summary: dict[str, Any] | None = None,
        decision: str = "",
        error: str | None = None,
    ) -> AgentAuditEvent:
        """Record structured audit event."""
        evt = AgentAuditEvent(
            audit_id=f"AUD-{len(self._events) + 1:06d}",
            investigation_id=investigation_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_name=agent_name,
            action_type=action_type,
            tool_name=tool_name,
            input_summary=input_summary or {},
            output_summary=output_summary or {},
            decision=decision,
            error=error,
        )
        self._events.append(evt)
        return evt

    def get_events_for_investigation(self, investigation_id: str) -> list[AgentAuditEvent]:
        """Retrieve audit events associated with a specific investigation_id."""
        return [e for e in self._events if e.investigation_id == investigation_id]
