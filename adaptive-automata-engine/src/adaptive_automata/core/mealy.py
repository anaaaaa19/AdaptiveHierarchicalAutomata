from typing import Generic, Hashable, Iterable, TypeVar
from .state import State
from .transition import MealyTransition

SymbolT = TypeVar("SymbolT", bound=Hashable)
OutputT = TypeVar("OutputT")


class MealyMachineValidationError(Exception):
    """Raised when Mealy Machine configuration violates transducer constraints."""
    pass


class InvalidMealyStateError(Exception):
    """Raised when execution hits an undefined transition or uninitialized state."""
    pass


class MealyMachine(Generic[SymbolT, OutputT]):
    """
    Mealy Machine finite state transducer.

    Formally defined as 6-tuple M = (Q, Sigma, Gamma, delta, lambda, q0):
      - Q: Finite set of states
      - Sigma: Input alphabet
      - Gamma: Output alphabet
      - delta: Transition function Q x Sigma -> Q
      - lambda: Output function Q x Sigma -> Gamma
      - q0: Initial state in Q
    """

    def __init__(self, name: str = "MealyMachine") -> None:
        self.name = name
        self._states: set[State] = set()
        self._input_alphabet: set[SymbolT] = set()
        self._output_alphabet: set[OutputT] = set()
        self._initial_state: State | None = None
        self._transitions: dict[tuple[State, SymbolT], tuple[State, OutputT]] = {}
        self._current_state: State | None = None
        self._execution_trace: list[tuple[State, SymbolT, State, OutputT]] = []

    @property
    def states(self) -> set[State]:
        return set(self._states)

    @property
    def input_alphabet(self) -> set[SymbolT]:
        return set(self._input_alphabet)

    @property
    def output_alphabet(self) -> set[OutputT]:
        return set(self._output_alphabet)

    @property
    def initial_state(self) -> State | None:
        return self._initial_state

    @property
    def current_state(self) -> State | None:
        return self._current_state

    @property
    def execution_trace(self) -> list[tuple[State, SymbolT, State, OutputT]]:
        return list(self._execution_trace)

    def add_state(self, state: State) -> None:
        """Add state to set Q."""
        self._states.add(state)
        if state.is_initial:
            if self._initial_state is not None and self._initial_state != state:
                raise MealyMachineValidationError(
                    f"Mealy machine already has initial state '{self._initial_state.name}'. "
                    f"Cannot set '{state.name}' as initial."
                )
            self._initial_state = state
            if self._current_state is None:
                self._current_state = state

    def add_transition(self, source: State, symbol: SymbolT, target: State, output: OutputT) -> None:
        """Add transition delta(source, symbol) = target and output lambda(source, symbol) = output."""
        if source not in self._states:
            self.add_state(source)
        if target not in self._states:
            self.add_state(target)

        self._input_alphabet.add(symbol)
        self._output_alphabet.add(output)

        key = (source, symbol)
        if key in self._transitions and self._transitions[key] != (target, output):
            raise MealyMachineValidationError(
                f"Conflicting Mealy transition for ({source.name}, {symbol}). "
                f"Existing: -> {self._transitions[key][0].name} / {self._transitions[key][1]}, "
                f"New: -> {target.name} / {output}."
            )

        self._transitions[key] = (target, output)

    def validate(self) -> None:
        """Validate Mealy Machine completeness and consistency."""
        if self._initial_state is None:
            raise MealyMachineValidationError("Mealy machine must have an initial state.")
        if self._initial_state not in self._states:
            raise MealyMachineValidationError(f"Initial state '{self._initial_state.name}' not in states Q.")

    def reset(self) -> State:
        """Reset machine execution to initial state."""
        if self._initial_state is None:
            raise InvalidMealyStateError("Cannot reset machine without initial state.")
        self._current_state = self._initial_state
        self._execution_trace.clear()
        return self._current_state

    def step(self, symbol: SymbolT) -> tuple[State, OutputT]:
        """
        Step single transition: delta(current_state, symbol) -> (next_state, output).

        Returns:
            Tuple of (next_state, output_symbol).
        """
        if self._current_state is None:
            if self._initial_state is None:
                raise InvalidMealyStateError("Initial state not set.")
            self._current_state = self._initial_state

        key = (self._current_state, symbol)
        if key not in self._transitions:
            raise InvalidMealyStateError(
                f"Undefined Mealy transition from '{self._current_state.name}' on symbol '{symbol}'."
            )

        next_state, output = self._transitions[key]
        self._execution_trace.append((self._current_state, symbol, next_state, output))
        self._current_state = next_state
        return next_state, output

    def process_sequence(self, sequence: Iterable[SymbolT]) -> tuple[list[OutputT], State]:
        """
        Transduce input sequence into output sequence.

        Returns:
            Tuple of (list_of_outputs, final_state).
        """
        self.reset()
        outputs: list[OutputT] = []
        for symbol in sequence:
            _, output = self.step(symbol)
            outputs.append(output)

        assert self._current_state is not None
        return outputs, self._current_state
