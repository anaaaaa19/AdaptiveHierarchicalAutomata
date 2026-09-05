"""
Session Reconstruction abstraction layer.

Defines extensible interfaces for grouping raw protocol messages into structured sessions,
initially supporting pre-grouped JSON traces while preparing for live network/PCAP input.
"""

from abc import ABC, abstractmethod
from typing import Any
from .trace import ProtocolSession, TraceLoader


class SessionReconstructor(ABC):
    """
    Abstract Base Class for Session Reconstruction engines.

    Transforms raw network traffic captures, stream logs, or pre-grouped trace structures
    into clean, ordered ProtocolSession instances.
    """

    @abstractmethod
    def reconstruct_sessions(self, raw_input: Any) -> list[ProtocolSession]:
        """
        Group and reconstruct raw input data into a list of ProtocolSessions.
        """
        pass


class PreGroupedSessionReconstructor(SessionReconstructor):
    """
    Session Reconstructor for pre-grouped trace streams or JSON strings.
    """

    def reconstruct_sessions(self, raw_input: str | bytes | list[Any] | dict[str, Any]) -> list[ProtocolSession]:
        if isinstance(raw_input, (str, bytes)):
            return TraceLoader.load_from_json(raw_input)
        elif isinstance(raw_input, (list, dict)):
            import json
            return TraceLoader.load_from_json(json.dumps(raw_input))
        else:
            raise TypeError(f"Unsupported input type for PreGroupedSessionReconstructor: {type(raw_input).__name__}")
