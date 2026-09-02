"""
Novelty Detector component.

Determines whether observed behavior is already represented by the current active protocol model,
or whether it constitutes a model-level novelty (NOVEL / UNKNOWN).
Novelty is strictly a model-level concept, not a security verdict.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from adaptive_automata.analysis.escalation import AnalysisLevel, AnalysisResult, AnalysisStatus
from adaptive_automata.models.versioning import VersionedProtocolModel


class NoveltyStatus(str, Enum):
    """Formal model-level novelty status."""
    KNOWN = "KNOWN"     # Fully represented in active model graph
    NOVEL = "NOVEL"     # Valid or structured novel behavior not in model graph
    UNKNOWN = "UNKNOWN" # Unresolved / undefined behavior


@dataclass(slots=True)
class NoveltyResult:
    """
    Evaluation output produced by NoveltyDetector.
    """
    status: NoveltyStatus
    state: str
    symbol: str
    hierarchical_level: AnalysisLevel
    details: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"NoveltyResult(status={self.status.value}, state='{self.state}', "
            f"symbol='{self.symbol}', level={self.hierarchical_level.value})"
        )


class NoveltyDetector:
    """
    Evaluates Phase 4 AnalysisResult structures to classify behavior novelty.
    """

    def detect_novelty(
        self,
        analysis_result: AnalysisResult,
        model: VersionedProtocolModel[str, str],
    ) -> NoveltyResult:
        """
        Determine model-level novelty from AnalysisResult.

        Returns:
            NoveltyResult indicating KNOWN, NOVEL, or UNKNOWN status.
        """
        st_name = analysis_result.state
        sym = analysis_result.symbol

        if analysis_result.status == AnalysisStatus.KNOWN:
            return NoveltyResult(
                status=NoveltyStatus.KNOWN,
                state=st_name,
                symbol=sym,
                hierarchical_level=analysis_result.level_used,
                details={"model_version": model.version},
            )
        elif analysis_result.status in (AnalysisStatus.NOVEL_BUT_VALID, AnalysisStatus.STRUCTURAL_VIOLATION):
            return NoveltyResult(
                status=NoveltyStatus.NOVEL,
                state=st_name,
                symbol=sym,
                hierarchical_level=analysis_result.level_used,
                details={"model_version": model.version, "analysis_reason": analysis_result.reason},
            )
        else:
            return NoveltyResult(
                status=NoveltyStatus.UNKNOWN,
                state=st_name,
                symbol=sym,
                hierarchical_level=analysis_result.level_used,
                details={"model_version": model.version, "analysis_reason": analysis_result.reason},
            )
