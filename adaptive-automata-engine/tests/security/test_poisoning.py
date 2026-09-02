"""Unit tests for Poisoning Attack Detection and Defense."""

from adaptive_automata.analysis import HierarchicalAnalyzer
from adaptive_automata.core import State, MealyMachine
from adaptive_automata.models import ModelSource, VersionedProtocolModel, ModelRegistry
from adaptive_automata.adaptation import AdaptationConfig, AdaptationState, AdaptiveModelEngine
from adaptive_automata.security import BehavioralAnalyzer, ReasonCode, SyntheticDatasetGenerator


def create_baseline_model() -> VersionedProtocolModel[str, str]:
    s0 = State("q0", is_initial=True)
    s1 = State("q1")
    mealy = MealyMachine[str, str]("PoisonTestProto")
    mealy.add_transition(s0, "SYN", s1, "SEND_SYN_ACK")
    mealy.validate()

    return VersionedProtocolModel[str, str](
        model_id="PoisonTestProto",
        version="v1.0.0",
        source=ModelSource.ACTIVE_HYBRID,
        mealy_machine=mealy,
    )


def test_poisoning_detection_and_model_protection():
    registry = ModelRegistry()
    model = create_baseline_model()
    registry.register_model(model)

    config = AdaptationConfig(minimum_observations=5, minimum_sessions=3, minimum_followups=2)
    analyzer = HierarchicalAnalyzer(fast_path_model=model)
    engine = AdaptiveModelEngine(analyzer, registry, config=config)
    sec_analyzer = BehavioralAnalyzer()

    poison_sessions = SyntheticDatasetGenerator.generate_poisoning_sessions(count=30)

    for sess, _ in poison_sessions:
        an_res, nov_res, state = engine.process_session(sess, proposed_target_state="q_poison", proposed_output_symbol="ERROR")
        ev = engine.evidence_store.get_evidence("q0:POISON_PAYLOAD")
        assessment = sec_analyzer.analyze_security(sess, an_res, nov_res, evidence=ev)

        assert state != AdaptationState.ACTIVATED

    # Model remains intact at v1.0.0
    assert engine.active_model.version == "v1.0.0"
    assert engine.accepted_candidates_count == 0
