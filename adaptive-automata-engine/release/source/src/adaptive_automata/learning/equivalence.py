"""
Equivalence Oracles (O_EQ) for Mealy Machine active learning.

Provides abstract equivalence oracle interface, bounded random sequence testing,
W-method test suite generation, and exact graph state equivalence testing.
"""

from abc import ABC, abstractmethod
from collections import deque
import random
from typing import Generic, Sequence, TypeVar

from adaptive_automata.core.mealy import InvalidMealyStateError, MealyMachine
from adaptive_automata.protocol.sut import MealyMachineSUT, SystemUnderTest

SymbolT = TypeVar("SymbolT")
OutputT = TypeVar("OutputT")


class EquivalenceOracle(Generic[SymbolT, OutputT], ABC):
    """
    Abstract Base Class for Equivalence Oracles (O_EQ).

    Given a hypothesis Mealy Machine H and a System Under Test SUT,
    finds a counterexample sequence x in Sigma* such that H(x) != SUT(x).
    """

    def __init__(self) -> None:
        self._equivalence_queries_count: int = 0

    @property
    def equivalence_queries_count(self) -> int:
        """Total number of equivalence queries executed."""
        return self._equivalence_queries_count

    def reset_query_counters(self) -> None:
        """Reset equivalence query counter."""
        self._equivalence_queries_count = 0

    @abstractmethod
    def find_counterexample(
        self,
        hypothesis: MealyMachine[SymbolT, OutputT],
        sut: SystemUnderTest[SymbolT, OutputT],
    ) -> tuple[SymbolT, ...] | None:
        """
        Search for a counterexample sequence where hypothesis output differs from SUT.

        Returns:
            Counterexample tuple x, or None if no counterexample found.
        """
        pass


class RandomSequenceEquivalenceOracle(EquivalenceOracle[SymbolT, OutputT]):
    """
    Practical equivalence oracle generating bounded random test sequences.

    Generates random sequences of length up to `max_sequence_length` over the SUT input alphabet.
    Deterministic when `seed` is provided.
    """

    def __init__(
        self,
        max_sequence_length: int = 10,
        num_sequences: int = 100,
        seed: int | None = 42,
    ) -> None:
        super().__init__()
        self.max_sequence_length = max_sequence_length
        self.num_sequences = num_sequences
        self.seed = seed

    def find_counterexample(
        self,
        hypothesis: MealyMachine[SymbolT, OutputT],
        sut: SystemUnderTest[SymbolT, OutputT],
    ) -> tuple[SymbolT, ...] | None:
        self._equivalence_queries_count += 1
        alphabet = sorted(list(sut.input_alphabet), key=lambda x: str(x))
        if not alphabet:
            return None

        rng = random.Random(self.seed)

        for _ in range(self.num_sequences):
            seq_len = rng.randint(1, self.max_sequence_length)
            seq = tuple(rng.choice(alphabet) for _ in range(seq_len))

            try:
                hyp_outputs, _ = hypothesis.process_sequence(seq)
                hyp_tuple = tuple(hyp_outputs)
            except InvalidMealyStateError:
                # Undefined transition in hypothesis implies discrepancy if SUT handles it
                return seq

            sut_outputs = sut.query(seq)

            if hyp_tuple != sut_outputs:
                return seq

        return None


class WMethodEquivalenceOracle(EquivalenceOracle[SymbolT, OutputT]):
    """
    Practical equivalence oracle generating bounded systematic sequences (W-method search).

    Tests sequences in increasing order of length up to `max_depth`.
    """

    def __init__(self, max_depth: int = 5) -> None:
        super().__init__()
        self.max_depth = max_depth

    def find_counterexample(
        self,
        hypothesis: MealyMachine[SymbolT, OutputT],
        sut: SystemUnderTest[SymbolT, OutputT],
    ) -> tuple[SymbolT, ...] | None:
        self._equivalence_queries_count += 1
        alphabet = sorted(list(sut.input_alphabet), key=lambda x: str(x))
        if not alphabet:
            return None

        queue: deque[tuple[SymbolT, ...]] = deque([(a,) for a in alphabet])

        while queue:
            seq = queue.popleft()

            try:
                hyp_outputs, _ = hypothesis.process_sequence(seq)
                hyp_tuple = tuple(hyp_outputs)
            except InvalidMealyStateError:
                return seq

            sut_outputs = sut.query(seq)

            if hyp_tuple != sut_outputs:
                return seq

            if len(seq) < self.max_depth:
                for a in alphabet:
                    queue.append(seq + (a,))

        return None


class ExactMealyEquivalenceOracle(EquivalenceOracle[SymbolT, OutputT]):
    """
    Exact graph equivalence oracle for research validation against ground-truth MealyMachineSUT.

    Explores product state graph between hypothesis and target Mealy machine using BFS.
    """

    def find_counterexample(
        self,
        hypothesis: MealyMachine[SymbolT, OutputT],
        sut: SystemUnderTest[SymbolT, OutputT],
    ) -> tuple[SymbolT, ...] | None:
        self._equivalence_queries_count += 1

        if not isinstance(sut, MealyMachineSUT):
            # Fallback to systematic BFS query if SUT internal machine is unavailable
            return WMethodEquivalenceOracle(max_depth=6).find_counterexample(hypothesis, sut)

        target_mealy = sut._mealy
        alphabet = sorted(list(sut.input_alphabet), key=lambda x: str(x))

        h_init = hypothesis.initial_state
        t_init = target_mealy.initial_state

        if h_init is None or t_init is None:
            return ()

        # Queue of tuples: (hyp_state, target_state, prefix_sequence)
        queue: deque[tuple[object, object, tuple[SymbolT, ...]]] = deque([(h_init, t_init, ())])
        visited: set[tuple[object, object]] = {(h_init, t_init)}

        while queue:
            h_curr, t_curr, seq = queue.popleft()

            for a in alphabet:
                # Step hypothesis
                hypothesis.reset()
                # Run trace to get to h_curr
                try:
                    hyp_out_seq, hyp_next = hypothesis.process_sequence(seq + (a,))
                    h_out = hyp_out_seq[-1]
                except InvalidMealyStateError:
                    return seq + (a,)

                # Step target
                target_mealy.reset()
                tgt_out_seq, tgt_next = target_mealy.process_sequence(seq + (a,))
                t_out = tgt_out_seq[-1]

                if h_out != t_out:
                    return seq + (a,)

                pair = (hyp_next, tgt_next)
                if pair not in visited:
                    visited.add(pair)
                    queue.append((hyp_next, tgt_next, seq + (a,)))

        return None
