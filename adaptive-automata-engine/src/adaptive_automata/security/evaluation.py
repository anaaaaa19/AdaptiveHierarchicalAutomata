"""
Security Evaluator component.

Computes EvaluationResult objects and benchmark statistics given ground-truth trace labels
and system security alerts.
"""

from typing import Sequence
from .metrics import ConfusionMatrix, EvaluationResult


class SecurityEvaluator:
    """
    Evaluates cybersecurity detection performance against labeled dataset traces.
    """

    def evaluate_predictions(
        self,
        actual_is_attack: Sequence[bool],
        predicted_is_attack: Sequence[bool],
        latencies_ms: Sequence[float] | None = None,
        unseen_attacks_count: tuple[int, int] | None = None, # (detected_unseen, total_unseen)
    ) -> EvaluationResult:
        """
        Compute comprehensive EvaluationResult from actual vs predicted boolean vectors.
        """
        cm = ConfusionMatrix()
        for actual, pred in zip(actual_is_attack, predicted_is_attack):
            cm.add_result(actual, pred)

        unseen_rate = 0.0
        if unseen_attacks_count and unseen_attacks_count[1] > 0:
            unseen_rate = round(unseen_attacks_count[0] / unseen_attacks_count[1], 4)

        lat_stats = EvaluationResult.compute_latency_stats(latencies_ms or [])

        return EvaluationResult(
            tp=cm.tp,
            tn=cm.tn,
            fp=cm.fp,
            fn=cm.fn,
            unseen_attack_detection_rate=unseen_rate,
            latency_metrics=lat_stats,
        )
