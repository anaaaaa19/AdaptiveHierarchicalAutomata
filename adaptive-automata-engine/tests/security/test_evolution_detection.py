"""Unit tests for Legitimate Protocol Evolution vs Suspicious Deviation Detection."""

from adaptive_automata.analysis import HierarchicalAnalyzer
from adaptive_automata.core import State, MealyMachine
from adaptive_automata.models import ModelSource, VersionedProtocolModel, ModelRegistry
from adaptive_automata.adaptation import AdaptationConfig, AdaptationState, AdaptiveModelEngine
from adaptive_automata.security import BehavioralAnalyzer, BehavioralClassification, SyntheticDatasetGenerator


def create_baseline_model() -> VersionedProtocolModel[str, str]:
    s0 = State("q0", is_initial=True)
    s1 = State("q1")
    mealy = MealyMachine[str, str]("EvolTestProto")
    mealy.add_transition(s0, "SYN", s1, "SEND_SYN_ACK")
    mealy.validate()

    return VersionedProtocolModel[str, str](
        model_id="EvolTestProto",
        version="v1.0.0",
        source=ModelSource.ACTIVE_HYBRID,
        mealy_machine=mealy,
    )


def test_distinguish_evolution_from_attack():
    registry = ModelRegistry()
    model = create_baseline_model()
    registry.register_model(model)

    config = AdaptationConfig(minimum_observations=3, minimum_sessions=3, minimum_followups=2, require_structural_validation=False)
    analyzer = HierarchicalAnalyzer(fast_path_model=model)
    engine = AdaptiveModelEngine(analyzer, registry, config=config)
    sec_analyzer = BehavioralAnalyzer()

    evol_sessions = SyntheticDatasetGenerator.generate_protocol_evolution_sessions(count=3)

    # Process 3 distinct sessions introducing CAPABILITIES extension
    for idx, (sess, _) in enumerate(evol_sessions, 1):
        an_res, nov_res, state = engine.process_session(
            sess,
            follows_up_successfully=True,
            structurally_valid=True,
            proposed_target_state="q2",
            proposed_output_symbol="CAPABILITIES_ACK",
        )
        ev = engine.evidence_store.get_evidence("q0:CAPABILITIES")
        assessment = sec_analyzer.analyze_security(sess, an_res, nov_res, evidence=ev)

        if idx < 3:
            assert state == AdaptationState.REJECTED  # Accumulating evidence
        else:
            assert state == AdaptationState.ACTIVATED # Multi-session evidence satisfied -> updated!

    # Active model updated to v2.0.0-adapted cleanly
    assert engine.active_model.version == "v2.0.0-adapted"
