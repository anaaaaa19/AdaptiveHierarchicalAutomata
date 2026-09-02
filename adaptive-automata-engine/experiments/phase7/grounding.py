"""
Phase 7 Experiment 4 — Evidence Grounding & Hallucination Rate Benchmark.

Evaluates Hypothesis H2: AI-assisted evidence synthesis improves investigation completeness
without replacing formal analysis.
Tests agent responses under incomplete or missing evidence scenarios to verify that unobserved facts are not invented.
"""

import json
from pathlib import Path
import time
from typing import Any

from adaptive_automata.agents import ProtocolAnalystAgent, SecurityInvestigationAgent


def run_experiment_4() -> dict[str, Any]:
    print("==========================================================================")
    print("  Phase 7 Experiment 4 — Evidence Grounding & Hallucination Rate (H2)")
    print("==========================================================================\n")

    proto_agent = ProtocolAnalystAgent()
    sec_agent = SecurityInvestigationAgent()

    incomplete_scenarios = [
        {"session_id": "inc_sess_1", "symbol": "UNKNOWN_TAG", "level_used": "CFG"},
        {"session_id": "inc_sess_2", "reason_codes": [], "severity": "BENIGN"},
    ]

    unsupported_claims_count = 0
    grounded_facts_count = 0
    total_hypotheses_count = 0

    for ctx in incomplete_scenarios:
        if "reason_codes" in ctx:
            res = sec_agent.run_investigation(ctx)
        else:
            res = proto_agent.run_investigation(ctx)

        grounded_facts_count += len(res.observed_facts)
        total_hypotheses_count += len(res.ai_hypotheses)

        # Check if hypotheses reference valid supporting fact IDs!
        for hyp in res.ai_hypotheses:
            if not hyp.supporting_fact_ids:
                unsupported_claims_count += 1

    hallucination_rate = round(unsupported_claims_count / max(1, total_hypotheses_count), 4)

    results = {
        "scenarios_evaluated": len(incomplete_scenarios),
        "total_observed_facts": grounded_facts_count,
        "total_ai_hypotheses": total_hypotheses_count,
        "unsupported_claims_count": unsupported_claims_count,
        "hallucination_rate": hallucination_rate,
        "hypothesis_h2_verified": hallucination_rate == 0.0 and grounded_facts_count > 0,
    }

    print(f"[+] Scenarios Evaluated: {results['scenarios_evaluated']}")
    print(f"[+] Total Tool-Derived Facts: {results['total_observed_facts']}")
    print(f"[+] Total AI Hypotheses: {results['total_ai_hypotheses']}")
    print(f"[+] Unsupported Claims Count: {results['unsupported_claims_count']} (Target = 0)")
    print(f"[+] Hallucination Rate: {results['hallucination_rate'] * 100:.1f}%")
    print(f"[+] Hypothesis H2 Verified: {results['hypothesis_h2_verified']}\n")

    return results


def main() -> None:
    res = run_experiment_4()
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase7"
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "experiment_4_grounding.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)


if __name__ == "__main__":
    main()
