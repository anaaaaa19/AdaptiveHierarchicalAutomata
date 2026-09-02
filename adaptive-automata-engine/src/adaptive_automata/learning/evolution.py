"""
Protocol Evolution Analyzer.

Identifies legitimate protocol extensions and version upgrades between baseline models
and new protocol traces, distinguishing valid extensions from malicious anomalies.
"""

from dataclasses import dataclass, field
from typing import Sequence

from adaptive_automata.models.versioning import ModelSource, VersionedProtocolModel
from adaptive_automata.protocol.session import ProtocolSession
from adaptive_automata.protocol.tokenizer import BaseMessageTokenizer
from .confidence import ConfidenceLevel, TransitionMetadata
from .passive import PassiveInferenceEngine


@dataclass(slots=True)
class ProtocolEvolutionResult:
    """
    Summary of protocol evolution analysis comparing a baseline model with new traces.
    """
    baseline_version: str
    evolution_version: str
    new_states_detected: list[str]
    new_valid_transitions: list[TransitionMetadata]
    is_valid_protocol_extension: bool
    description: str

    def __repr__(self) -> str:
        return (
            f"ProtocolEvolutionResult({self.baseline_version} -> {self.evolution_version} | "
            f"new_states={len(self.new_states_detected)}, new_transitions={len(self.new_valid_transitions)}, "
            f"is_extension={self.is_valid_protocol_extension})"
        )


class ProtocolEvolutionAnalyzer:
    """
    Analyzes protocol version upgrades and detects legitimate protocol extensions.
    """

    def __init__(self, passive_engine: PassiveInferenceEngine | None = None) -> None:
        self.passive_engine = passive_engine or PassiveInferenceEngine()

    def analyze_evolution(
        self,
        baseline_model: VersionedProtocolModel[str, str],
        new_sessions: Sequence[ProtocolSession],
        tokenizer: BaseMessageTokenizer | None = None,
        new_version: str = "v2.0.0-evolution",
    ) -> tuple[VersionedProtocolModel[str, str], ProtocolEvolutionResult]:
        """
        Compare new protocol traces against a baseline model to detect valid extensions.

        Returns:
            Tuple of (updated VersionedProtocolModel, ProtocolEvolutionResult).
        """
        # Step 1: Passively infer model from new traces
        new_model = self.passive_engine.infer_model(
            sessions=new_sessions,
            tokenizer=tokenizer,
            model_id=baseline_model.model_id,
            version=new_version,
        )

        baseline_transitions = baseline_model.mealy_machine._transitions
        new_mealy = new_model.mealy_machine

        new_states: list[str] = []
        baseline_state_names = {s.name for s in baseline_model.mealy_machine.states}

        for st in new_mealy.states:
            if st.name not in baseline_state_names:
                new_states.append(st.name)

        new_valid_transitions: list[TransitionMetadata] = []

        # Compare transitions
        for (src_st, sym), (tgt_st, out) in new_mealy._transitions.items():
            key = (src_st.name, sym)

            # Check if this transition existed in baseline
            base_meta = baseline_model.transition_metadata.get(key)
            is_new = (base_meta is None or base_meta.observation_count == 0 or base_meta.status == ConfidenceLevel.UNKNOWN)

            if is_new:
                meta = new_model.transition_metadata.get(key)
                if meta:
                    new_valid_transitions.append(meta)
                else:
                    new_valid_transitions.append(
                        TransitionMetadata(
                            source_state=src_st.name,
                            input_symbol=sym,
                            target_state=tgt_st.name,
                            output_symbol=out,
                            observation_count=1,
                            confidence_score=0.9,
                            status=ConfidenceLevel.OBSERVED,
                        )
                    )

        is_extension = (len(new_valid_transitions) > 0)
        desc = (
            f"Detected {len(new_valid_transitions)} legitimate new protocol transitions "
            f"and {len(new_states)} new states introduced in version {new_version}."
            if is_extension else "No protocol evolution detected."
        )

        result = ProtocolEvolutionResult(
            baseline_version=baseline_model.version,
            evolution_version=new_version,
            new_states_detected=new_states,
            new_valid_transitions=new_valid_transitions,
            is_valid_protocol_extension=is_extension,
            description=desc,
        )

        # Build combined transition metadata
        updated_metadata = dict(baseline_model.transition_metadata)
        updated_metadata.update(new_model.transition_metadata)

        updated_metrics = dict(new_model.metrics)
        updated_metrics["baseline_version"] = baseline_model.version
        updated_metrics["new_transitions_added"] = len(new_valid_transitions)

        evolved_model = VersionedProtocolModel[str, str](
            model_id=baseline_model.model_id,
            version=new_version,
            source=ModelSource.PROTOCOL_EVOLUTION,
            mealy_machine=new_mealy,
            transition_metadata=updated_metadata,
            metrics=updated_metrics,
        )

        return evolved_model, result
