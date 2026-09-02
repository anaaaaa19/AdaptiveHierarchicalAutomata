"""
Phase 6 Experiment 2 — Unseen Zero-Day Behavior Detection Benchmark.

Evaluates Hypothesis H4: A formal hierarchical system can detect previously unseen protocol deviations
without requiring the exact attack pattern to be present during learning.
Withholds zero-day attack sequences from model training/learning.
"""

import json
from pathlib import Path
import time
from typing import Any

from adaptive_automata.analysis import HierarchicalAnalyzer
from adaptive_automata.models import ModelRegistry
from adaptive_automata.protocol import TraceLoader, create_toy_protocol_sut
from adaptive_automata.learning import HybridActiveLearner, PassiveInferenceEngine
from adaptive_automata.adaptation import NoveltyDetector
from adaptive_automata.security import (
    BehavioralAnalyzer,
    BehavioralClassification,
    SecurityEvaluator,
    SyntheticDatasetGenerator,
)



def run_zero_day_experiment() -> dict[str, Any]:
    print("==========================================================================")
    print("  Phase 6 Experiment 2 — Unseen Zero-Day Behavior Benchmark (H4)")
    print("==========================================================================\n")

    base_dir = Path(__file__).parent.parent.parent
    v1_path = base_dir / "examples" / "data" / "toy_protocol_v1.json"
    v1_sessions = TraceLoader.load_from_file(str(v1_path))

    registry = ModelRegistry()
    passive_engine = PassiveInferenceEngine()
    passive_model = passive_engine.infer_model(v1_sessions, model_id="ZeroDayProto", version="v1.0.0-passive")

    sut = create_toy_protocol_sut()
    hybrid_learner = HybridActiveLearner[str, str]()
    baseline_model = hybrid_learner.refine_model(passive_model, sut, new_version="v1.1.0-hybrid")
    registry.register_model(baseline_model)

    analyzer = HierarchicalAnalyzer(fast_path_model=baseline_model)
    novelty_det = NoveltyDetector()
    sec_analyzer = BehavioralAnalyzer()
    evaluator = SecurityEvaluator()

    # Zero-day test set: 10 normal + 10 previously unseen zero-day attack sessions
    normal_traces = SyntheticDatasetGenerator.generate_normal_sessions(10)
    zero_day_traces = SyntheticDatasetGenerator.generate_unseen_zero_day_deviations(10)
    test_dataset = normal_traces + zero_day_traces

    actual_is_attack = [label for _, label in test_dataset]
    preds, lats = [], []
    unseen_detected = 0

    for sess, is_attack in test_dataset:
        st_t = time.perf_counter()
        an_res = analyzer.analyze_session(sess)
        nov_res = novelty_det.detect_novelty(an_res, baseline_model)
        assessment = sec_analyzer.analyze_security(sess, an_res, nov_res)
        lats.append((time.perf_counter() - st_t) * 1000)

        is_alert = assessment.behavioral_classification in (
            BehavioralClassification.POTENTIAL_ATTACK,
            BehavioralClassification.SUSPICIOUS,
            BehavioralClassification.PROTOCOL_VIOLATION,
        )
        preds.append(is_alert)
        if is_attack and is_alert:
            unseen_detected += 1

    eval_result = evaluator.evaluate_predictions(
        actual_is_attack,
        preds,
        lats,
        unseen_attacks_count=(unseen_detected, 10),
    )

    print(f"[+] Total Zero-Day Attack Traces Evaluated: 10")
    print(f"[+] Zero-Day Attacks Detected: {unseen_detected} / 10")
    print(f"[+] Unseen Attack Detection Rate: {eval_result.unseen_attack_detection_rate * 100:.1f}%")
    print(f"[+] Precision: {eval_result.precision}, Recall: {eval_result.recall}, F1-score: {eval_result.f1_score}")
    print(f"[+] False Positive Rate: {eval_result.false_positive_rate:.4f}\n")

    return {
        "Unseen_Zero_Day_Benchmark": eval_result.to_dict(),
        "hypothesis_h4_verified": eval_result.unseen_attack_detection_rate >= 0.9,
    }


def main() -> None:
    res = run_zero_day_experiment()
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase6"
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "experiment_2_zero_day.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)


if __name__ == "__main__":
    main()
