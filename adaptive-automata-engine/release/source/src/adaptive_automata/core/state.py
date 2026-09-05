from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class State:
    """
    Represents an immutable, hashable state in an automaton.

    Attributes:
        name: Unique label identifying the state.
        is_initial: Flag indicating if this state is the starting state.
        is_accepting: Flag indicating if this state is an accepting (final) state.
        metadata: Optional key-value pairs associated with state properties or protocol context.
    """
    name: str
    is_initial: bool = False
    is_accepting: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict, hash=False, compare=False)

    def __repr__(self) -> str:
        flags = []
        if self.is_initial:
            flags.append("initial")
        if self.is_accepting:
            flags.append("accepting")
        flag_str = f" ({','.join(flags)})" if flags else ""
        return f"State('{self.name}'{flag_str})"
