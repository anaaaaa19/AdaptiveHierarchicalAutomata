import pytest
from adaptive_automata.core import State, DFA, DFAValidationError, InvalidStateError


def test_dfa_creation_and_transitions():
    s0 = State("IDLE", is_initial=True)
    s1 = State("SYN_RCVD")
    s2 = State("ESTABLISHED", is_accepting=True)

    dfa = DFA[str]("TCP_Handshake")
    dfa.add_state(s0)
    dfa.add_state(s1)
    dfa.add_state(s2)

    dfa.add_transition(s0, "SYN", s1)
    dfa.add_transition(s1, "ACK", s2)

    dfa.validate()

    assert dfa.initial_state == s0
    assert dfa.accepting_states == {s2}
    assert dfa.states == {s0, s1, s2}
    assert dfa.alphabet == {"SYN", "ACK"}


def test_dfa_sequence_processing_accept():
    s0 = State("CLOSED", is_initial=True)
    s1 = State("OPEN")
    s2 = State("AUTHENTICATED", is_accepting=True)

    dfa = DFA[str]()
    dfa.add_transition(s0, "CONNECT", s1)
    dfa.add_transition(s1, "AUTH_PASS", s2)

    accepted, final_state, trace = dfa.process_sequence(["CONNECT", "AUTH_PASS"])

    assert accepted is True
    assert final_state == s2
    assert len(trace) == 2


def test_dfa_sequence_processing_reject():
    s0 = State("CLOSED", is_initial=True)
    s1 = State("OPEN")
    s2 = State("AUTHENTICATED", is_accepting=True)

    dfa = DFA[str]()
    dfa.add_transition(s0, "CONNECT", s1)

    accepted, final_state, _ = dfa.process_sequence(["CONNECT"])

    assert accepted is False
    assert final_state == s1


def test_dfa_undefined_transition():
    s0 = State("INIT", is_initial=True)
    dfa = DFA[str]()
    dfa.add_state(s0)

    with pytest.raises(InvalidStateError, match="Undefined transition"):
        dfa.step("INVALID_SYMBOL")


def test_dfa_multiple_initial_states_rejected():
    s0 = State("S0", is_initial=True)
    s1 = State("S1", is_initial=True)

    dfa = DFA[str]()
    dfa.add_state(s0)

    with pytest.raises(DFAValidationError, match="already has initial state"):
        dfa.add_state(s1)


def test_dfa_nondeterminism_rejected():
    s0 = State("S0", is_initial=True)
    s1 = State("S1")
    s2 = State("S2")

    dfa = DFA[str]()
    dfa.add_transition(s0, "A", s1)

    with pytest.raises(DFAValidationError, match="Non-deterministic transition"):
        dfa.add_transition(s0, "A", s2)
