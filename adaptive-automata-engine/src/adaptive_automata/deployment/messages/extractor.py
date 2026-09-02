"""
Message Extractor and Protocol Adapters Component.
"""

from abc import ABC, abstractmethod
from typing import Sequence

from adaptive_automata.deployment.packet.processor import ProcessedPacket


class ProtocolAdapter(ABC):
    """
    Abstract Protocol Adapter converting raw packet payloads into high-level protocol messages.
    """

    @abstractmethod
    def identify(self, payload: bytes) -> bool:
        """Return True if payload matches protocol signature."""
        pass

    @abstractmethod
    def extract_messages(self, payload: bytes) -> list[str]:
        """Extract protocol message string(s) from byte payload."""
        pass


class ToyProtocolAdapter(ProtocolAdapter):
    """
    Adapter for standard research text/toy protocol (e.g. 'CONNECT:user', 'AUTH:pass', 'DATA:chunk', 'FIN').
    """

    def identify(self, payload: bytes) -> bool:
        text = payload.decode("utf-8", errors="ignore")
        return any(cmd in text for cmd in ("SYN", "CONNECT", "AUTH", "REQ", "DATA", "FIN", "LOGOUT", "CAPABILITIES"))

    def extract_messages(self, payload: bytes) -> list[str]:
        text = payload.decode("utf-8", errors="replace").strip()
        if not text:
            return []
        # Split by newlines or semicolon delimiters
        lines = [line.strip() for line in text.replace(";", "\n").splitlines() if line.strip()]
        return lines if lines else [text]


class HTTPAdapter(ProtocolAdapter):
    """
    Adapter for HTTP/1.x messages.
    """

    def identify(self, payload: bytes) -> bool:
        text = payload.decode("utf-8", errors="ignore")
        return any(text.startswith(m) for m in ("GET ", "POST ", "PUT ", "DELETE ", "HEAD ", "HTTP/1."))

    def extract_messages(self, payload: bytes) -> list[str]:
        text = payload.decode("utf-8", errors="replace").strip()
        if not text:
            return []
        first_line = text.splitlines()[0] if text.splitlines() else text
        return [first_line]


class MQTTAdapter(ProtocolAdapter):
    """
    Adapter for MQTT protocol control packets.
    """

    def identify(self, payload: bytes) -> bool:
        if not payload:
            return False
        if any(c in payload[:10] for c in (b":", b"\n", b" ")) or all(32 <= b <= 126 for b in payload[:10]):
            return False
        packet_type = (payload[0] & 0xF0) >> 4
        return 1 <= packet_type <= 14

    def extract_messages(self, payload: bytes) -> list[str]:
        if not payload:
            return []
        packet_type = (payload[0] & 0xF0) >> 4
        type_names = {
            1: "CONNECT", 2: "CONNACK", 3: "PUBLISH", 4: "PUBACK",
            5: "PUBREC", 6: "PUBREL", 7: "PUBCOMP", 8: "SUBSCRIBE",
            9: "SUBACK", 10: "UNSUBSCRIBE", 11: "UNSUBACK", 12: "PINGREQ",
            13: "PINGRESP", 14: "DISCONNECT"
        }
        name = type_names.get(packet_type, "UNKNOWN_MQTT")
        return [name]


class MessageExtractor:
    """
    Message Extractor evaluating payloads through registered ProtocolAdapters.
    """

    def __init__(self, adapters: Sequence[ProtocolAdapter] | None = None) -> None:
        self.adapters: list[ProtocolAdapter] = list(adapters or [ToyProtocolAdapter(), HTTPAdapter(), MQTTAdapter()])

    def extract(self, processed_pkt: ProcessedPacket) -> list[str]:
        """
        Extract protocol messages from ProcessedPacket.
        """
        payload = processed_pkt.payload_slice
        if not payload:
            return []

        for adapter in self.adapters:
            if adapter.identify(payload):
                return adapter.extract_messages(payload)

        # Fallback raw string extraction
        raw_text = payload.decode("utf-8", errors="replace").strip()
        return [raw_text] if raw_text else []
