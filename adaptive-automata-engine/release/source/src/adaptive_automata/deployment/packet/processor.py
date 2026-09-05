"""
Packet Processor Component.
"""

from dataclasses import dataclass
from typing import Any

from adaptive_automata.deployment.pipeline.events import RawPacket


@dataclass(slots=True)
class ProcessedPacket:
    """
    Structured container holding processed packet metadata and trimmed payload data.
    """
    packet_id: str
    flow_key: tuple[str, int, str, int, str]
    direction: str
    timestamp: float
    payload_slice: bytes
    length: int

    @property
    def payload_str(self) -> str:
        """Decode payload slice safely to string snippet."""
        return self.payload_slice.decode("utf-8", errors="replace")


class PacketProcessor:
    """
    Packet Processor handling transport metadata extraction, directionality determination,
    and memory-bounded payload slicing.
    """

    def __init__(self, max_payload_bytes: int = 4096, server_ports: set[int] | None = None) -> None:
        self.max_payload_bytes = max_payload_bytes
        self.server_ports = server_ports or {80, 443, 8080, 1883, 5000}

    def process(self, raw_pkt: RawPacket) -> ProcessedPacket:
        """
        Process raw packet into ProcessedPacket.
        """
        # Determine direction based on server ports
        if raw_pkt.dst_port in self.server_ports:
            direction = "INBOUND"
        elif raw_pkt.src_port in self.server_ports:
            direction = "OUTBOUND"
        else:
            direction = "CLIENT_TO_SERVER" if raw_pkt.src_port > raw_pkt.dst_port else "SERVER_TO_CLIENT"

        # Slice payload to prevent RAM expansion
        trimmed_payload = raw_pkt.payload[: self.max_payload_bytes]

        return ProcessedPacket(
            packet_id=raw_pkt.packet_id,
            flow_key=raw_pkt.flow_key,
            direction=direction,
            timestamp=raw_pkt.timestamp,
            payload_slice=trimmed_payload,
            length=raw_pkt.length,
        )
