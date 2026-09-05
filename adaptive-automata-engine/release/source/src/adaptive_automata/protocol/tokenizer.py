"""
Protocol Stream and Message Tokenizer abstractions.

Converts raw protocol streams and structured ProtocolMessage instances into discrete
ProtocolTokens and (input_symbol, output_symbol) transduction tuples.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping

from .trace import MessageDirection, ProtocolMessage, ProtocolSession


@dataclass(frozen=True, slots=True)
class ProtocolToken:
    """
    Discrete protocol symbol produced by tokenizing a protocol stream or message.

    Attributes:
        token_type: High-level classification (e.g., 'HEADER', 'COMMAND', 'DELIMITER', 'PAYLOAD').
        value: Raw or parsed string/bytes payload value.
        position: Index or offset in source stream.
        metadata: Additional contextual metadata (e.g. lengths, headers).
    """
    token_type: str
    value: Any
    position: int = 0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"ProtocolToken({self.token_type}: {self.value!r} @ pos {self.position})"


class BaseTokenizer(ABC):
    """Abstract base tokenizer for converting raw protocol inputs into ProtocolToken sequences."""

    @abstractmethod
    def tokenize(self, stream: Any) -> list[ProtocolToken]:
        """Tokenize protocol stream input into a list of ProtocolTokens."""
        pass


class DelimiterTokenizer(BaseTokenizer):
    """Tokenizes string streams separated by delimiters (e.g., space, newline, pipe)."""

    def __init__(self, delimiter: str = " ", default_token_type: str = "SYMBOL") -> None:
        self.delimiter = delimiter
        self.default_token_type = default_token_type

    def tokenize(self, stream: str) -> list[ProtocolToken]:
        if not isinstance(stream, str):
            raise TypeError(f"DelimiterTokenizer expects str, got {type(stream).__name__}")

        raw_parts = stream.strip().split(self.delimiter)
        tokens: list[ProtocolToken] = []
        pos = 0
        for part in raw_parts:
            if not part:
                continue
            is_valid_identifier = part.replace("_", "").isalnum()
            tokens.append(
                ProtocolToken(
                    token_type=part.upper() if is_valid_identifier else self.default_token_type,
                    value=part,
                    position=pos,
                )
            )
            pos += 1
        return tokens


class BaseMessageTokenizer(ABC):
    """
    Abstract Base Class for message-level protocol tokenizers.

    Transforms structured ProtocolMessages into discrete ProtocolTokens and session transduction tuples.
    """

    @abstractmethod
    def tokenize_message(self, message: ProtocolMessage) -> ProtocolToken:
        """Convert a single ProtocolMessage into a canonical ProtocolToken."""
        pass

    def tokenize_session(self, session: ProtocolSession) -> list[tuple[str, str]]:
        """
        Tokenize a full session into a list of (input_symbol, output_symbol) transduction tuples.
        """
        pairs: list[tuple[str, str]] = []
        msgs = session.messages
        i = 0
        n = len(msgs)
        while i < n - 1:
            req = msgs[i]
            resp = msgs[i + 1]
            if req.direction == MessageDirection.CLIENT_TO_SERVER and resp.direction == MessageDirection.SERVER_TO_CLIENT:
                t_req = self.tokenize_message(req)
                t_resp = self.tokenize_message(resp)
                pairs.append((t_req.token_type, t_resp.token_type))
                i += 2
            else:
                i += 1
        return pairs


class HeaderCommandTokenizer(BaseMessageTokenizer):
    """
    Tokenizer using high-level message types/commands, ignoring dynamic payload fields.
    """

    def tokenize_message(self, message: ProtocolMessage) -> ProtocolToken:
        cmd_type = message.message_type.upper().strip()
        return ProtocolToken(
            token_type=cmd_type,
            value=message.payload,
            position=message.sequence_number,
            metadata={"direction": message.direction.value},
        )


class JSONMessageTokenizer(BaseMessageTokenizer):
    """
    Modular tokenizer extracting message structural headers while abstracting payload fields.
    """

    def __init__(self, header_field: str = "cmd", type_override_field: str | None = None) -> None:
        self.header_field = header_field
        self.type_override_field = type_override_field

    def tokenize_message(self, message: ProtocolMessage) -> ProtocolToken:
        payload = message.payload
        token_label = message.message_type

        if isinstance(payload, dict):
            if self.header_field in payload:
                token_label = str(payload[self.header_field])
            elif self.type_override_field and self.type_override_field in payload:
                token_label = str(payload[self.type_override_field])

        token_type = token_label.upper().strip()
        return ProtocolToken(
            token_type=token_type,
            value=message.payload,
            position=message.sequence_number,
            metadata={"session_id": message.session_id, "direction": message.direction.value},
        )
