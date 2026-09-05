from typing import Generic, Hashable, Iterable, Sequence, TypeVar
from .state import State
from .transition import Transition

SymbolT = TypeVar("SymbolT", bound=Hashable)


class DFAValidationError(Exception):
    """Raised when a DFA configuration or transition table violates DFA constraints."""
    pass


class InvalidStateError(Exception):
    """Raised when encountering an undefined or invalid state operation."""
    pass


class DFA(Generic[SymbolT]):
    """
    Deterministic Finite Automaton (DFA) engine.

    Formally defined as 5-tuple M = (Q, Sigma, delta, q0, F):
      - Q: Finite set of states
      - Sigma: Input alphabet
      - delta: Transition function Q x Sigma -> Q
      - q0: Initial state (q0 in Q)
      - F: Set of accepting states (F subset of Q)
    """

    def __init__(self, name: str = "DFA") -> None:
        self.name = name
        self._states: set[State] = set()
        self._alphabet: set[SymbolT] = set()
        self._initial_state: State | None = None
        self._accepting_states: set[State] = set()
        self._transitions: dict[tuple[State, SymbolT], State] = {}
        self._current_state: State | None = None
        self._execution_trace: list[tuple[State, SymbolT, State]] = []

    @property
    def states(self) -> set[State]:
        return set(self._states)

    @property
    def alphabet(self) -> set[SymbolT]:
        return set(self._alphabet)

    @property
    def initial_state(self) -> State | None:
        return self._initial_state

    @property
    def accepting_states(self) -> set[State]:
        return set(self._accepting_states)

    @property
    def current_state(self) -> State | None:
        return self._current_state

    @property
    def execution_trace(self) -> list[tuple[State, SymbolT, State]]:
        return list(self._execution_trace)

    def add_state(self, state: State) -> None:
        """Add a state to the DFA state set Q."""
        self._states.add(state)
        if state.is_initial:
            if self._initial_state is not None and self._initial_state != state:
                raise DFAValidationError(
                    f"DFA already has initial state '{self._initial_state.name}'. "
                    f"Cannot add second initial state '{state.name}'."
                )
            self._initial_state = state
            if self._current_state is None:
                self._current_state = state

        if state.is_accepting:
            self._accepting_states.add(state)

    def add_transition(self, source: State, symbol: SymbolT, target: State) -> None:
        """Add transition delta(source, symbol) = target."""
        if source not in self._states:
            self.add_state(source)
        if target not in self._states:
            self.add_state(target)

        self._alphabet.add(symbol)
        key = (source, symbol)
        if key in self._transitions and self._transitions[key] != target:
            raise DFAValidationError(
                f"Non-deterministic transition detected for ({source.name}, {symbol}). "
                f"Existing: '{self._transitions[key].name}', New: '{target.name}'."
            )
        self._transitions[key] = target

    def validate(self, allow_partial: bool = True) -> None:
        """
        Validate automaton integrity.

        Args:
            allow_partial: If False, verifies that delta is defined for all (q, s) in Q x Sigma.
        """
        if self._initial_state is None:
            raise DFAValidationError("DFA must have exactly one initial state.")

        if self._initial_state not in self._states:
            raise DFAValidationError(f"Initial state '{self._initial_state.name}' not in states Q.")

        for acc in self._accepting_states:
            if acc not in self._states:
                raise DFAValidationError(f"Accepting state '{acc.name}' not in states Q.")

        if not allow_partial:
            for state in self._states:
                for symbol in self._alphabet:
                    if (state, symbol) not in self._transitions:
                        raise DFAValidationError(
                            f"Incomplete DFA: Missing transition for ({state.name}, {symbol})."
                        )

    def reset(self) -> State:
        """Reset execution state to initial state."""
        if self._initial_state is None:
            raise InvalidStateError("Cannot reset DFA with no initial state defined.")
        self._current_state = self._initial_state
        self._execution_trace.clear()
        return self._current_state

    def step(self, symbol: SymbolT) -> State:
        """
        Execute a single transition delta(current_state, symbol) -> next_state.

        Returns:
            The new current State.

        Raises:
            InvalidStateError: If current_state is unset or transition is undefined.
        """
        if self._current_state is None:
            if self._initial_state is None:
                raise InvalidStateError("Initial state is not set.")
            self._current_state = self._initial_state

        key = (self._current_state, symbol)
        if key not in self._transitions:
            raise InvalidStateError(
                f"Undefined transition from state '{self._current_state.name}' on symbol '{symbol}'."
            )

        next_state = self._transitions[key]
        self._execution_trace.append((self._current_state, symbol, next_state))
        self._current_state = next_state
        return self._current_state

    def process_sequence(self, sequence: Iterable[SymbolT]) -> tuple[bool, State, list[tuple[State, SymbolT, State]]]:
        """
        Process a sequence of input symbols from the initial state.

        Returns:
            Tuple of (is_accepted, final_state, execution_trace).
        """
        self.reset()
        for symbol in sequence:
            self.step(symbol)

        assert self._current_state is not None
        is_accepted = self._current_state in self._accepting_states
        return is_accepted, self._current_state, self.execution_trace
