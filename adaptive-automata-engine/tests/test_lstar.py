"""Comprehensive unit and integration tests for L* Active Learning Algorithm."""

import pytest
from adaptive_automata.core import State, MealyMachine
from adaptive_automata.protocol import create_toy_protocol_sut, MealyMachineSUT
from adaptive_automata.learning import (
    LStarLearner,
    ExactMealyEquivalenceOracle,
    RandomSequenceEquivalenceOracle,
    WMethodEquivalenceOracle,
)


def test_learn_toy_protocol_exact_oracle():
    sut = create_toy_protocol_sut()
    learner = LStarLearner[str, str](
        equivalence_oracle=ExactMealyEquivalenceOracle[str, str]()
    )

    result = learner.learn(sut)

    assert result.converged
    assert result.num_states == 4
    assert result.membership_queries > 0
    assert result.learning_iterations >= 1
    assert len(result.learned_mealy.states) == 4

    # Validate output on sequence
    test_seq = ("SYN", "ACK", "AUTH", "DATA")
    expected_out = sut.query(test_seq)
    learned_out, _ = result.learned_mealy.process_sequence(test_seq)
    assert tuple(learned_out) == expected_out


def test_learn_toy_protocol_w_method_oracle():
    sut = create_toy_protocol_sut()
    learner = LStarLearner[str, str](
        equivalence_oracle=WMethodEquivalenceOracle[str, str](max_depth=4)
    )

    result = learner.learn(sut)

    assert result.converged
    assert result.num_states == 4
    test_seq = ("SYN", "ACK", "AUTH", "DATA", "FIN")
    assert tuple(result.learned_mealy.process_sequence(test_seq)[0]) == sut.query(test_seq)


def test_learn_toy_protocol_random_oracle():
    sut = create_toy_protocol_sut()
    learner = LStarLearner[str, str](
        equivalence_oracle=RandomSequenceEquivalenceOracle[str, str](
            max_sequence_length=6, num_sequences=100, seed=42
        )
    )

    result = learner.learn(sut)

    assert result.converged
    assert result.num_states == 4


def test_learn_custom_binary_mealy():
    """Test learning a 3-state binary input Mealy machine."""
    s0 = State("s0", is_initial=True)
    s1 = State("s1")
    s2 = State("s2")

    mealy = MealyMachine[str, str]("Binary3State")
    mealy.add_transition(s0, "0", s1, "A")
    mealy.add_transition(s0, "1", s0, "B")
    mealy.add_transition(s1, "0", s2, "B")
    mealy.add_transition(s1, "1", s0, "A")
    mealy.add_transition(s2, "0", s0, "A")
    mealy.add_transition(s2, "1", s1, "B")
    mealy.validate()

    sut = MealyMachineSUT(mealy)
    learner = LStarLearner[str, str](
        equivalence_oracle=ExactMealyEquivalenceOracle[str, str]()
    )

    result = learner.learn(sut)

    assert result.converged
    assert result.num_states == 3
    assert len(result.learned_mealy.states) == 3

    # Test random sequence transduction equivalence
    seq = ("0", "0", "1", "0", "1", "1", "0")
    assert tuple(result.learned_mealy.process_sequence(seq)[0]) == sut.query(seq)


def test_query_budget_exceeded():
    sut = create_toy_protocol_sut()
    # Set restrictive membership query budget
    learner = LStarLearner[str, str](
        equivalence_oracle=ExactMealyEquivalenceOracle[str, str](),
        max_membership_queries=5,
    )

    result = learner.learn(sut)
    assert not result.converged
