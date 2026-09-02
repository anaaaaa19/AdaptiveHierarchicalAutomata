"""
Session Manager Component for Protocol Session Reconstruction and State Tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import threading
import time
from typing import Any

from adaptive_automata.protocol.trace import ProtocolSession, ProtocolMessage, MessageDirection
from adaptive_automata.deployment.packet.processor import ProcessedPacket


@dataclass
class NetworkMetadata:
    """Network-level tuple metadata."""
    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    protocol: str


@dataclass
class ProtocolState:
    """Formal protocol state tracking."""
    current_formal_state: str = "q0"
    recent_symbols: list[str] = field(default_factory=list)
    packet_count: int = 0
    byte_count: int = 0
    active_model_version: str = "v1.0.0"


@dataclass
class SecurityState:
    """Security risk and alert tracking."""
    deviation_count: int = 0
    highest_severity: str = "BENIGN"
    last_assessment_status: str = "KNOWN"
    alerts_generated: int = 0


class SessionContext:
    """
    Separated Session Container isolating network metadata, formal protocol state,
    and security evaluation state.
    """

    def __init__(
        self,
        session_id: str,
        network_meta: NetworkMetadata,
        model_version: str = "v1.0.0",
    ) -> None:
        self.session_id = session_id
        self.network = network_meta
        self.protocol = ProtocolState(active_model_version=model_version)
        self.security = SecurityState()
        self.start_time: float = time.time()
        self.last_seen: float = time.time()
        self.is_closed: bool = False
        self.close_reason: str = ""
        self._raw_messages: list[str] = []

    def touch(self) -> None:
        self.last_seen = time.time()

    def record_packet(self, processed_pkt: ProcessedPacket) -> None:
        self.touch()
        self.protocol.packet_count += 1
        self.protocol.byte_count += processed_pkt.length
        if processed_pkt.payload_str:
            self._raw_messages.append(processed_pkt.payload_str)

    def to_protocol_session(self) -> ProtocolSession:
        """Convert session state into Phase 1-7 ProtocolSession object."""
        msgs = []
        for idx, raw_msg in enumerate(self._raw_messages):
            msg_type = raw_msg.split(":")[0].strip() if ":" in raw_msg else raw_msg.strip()
            pm = ProtocolMessage(
                session_id=self.session_id,
                sequence_number=idx + 1,
                direction=MessageDirection.CLIENT_TO_SERVER if idx % 2 == 0 else MessageDirection.SERVER_TO_CLIENT,
                message_type=msg_type,
                payload={"raw": raw_msg},
            )
            msgs.append(pm)
        return ProtocolSession(session_id=self.session_id, messages=msgs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "network": {
                "src_ip": self.network.src_ip,
                "src_port": self.network.src_port,
                "dst_ip": self.network.dst_ip,
                "dst_port": self.network.dst_port,
                "protocol": self.network.protocol,
            },
            "protocol": {
                "current_formal_state": self.protocol.current_formal_state,
                "recent_symbols": self.protocol.recent_symbols[-10:],
                "packet_count": self.protocol.packet_count,
                "byte_count": self.protocol.byte_count,
                "model_version": self.protocol.active_model_version,
            },
            "security": {
                "deviation_count": self.security.deviation_count,
                "highest_severity": self.security.highest_severity,
                "last_assessment_status": self.security.last_assessment_status,
                "alerts_generated": self.security.alerts_generated,
            },
            "start_time": datetime.fromtimestamp(self.start_time, timezone.utc).isoformat(),
            "last_seen": datetime.fromtimestamp(self.last_seen, timezone.utc).isoformat(),
            "is_closed": self.is_closed,
            "close_reason": self.close_reason,
        }


class SessionManager:
    """
    Session Manager maintaining active session table, 5-tuple lookup, and timeout cleanup.
    """

    def __init__(
        self,
        max_inactivity_sec: float = 300.0,
        max_sessions: int = 10000,
    ) -> None:
        self.max_inactivity_sec = max_inactivity_sec
        self.max_sessions = max_sessions
        self._lock = threading.Lock()
        self._flow_to_session: dict[tuple[str, int, str, int, str], str] = {}
        self._sessions: dict[str, SessionContext] = {}

    def get_or_create_session(
        self,
        processed_pkt: ProcessedPacket,
        active_model_version: str = "v1.0.0",
    ) -> SessionContext:
        with self._lock:
            flow = processed_pkt.flow_key
            src_ip, src_port, dst_ip, dst_port, proto = flow
            rev_flow = (dst_ip, dst_port, src_ip, src_port, proto)

            session_id = self._flow_to_session.get(flow) or self._flow_to_session.get(rev_flow)

            if not session_id:
                # Session capacity enforcement
                if len(self._sessions) >= self.max_sessions:
                    self._cleanup_expired_unlocked(force_evict_oldest=True)

                session_id = f"sess_{src_ip}:{src_port}_{dst_ip}:{dst_port}_{int(time.time() * 1000)}"
                meta = NetworkMetadata(
                    src_ip=src_ip,
                    src_port=src_port,
                    dst_ip=dst_ip,
                    dst_port=dst_port,
                    protocol=proto,
                )
                ctx = SessionContext(session_id, meta, model_version=active_model_version)
                self._sessions[session_id] = ctx
                self._flow_to_session[flow] = session_id
                self._flow_to_session[rev_flow] = session_id

            ctx = self._sessions[session_id]
            ctx.record_packet(processed_pkt)
            return ctx

    def get_session(self, session_id: str) -> SessionContext | None:
        with self._lock:
            return self._sessions.get(session_id)

    def list_active_sessions(self) -> list[SessionContext]:
        with self._lock:
            return [ctx for ctx in self._sessions.values() if not ctx.is_closed]

    def cleanup_expired(self) -> int:
        with self._lock:
            return self._cleanup_expired_unlocked()

    def _cleanup_expired_unlocked(self, force_evict_oldest: bool = False) -> int:
        now = time.time()
        expired_ids = []
        for sess_id, ctx in self._sessions.items():
            if now - ctx.last_seen > self.max_inactivity_sec:
                expired_ids.append(sess_id)

        if not expired_ids and force_evict_oldest and self._sessions:
            oldest_id = min(self._sessions.keys(), key=lambda k: self._sessions[k].last_seen)
            expired_ids.append(oldest_id)

        for sess_id in expired_ids:
            ctx = self._sessions[sess_id]
            ctx.is_closed = True
            ctx.close_reason = "TIMEOUT" if not force_evict_oldest else "RESOURCE_LIMIT"
            # Remove flow pointers
            flows_to_remove = [f for f, sid in self._flow_to_session.items() if sid == sess_id]
            for f in flows_to_remove:
                del self._flow_to_session[f]
            del self._sessions[sess_id]

        return len(expired_ids)
