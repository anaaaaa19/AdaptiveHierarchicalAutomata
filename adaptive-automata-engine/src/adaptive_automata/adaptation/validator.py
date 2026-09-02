"""
Formal Validator component.

Performs rigorous formal safety and regression validation on CandidateModels prior to model activation.
Verifies graph integrity, existing behavior preservation, and trace regression.
"""

from dataclasses import dataclass, field
from typing import Sequence

from adaptive_automata.core.mealy import MealyMachine, MealyMachineValidationError
from adaptive_automata.core.state import State
from adaptive_automata.models.versioning import VersionedProtocolModel
from adaptive_automata.protocol.session import ProtocolSession
from .candidate import CandidateModel


@dataclass(slots=True)
class ValidationResult:
    """
    Formal validation evaluation report.
    """
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    tested_traces_count: int = 0

    def __repr__(self) -> str:
        return (
            f"ValidationResult(valid={self.valid}, errors={len(self.errors)}, "
            f"warnings={len(self.warnings)}, tested_traces={self.tested_traces_count})"
        )


class FormalValidator:
    """
    Formal safety validator for CandidateModels.
    """

    def validate_candidate(
        self,
        candidate: CandidateModel,
        baseline_model: VersionedProtocolModel[str, str],
        regression_traces: Sequence[ProtocolSession] | None = None,
    ) -> ValidationResult:
        """
        Validate candidate model against baseline model and regression traces.

        Returns:
            ValidationResult indicating whether candidate model is safe and valid.
        """
        errors: list[str] = []
        warnings: list[str] = []

        base_mealy = baseline_model.mealy_machine

        # Step 1: Create trial Mealy machine starting from baseline graph
        trial_mealy = MealyMachine[str, str](name=f"Trial_{candidate.candidate_id}")
        state_map: dict[str, State] = {}

        # Copy baseline states
        for st in base_mealy.states:
            new_st = State(st.name, is_initial=st.is_initial, is_accepting=st.is_accepting)
            state_map[st.name] = new_st
            trial_mealy.add_state(new_st)

        # Copy baseline transitions
        for (src_st, sym), (tgt_st, out) in base_mealy._transitions.items():
            trial_mealy.add_transition(state_map[src_st.name], sym, state_map[tgt_st.name], out)

        # Step 2: Apply proposed candidate transitions
        for src_name, sym, tgt_name, out in candidate.proposed_transitions:
            if not src_name or not tgt_name or not sym:
                errors.append(f"Invalid transition definition: ({src_name}, {sym}) -> {tgt_name}.")
                continue

            if src_name not in state_map:
                st = State(src_name)
                state_map[src_name] = st
                trial_mealy.add_state(st)

            if tgt_name not in state_map:
                st = State(tgt_name)
                state_map[tgt_name] = st
                trial_mealy.add_state(st)

            src_st = state_map[src_name]
            tgt_st = state_map[tgt_name]

            # Check if attempting to overwrite an existing baseline transition with conflicting output
            key = (src_st, sym)
            if key in trial_mealy._transitions:
                existing_tgt, existing_out = trial_mealy._transitions[key]
                if existing_tgt != tgt_st or existing_out != out:
                    errors.append(
                        f"Candidate transition for ({src_name}, {sym}) conflicts with baseline. "
                        f"Existing: -> {existing_tgt.name} / {existing_out}, Proposed: -> {tgt_name} / {out}."
                    )
            else:
                try:
                    trial_mealy.add_transition(src_st, sym, tgt_st, out)
                except MealyMachineValidationError as e:
                    errors.append(f"Mealy validation error applying candidate transition: {e}")

        # Step 3: Validate trial machine integrity
        try:
            trial_mealy.validate()
        except Exception as e:
            errors.append(f"Candidate trial machine validation failed: {e}")

        # Step 4: Regression testing against baseline session traces
        traces_tested = 0
        if regression_traces and not errors:
            for sess in regression_traces:
                pairs = sess.get_transduction_pairs()
                if not pairs:
                    continue

                traces_tested += 1
                in_seq = [inp for inp, _ in pairs]
                expected_out = [out for _, out in pairs]

                try:
                    baseline_out, _ = base_mealy.process_sequence(in_seq)
                    trial_out, _ = trial_mealy.process_sequence(in_seq)

                    # Candidate MUST preserve valid baseline transductions
                    if tuple(trial_out) != tuple(baseline_out):
                        errors.append(
                            f"Regression failure on session '{sess.session_id}': "
                            f"Candidate outputs {trial_out} != Baseline outputs {baseline_out}."
                        )
                except Exception as e:
                    # If baseline accepted but trial failed, report regression
                    errors.append(f"Regression exception on session '{sess.session_id}': {e}")

        is_valid = len(errors) == 0

        return ValidationResult(
            valid=is_valid,
            errors=errors,
            warnings=warnings,
            tested_traces_count=traces_tested,
        )
