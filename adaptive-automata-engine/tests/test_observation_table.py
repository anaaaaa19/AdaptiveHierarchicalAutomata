"""Unit tests for ObservationTable data structure and hypothesis construction."""

import pytest
from adaptive_automata.protocol import create_toy_protocol_sut
from adaptive_automata.learning.observation_table import ObservationTable


def test_observation_table_initialization():
    alphabet = ["SYN", "ACK", "AUTH"]
    table = ObservationTable[str, str](alphabet)

    assert table.S == [()]
    assert table.E == [("ACK",), ("AUTH",), ("SYN",)]  # sorted order
    assert len(table.S_dot_Sigma) == 3


def test_observation_table_update_and_closedness():
    sut = create_toy_protocol_sut()
    table = ObservationTable[str, str](sut.input_alphabet)

    # Initial table population
    queries = table.update(sut)
    assert queries > 0

    # Initially non-closed
    assert not table.is_closed()
    unclosed = table.find_unclosed_prefix()
    assert unclosed is not None

    # Make closed
    was_modified = table.make_closed(sut)
    assert was_modified
    assert table.is_closed()


def test_hypothesis_generation_from_table():
    sut = create_toy_protocol_sut()
    table = ObservationTable[str, str](sut.input_alphabet)

    table.update(sut)
    table.make_closed(sut)
    table.make_consistent(sut)

    # Convert to hypothesis Mealy Machine
    hypothesis = table.to_mealy_machine()
    assert hypothesis.initial_state is not None
    assert len(hypothesis.states) >= 1
    assert hypothesis.input_alphabet == sut.input_alphabet
