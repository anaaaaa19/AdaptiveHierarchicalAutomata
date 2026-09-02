"""
Phase 7 Experiment 6 — Agent Failure & Safe Fallback Benchmark.

Evaluates Hypothesis H6: The underlying formal detection system remains operational and safe
when the AI layer fails.
Simulates AI layer disabled/unavailable modes and verifies clean fallback to non-AI formal execution.
"""

import json
from pathlib import Path
import time
from typing import Any

from adaptive_automata.agents import AgentConfig, AgentMode, AgentRouter


def run_experiment_6() -> dict[str, Any]:
    print("==========================================================================")
    print("  Phase 7 Experiment 6 — Agent Failure & Safe Fallback Benchmark (H6)")
    print("==========================================================================\n")

    # Mode 1: Agent DISABLED (Simulating LLM unavailable / AI service outage)
    cfg_disabled = AgentConfig(enabled=False, mode=AgentMode.DISABLED)
    router_disabled = AgentRouter(cfg_disabled)

    event_ctx = {
        "session_id": "fallback_test_001",
        "symbol": "UNKNOWN_TRANSITION",
        "severity": "HIGH",
    }

    t0 = time.perf_counter()
    res = router_disabled.route_and_execute("SECURITY_ALERT", event_ctx)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    fallback_successful = res.classification == "FORMAL_ONLY_FALLBACK" and "DISABLED" in res.explanation

    results = {
        "agent_mode": cfg_disabled.mode.value,
        "fallback_classification": res.classification,
        "fallback_explanation": res.explanation,
        "fallback_latency_ms": round(elapsed_ms, 4),
        "formal_system_operational": fallback_successful,
        "hypothesis_h6_verified": fallback_successful,
    }

    print(f"[+] Agent Layer Mode: {results['agent_mode']}")
    print(f"[+] Fallback Classification: {results['fallback_classification']}")
    print(f"[+] Fallback Explanation: '{results['fallback_explanation']}'")
    print(f"[+] Formal System Operational: {results['formal_system_operational']}")
    print(f"[+] Hypothesis H6 Verified: {results['hypothesis_h6_verified']}\n")

    return results


def main() -> None:
    res = run_experiment_6()
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase7"
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "experiment_6_failure_modes.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)


if __name__ == "__main__":
    main()
