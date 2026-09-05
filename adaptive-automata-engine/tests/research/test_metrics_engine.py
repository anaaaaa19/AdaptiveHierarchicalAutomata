"""
Unit tests for MetricsEngine correctness, precision, recall, F1, and latency calculations.
"""

from adaptive_automata.evaluation.baselines import EvalResult
from adaptive_automata.evaluation.dataset import ProtocolSample
from adaptive_automata.evaluation.metrics import MetricsEngine, EvaluationMetrics


def test_metrics_calculation_correctness():
    # 2 TP, 2 TN, 1 FP, 1 FN
    samples_and_results = [
        # Normal sequence accepted -> TN
        (
            ProtocolSample("1", "proto", ["HELLO"], "normal", "normal"),
            EvalResult(is_accepted=True, is_anomaly=False, is_novel=False, escalation_level="DFA", execution_time_ms=1.0),
        ),
        # Normal sequence accepted -> TN
        (
            ProtocolSample("2", "proto", ["HELLO"], "normal", "normal"),
            EvalResult(is_accepted=True, is_anomaly=False, is_novel=False, escalation_level="DFA", execution_time_ms=1.5),
        ),
        # Normal sequence rejected -> FP
        (
            ProtocolSample("3", "proto", ["HELLO"], "normal", "normal"),
            EvalResult(is_accepted=False, is_anomaly=True, is_novel=True, escalation_level="REJECT", execution_time_ms=2.0),
        ),
        # Anomaly rejected -> TP
        (
            ProtocolSample("4", "proto", ["BAD"], "anomalous", "structural_anomaly"),
            EvalResult(is_accepted=False, is_anomaly=True, is_novel=True, escalation_level="REJECT", execution_time_ms=1.0),
        ),
        # Anomaly rejected -> TP
        (
            ProtocolSample("5", "proto", ["BAD"], "anomalous", "structural_anomaly"),
            EvalResult(is_accepted=False, is_anomaly=True, is_novel=True, escalation_level="REJECT", execution_time_ms=1.0),
        ),
        # Anomaly accepted -> FN
        (
            ProtocolSample("6", "proto", ["BAD"], "anomalous", "structural_anomaly"),
            EvalResult(is_accepted=True, is_anomaly=False, is_novel=False, escalation_level="DFA", execution_time_ms=1.0),
        ),
    ]

    metrics: EvaluationMetrics = MetricsEngine.compute_metrics(samples_and_results)

    assert metrics.tp == 2
    assert metrics.tn == 2
    assert metrics.fp == 1
    assert metrics.fn == 1

    # Precision = TP / (TP + FP) = 2 / (2 + 1) = 0.6667
    assert abs(metrics.precision - 2 / 3) < 1e-3
    # Recall = TP / (TP + FN) = 2 / (2 + 1) = 0.6667
    assert abs(metrics.recall - 2 / 3) < 1e-3
    # F1 = 2 * P * R / (P + R) = 0.6667
    assert abs(metrics.f1 - 2 / 3) < 1e-3
    # Accuracy = (2 + 2) / 6 = 0.6667
    assert abs(metrics.accuracy - 4 / 6) < 1e-3
