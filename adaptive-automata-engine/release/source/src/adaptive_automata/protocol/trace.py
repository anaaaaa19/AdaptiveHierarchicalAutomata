"""
Protocol Trace Representation and Loader for recorded network traffic sessions.

Provides deterministic data structures for protocol messages and sessions,
and a loader for parsing and validating JSON trace streams.
"""

from dataclasses import dataclass, field
from enum import Enum
import json
from typing import Any, Mapping, Sequence


class MalformedTraceError(Exception):
    """Raised when a trace file or data structure violates protocol session constraints."""
    pass


class MessageDirection(str, Enum):
    """Direction of protocol message in a session."""
    CLIENT_TO_SERVER = "INBOUND"
    SERVER_TO_CLIENT = "OUTBOUND"

    @classmethod
    def from_str(cls, val: str) -> "MessageDirection":
        clean = val.strip().upper()
        if clean in ("INBOUND", "CLIENT_TO_SERVER", "REQUEST", "REQ", "C2S"):
            return cls.CLIENT_TO_SERVER
        elif clean in ("OUTBOUND", "SERVER_TO_CLIENT", "RESPONSE", "RESP", "RES", "S2C"):
            return cls.SERVER_TO_CLIENT
        raise MalformedTraceError(f"Unknown message direction: '{val}'")


@dataclass(frozen=True, slots=True)
class ProtocolMessage:
    """
    Deterministic representation of a single message exchange event.

    Attributes:
        session_id: Identifier of parent protocol session.
        sequence_number: 1-indexed order within session.
        direction: CLIENT_TO_SERVER (request) or SERVER_TO_CLIENT (response).
        message_type: High-level header or command type (e.g. 'SYN', 'AUTH_REQ', 'ACK').
        payload: Message payload dictionary or parameters.
        timestamp: Epoch timestamp in seconds.
        metadata: Additional contextual properties.
    """
    session_id: str
    sequence_number: int
    direction: MessageDirection
    message_type: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProtocolSession:
    """
    Deterministic ordered sequence of protocol messages forming a session.

    Attributes:
        session_id: Unique session label.
        messages: Chronologically ordered list of ProtocolMessage instances.
        duration_ms: Total session duration.
        metadata: Session-level metadata.
    """
    session_id: str
    messages: list[ProtocolMessage] = field(default_factory=list)
    duration_ms: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def get_transduction_pairs(self) -> list[tuple[str, str]]:
        """
        Extract transductions: pairs of consecutive (INBOUND message_type, OUTBOUND message_type).

        Returns:
            List of (input_symbol, output_symbol) tuples.
        """
        pairs: list[tuple[str, str]] = []
        i = 0
        n = len(self.messages)
        while i < n - 1:
            req = self.messages[i]
            resp = self.messages[i + 1]
            if req.direction == MessageDirection.CLIENT_TO_SERVER and resp.direction == MessageDirection.SERVER_TO_CLIENT:
                pairs.append((req.message_type, resp.message_type))
                i += 2
            else:
                i += 1
        return pairs


class TraceLoader:
    """Loader and validator for recorded protocol traces in JSON format."""

    @classmethod
    def load_from_json(cls, raw_json: str | bytes) -> list[ProtocolSession]:
        """
        Parse and validate JSON trace content into a list of ProtocolSession objects.

        Raises:
            MalformedTraceError: If JSON structure or message fields are invalid.
        """
        try:
            data = json.loads(raw_json)
        except Exception as e:
            raise MalformedTraceError(f"Invalid JSON syntax in trace: {e}") from e

        if isinstance(data, dict):
            if "sessions" in data:
                sessions_raw = data["sessions"]
            elif "session_id" in data:
                sessions_raw = [data]
            else:
                raise MalformedTraceError("JSON trace root dict missing 'sessions' array.")
        elif isinstance(data, list):
            sessions_raw = data
        else:
            raise MalformedTraceError("JSON trace root must be an array of sessions or an object containing 'sessions'.")

        sessions: list[ProtocolSession] = []
        for sess_idx, sess_dict in enumerate(sessions_raw):
            if not isinstance(sess_dict, dict):
                raise MalformedTraceError(f"Session item at index {sess_idx} is not a dictionary.")

            session_id = str(sess_dict.get("session_id", f"sess_{sess_idx}"))
            raw_msgs = sess_dict.get("messages", [])
            if not isinstance(raw_msgs, list):
                raise MalformedTraceError(f"Session '{session_id}' field 'messages' must be a list.")

            messages: list[ProtocolMessage] = []
            for msg_idx, msg_dict in enumerate(raw_msgs):
                if not isinstance(msg_dict, dict):
                    raise MalformedTraceError(f"Message at index {msg_idx} in session '{session_id}' is not a dict.")

                if "message_type" not in msg_dict or "direction" not in msg_dict:
                    raise MalformedTraceError(
                        f"Message at index {msg_idx} in session '{session_id}' missing 'message_type' or 'direction'."
                    )

                direction = MessageDirection.from_str(str(msg_dict["direction"]))
                seq_num = int(msg_dict.get("sequence_number", msg_idx + 1))
                msg_type = str(msg_dict["message_type"]).strip()
                payload = msg_dict.get("payload", {})
                timestamp = float(msg_dict.get("timestamp", 0.0))
                metadata = msg_dict.get("metadata", {})

                messages.append(
                    ProtocolMessage(
                        session_id=session_id,
                        sequence_number=seq_num,
                        direction=direction,
                        message_type=msg_type,
                        payload=payload if isinstance(payload, dict) else {"raw": payload},
                        timestamp=timestamp,
                        metadata=metadata if isinstance(metadata, dict) else {},
                    )
                )

            # Sort chronologically by sequence_number
            messages.sort(key=lambda m: m.sequence_number)
            duration = float(sess_dict.get("duration_ms", 0.0))
            metadata = sess_dict.get("metadata", {})

            sessions.append(
                ProtocolSession(
                    session_id=session_id,
                    messages=messages,
                    duration_ms=duration,
                    metadata=metadata if isinstance(metadata, dict) else {},
                )
            )

        return sessions

    @classmethod
    def load_from_file(cls, filepath: str) -> list[ProtocolSession]:
        """Load and validate JSON trace file from filesystem path."""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return cls.load_from_json(content)
