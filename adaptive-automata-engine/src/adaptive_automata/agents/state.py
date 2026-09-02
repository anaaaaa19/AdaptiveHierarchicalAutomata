"""
Agent State Machine and Lifecycle Tracker.

Enforces valid state transitions for agent workflows, preventing illegal state shortcuts
(e.g., jumping from RECEIVED_EVENT directly to MODEL_UPDATED or PROPOSAL).
"""

from enum import Enum


class InvalidAgentStateTransitionError(Exception):
    """Raised when an illegal lifecycle transition is attempted in an agent workflow."""
    pass


class AgentState(str, Enum):
    """Lifecycle states for agentic workflows."""
    IDLE = "IDLE"
    RECEIVED_EVENT = "RECEIVED_EVENT"
    PLANNING = "PLANNING"
    INVESTIGATING = "INVESTIGATING"
    EVIDENCE_COLLECTION = "EVIDENCE_COLLECTION"
    REASONING = "REASONING"
    PROPOSAL = "PROPOSAL"
    GUARD_VALIDATION = "GUARD_VALIDATION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentStateTracker:
    """
    Tracks and enforces valid state transitions for an active agent investigation.
    """

    _LEGAL_TRANSITIONS: dict[AgentState, set[AgentState]] = {
        AgentState.IDLE: {AgentState.RECEIVED_EVENT},
        AgentState.RECEIVED_EVENT: {AgentState.PLANNING, AgentState.FAILED},
        AgentState.PLANNING: {AgentState.INVESTIGATING, AgentState.FAILED},
        AgentState.INVESTIGATING: {AgentState.EVIDENCE_COLLECTION, AgentState.FAILED},
        AgentState.EVIDENCE_COLLECTION: {AgentState.REASONING, AgentState.FAILED},
        AgentState.REASONING: {AgentState.PROPOSAL, AgentState.COMPLETED, AgentState.FAILED},
        AgentState.PROPOSAL: {AgentState.GUARD_VALIDATION, AgentState.FAILED},
        AgentState.GUARD_VALIDATION: {AgentState.COMPLETED, AgentState.FAILED},
        AgentState.COMPLETED: {AgentState.IDLE},
        AgentState.FAILED: {AgentState.IDLE},
    }

    def __init__(self, investigation_id: str) -> None:
        self.investigation_id = investigation_id
        self._current_state = AgentState.IDLE
        self._history: list[AgentState] = [AgentState.IDLE]

    @property
    def current_state(self) -> AgentState:
        return self._current_state

    @property
    def history(self) -> list[AgentState]:
        return list(self._history)

    def transition_to(self, new_state: AgentState) -> None:
        """
        Transition agent workflow to a new state.
        Raises InvalidAgentStateTransitionError if transition is illegal.
        """
        allowed = self._LEGAL_TRANSITIONS.get(self._current_state, set())
        if new_state not in allowed:
            raise InvalidAgentStateTransitionError(
                f"Illegal agent state transition from '{self._current_state.value}' to '{new_state.value}' "
                f"in investigation '{self.investigation_id}'. Allowed: {[s.value for s in allowed]}"
            )

        self._current_state = new_state
        self._history.append(new_state)

    def reset(self) -> None:
        """Reset state machine back to IDLE."""
        self._current_state = AgentState.IDLE
        self._history = [AgentState.IDLE]

    def __repr__(self) -> str:
        return f"AgentStateTracker(id='{self.investigation_id}', state={self._current_state.value})"
