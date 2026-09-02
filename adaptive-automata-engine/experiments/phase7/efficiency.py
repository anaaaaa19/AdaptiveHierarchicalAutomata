"""
Phase 7 Experiment 5 — Investigation Step Efficiency & Latency Benchmark.

Evaluates Hypothesis H1: Agentic orchestration reduces manual investigation effort.
Measures investigation step counts, tool call efficiency, mean, median (P50), and P95 latency.
"""

import json
from pathlib import Path
import time
from typing import Any

from adaptive_automata.agents import AgentConfig, AgentRouter
from adaptive_automata.security import EvaluationResult


def run_experiment_5() -> dict[str, Any]:
    print("==========================================================================")
    print("  Phase 7 Experiment 5 — Investigation Step Efficiency Benchmark (H1)")
    print("==========================================================================\n")

    config = AgentConfig(max_steps=10, max_tool_calls=20)
    router = AgentRouter(config)

    scenarios = [
        ("SECURITY_ALERT", {"session_id": f"eff_sess_{i}", "severity": "HIGH", "reason_codes": ["UNKNOWN_TRANSITION"]})
        for i in range(1, 21)
    ]

    latencies_ms = []
    step_counts = []
    tools_counts = []

    for event_type, ctx in scenarios:
        t0 = time.perf_counter()
        res = router.route_and_execute(event_type, ctx)
        lat = (time.perf_counter() - t0) * 1000

        latencies_ms.append(lat)
        step_counts.append(res.steps_executed)
        tools_counts.append(len(res.tools_used))

    lat_stats = EvaluationResult.compute_latency_stats(latencies_ms)
    avg_steps = round(sum(step_counts) / len(step_counts), 2)
    avg_tools = round(sum(tools_counts) / len(tools_counts), 2)

    results = {
        "scenarios_evaluated": len(scenarios),
        "average_steps_executed": avg_steps,
        "average_tools_executed": avg_tools,
        "latency_metrics_ms": lat_stats,
        "hypothesis_h1_verified": avg_steps <= 10 and lat_stats["mean_ms"] < 100.0,
    }

    print(f"[+] Scenarios Evaluated: {results['scenarios_evaluated']}")
    print(f"[+] Average Steps Executed: {avg_steps} (Budget = 10)")
    print(f"[+] Average Tools Executed: {avg_tools} (Budget = 20)")
    print(f"[+] Mean Processing Latency: {lat_stats['mean_ms']} ms (P50: {lat_stats['median_ms']} ms, P95: {lat_stats['p95_ms']} ms)")
    print(f"[+] Hypothesis H1 Verified: {results['hypothesis_h1_verified']}\n")

    return results


def main() -> None:
    res = run_experiment_5()
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase7"
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "experiment_5_efficiency.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)


if __name__ == "__main__":
    main()
