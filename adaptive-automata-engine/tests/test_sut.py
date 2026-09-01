"""Unit tests for System Under Test (SUT) abstraction and MealyMachineSUT simulator."""

import pytest
from adaptive_automata.core import State, MealyMachine
from adaptive_automata.protocol import SystemUnderTest, MealyMachineSUT, create_toy_protocol_sut


def test_toy_protocol_sut_queries():
    sut = create_toy_protocol_sut()

    assert sut.input_alphabet == {"SYN", "ACK", "AUTH", "DATA", "FIN"}
    assert sut.membership_queries_count == 0
    assert sut.total_symbols_queried == 0

    # Test happy path handshake query
    outputs = sut.query(("SYN", "ACK", "AUTH"))
    assert outputs == ("SEND_SYN_ACK", "ALLOCATE_SESSION", "GRANT_TOKEN")
    assert sut.membership_queries_count == 1
    assert sut.total_symbols_queried == 3

    # Test error fallback for invalid transition
    outputs_invalid = sut.query(("ACK",))
    assert outputs_invalid == ("ERROR",)
    assert sut.membership_queries_count == 2
    assert sut.total_symbols_queried == 4


def test_custom_mealy_sut():
    s0 = State("q0", is_initial=True)
    s1 = State("q1")

    mealy = MealyMachine[str, int]("SimpleMealy")
    mealy.add_transition(s0, "a", s1, 100)
    mealy.add_transition(s1, "b", s0, 200)

    sut = MealyMachineSUT(mealy)
    res = sut.query(("a", "b", "a"))
    assert res == (100, 200, 100)
