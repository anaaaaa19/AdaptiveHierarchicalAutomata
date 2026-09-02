"""Unit tests for ConfusionMatrix and EvaluationResult metrics computation."""

from adaptive_automata.security import ConfusionMatrix, EvaluationResult


def test_confusion_matrix_and_evaluation_result():
    cm = ConfusionMatrix()
    # 8 TP, 2 FN, 1 FP, 9 TN
    for _ in range(8):
        cm.add_result(is_actual_attack=True, is_predicted_attack=True)
    for _ in range(2):
        cm.add_result(is_actual_attack=True, is_predicted_attack=False)
    for _ in range(1):
        cm.add_result(is_actual_attack=False, is_predicted_attack=True)
    for _ in range(9):
        cm.add_result(is_actual_attack=False, is_predicted_attack=False)

    assert cm.tp == 8
    assert cm.fn == 2
    assert cm.fp == 1
    assert cm.tn == 9

    eval_res = EvaluationResult(tp=cm.tp, tn=cm.tn, fp=cm.fp, fn=cm.fn)

    assert eval_res.total_samples == 20
    assert eval_res.precision == round(8 / 9, 4)
    assert eval_res.recall == 0.8
    assert eval_res.f1_score > 0.8
    assert eval_res.accuracy == 0.85
    assert eval_res.false_positive_rate == round(1 / 10, 4)
    assert eval_res.false_negative_rate == 0.2


def test_latency_stats():
    latencies = [1.0, 2.0, 3.0, 4.0, 5.0, 10.0]
    stats = EvaluationResult.compute_latency_stats(latencies)

    assert "mean_ms" in stats
    assert "median_ms" in stats
    assert "p95_ms" in stats
    assert stats["median_ms"] > 0
