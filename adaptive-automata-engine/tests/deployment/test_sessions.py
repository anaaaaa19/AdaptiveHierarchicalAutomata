"""
Tests for SessionManager component.
"""

from adaptive_automata.deployment.packet.processor import ProcessedPacket
from adaptive_automata.deployment.sessions.manager import SessionManager


def test_session_manager_flow_grouping():
    sm = SessionManager(max_inactivity_sec=300)
    pkt1 = ProcessedPacket("p1", ("10.0.0.1", 1000, "10.0.0.2", 80, "TCP"), "INBOUND", 0.0, b"SYN", 3)
    pkt2 = ProcessedPacket("p2", ("10.0.0.2", 80, "10.0.0.1", 1000, "TCP"), "OUTBOUND", 0.0, b"SYN-ACK", 7)

    s1 = sm.get_or_create_session(pkt1)
    s2 = sm.get_or_create_session(pkt2)

    assert s1.session_id == s2.session_id
    assert s1.protocol.packet_count == 2
    assert s1.protocol.byte_count == 10
