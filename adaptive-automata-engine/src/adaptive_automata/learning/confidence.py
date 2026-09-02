"""
Model Confidence Metrics and Transition Metadata calculation.

Provides transition observation counting, confidence scoring using Laplace smoothing,
and formal status classification distinguishing observed, probable, uncertain, and unknown behavior.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Sequence, TypeVar

SymbolT = TypeVar("SymbolT")
OutputT = TypeVar("OutputT")


class ConfidenceLevel(str, Enum):
    """Classification status for automaton state transitions."""
    OBSERVED = "OBSERVED"           # High empirical observation count (N >= threshold)
    PROBABLE = "PROBABLE"           # Moderate observation count (0 < N < threshold)
    UNCERTAIN = "UNCERTAIN"         # Inferred/hypothesized with minimal evidence
    UNKNOWN = "UNKNOWN"             # Unexplored transition (N == 0)
    ACTIVE_VERIFIED = "ACTIVE_VERIFIED" # Verified via active SUT membership query


@dataclass(slots=True)
class TransitionMetadata:
    """
    Empirical metrics and confidence classification for a state transition.

    Attributes:
        source_state: Label of origin state.
        input_symbol: Input symbol trigger.
        target_state: Label of destination state.
        output_symbol: Transduction output symbol.
        observation_count: Number of times this transition was observed in traces (N).
        confidence_score: Computed probability / confidence metric in [0.0, 1.0].
        status: ConfidenceLevel classification.
    """
    source_state: str
    input_symbol: str
    target_state: str
    output_symbol: str
    observation_count: int = 0
    confidence_score: float = 0.0
    status: ConfidenceLevel = ConfidenceLevel.UNKNOWN

    def __repr__(self) -> str:
        return (
            f"TransitionMetadata({self.source_state} --[{self.input_symbol} / {self.output_symbol}]--> "
            f"{self.target_state} | N={self.observation_count}, conf={self.confidence_score:.3f}, status={self.status.value})"
        )


class ConfidenceCalculator:
    """
    Calculates transition confidence scores and status classifications.
    """

    def __init__(self, observation_threshold: int = 5, smoothing_alpha: float = 1.0) -> None:
        self.observation_threshold = observation_threshold
        self.smoothing_alpha = smoothing_alpha

    def compute_confidence(
        self,
        observation_count: int,
        total_state_observations: int,
        alphabet_size: int,
        is_active_verified: bool = False,
    ) -> tuple[float, ConfidenceLevel]:
        """
        Compute Laplace-smoothed confidence score and ConfidenceLevel status.

        Formula:
            C = (N + alpha) / (N_total + alpha * |Sigma|)
        """
        if is_active_verified:
            score = 1.0
            status = ConfidenceLevel.ACTIVE_VERIFIED
            return score, status

        if total_state_observations == 0:
            denom = self.smoothing_alpha * max(1, alphabet_size)
            score = self.smoothing_alpha / denom
            status = ConfidenceLevel.UNKNOWN
            return score, status

        num = observation_count + self.smoothing_alpha
        denom = total_state_observations + (self.smoothing_alpha * max(1, alphabet_size))
        score = num / denom

        if observation_count >= self.observation_threshold:
            status = ConfidenceLevel.OBSERVED
        elif observation_count > 0:
            status = ConfidenceLevel.PROBABLE
        else:
            status = ConfidenceLevel.UNKNOWN

        return score, status
