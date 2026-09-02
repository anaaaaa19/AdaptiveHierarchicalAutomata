"""
Synthetic Protocol-Security Dataset Generator.

Generates labeled deterministic protocol session datasets for cybersecurity benchmark evaluation:
  - Normal sessions
  - Known deviation attack sessions
  - Unseen (zero-day style) attack sessions
  - Legitimate protocol evolution sessions
  - Single-session high-frequency poisoning attack sessions
"""

from typing import Any
from adaptive_automata.protocol import MessageDirection, ProtocolMessage, ProtocolSession


class SyntheticDatasetGenerator:
    """
    Generates synthetic labeled protocol datasets for security research evaluation.
    """

    @staticmethod
    def generate_normal_sessions(count: int = 10) -> list[tuple[ProtocolSession, bool]]:
        """
        Generate valid normal protocol sessions.
        Returns list of (ProtocolSession, is_attack=False).
        """
        sessions: list[tuple[ProtocolSession, bool]] = []
        for i in range(1, count + 1):
            sess_id = f"norm_sess_{i}"
            msgs = [
                ProtocolMessage(sess_id, 1, MessageDirection.CLIENT_TO_SERVER, "SYN"),
                ProtocolMessage(sess_id, 2, MessageDirection.SERVER_TO_CLIENT, "SEND_SYN_ACK"),
                ProtocolMessage(sess_id, 3, MessageDirection.CLIENT_TO_SERVER, "ACK"),
                ProtocolMessage(sess_id, 4, MessageDirection.SERVER_TO_CLIENT, "ALLOCATE_SESSION"),
                ProtocolMessage(sess_id, 5, MessageDirection.CLIENT_TO_SERVER, "AUTH"),
                ProtocolMessage(sess_id, 6, MessageDirection.SERVER_TO_CLIENT, "GRANT"),
                ProtocolMessage(sess_id, 7, MessageDirection.CLIENT_TO_SERVER, "DATA"),
                ProtocolMessage(sess_id, 8, MessageDirection.SERVER_TO_CLIENT, "ACK_DATA"),
                ProtocolMessage(sess_id, 9, MessageDirection.CLIENT_TO_SERVER, "FIN"),
                ProtocolMessage(sess_id, 10, MessageDirection.SERVER_TO_CLIENT, "CLOSE"),
            ]
            sessions.append((ProtocolSession(sess_id, messages=msgs), False))
        return sessions

    @staticmethod
    def generate_known_deviations(count: int = 5) -> list[tuple[ProtocolSession, bool]]:
        """
        Generate known attack/deviation sessions.
        Returns list of (ProtocolSession, is_attack=True).
        """
        sessions: list[tuple[ProtocolSession, bool]] = []
        for i in range(1, count + 1):
            sess_id = f"known_dev_sess_{i}"
            msgs = [
                ProtocolMessage(sess_id, 1, MessageDirection.CLIENT_TO_SERVER, "SYN"),
                ProtocolMessage(sess_id, 2, MessageDirection.SERVER_TO_CLIENT, "SEND_SYN_ACK"),
                ProtocolMessage(sess_id, 3, MessageDirection.CLIENT_TO_SERVER, "INVALID_STATE_SKIP"),
                ProtocolMessage(sess_id, 4, MessageDirection.SERVER_TO_CLIENT, "ERROR"),
            ]
            sessions.append((ProtocolSession(sess_id, messages=msgs), True))
        return sessions

    @staticmethod
    def generate_unseen_zero_day_deviations(count: int = 5) -> list[tuple[ProtocolSession, bool]]:
        """
        Generate previously unseen zero-day style attack sessions.
        Returns list of (ProtocolSession, is_attack=True).
        """
        sessions: list[tuple[ProtocolSession, bool]] = []
        for i in range(1, count + 1):
            sess_id = f"zero_day_sess_{i}"
            msgs = [
                ProtocolMessage(sess_id, 1, MessageDirection.CLIENT_TO_SERVER, "SYN"),
                ProtocolMessage(sess_id, 2, MessageDirection.SERVER_TO_CLIENT, "SEND_SYN_ACK"),
                ProtocolMessage(sess_id, 3, MessageDirection.CLIENT_TO_SERVER, "UNSEEN_EXPLOIT_PAYLOAD"),
                ProtocolMessage(sess_id, 4, MessageDirection.SERVER_TO_CLIENT, "ERROR_UNHANDLED"),
                ProtocolMessage(sess_id, 5, MessageDirection.CLIENT_TO_SERVER, "MALFORMED_RECURSIVE_TAG"),
                ProtocolMessage(sess_id, 6, MessageDirection.SERVER_TO_CLIENT, "CRASH"),
            ]
            sessions.append((ProtocolSession(sess_id, messages=msgs), True))
        return sessions

    @staticmethod
    def generate_protocol_evolution_sessions(count: int = 5) -> list[tuple[ProtocolSession, bool]]:
        """
        Generate legitimate protocol evolution sessions (CAPABILITIES extension).
        Returns list of (ProtocolSession, is_attack=False).
        """
        sessions: list[tuple[ProtocolSession, bool]] = []
        for i in range(1, count + 1):
            sess_id = f"evol_sess_{i}"
            msgs = [
                ProtocolMessage(sess_id, 1, MessageDirection.CLIENT_TO_SERVER, "SYN"),
                ProtocolMessage(sess_id, 2, MessageDirection.SERVER_TO_CLIENT, "SEND_SYN_ACK"),
                ProtocolMessage(sess_id, 3, MessageDirection.CLIENT_TO_SERVER, "ACK"),
                ProtocolMessage(sess_id, 4, MessageDirection.SERVER_TO_CLIENT, "ALLOCATE_SESSION"),
                ProtocolMessage(sess_id, 5, MessageDirection.CLIENT_TO_SERVER, "CAPABILITIES"),
                ProtocolMessage(sess_id, 6, MessageDirection.SERVER_TO_CLIENT, "CAPABILITIES_ACK"),
                ProtocolMessage(sess_id, 7, MessageDirection.CLIENT_TO_SERVER, "FIN"),
                ProtocolMessage(sess_id, 8, MessageDirection.SERVER_TO_CLIENT, "CLOSE"),
            ]
            sessions.append((ProtocolSession(sess_id, messages=msgs), False))
        return sessions

    @staticmethod
    def generate_poisoning_sessions(count: int = 50) -> list[tuple[ProtocolSession, bool]]:
        """
        Generate single-session high-frequency poisoning attack sessions.
        Returns list of (ProtocolSession, is_attack=True).
        """
        sessions: list[tuple[ProtocolSession, bool]] = []
        sess_id = "attacker_single_session"
        for i in range(1, count + 1):
            msgs = [
                ProtocolMessage(sess_id, 1, MessageDirection.CLIENT_TO_SERVER, "POISON_PAYLOAD"),
                ProtocolMessage(sess_id, 2, MessageDirection.SERVER_TO_CLIENT, "ERROR"),
            ]
            sessions.append((ProtocolSession(sess_id, messages=msgs), True))
        return sessions

