"""
Tests for PacketProcessor component.
"""

from adaptive_automata.deployment.packet.processor import PacketProcessor
from adaptive_automata.deployment.pipeline.events import RawPacket


def test_packet_processor_direction_and_slicing():
    proc = PacketProcessor(max_payload_bytes=10)
    raw = RawPacket("p1", "10.0.0.1", 45000, "10.0.0.2", 80, "TCP", 0.0, b"VERY_LONG_PAYLOAD_STRING_HERE", 30)
    res = proc.process(raw)

    assert res.direction == "INBOUND"
    assert len(res.payload_slice) == 10
    assert res.payload_str == "VERY_LONG_"
