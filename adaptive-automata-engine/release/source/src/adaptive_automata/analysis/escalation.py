"""
Escalation Controller and Unified Analysis Result types.

Decides whether fast-path DFA/Mealy deviations escalate to PDA and/or CFG formal models
according to the central design principle:
'Use the least expressive formal model capable of explaining the observed behavior.'
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Sequence

from .event import DeviationEvent


class AnalysisLevel(str, Enum):
    """Formal model hierarchy level used for analysis."""
    DFA_MEALY = "DFA_MEALY"
    PDA = "PDA"
    CFG = "CFG"
    UNRESOLVED = "UNRESOLVED"


class AnalysisStatus(str, Enum):
    """Classification status for evaluated protocol sequences."""
    KNOWN = "KNOWN"                           # Fully recognized by DFA/Mealy fast-path
    NOVEL_BUT_VALID = "NOVEL_BUT_VALID"       # Rejected by regular DFA, but validated by higher PDA/CFG formal model
    STRUCTURAL_VIOLATION = "STRUCTURAL_VIOLATION" # Grammar/framing syntax error in higher model
    ANOMALOUS = "ANOMALOUS"                   # Explicit anomaly violation
    UNKNOWN = "UNKNOWN"                       # Unresolved novel behavior (not automatically labeled malicious)


@dataclass(slots=True)
class AnalysisResult:
    """
    Unified evaluation result produced by the Hierarchical Analyzer.
    """
    status: AnalysisStatus
    level_used: AnalysisLevel
    reason: str
    state: str
    symbol: str
    confidence_score: float | None
    model_version: str
    details: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        conf_str = f"{self.confidence_score:.3f}" if self.confidence_score is not None else "N/A"
        return (
            f"AnalysisResult(status={self.status.value}, level={self.level_used.value}, "
            f"state='{self.state}', symbol='{self.symbol}', conf={conf_str}, "
            f"version='{self.model_version}', reason='{self.reason}')"
        )


class EscalationController:
    """
    Controls formal model escalation decisions when fast-path DFA/Mealy deviations occur.
    """

    def __init__(self, allow_pda: bool = True, allow_cfg: bool = True) -> None:
        self.allow_pda = allow_pda
        self.allow_cfg = allow_cfg

    def should_escalate_to_pda(self, deviation: DeviationEvent, sequence: Sequence[str]) -> bool:
        """
        Decide whether a deviation should escalate to PDA analysis.

        Escalates if PDA analysis is enabled and the sequence contains structural framing
        symbols (e.g., container tags, push/pop headers, nested blocks).
        """
        if not self.allow_pda:
            return False

        # Structural indicator symbols for PDA stack operations
        framing_indicators = {
            "OPEN_BLOCK", "CLOSE_BLOCK", "BEGIN_CONTAINER", "END_CONTAINER",
            "PUSH", "POP", "HEADER_NESTED", "PAYLOAD_WRAPPER", "OPEN", "CLOSE"
        }
        for sym in sequence:
            if any(ind in str(sym).upper() for ind in framing_indicators):
                return True

        # Default fallback: escalate to PDA if deviation occurred after initial state
        return deviation.position > 0

    def should_escalate_to_cfg(self, deviation: DeviationEvent, sequence: Sequence[str], pda_failed: bool) -> bool:
        """
        Decide whether a deviation should escalate to CFG parser analysis.

        Escalates if CFG analysis is enabled and either PDA failed or grammar symbols are present.
        """
        if not self.allow_cfg:
            return False

        return pda_failed or len(sequence) >= 3
