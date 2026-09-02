"""
Phase 6 Experiment 1 — Baseline Comparison Benchmark Runner.

Compares Baseline 1 (Static DFA), Baseline 2 (Static Hierarchical), Baseline 3 (Naive Adaptive),
and Baseline 4 (Proposed Adaptive Hierarchical Security System) on labeled normal and deviation traces.
Evaluates Hypotheses H1 & H5.
"""

import json
from pathlib import Path
import time
from typing import Any

import sys
sys.path.append(str(Path(__file__).parent.parent / "phase5"))

from adaptive_automata.analysis import HierarchicalAnalyzer
from adaptive_automata.models import ModelRegistry
from adaptive_automata.protocol import TraceLoader, create_toy_protocol_sut
from adaptive_automata.learning import HybridActiveLearner, PassiveInferenceEngine
from adaptive_automata.adaptation import AdaptationConfig, AdaptiveModelEngine, NoveltyDetector
from adaptive_automata.security import (
    BehavioralAnalyzer,
    BehavioralClassification,
    EvaluationResult,
    SecurityEvaluator,
    SyntheticDatasetGenerator,
)
from baselines import Baseline1StaticModel, Baseline2HierarchicalModel, Baseline3NaiveAdaptiveModel


def run_baseline_experiment() -> dict[str, Any]:
    print("==========================================================================")
    print("  Phase 6 Experiment 1 — Baseline Comparison Benchmark")
    print("==========================================================================\n")

    base_dir = Path(__file__).parent.parent.parent
    v1_path = base_dir / "examples" / "data" / "toy_protocol_v1.json"
    v1_sessions = TraceLoader.load_from_file(str(v1_path))

    registry = ModelRegistry()
    passive_engine = PassiveInferenceEngine()
    passive_model = passive_engine.infer_model(v1_sessions, model_id="SecurityExpProto", version="v1.0.0-passive")

    sut = create_toy_protocol_sut()
    hybrid_learner = HybridActiveLearner[str, str]()
    baseline_model = hybrid_learner.refine_model(passive_model, sut, new_version="v1.1.0-hybrid")
    registry.register_model(baseline_model)

    analyzer = HierarchicalAnalyzer(fast_path_model=baseline_model)
    novelty_det = NoveltyDetector()
    sec_analyzer = BehavioralAnalyzer()
    evaluator = SecurityEvaluator()

    # Generate synthetic benchmark dataset: 20 normal + 20 known deviations
    normal_traces = SyntheticDatasetGenerator.generate_normal_sessions(20)
    dev_traces = SyntheticDatasetGenerator.generate_known_deviations(20)
    dataset = normal_traces + dev_traces

    actual_is_attack = [label for _, label in dataset]

    # Baseline 1: Static DFA Detector
    b1_preds, b1_lats = [], []
    for sess, _ in dataset:
        st_t = time.perf_counter()
        pairs = sess.get_transduction_pairs()
        mealy = baseline_model.mealy_machine
        mealy.reset()
        curr = mealy.current_state
        is_att = False
        for sym, _ in pairs:
            if (curr, sym) in mealy._transitions:
                curr, _ = mealy.step(sym)
            else:
                is_att = True
                break
        b1_lats.append((time.perf_counter() - st_t) * 1000)
        b1_preds.append(is_att)
    b1_eval = evaluator.evaluate_predictions(actual_is_attack, b1_preds, b1_lats)

    # Baseline 2: Static Hierarchical Detector (Phase 4 DFA+PDA+CFG, No Adaptation)
    b2_preds, b2_lats = [], []
    for sess, _ in dataset:
        st_t = time.perf_counter()
        res = analyzer.analyze_session(sess)
        b2_lats.append((time.perf_counter() - st_t) * 1000)
        b2_preds.append(res.status != "KNOWN")
    b2_eval = evaluator.evaluate_predictions(actual_is_attack, b2_preds, b2_lats)

    # Proposed System: Phase 4 + Phase 5 + Phase 6
    b4_preds, b4_lats = [], []
    config_4 = AdaptationConfig(minimum_observations=5, minimum_sessions=3, minimum_followups=2)
    engine_4 = AdaptiveModelEngine(analyzer, registry, config=config_4)

    for sess, _ in dataset:
        st_t = time.perf_counter()
        an_res = analyzer.analyze_session(sess)
        nov_res = novelty_det.detect_novelty(an_res, baseline_model)
        assessment = sec_analyzer.analyze_security(sess, an_res, nov_res)
        b4_lats.append((time.perf_counter() - st_t) * 1000)
        is_alert = assessment.behavioral_classification in (
            BehavioralClassification.POTENTIAL_ATTACK,
            BehavioralClassification.SUSPICIOUS,
            BehavioralClassification.PROTOCOL_VIOLATION,
        )
        b4_preds.append(is_alert)
    b4_eval = evaluator.evaluate_predictions(actual_is_attack, b4_preds, b4_lats)

    summary = {
        "Baseline_1_Static_DFA": b1_eval.to_dict(),
        "Baseline_2_Static_Hierarchical": b2_eval.to_dict(),
        "Proposed_Adaptive_Hierarchical_Security_System": b4_eval.to_dict(),
    }

    print("[+] Baseline 1 Precision:", b1_eval.precision, "Recall:", b1_eval.recall, "F1:", b1_eval.f1_score)
    print("[+] Proposed System Precision:", b4_eval.precision, "Recall:", b4_eval.recall, "F1:", b4_eval.f1_score)
    print("[+] Proposed Mean Latency:", b4_eval.latency_metrics["mean_ms"], "ms\n")

    return summary


def main() -> None:
    res = run_baseline_experiment()
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase6"
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "experiment_1_baselines.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)


if __name__ == "__main__":
    main()
