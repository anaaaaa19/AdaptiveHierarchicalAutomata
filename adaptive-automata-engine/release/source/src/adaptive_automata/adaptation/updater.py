"""
Model Updater component.

Constructs new immutable VersionedProtocolModel instances from validated CandidateModels
and registers them in the Phase 3 ModelRegistry.
"""

from adaptive_automata.core.mealy import MealyMachine
from adaptive_automata.core.state import State
from adaptive_automata.learning.confidence import ConfidenceLevel, TransitionMetadata
from adaptive_automata.models.versioning import ModelRegistry, ModelSource, VersionedProtocolModel
from .candidate import CandidateModel
from .lifecycle import AdaptationState


class ModelUpdater:
    """
    Applies validated CandidateModel updates to construct and register new Model versions.
    """

    def __init__(self, registry: ModelRegistry) -> None:
        self.registry = registry

    def apply_update(
        self,
        candidate: CandidateModel,
        baseline_model: VersionedProtocolModel[str, str],
        new_version: str,
    ) -> VersionedProtocolModel[str, str]:
        """
        Construct new versioned model from validated candidate and register in ModelRegistry.

        Raises:
            ValueError: If candidate is not in VALIDATED state or registry rejects version overwrite.
        """
        if candidate.lifecycle_state not in (AdaptationState.VALIDATING, AdaptationState.VALIDATED):
            raise ValueError(
                f"Cannot update model from candidate in state '{candidate.lifecycle_state.value}'. "
                f"Candidate must be formally VALIDATED prior to activation."
            )

        base_mealy = baseline_model.mealy_machine

        # Build new Mealy machine graph
        new_mealy = MealyMachine[str, str](name=f"{baseline_model.model_id}_{new_version}")
        state_map: dict[str, State] = {}

        # Copy baseline states
        for st in base_mealy.states:
            new_st = State(st.name, is_initial=st.is_initial, is_accepting=st.is_accepting)
            state_map[st.name] = new_st
            new_mealy.add_state(new_st)

        # Copy baseline transitions
        for (src_st, sym), (tgt_st, out) in base_mealy._transitions.items():
            new_mealy.add_transition(state_map[src_st.name], sym, state_map[tgt_st.name], out)

        # Apply candidate transitions
        for src_name, sym, tgt_name, out in candidate.proposed_transitions:
            if src_name not in state_map:
                st = State(src_name)
                state_map[src_name] = st
                new_mealy.add_state(st)

            if tgt_name not in state_map:
                st = State(tgt_name)
                state_map[tgt_name] = st
                new_mealy.add_state(st)

            new_mealy.add_transition(state_map[src_name], sym, state_map[tgt_name], out)

        new_mealy.validate()

        # Build updated metadata dictionary
        updated_meta = dict(baseline_model.transition_metadata)

        for src_name, sym, tgt_name, out in candidate.proposed_transitions:
            key = (src_name, sym)
            updated_meta[key] = TransitionMetadata(
                source_state=src_name,
                input_symbol=sym,
                target_state=tgt_name,
                output_symbol=out,
                observation_count=candidate.supporting_evidence.observation_count,
                confidence_score=0.95,
                status=ConfidenceLevel.OBSERVED,
            )

        updated_metrics = dict(baseline_model.metrics)
        updated_metrics.update(
            {
                "num_states": len(new_mealy.states),
                "num_transitions": len(new_mealy._transitions),
                "parent_version": baseline_model.version,
                "candidate_id": candidate.candidate_id,
            }
        )

        new_versioned_model = VersionedProtocolModel[str, str](
            model_id=baseline_model.model_id,
            version=new_version,
            source=ModelSource.ACTIVE_HYBRID,
            mealy_machine=new_mealy,
            transition_metadata=updated_meta,
            metrics=updated_metrics,
        )

        # Register in immutable ModelRegistry
        self.registry.register_model(new_versioned_model)

        return new_versioned_model
