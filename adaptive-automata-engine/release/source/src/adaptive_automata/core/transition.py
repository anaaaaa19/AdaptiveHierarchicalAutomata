from dataclasses import dataclass
from typing import Generic, TypeVar
from .state import State

SymbolT = TypeVar("SymbolT")
OutputT = TypeVar("OutputT")


@dataclass(frozen=True, slots=True)
class Transition(Generic[SymbolT]):
    """
    Represents a state transition in a Deterministic Finite Automaton (DFA).

    delta(source, symbol) -> target
    """
    source: State
    symbol: SymbolT
    target: State

    def __repr__(self) -> str:
        return f"Transition({self.source.name} --[{self.symbol}]--> {self.target.name})"


@dataclass(frozen=True, slots=True)
class MealyTransition(Generic[SymbolT, OutputT]):
    """
    Represents a state transition with output generation in a Mealy Machine.

    delta(source, symbol) -> target
    lambda(source, symbol) -> output
    """
    source: State
    symbol: SymbolT
    target: State
    output: OutputT

    def __repr__(self) -> str:
        return f"MealyTransition({self.source.name} --[{self.symbol} / {self.output}]--> {self.target.name})"
