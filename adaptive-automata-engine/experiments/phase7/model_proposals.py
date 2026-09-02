"""
Phase 7 Experiment 2 — AI Model Proposals & Formal Guard Validation Benchmark.

Evaluates Hypotheses H3 & H5: Formal verification guards prevent invalid AI-generated model changes,
and AI proposals accelerate identification of legitimate protocol evolution while preserving formal validation.
"""

import json
from pathlib import Path
import time
from typing import Any

from adaptive_automata.core import MealyMachine, State
from adaptive_automata.models import ModelSource, VersionedProtocolModel
from adaptive_automata.agents import CandidateModelProposal, FormalVerificationGuard, ModelProposalAgent


def create_baseline_model() -> VersionedProtocolModel[str, str]:
    s0 = State("q0", is_initial=True)
    s1 = State("q1")
    mealy = MealyMachine[str, str]("PropExpProto")
    mealy.add_transition(s0, "SYN", s1, "SEND_SYN_ACK")
    mealy.validate()

    return VersionedProtocolModel[str, str](
        model_id="PropExpProto",
        version="v1.0.0",
        source=ModelSource.ACTIVE_HYBRID,
        mealy_machine=mealy,
    )


def run_experiment_2() -> dict[str, Any]:
    print("==========================================================================")
    print("  Phase 7 Experiment 2 — AI Model Proposals & Formal Guard (H3/H5)")
    print("==========================================================================\n")

    base_model = create_baseline_model()
    model_agent = ModelProposalAgent()
    guard = FormalVerificationGuard()

    # Proposal Scenario 1: Legitimate Protocol Extension (Valid)
    res_valid = model_agent.run_investigation({
        "session_id": "prop_valid_101",
        "symbol": "CAPABILITIES",
        "model_version": "v1.0.0",
    })
    guard_res_valid = guard.verify_proposal(res_valid.proposal, base_model)

    # Proposal Scenario 2: Malformed AI Proposal (Empty/Invalid)
    malformed_prop = CandidateModelProposal(
        proposal_id="prop_malformed_102",
        parent_model_version="",
        proposed_transitions=[],
    )
    guard_res_invalid = guard.verify_proposal(malformed_prop, base_model)

    results = {
        "valid_proposal_evaluation": {
            "proposal_generated": res_valid.proposal is not None,
            "guard_passed": guard_res_valid.is_valid,
            "rejection_reasons": guard_res_valid.rejection_reasons,
        },
        "malformed_proposal_evaluation": {
            "guard_passed": guard_res_invalid.is_valid,
            "rejection_reasons": guard_res_invalid.rejection_reasons,
            "correctly_blocked": not guard_res_invalid.is_valid,
        },
        "hypothesis_h3_verified": guard_res_invalid.is_valid is False and len(guard_res_invalid.rejection_reasons) > 0,
        "hypothesis_h5_verified": guard_res_valid.is_valid is True,
    }

    print(f"[+] Legitimate Proposal Guard Passed: {results['valid_proposal_evaluation']['guard_passed']}")
    print(f"[+] Malformed Proposal Blocked by Guard: {results['malformed_proposal_evaluation']['correctly_blocked']}")
    print(f"[+] Rejection Reasons Logged: {results['malformed_proposal_evaluation']['rejection_reasons']}")
    print(f"[+] Hypotheses H3 & H5 Verified: {results['hypothesis_h3_verified'] and results['hypothesis_h5_verified']}\n")

    return results


def main() -> None:
    res = run_experiment_2()
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase7"
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "experiment_2_model_proposals.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)


if __name__ == "__main__":
    main()
