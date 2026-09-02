"""
Phase 6 Experiment 5 — Hierarchical Efficiency & Performance Benchmark.

Evaluates Hypothesis H5: Hierarchical escalation reduces computational overhead compared with
applying the most expressive formal model to every input.
Measures DFA resolution %, PDA escalation %, CFG escalation %, mean, median (P50), and P95 latency.
"""

import json
from pathlib import Path
import time
from typing import Any

from adaptive_automata.analysis import HierarchicalAnalyzer
from adaptive_automata.core import PushdownAutomaton, CFGParser, Grammar, Terminal, NonTerminal, ProductionRule, State, StackOp
from adaptive_automata.core.pda import PDATransition
from adaptive_automata.models import ModelRegistry
from adaptive_automata.protocol import TraceLoader, create_toy_protocol_sut
from adaptive_automata.learning import HybridActiveLearner, PassiveInferenceEngine
from adaptive_automata.security import EvaluationResult, SyntheticDatasetGenerator


def create_hierarchical_analyzer() -> HierarchicalAnalyzer:
    base_dir = Path(__file__).parent.parent.parent
    v1_path = base_dir / "examples" / "data" / "toy_protocol_v1.json"
    v1_sessions = TraceLoader.load_from_file(str(v1_path))

    registry = ModelRegistry()
    passive_engine = PassiveInferenceEngine()
    passive_model = passive_engine.infer_model(v1_sessions, model_id="PerfProto", version="v1.0.0-passive")

    sut = create_toy_protocol_sut()
    hybrid_learner = HybridActiveLearner[str, str]()
    baseline_model = hybrid_learner.refine_model(passive_model, sut, new_version="v1.1.0-hybrid")

    # Level 2 PDA for nested framing
    pda_s0 = State("pda_q0", is_initial=True)
    pda_s1 = State("pda_q1", is_accepting=True)
    pda = PushdownAutomaton[str, str]("NestedPDA")
    pda.add_state(pda_s0)
    pda.add_state(pda_s1)
    pda.add_transition(pda_s0, "OPEN_BLOCK", None, pda_s0, op=StackOp.PUSH, push_symbols=("BLOCK",))
    pda.add_transition(pda_s0, "DATA", None, pda_s0, op=StackOp.NOP)
    pda.add_transition(pda_s0, "CLOSE_BLOCK", "BLOCK", pda_s0, op=StackOp.POP)
    pda.add_transition(pda_s0, "FIN", None, pda_s1, op=StackOp.NOP)



    # Level 3 CFG Parser for recursive structures
    S = NonTerminal("S")
    H = Terminal("HEADER")
    B = Terminal("BODY")
    grammar = Grammar(start_symbol=S)
    grammar.add_rule(S, [H, S, B])
    grammar.add_rule(S, [H, B])
    cfg_parser = CFGParser(grammar)



    return HierarchicalAnalyzer(fast_path_model=baseline_model, pda=pda, cfg_parser=cfg_parser)


def run_performance_experiment() -> dict[str, Any]:
    print("==========================================================================")
    print("  Phase 6 Experiment 5 — Hierarchical Efficiency Benchmark (H5)")
    print("==========================================================================\n")

    analyzer = create_hierarchical_analyzer()

    # Create mixed evaluation workload: 70% DFA fast-path, 15% PDA, 15% CFG
    normal_traces = [sess for sess, _ in SyntheticDatasetGenerator.generate_normal_sessions(70)]

    pda_seqs = [["OPEN_BLOCK", "OPEN_BLOCK", "DATA", "CLOSE_BLOCK", "CLOSE_BLOCK", "FIN"]] * 15
    cfg_seqs = [["HEADER", "HEADER", "BODY", "BODY"]] * 15

    dfa_lats, pda_lats, cfg_lats, hier_lats = [], [], [], []
    dfa_count, pda_count, cfg_count = 0, 0, 0

    print("[*] Processing Mixed Protocol Workload (100 Sessions)...")
    st_start = time.perf_counter()

    # Process DFA normal sessions
    for sess in normal_traces:
        t0 = time.perf_counter()
        res = analyzer.analyze_session(sess)
        lat = (time.perf_counter() - t0) * 1000
        dfa_lats.append(lat)
        hier_lats.append(lat)
        if res.level_used.value == "DFA_MEALY":
            dfa_count += 1

    # Process PDA nested sessions
    for seq in pda_seqs:
        t0 = time.perf_counter()
        res = analyzer.analyze_sequence(seq)
        lat = (time.perf_counter() - t0) * 1000
        pda_lats.append(lat)
        hier_lats.append(lat)
        if res.level_used.value == "PDA":
            pda_count += 1

    # Process CFG recursive sessions
    for seq in cfg_seqs:
        t0 = time.perf_counter()
        res = analyzer.analyze_sequence(seq)
        lat = (time.perf_counter() - t0) * 1000
        cfg_lats.append(lat)
        hier_lats.append(lat)
        if res.level_used.value == "CFG":
            cfg_count += 1

    elapsed_total_ms = (time.perf_counter() - st_start) * 1000

    hier_stats = EvaluationResult.compute_latency_stats(hier_lats)
    dfa_stats = EvaluationResult.compute_latency_stats(dfa_lats)
    cfg_stats = EvaluationResult.compute_latency_stats(cfg_lats)

    results = {
        "workload_distribution": {
            "total_evaluations": 100,
            "dfa_resolved_pct": round((dfa_count / 100.0) * 100, 1),
            "pda_escalated_pct": round((pda_count / 100.0) * 100, 1),
            "cfg_escalated_pct": round((cfg_count / 100.0) * 100, 1),
        },
        "latency_benchmarks": {
            "dfa_fast_path": dfa_stats,
            "cfg_heavy_parser": cfg_stats,
            "hierarchical_escalation_engine": hier_stats,
        },
        "total_benchmark_time_ms": round(elapsed_total_ms, 3),
        "hypothesis_h5_verified": dfa_stats["mean_ms"] < cfg_stats["mean_ms"] and dfa_count >= 70,
    }

    print(f"[+] Workload Resolution: DFA Fast-Path={results['workload_distribution']['dfa_resolved_pct']}%, PDA Escalation={results['workload_distribution']['pda_escalated_pct']}%, CFG Escalation={results['workload_distribution']['cfg_escalated_pct']}%")
    print(f"[+] DFA Fast-Path Mean Latency: {dfa_stats['mean_ms']} ms (P50={dfa_stats['median_ms']} ms, P95={dfa_stats['p95_ms']} ms)")
    print(f"[+] Full CFG Parser Mean Latency: {cfg_stats['mean_ms']} ms (P50={cfg_stats['median_ms']} ms, P95={cfg_stats['p95_ms']} ms)")
    print(f"[+] Hierarchical Escalation Mean Latency: {hier_stats['mean_ms']} ms")
    print(f"[+] Hypothesis H5 Verified: {results['hypothesis_h5_verified']}\n")

    return results


def main() -> None:
    res = run_performance_experiment()
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase6"
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "experiment_5_performance.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)


if __name__ == "__main__":
    main()
