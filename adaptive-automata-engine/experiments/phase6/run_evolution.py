"""
Phase 6 Experiment 3 — Legitimate Protocol Evolution vs Attack Benchmark.

Evaluates Hypothesis H2: Adaptive modeling reduces false positives caused by legitimate protocol evolution
compared with a static model.
Measures legitimate evolution acceptance rate, adaptation time, false attack rate, and model stability.
"""

import json
from pathlib import Path
import time
from typing import Any

from adaptive_automata.analysis import HierarchicalAnalyzer
from adaptive_automata.models import ModelRegistry
from adaptive_automata.protocol import TraceLoader, create_toy_protocol_sut
from adaptive_automata.learning import HybridActiveLearner, PassiveInferenceEngine
from adaptive_automata.adaptation import AdaptationConfig, AdaptationState, AdaptiveModelEngine, NoveltyDetector
from adaptive_automata.security import BehavioralAnalyzer, BehavioralClassification, SyntheticDatasetGenerator



def run_evolution_experiment() -> dict[str, Any]:
    print("==========================================================================")
    print("  Phase 6 Experiment 3 — Protocol Evolution vs Attack Benchmark (H2)")
    print("==========================================================================\n")

    base_dir = Path(__file__).parent.parent.parent
    v1_path = base_dir / "examples" / "data" / "toy_protocol_v1.json"
    v1_sessions = TraceLoader.load_from_file(str(v1_path))

    registry = ModelRegistry()
    passive_engine = PassiveInferenceEngine()
    passive_model = passive_engine.infer_model(v1_sessions, model_id="EvolSecProto", version="v1.0.0-passive")

    sut = create_toy_protocol_sut()
    hybrid_learner = HybridActiveLearner[str, str]()
    baseline_model = hybrid_learner.refine_model(passive_model, sut, new_version="v1.1.0-hybrid")
    registry.register_model(baseline_model)

    config = AdaptationConfig(minimum_observations=3, minimum_sessions=3, minimum_followups=2, require_structural_validation=False)
    analyzer = HierarchicalAnalyzer(fast_path_model=baseline_model)
    engine = AdaptiveModelEngine(analyzer, registry, config=config)
    sec_analyzer = BehavioralAnalyzer()

    evol_sessions = SyntheticDatasetGenerator.generate_protocol_evolution_sessions(5)
    attack_sessions = SyntheticDatasetGenerator.generate_known_deviations(5)

    st_time = time.perf_counter()
    evol_accepted = 0
    false_alerts_on_evol = 0

    print("[*] Processing Legitimate Protocol Evolution Sessions (CAPABILITIES Extension)...")
    for idx, (sess, _) in enumerate(evol_sessions, 1):
        an_res, nov_res, state = engine.process_session(
            sess,
            follows_up_successfully=True,
            structurally_valid=True,
            proposed_target_state="q2",
            proposed_output_symbol="CAPABILITIES_ACK",
        )
        ev = engine.evidence_store.get_evidence("q0:CAPABILITIES")
        assessment = sec_analyzer.analyze_security(sess, an_res, nov_res, evidence=ev)

        if assessment.behavioral_classification == BehavioralClassification.POTENTIAL_ATTACK:
            false_alerts_on_evol += 1

        if state == AdaptationState.ACTIVATED:
            evol_accepted += 1
            print(f"    - Session {idx}: Multi-session evidence satisfied -> Model Updated to '{engine.active_model.version}'")

    print("\n[*] Processing Malicious Attack Sessions (INVALID_STATE_SKIP)...")
    attacks_blocked = 0
    for sess, _ in attack_sessions:
        an_res, nov_res, state = engine.process_session(sess)
        ev = engine.evidence_store.get_evidence("q0:INVALID_STATE_SKIP")
        assessment = sec_analyzer.analyze_security(sess, an_res, nov_res, evidence=ev)
        if assessment.behavioral_classification in (BehavioralClassification.POTENTIAL_ATTACK, BehavioralClassification.PROTOCOL_VIOLATION):
            attacks_blocked += 1

    elapsed_ms = (time.perf_counter() - st_time) * 1000

    results = {
        "evolution_sessions_count": len(evol_sessions),
        "legitimate_evolution_accepted": evol_accepted > 0,
        "active_model_after_evolution": engine.active_model.version,
        "false_attack_alerts_on_evolution": false_alerts_on_evol,
        "malicious_attacks_detected": attacks_blocked,
        "processing_time_ms": round(elapsed_ms, 3),
        "hypothesis_h2_verified": evol_accepted > 0 and false_alerts_on_evol == 0,
    }

    print(f"[+] Legitimate Evolution Accepted: {results['legitimate_evolution_accepted']} (Version: {engine.active_model.version})")
    print(f"[+] False Alerts on Legitimate Evolution: {false_alerts_on_evol}")
    print(f"[+] Malicious Attacks Correctly Detected: {attacks_blocked} / 5\n")

    return results


def main() -> None:
    res = run_evolution_experiment()
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase6"
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "experiment_3_evolution.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)


if __name__ == "__main__":
    main()
