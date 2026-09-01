from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class ProtocolToken:
    """
    Discrete protocol symbol produced by tokenizing a protocol stream.

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
    """Abstract base tokenizer for converting protocol inputs into ProtocolToken sequences."""

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
