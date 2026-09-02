"""Unit tests for Pushdown Automata (PDA) core engine."""

import pytest
from adaptive_automata.core import State, PushdownAutomaton, StackOp, PDAValidationError, InvalidPDAStateError


def test_pda_stack_push_pop():
    s0 = State("q0", is_initial=True)
    s1 = State("q1")
    s2 = State("q2", is_accepting=True)

    pda = PushdownAutomaton[str, str]("BracketMatcher", initial_stack_symbol="$")
    pda.add_state(s0)
    pda.add_state(s1)
    pda.add_state(s2)

    # Transition: q0 --['OPEN', top=$ / PUSH('B')]--> q1
    pda.add_transition(s0, "OPEN", "$", s1, op=StackOp.PUSH, push_symbols=["B"])
    # Transition: q1 --['OPEN', top=B / PUSH('B')]--> q1
    pda.add_transition(s1, "OPEN", "B", s1, op=StackOp.PUSH, push_symbols=["B"])
    # Transition: q1 --['CLOSE', top=B / POP]--> q1
    pda.add_transition(s1, "CLOSE", "B", s1, op=StackOp.POP, pop_count=1)
    # Transition: q1 --['FIN', top=$ / NOP]--> q2
    pda.add_transition(s1, "FIN", "$", s2, op=StackOp.NOP)


    pda.validate()

    # Valid matched sequence: OPEN, OPEN, CLOSE, CLOSE, FIN
    is_acc, final_st, stack_snap, _ = pda.process_sequence(["OPEN", "OPEN", "CLOSE", "CLOSE", "FIN"])
    assert is_acc
    assert final_st == s2
    assert stack_snap == ("$",)


def test_pda_rejection_unmatched():
    s0 = State("q0", is_initial=True)
    s1 = State("q1", is_accepting=True)

    pda = PushdownAutomaton[str, str]("UnmatchedTest")
    pda.add_transition(s0, "PUSH", None, s1, op=StackOp.PUSH, push_symbols=["X"])
    pda.validate()

    is_acc, _, stack_snap, _ = pda.process_sequence(["PUSH"])
    # Rejected because stack contains leftover symbol X and no initial symbol
    assert not is_acc
    assert stack_snap == ("X",)
