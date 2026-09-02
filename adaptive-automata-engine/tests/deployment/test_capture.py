"""
Tests for PacketCaptureSource implementations.
"""

from adaptive_automata.deployment.capture.replay import ReplayCaptureSource
from adaptive_automata.deployment.capture.live import LiveCaptureSource


def test_replay_capture_source():
    cap = ReplayCaptureSource()
    cap.add_packet("192.168.1.1", 1234, "192.168.1.2", 80, "TCP", "SYN")
    cap.add_packet("192.168.1.2", 80, "192.168.1.1", 1234, "TCP", "SYN-ACK")

    pkts = list(cap.packets())
    assert len(pkts) == 2
    assert pkts[0].src_ip == "192.168.1.1"
    assert pkts[0].payload == b"SYN"
    assert pkts[1].payload == b"SYN-ACK"


def test_live_capture_source_fallback():
    cap = LiveCaptureSource(interface="non_existent_interface", max_packets=5)
    pkts = list(cap.packets())
    assert len(pkts) == 5
    assert pkts[0].protocol == "TCP"
