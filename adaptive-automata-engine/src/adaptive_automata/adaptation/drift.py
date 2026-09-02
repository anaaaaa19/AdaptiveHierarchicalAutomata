"""
Concept Drift Detector component.

Detects statistical behavioral shifts over sliding observation windows using
Jensen-Shannon Divergence (JSD) distance between distribution snapshots.

CRITICAL PRINCIPLE:
Concept drift detection is an adaptation trigger signal, NOT an automatic model update command.
"""

from collections import Counter
from dataclasses import dataclass, field
import math
from typing import Sequence


@dataclass(slots=True)
class DriftConfig:
    """
    Configuration parameters for sliding-window concept drift detection.
    """
    window_size: int = 50
    threshold: float = 0.2  # Jensen-Shannon Divergence threshold in [0.0, 1.0]


@dataclass(slots=True)
class DriftResult:
    """
    Evaluation output produced by ConceptDriftDetector.
    """
    detected: bool
    js_divergence_score: float
    threshold: float
    affected_behaviors: list[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"DriftResult(detected={self.detected}, score={self.js_divergence_score:.4f}, "
            f"threshold={self.threshold}, affected={len(self.affected_behaviors)})"
        )


class ConceptDriftDetector:
    """
    Sliding-window statistical Concept Drift Detector using Jensen-Shannon Divergence.
    """

    def __init__(self, config: DriftConfig | None = None) -> None:
        self.config = config or DriftConfig()

    def _compute_kl_divergence(self, p: dict[str, float], q: dict[str, float]) -> float:
        """Kullback-Leibler (KL) divergence D_KL(P || Q)."""
        kl = 0.0
        for x, p_val in p.items():
            if p_val > 0:
                q_val = q.get(x, 1e-9)
                kl += p_val * math.log2(p_val / q_val)
        return kl

    def compute_js_divergence(self, p_counts: Mapping[str, int], q_counts: Mapping[str, int]) -> float:
        """
        Compute Jensen-Shannon Divergence (JSD) between two frequency distributions P and Q.

        JSD(P || Q) = 0.5 * D_KL(P || M) + 0.5 * D_KL(Q || M), where M = 0.5 * (P + Q).
        Returns:
            Bounded JSD score in [0.0, 1.0].
        """
        all_keys = set(p_counts.keys()).union(set(q_counts.keys()))
        if not all_keys:
            return 0.0

        p_total = sum(p_counts.values()) or 1
        q_total = sum(q_counts.values()) or 1

        p_dist: dict[str, float] = {k: p_counts.get(k, 0) / p_total for k in all_keys}
        q_dist: dict[str, float] = {k: q_counts.get(k, 0) / q_total for k in all_keys}

        m_dist: dict[str, float] = {k: 0.5 * (p_dist[k] + q_dist[k]) for k in all_keys}

        kl_pm = self._compute_kl_divergence(p_dist, m_dist)
        kl_qm = self._compute_kl_divergence(q_dist, m_dist)

        jsd = 0.5 * kl_pm + 0.5 * kl_qm
        return max(0.0, min(1.0, round(jsd, 4)))

    def detect_drift(
        self,
        recent_symbols: Sequence[str],
        baseline_symbols: Sequence[str],
    ) -> DriftResult:
        """
        Compare recent sliding-window symbol distribution against baseline distribution.

        Returns:
            DriftResult indicating whether statistical drift was detected.
        """
        if not recent_symbols or not baseline_symbols:
            return DriftResult(detected=False, js_divergence_score=0.0, threshold=self.config.threshold)

        win_size = min(len(recent_symbols), self.config.window_size)
        recent_win = recent_symbols[-win_size:]

        p_counts = dict(Counter(baseline_symbols))
        q_counts = dict(Counter(recent_win))

        jsd_score = self.compute_js_divergence(p_counts, q_counts)
        is_detected = jsd_score >= self.config.threshold

        affected: list[str] = []
        if is_detected:
            # Find symbols with significant frequency shift
            for sym, q_cnt in q_counts.items():
                p_cnt = p_counts.get(sym, 0)
                if abs((q_cnt / len(recent_win)) - (p_cnt / len(baseline_symbols))) > 0.1:
                    affected.append(sym)

        return DriftResult(
            detected=is_detected,
            js_divergence_score=jsd_score,
            threshold=self.config.threshold,
            affected_behaviors=affected,
        )
