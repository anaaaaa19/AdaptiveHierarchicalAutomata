"""
Pushdown Automata (PDA) formal model implementation.

Formally defined as 7-tuple M = (Q, Sigma, Gamma, delta, q0, Z0, F):
  - Q: Finite set of states
  - Sigma: Input alphabet
  - Gamma: Stack alphabet
  - delta: Transition function Q x (Sigma U {epsilon}) x Gamma -> P(Q x Gamma*)
  - q0: Initial state in Q
  - Z0: Initial stack symbol in Gamma
  - F: Set of accepting states in Q
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, Hashable, Iterable, Sequence, TypeVar

from .state import State

SymbolT = TypeVar("SymbolT", bound=Hashable)
StackSymbolT = TypeVar("StackSymbolT", bound=Hashable)


class PDAValidationError(Exception):
    """Raised when PDA configuration violates formal constraints."""
    pass


class InvalidPDAStateError(Exception):
    """Raised when execution hits an undefined transition or stack underflow."""
    pass


class StackOp(str, Enum):
    """Stack manipulation operation type."""
    PUSH = "PUSH"
    POP = "POP"
    NOP = "NOP"


@dataclass(frozen=True, slots=True)
class PDATransition(Generic[SymbolT, StackSymbolT]):
    """
    Represents a state transition with stack operations in a Pushdown Automaton.

    delta(source, symbol, stack_top) -> (target, op, push_symbols)
    """
    source: State
    symbol: SymbolT
    stack_top: StackSymbolT | None
    target: State
    op: StackOp = StackOp.NOP
    push_symbols: tuple[StackSymbolT, ...] = ()
    pop_count: int = 1

    def __repr__(self) -> str:
        top_str = f"top={self.stack_top}" if self.stack_top is not None else "top=*"
        op_str = f"{self.op.value}({self.push_symbols if self.op == StackOp.PUSH else ''})"
        return f"PDATransition({self.source.name} --[{self.symbol}, {top_str} / {op_str}]--> {self.target.name})"


class PushdownAutomaton(Generic[SymbolT, StackSymbolT]):
    """
    Deterministic Pushdown Automaton (PDA) engine.
    """

    def __init__(
        self,
        name: str = "PushdownAutomaton",
        initial_stack_symbol: StackSymbolT | None = None,
    ) -> None:
        self.name = name
        self._states: set[State] = set()
        self._input_alphabet: set[SymbolT] = set()
        self._stack_alphabet: set[StackSymbolT] = set()
        self._initial_state: State | None = None
        self._accepting_states: set[State] = set()
        self._initial_stack_symbol: StackSymbolT | None = initial_stack_symbol
        if initial_stack_symbol is not None:
            self._stack_alphabet.add(initial_stack_symbol)

        # Map: (source, symbol, stack_top) -> (target, op, push_symbols, pop_count)
        self._transitions: dict[
            tuple[State, SymbolT, StackSymbolT | None],
            tuple[State, StackOp, tuple[StackSymbolT, ...], int],
        ] = {}

        self._current_state: State | None = None
        self._stack: list[StackSymbolT] = []
        self._execution_trace: list[tuple[State, SymbolT, tuple[StackSymbolT, ...], State, tuple[StackSymbolT, ...]]] = []

    @property
    def states(self) -> set[State]:
        return set(self._states)

    @property
    def input_alphabet(self) -> set[SymbolT]:
        return set(self._input_alphabet)

    @property
    def stack_alphabet(self) -> set[StackSymbolT]:
        return set(self._stack_alphabet)

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
    def stack(self) -> tuple[StackSymbolT, ...]:
        return tuple(self._stack)

    @property
    def execution_trace(self) -> list[tuple[State, SymbolT, tuple[StackSymbolT, ...], State, tuple[StackSymbolT, ...]]]:
        return list(self._execution_trace)

    def add_state(self, state: State) -> None:
        """Add state to set Q."""
        self._states.add(state)
        if state.is_initial:
            if self._initial_state is not None and self._initial_state != state:
                raise PDAValidationError(
                    f"PDA already has initial state '{self._initial_state.name}'. "
                    f"Cannot set '{state.name}' as initial."
                )
            self._initial_state = state
            if self._current_state is None:
                self._current_state = state

        if state.is_accepting:
            self._accepting_states.add(state)

    def add_transition(
        self,
        source: State,
        symbol: SymbolT,
        stack_top: StackSymbolT | None,
        target: State,
        op: StackOp = StackOp.NOP,
        push_symbols: Sequence[StackSymbolT] = (),
        pop_count: int = 1,
    ) -> None:
        """
        Add transition delta(source, symbol, stack_top) -> (target, op, push_symbols).
        """
        if source not in self._states:
            self.add_state(source)
        if target not in self._states:
            self.add_state(target)

        self._input_alphabet.add(symbol)
        if stack_top is not None:
            self._stack_alphabet.add(stack_top)
        for ps in push_symbols:
            self._stack_alphabet.add(ps)

        key = (source, symbol, stack_top)
        if key in self._transitions:
            existing = self._transitions[key]
            raise PDAValidationError(
                f"Conflicting PDA transition for ({source.name}, {symbol}, {stack_top}). "
                f"Existing: -> {existing[0].name}, New: -> {target.name}."
            )

        self._transitions[key] = (target, op, tuple(push_symbols), pop_count)

    def validate(self) -> None:
        """Validate PDA state configuration."""
        if self._initial_state is None:
            raise PDAValidationError("PDA must have an initial state.")
        if self._initial_state not in self._states:
            raise PDAValidationError(f"Initial state '{self._initial_state.name}' not in states Q.")

    def reset(self) -> State:
        """Reset execution state and stack."""
        if self._initial_state is None:
            raise InvalidPDAStateError("Cannot reset PDA without initial state.")
        self._current_state = self._initial_state
        self._stack.clear()
        if self._initial_stack_symbol is not None:
            self._stack.append(self._initial_stack_symbol)
        self._execution_trace.clear()
        return self._current_state

    def step(self, symbol: SymbolT) -> State:
        """
        Execute a single transition delta(current_state, symbol, stack_top) -> next_state.
        """
        if self._current_state is None:
            if self._initial_state is None:
                raise InvalidPDAStateError("Initial state not set.")
            self._current_state = self._initial_state

        stack_top = self._stack[-1] if self._stack else None
        before_stack = tuple(self._stack)

        key = (self._current_state, symbol, stack_top)
        if key not in self._transitions:
            # Fallback to wildcard stack_top None if defined
            key_wildcard = (self._current_state, symbol, None)
            if key_wildcard in self._transitions:
                key = key_wildcard
            else:
                raise InvalidPDAStateError(
                    f"Undefined PDA transition from state '{self._current_state.name}' on symbol '{symbol}' with stack top '{stack_top}'."
                )

        target, op, push_syms, pop_cnt = self._transitions[key]

        # Execute stack operation
        if op == StackOp.POP:
            if len(self._stack) < pop_cnt:
                raise InvalidPDAStateError(
                    f"Stack underflow during POP operation on state '{self._current_state.name}'. "
                    f"Required: {pop_cnt}, Available: {len(self._stack)}."
                )
            for _ in range(pop_cnt):
                self._stack.pop()
        elif op == StackOp.PUSH:
            for ps in push_syms:
                self._stack.append(ps)

        after_stack = tuple(self._stack)
        self._execution_trace.append((self._current_state, symbol, before_stack, target, after_stack))
        self._current_state = target
        return self._current_state

    def process_sequence(self, sequence: Iterable[SymbolT]) -> tuple[bool, State, tuple[StackSymbolT, ...], list]:
        """
        Process an input sequence from the initial state.

        Returns:
            Tuple of (is_accepted, final_state, final_stack, execution_trace).
        """
        self.reset()
        for symbol in sequence:
            self.step(symbol)

        assert self._current_state is not None
        # Accepted if final state is in accepting_states and stack has no leftover temporary frames
        is_accepted = self._current_state in self._accepting_states
        if self._initial_stack_symbol is not None:
            # Accept if stack contains only initial_stack_symbol or is empty
            if len(self._stack) > 1 or (len(self._stack) == 1 and self._stack[0] != self._initial_stack_symbol):
                is_accepted = False
        else:
            if len(self._stack) > 0:
                is_accepted = False

        return is_accepted, self._current_state, self.stack, self.execution_trace
