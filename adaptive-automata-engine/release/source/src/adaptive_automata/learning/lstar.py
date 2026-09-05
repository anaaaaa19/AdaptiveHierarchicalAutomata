"""
L* Active Automata Learning algorithm for Mealy Machines.

Orchestrates the active learning loop: table initialization, closedness/consistency
maintenance, hypothesis building, equivalence queries, and counterexample refinement.
"""

from dataclasses import dataclass
from typing import Generic, TypeVar

from adaptive_automata.core.mealy import MealyMachine
from adaptive_automata.protocol.sut import SystemUnderTest
from .equivalence import ExactMealyEquivalenceOracle, EquivalenceOracle
from .observation_table import ObservationTable

SymbolT = TypeVar("SymbolT")
OutputT = TypeVar("OutputT")


@dataclass(slots=True)
class LearningResult(Generic[SymbolT, OutputT]):
    """
    Encapsulates final learned Mealy Machine model and learning process metrics.
    """
    learned_mealy: MealyMachine[SymbolT, OutputT]
    membership_queries: int
    total_symbols_queried: int
    equivalence_queries: int
    counterexamples_found: int
    num_states: int
    learning_iterations: int
    observation_table: ObservationTable[SymbolT, OutputT]
    converged: bool

    def __repr__(self) -> str:
        return (
            f"LearningResult(converged={self.converged}, "
            f"states={self.num_states}, "
            f"iterations={self.learning_iterations}, "
            f"membership_queries={self.membership_queries}, "
            f"total_symbols={self.total_symbols_queried}, "
            f"equivalence_queries={self.equivalence_queries}, "
            f"counterexamples={self.counterexamples_found})"
        )


class LStarLearner(Generic[SymbolT, OutputT]):
    """
    Active L* Learner for Mealy Machines.

    Infers an unknown Mealy machine transducing Sigma* -> Gamma* via black-box SUT queries.
    """

    def __init__(
        self,
        equivalence_oracle: EquivalenceOracle[SymbolT, OutputT] | None = None,
        max_iterations: int = 100,
        max_membership_queries: int = 10000,
    ) -> None:
        self.oracle = equivalence_oracle or ExactMealyEquivalenceOracle[SymbolT, OutputT]()
        self.max_iterations = max_iterations
        self.max_membership_queries = max_membership_queries

    def learn(self, sut: SystemUnderTest[SymbolT, OutputT]) -> LearningResult[SymbolT, OutputT]:
        """
        Execute active L* learning algorithm against the SUT.

        Returns:
            LearningResult containing inferred Mealy machine and learning statistics.
        """
        sut.reset_query_counters()
        self.oracle.reset_query_counters()

        table = ObservationTable[SymbolT, OutputT](sut.input_alphabet)
        table.update(sut)

        iterations = 0
        counterexamples_found = 0
        converged = False

        while iterations < self.max_iterations and sut.membership_queries_count < self.max_membership_queries:
            iterations += 1

            # Phase A: Ensure table is closed and consistent
            while True:
                closed_changed = table.make_closed(sut)
                consistent_changed = table.make_consistent(sut)
                if not closed_changed and not consistent_changed:
                    break

            # Phase B: Construct hypothesis Mealy machine
            hypothesis = table.to_mealy_machine(name=f"MealyHypothesis_v{iterations}")

            # Phase C: Equivalence Query (O_EQ)
            counterexample = self.oracle.find_counterexample(hypothesis, sut)

            if counterexample is None:
                # Target machine learned successfully!
                converged = True
                break

            # Phase D: Counterexample refinement
            counterexamples_found += 1

            # Add all non-empty prefixes of counterexample to S
            for k in range(1, len(counterexample) + 1):
                prefix = counterexample[:k]
                table.add_prefix(prefix)

            # Re-query SUT for new table entries
            table.update(sut)

        # Final table cleanup and model construction
        if not table.is_closed():
            table.make_closed(sut)
        if not table.is_consistent():
            table.make_consistent(sut)

        final_mealy = table.to_mealy_machine(name="LearnedProtocolMealy")

        return LearningResult(
            learned_mealy=final_mealy,
            membership_queries=sut.membership_queries_count,
            total_symbols_queried=sut.total_symbols_queried,
            equivalence_queries=self.oracle.equivalence_queries_count,
            counterexamples_found=counterexamples_found,
            num_states=len(final_mealy.states),
            learning_iterations=iterations,
            observation_table=table,
            converged=converged,
        )
