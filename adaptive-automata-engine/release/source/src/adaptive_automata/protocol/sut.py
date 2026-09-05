"""
System Under Test (SUT) abstraction for active automata learning.

Provides an abstract base interface for black-box protocol interaction and a
concrete deterministic Mealy Machine simulator wrapper for research and testing.
"""

from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar
from adaptive_automata.core.mealy import MealyMachine
from adaptive_automata.core.state import State

SymbolT = TypeVar("SymbolT")
OutputT = TypeVar("OutputT")


class SystemUnderTest(Generic[SymbolT, OutputT], ABC):
    """
    Abstract Base Class for a System Under Test (SUT).

    An SUT acts as a black-box membership oracle O_MQ: Sigma* -> Gamma*.
    Given an input sequence of symbols, the SUT executes the sequence from its
    initial state and returns the sequence of output symbols generated.
    """

    def __init__(self) -> None:
        self._membership_queries_count: int = 0
        self._total_symbols_queried: int = 0

    @property
    @abstractmethod
    def input_alphabet(self) -> set[SymbolT]:
        """Return the set of valid input symbols Sigma supported by the SUT."""
        pass

    @property
    def membership_queries_count(self) -> int:
        """Total number of membership queries executed against this SUT."""
        return self._membership_queries_count

    @property
    def total_symbols_queried(self) -> int:
        """Total length of all input sequences queried against this SUT."""
        return self._total_symbols_queried

    def reset_query_counters(self) -> None:
        """Reset membership query performance counters."""
        self._membership_queries_count = 0
        self._total_symbols_queried = 0

    @abstractmethod
    def reset(self) -> None:
        """Reset the internal state of the SUT to its initial state."""
        pass

    @abstractmethod
    def step(self, symbol: SymbolT) -> OutputT:
        """
        Execute a single input symbol step on the SUT.

        Returns:
            Output symbol produced by the transition.
        """
        pass

    def query(self, sequence: Sequence[SymbolT]) -> tuple[OutputT, ...]:
        """
        Membership Query (O_MQ): Execute an input sequence on the SUT from initial state.

        Args:
            sequence: Sequence of input symbols (s_1, s_2, ..., s_n).

        Returns:
            Tuple of corresponding output symbols (o_1, o_2, ..., o_n).
        """
        self._membership_queries_count += 1
        self._total_symbols_queried += len(sequence)

        self.reset()
        outputs: list[OutputT] = []
        for symbol in sequence:
            output = self.step(symbol)
            outputs.append(output)
        return tuple(outputs)


class MealyMachineSUT(SystemUnderTest[SymbolT, OutputT]):
    """
    Black-box System Under Test wrapper around a MealyMachine transducer.

    Hides internal state graph and transition table from the learner, exposing
    only membership sequence queries.
    """

    def __init__(self, mealy: MealyMachine[SymbolT, OutputT]) -> None:
        super().__init__()
        mealy.validate()
        self._mealy = mealy

    @property
    def input_alphabet(self) -> set[SymbolT]:
        return self._mealy.input_alphabet

    def reset(self) -> None:
        self._mealy.reset()

    def step(self, symbol: SymbolT) -> OutputT:
        _, output = self._mealy.step(symbol)
        return output


def create_toy_protocol_sut() -> MealyMachineSUT[str, str]:
    """
    Factory constructing a complete, deterministic toy protocol SUT.

    Simulates a stateful protocol with 4 states:
      - CLOSED (initial)
      - SYN_SENT
      - ESTABLISHED
      - AUTHENTICATED

    Supported alphabet: {"SYN", "ACK", "AUTH", "DATA", "FIN"}
    """
    s_closed = State("CLOSED", is_initial=True)
    s_syn_sent = State("SYN_SENT")
    s_established = State("ESTABLISHED")
    s_authenticated = State("AUTHENTICATED")

    states = [s_closed, s_syn_sent, s_established, s_authenticated]
    alphabet = {"SYN", "ACK", "AUTH", "DATA", "FIN"}

    mealy = MealyMachine[str, str]("ToyProtocolSUT")
    for s in states:
        mealy.add_state(s)

    # Defined happy-path transitions
    defined_transitions = {
        (s_closed, "SYN"): (s_syn_sent, "SEND_SYN_ACK"),
        (s_syn_sent, "ACK"): (s_established, "ALLOCATE_SESSION"),
        (s_established, "AUTH"): (s_authenticated, "GRANT_TOKEN"),
        (s_authenticated, "DATA"): (s_authenticated, "ACK_DATA"),
        (s_authenticated, "FIN"): (s_closed, "CLOSE_SESSION"),
        (s_established, "FIN"): (s_closed, "CLOSE_SESSION"),
    }

    # Add defined transitions
    for (src, sym), (tgt, out) in defined_transitions.items():
        mealy.add_transition(src, sym, tgt, out)

    # Complete the Mealy Machine by adding error self-loops/reset for undefined inputs
    for state in states:
        for symbol in alphabet:
            key = (state, symbol)
            if key not in defined_transitions:
                mealy.add_transition(state, symbol, s_closed, "ERROR")

    mealy.validate()
    return MealyMachineSUT(mealy)
