"""Unit tests for AgentStateTracker and lifecycle state transitions."""

import pytest
from adaptive_automata.agents import AgentState, AgentStateTracker, InvalidAgentStateTransitionError


def test_valid_agent_state_transitions():
    tracker = AgentStateTracker("INV-001")
    assert tracker.current_state == AgentState.IDLE

    tracker.transition_to(AgentState.RECEIVED_EVENT)
    tracker.transition_to(AgentState.PLANNING)
    tracker.transition_to(AgentState.INVESTIGATING)
    tracker.transition_to(AgentState.EVIDENCE_COLLECTION)
    tracker.transition_to(AgentState.REASONING)
    tracker.transition_to(AgentState.COMPLETED)

    assert tracker.current_state == AgentState.COMPLETED
    assert len(tracker.history) == 7


def test_invalid_agent_state_shortcut_raises_error():
    tracker = AgentStateTracker("INV-002")

    # Direct shortcut from RECEIVED_EVENT to PROPOSAL is illegal!
    tracker.transition_to(AgentState.RECEIVED_EVENT)
    with pytest.raises(InvalidAgentStateTransitionError) as exc_info:
        tracker.transition_to(AgentState.PROPOSAL)

    assert "Illegal agent state transition" in str(exc_info.value)
