"""
Security Metrics and Confusion Matrix Evaluation component.

Provides ConfusionMatrix and EvaluationResult containers computing precision, recall, F1-score,
accuracy, false positive rate (FPR), false negative rate (FNR), and latency statistics.
"""

from dataclasses import dataclass, field
import math
from typing import Any, Sequence


@dataclass(slots=True)
class ConfusionMatrix:
    """
    Standard binary confusion matrix accumulator.
    """
    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0

    def add_result(self, is_actual_attack: bool, is_predicted_attack: bool) -> None:
        """Record a prediction result."""
        if is_actual_attack and is_predicted_attack:
            self.tp += 1
        elif not is_actual_attack and is_predicted_attack:
            self.fp += 1
        elif not is_actual_attack and not is_predicted_attack:
            self.tn += 1
        elif is_actual_attack and not is_predicted_attack:
            self.fn += 1


@dataclass(slots=True)
class EvaluationResult:
    """
    Comprehensive cybersecurity evaluation benchmark report.
    """
    tp: int
    tn: int
    fp: int
    fn: int
    unseen_attack_detection_rate: float = 0.0
    legitimate_evolution_acceptance_rate: float = 0.0
    incorrect_adaptation_rate: float = 0.0
    latency_metrics: dict[str, float] = field(default_factory=dict)
    additional_metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_samples(self) -> int:
        return self.tp + self.tn + self.fp + self.fn

    @property
    def precision(self) -> float:
        denom = self.tp + self.fp
        return round(self.tp / denom, 4) if denom > 0 else 0.0

    @property
    def recall(self) -> float:
        denom = self.tp + self.fn
        return round(self.tp / denom, 4) if denom > 0 else 0.0

    @property
    def f1_score(self) -> float:
        p, r = self.precision, self.recall
        denom = p + r
        return round(2.0 * (p * r) / denom, 4) if denom > 0 else 0.0

    @property
    def accuracy(self) -> float:
        denom = self.total_samples
        return round((self.tp + self.tn) / denom, 4) if denom > 0 else 0.0

    @property
    def false_positive_rate(self) -> float:
        denom = self.fp + self.tn
        return round(self.fp / denom, 4) if denom > 0 else 0.0

    @property
    def false_negative_rate(self) -> float:
        denom = self.fn + self.tp
        return round(self.fn / denom, 4) if denom > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics summary to dictionary."""
        return {
            "tp": self.tp,
            "tn": self.tn,
            "fp": self.fp,
            "fn": self.fn,
            "total_samples": self.total_samples,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "accuracy": self.accuracy,
            "false_positive_rate": self.false_positive_rate,
            "false_negative_rate": self.false_negative_rate,
            "unseen_attack_detection_rate": self.unseen_attack_detection_rate,
            "legitimate_evolution_acceptance_rate": self.legitimate_evolution_acceptance_rate,
            "incorrect_adaptation_rate": self.incorrect_adaptation_rate,
            "latency_metrics": self.latency_metrics,
        }

    @staticmethod
    def compute_latency_stats(latencies_ms: Sequence[float]) -> dict[str, float]:
        """Compute mean, median (P50), and P95 latency statistics in milliseconds."""
        if not latencies_ms:
            return {"mean_ms": 0.0, "median_ms": 0.0, "p95_ms": 0.0}

        sorted_lat = sorted(latencies_ms)
        n = len(sorted_lat)

        mean_val = sum(sorted_lat) / n
        median_val = sorted_lat[n // 2]
        p95_idx = min(n - 1, int(math.ceil(0.95 * n)) - 1)
        p95_val = sorted_lat[p95_idx]

        return {
            "mean_ms": round(mean_val, 4),
            "median_ms": round(median_val, 4),
            "p95_ms": round(p95_val, 4),
        }
