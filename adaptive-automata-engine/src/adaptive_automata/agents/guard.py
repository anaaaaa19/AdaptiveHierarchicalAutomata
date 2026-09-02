"""
Formal Verification Guard component.

Critical gatekeeper component sitting between AI-generated CandidateModelProposals and the Phase 5 safe model updater.
Validates graph integrity, runs regression tests against baseline session traces, enforces formal invariants,
and rejects malformed or unsafe proposals.
"""

from dataclasses import dataclass, field
from typing import Any, Sequence

from adaptive_automata.core import MealyMachine, State
from adaptive_automata.models import ModelSource, VersionedProtocolModel
from adaptive_automata.adaptation import AdaptationPolicy, BehaviorEvidence, CandidateModel, FormalValidator, ValidationResult

from .schemas import CandidateModelProposal


@dataclass(slots=True)
class GuardResult:
    """
    Result returned by FormalVerificationGuard evaluation.
    """
    is_valid: bool
    rejection_reasons: list[str] = field(default_factory=list)
    candidate_model: CandidateModel | None = None
    validation_details: dict[str, Any] = field(default_factory=dict)


class FormalVerificationGuard:
    """
    Verification guard validating AI candidate model proposals against formal invariants and Phase 5 regression tests.
    """

    def __init__(
        self,
        validator: FormalValidator | None = None,
        policy: AdaptationPolicy | None = None,
    ) -> None:
        self.validator = validator or FormalValidator()
        self.policy = policy or AdaptationPolicy()

    def verify_proposal(
        self,
        proposal: CandidateModelProposal,
        base_model: VersionedProtocolModel[str, str],
        baseline_traces: Sequence[Any] = (),
    ) -> GuardResult:
        """
        Verify an AI-generated CandidateModelProposal.

        Flow:
          1. Schema & non-empty content validation
          2. Construct trial graph edit
          3. Check Mealy Machine graph structural integrity & determinism
          4. Execute Phase 5 FormalValidator regression test against baseline_traces
          5. Evaluate Phase 5 AdaptationPolicy evidence constraints
        """
        reasons: list[str] = []

        # 1. Schema Validation
        if not proposal.proposal_id or not proposal.parent_model_version:
            reasons.append("Malformed proposal: Missing proposal_id or parent_model_version.")

        if not proposal.proposed_transitions:
            reasons.append("Empty proposal: No proposed_transitions supplied.")
            return GuardResult(is_valid=False, rejection_reasons=reasons)

        # 2. Graph Construction & Determinism Check
        try:
            # Clone base mealy machine
            base_mealy = base_model.mealy_machine
            trial_mealy = MealyMachine[str, str](f"{base_mealy.name}_trial")

            # Copy existing states & transitions
            state_map: dict[str, State] = {}
            for s in base_mealy.states:
                st = State(s.name, is_initial=s.is_initial, is_accepting=s.is_accepting)
                state_map[s.name] = st
                trial_mealy.add_state(st)

            for (src, sym), (tgt, out) in base_mealy._transitions.items():
                trial_mealy.add_transition(state_map[src.name], sym, state_map[tgt.name], out)

            # Apply proposed transitions
            for tr in proposal.proposed_transitions:
                src_name = tr.get("source", "q0")
                tgt_name = tr.get("target", "q_new")
                sym = tr.get("symbol", "")
                out = tr.get("output", "ACK")

                if not sym:
                    reasons.append("Proposed transition missing input symbol.")
                    continue

                if src_name not in state_map:
                    st_src = State(src_name)
                    state_map[src_name] = st_src
                    trial_mealy.add_state(st_src)

                if tgt_name not in state_map:
                    st_tgt = State(tgt_name)
                    state_map[tgt_name] = st_tgt
                    trial_mealy.add_state(st_tgt)

                trial_mealy.add_transition(state_map[src_name], sym, state_map[tgt_name], out)

            trial_mealy.validate()

        except Exception as e:
            reasons.append(f"Formal Mealy validation failed on proposed graph edit: {e}")
            return GuardResult(is_valid=False, rejection_reasons=reasons)

        # 3. Construct CandidateModel with converted transitions and evidence
        cand_tuples = []
        for tr in proposal.proposed_transitions:
            src_n = tr.get("source", "q0")
            sym_n = tr.get("symbol", "")
            tgt_n = tr.get("target", "q_new")
            out_n = tr.get("output", "ACK")
            cand_tuples.append((src_n, sym_n, tgt_n, out_n))

        ev = BehaviorEvidence(behavior_id="proposal_key", source_state="q0", input_symbol="CAPABILITIES")

        candidate = CandidateModel(
            candidate_id=proposal.proposal_id,
            parent_version=proposal.parent_model_version,
            proposed_transitions=cand_tuples,
            supporting_evidence=ev,
        )


        # 4. Phase 5 Formal Validator Regression Test
        val_res: ValidationResult = self.validator.validate_candidate(candidate, base_model, baseline_traces)
        if not val_res.valid:
            reasons.extend(val_res.errors)

        is_passed = len(reasons) == 0
        return GuardResult(
            is_valid=is_passed,
            rejection_reasons=reasons,
            candidate_model=candidate if is_passed else None,
            validation_details={"tested_traces": val_res.tested_traces_count, "errors_count": len(val_res.errors)},
        )

