"""
Phase 7 Experiment 1 — Formal vs AI-Assisted Workflow Benchmark Runner.

Compares Mode A (Formal System Only) vs Mode B (Formal System + AI Explanation) vs Mode C (Formal System + AI Investigation).
Evaluates Hypotheses H1 & H2.
"""

import json
from pathlib import Path
import time
from typing import Any

from adaptive_automata.agents import AgentConfig, AgentMode, AgentRouter
from adaptive_automata.security import SyntheticDatasetGenerator



def run_experiment_1() -> dict[str, Any]:
    print("==========================================================================")
    print("  Phase 7 Experiment 1 — Formal vs AI-Assisted Workflow Benchmark (H1/H2)")
    print("==========================================================================\n")

    # Mode A: Formal System Only (Agent DISABLED)
    cfg_a = AgentConfig(enabled=False, mode=AgentMode.DISABLED)
    router_a = AgentRouter(cfg_a)

    # Mode B: Advisory Mode (AI Explanation)
    cfg_b = AgentConfig(enabled=True, mode=AgentMode.ADVISORY)
    router_b = AgentRouter(cfg_b)

    # Mode C: Assisted Mode (AI Investigation)
    cfg_c = AgentConfig(enabled=True, mode=AgentMode.ASSISTED)
    router_c = AgentRouter(cfg_c)

    event_ctx = {
        "session_id": "exp1_sess_100",
        "symbol": "CAPABILITIES",
        "level_used": "PDA",
        "severity": "LOW",
        "is_evolution_candidate": True,
    }

    # Measure Mode A
    t0 = time.perf_counter()
    res_a = router_a.route_and_execute("MODEL_EVOLUTION", event_ctx)
    lat_a = (time.perf_counter() - t0) * 1000

    # Measure Mode B
    t0 = time.perf_counter()
    res_b = router_b.route_and_execute("EXPLANATION_REQUEST", event_ctx)
    lat_b = (time.perf_counter() - t0) * 1000

    # Measure Mode C
    t0 = time.perf_counter()
    res_c = router_c.route_and_execute("MODEL_EVOLUTION_REQUEST", event_ctx)
    lat_c = (time.perf_counter() - t0) * 1000

    results = {
        "Mode_A_Formal_Only": {
            "classification": res_a.classification,
            "steps_executed": res_a.steps_executed,
            "latency_ms": round(lat_a, 4),
        },
        "Mode_B_Formal_Plus_Explanation": {
            "classification": res_b.classification,
            "explanation_provided": len(res_b.explanation) > 0,
            "latency_ms": round(lat_b, 4),
        },
        "Mode_C_Formal_Plus_AI_Investigation": {
            "classification": res_c.classification,
            "proposal_generated": res_c.proposal is not None,
            "steps_executed": res_c.steps_executed,
            "latency_ms": round(lat_c, 4),
        },
        "hypothesis_h1_verified": res_c.steps_executed > 0 and res_c.proposal is not None,
        "hypothesis_h2_verified": len(res_b.explanation) > 0 and "CAPABILITIES" in res_b.explanation,
    }

    print(f"[+] Mode A (Formal Only) Latency: {results['Mode_A_Formal_Only']['latency_ms']} ms")
    print(f"[+] Mode B (Formal + AI Explanation) Latency: {results['Mode_B_Formal_Plus_Explanation']['latency_ms']} ms")
    print(f"[+] Mode C (Formal + AI Investigation) Latency: {results['Mode_C_Formal_Plus_AI_Investigation']['latency_ms']} ms")
    print(f"[+] Hypotheses H1 & H2 Verified: {results['hypothesis_h1_verified'] and results['hypothesis_h2_verified']}\n")

    return results


def main() -> None:
    res = run_experiment_1()
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase7"
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "experiment_1_agent_vs_formal.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)


if __name__ == "__main__":
    main()
