"""Unit tests for Equivalence Oracles."""

import pytest
from adaptive_automata.core import State, MealyMachine
from adaptive_automata.protocol import create_toy_protocol_sut, MealyMachineSUT
from adaptive_automata.learning.observation_table import ObservationTable
from adaptive_automata.learning.equivalence import (
    RandomSequenceEquivalenceOracle,
    WMethodEquivalenceOracle,
    ExactMealyEquivalenceOracle,
)


def test_exact_mealy_equivalence_oracle():
    sut = create_toy_protocol_sut()

    table = ObservationTable[str, str](sut.input_alphabet)
    table.update(sut)
    table.make_closed(sut)
    table.make_consistent(sut)

    complete_hypothesis = table.to_mealy_machine()

    oracle = ExactMealyEquivalenceOracle[str, str]()
    
    # 1. Complete hypothesis should yield NO counterexample (ce is None)
    ce_none = oracle.find_counterexample(complete_hypothesis, sut)
    assert ce_none is None

    # 2. Build an incomplete dummy single-state hypothesis
    s0 = State("q0", is_initial=True)
    incomplete_hyp = MealyMachine[str, str]("IncompleteHypothesis")
    incomplete_hyp.add_state(s0)
    for sym in sut.input_alphabet:
        incomplete_hyp.add_transition(s0, sym, s0, "WRONG_OUTPUT")
    incomplete_hyp.validate()

    # Incomplete hypothesis should yield a counterexample
    ce_found = oracle.find_counterexample(incomplete_hyp, sut)
    assert ce_found is not None
    assert isinstance(ce_found, tuple)


def test_random_sequence_equivalence_oracle():
    sut = create_toy_protocol_sut()

    s0 = State("q0", is_initial=True)
    incomplete_hyp = MealyMachine[str, str]("IncompleteHypothesis")
    incomplete_hyp.add_state(s0)
    for sym in sut.input_alphabet:
        incomplete_hyp.add_transition(s0, sym, s0, "WRONG_OUTPUT")
    incomplete_hyp.validate()

    oracle = RandomSequenceEquivalenceOracle[str, str](max_sequence_length=6, num_sequences=50, seed=123)
    ce = oracle.find_counterexample(incomplete_hyp, sut)

    assert oracle.equivalence_queries_count == 1
    assert ce is not None


def test_w_method_equivalence_oracle():
    sut = create_toy_protocol_sut()

    s0 = State("q0", is_initial=True)
    incomplete_hyp = MealyMachine[str, str]("IncompleteHypothesis")
    incomplete_hyp.add_state(s0)
    for sym in sut.input_alphabet:
        incomplete_hyp.add_transition(s0, sym, s0, "WRONG_OUTPUT")
    incomplete_hyp.validate()

    oracle = WMethodEquivalenceOracle[str, str](max_depth=3)
    ce = oracle.find_counterexample(incomplete_hyp, sut)

    assert oracle.equivalence_queries_count == 1
    assert ce is not None
