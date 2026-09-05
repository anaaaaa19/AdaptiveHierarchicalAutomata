"""
Offline / PCAP Replay Packet Capture Source.
"""

from typing import Any, Iterable, Iterator, Sequence
import time

from adaptive_automata.deployment.capture.base import PacketCaptureSource
from adaptive_automata.deployment.pipeline.events import RawPacket


class ReplayCaptureSource(PacketCaptureSource):
    """
    Replay packet capture source consuming pre-recorded sequence data, JSON trace dictionaries,
    or simulated network packet lists for reproducible testing and benchmarking.
    """

    def __init__(self, packet_records: Iterable[dict[str, Any] | RawPacket] | None = None) -> None:
        self._raw_records: list[dict[str, Any] | RawPacket] = list(packet_records or [])
        self._running = False
        self._packets_read = 0

    def add_packet(
        self,
        src_ip: str,
        src_port: int,
        dst_ip: str,
        dst_port: int,
        protocol: str,
        payload: bytes | str,
        timestamp: float | None = None,
    ) -> None:
        payload_bytes = payload.encode("utf-8") if isinstance(payload, str) else payload
        ts = timestamp if timestamp is not None else time.time()
        pkt = RawPacket(
            packet_id=f"pkt_{len(self._raw_records) + 1}",
            src_ip=src_ip,
            src_port=src_port,
            dst_ip=dst_ip,
            dst_port=dst_port,
            protocol=protocol,
            timestamp=ts,
            payload=payload_bytes,
            length=len(payload_bytes),
        )
        self._raw_records.append(pkt)

    def start(self) -> None:
        self._running = True
        self._packets_read = 0

    def stop(self) -> None:
        self._running = False

    @property
    def is_active(self) -> bool:
        return self._running

    def packets(self) -> Iterator[RawPacket]:
        self._running = True
        for idx, rec in enumerate(self._raw_records):
            if not self._running:
                break
            self._packets_read += 1
            if isinstance(rec, RawPacket):
                yield rec
            else:
                payload = rec.get("payload", b"")
                if isinstance(payload, str):
                    payload = payload.encode("utf-8")
                yield RawPacket(
                    packet_id=rec.get("packet_id", f"pkt_{idx + 1}"),
                    src_ip=rec.get("src_ip", "192.168.1.10"),
                    src_port=rec.get("src_port", 5000),
                    dst_ip=rec.get("dst_ip", "192.168.1.20"),
                    dst_port=rec.get("dst_port", 80),
                    protocol=rec.get("protocol", "TCP"),
                    timestamp=rec.get("timestamp", time.time()),
                    payload=payload,
                    length=len(payload),
                )
        self._running = False
