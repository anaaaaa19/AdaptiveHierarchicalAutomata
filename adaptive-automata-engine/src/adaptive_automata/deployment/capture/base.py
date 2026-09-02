"""
Abstract Base Class for Packet Capture Sources.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from adaptive_automata.deployment.pipeline.events import RawPacket


class PacketCaptureSource(ABC):
    """
    Abstract interface for packet sources (PCAP replay, synthetic stream, live socket).
    Ensures formal engine and detection logic remain completely independent of packet libraries.
    """

    @abstractmethod
    def start(self) -> None:
        """Initialize and start packet capture stream."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop packet capture stream and clean up resources."""
        pass

    @abstractmethod
    def packets(self) -> Iterator[RawPacket]:
        """Yield captured RawPacket instances."""
        pass

    @property
    @abstractmethod
    def is_active(self) -> bool:
        """Return True if capture stream is active."""
        pass
