"""
Deviation Event data representation.

Standardized event emitted when the DFA/Mealy fast path encounters an undefined
or low-confidence transition error.
"""

from dataclasses import dataclass, field
from time import time
from typing import Sequence


@dataclass(frozen=True, slots=True)
class DeviationEvent:
    """
    Standardized event emitted when fast-path automaton execution encounters a deviation.

    Attributes:
        session_id: Parent session label.
        current_state: Origin state label at failure moment.
        input_symbol: Symbol triggering the deviation.
        position: Symbol index in input sequence where deviation occurred.
        reason: Explanatory error string.
        model_version: Version string of active fast-path model.
        trace_snippet: Preceding input symbols leading up to deviation.
        timestamp: Epoch timestamp.
    """
    session_id: str
    current_state: str
    input_symbol: str
    position: int
    reason: str
    model_version: str
    trace_snippet: tuple[str, ...] = field(default_factory=tuple)
    timestamp: float = field(default_factory=time)

    def __repr__(self) -> str:
        return (
            f"DeviationEvent(session='{self.session_id}', pos={self.position}, "
            f"state='{self.current_state}', symbol='{self.input_symbol}', "
            f"version='{self.model_version}', reason='{self.reason}')"
        )
