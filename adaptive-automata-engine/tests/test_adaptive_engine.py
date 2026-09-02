"""Unit and integration tests for AdaptiveModelEngine orchestrator."""

from adaptive_automata.analysis import HierarchicalAnalyzer
from adaptive_automata.core import State, MealyMachine
from adaptive_automata.models import ModelSource, VersionedProtocolModel, ModelRegistry
from adaptive_automata.protocol import ProtocolSession, ProtocolMessage, MessageDirection
from adaptive_automata.adaptation.config import AdaptationConfig
from adaptive_automata.adaptation.engine import AdaptiveModelEngine
from adaptive_automata.adaptation.lifecycle import AdaptationState
from adaptive_automata.adaptation.policy import AdaptationPolicy


def create_sample_model(version: str = "v1.0.0") -> VersionedProtocolModel[str, str]:
    s0 = State("q0", is_initial=True)
    s1 = State("q1")
    mealy = MealyMachine[str, str]("EngineTestProto")
    mealy.add_transition(s0, "SYN", s1, "SEND_SYN_ACK")
    mealy.validate()

    return VersionedProtocolModel[str, str](
        model_id="EngineTestProto",
        version=version,
        source=ModelSource.ACTIVE_HYBRID,
        mealy_machine=mealy,
    )


def test_engine_initialization_and_known_session():
    registry = ModelRegistry()
    model = create_sample_model()
    registry.register_model(model)

    analyzer = HierarchicalAnalyzer(fast_path_model=model)
    engine = AdaptiveModelEngine(analyzer, registry)

    known_session = ProtocolSession(
        "sess_known",
        messages=[
            ProtocolMessage("sess_known", 1, MessageDirection.CLIENT_TO_SERVER, "SYN"),
            ProtocolMessage("sess_known", 2, MessageDirection.SERVER_TO_CLIENT, "SEND_SYN_ACK"),
        ]
    )

    an_res, nov_res, state = engine.process_session(known_session)
    assert nov_res.status.value == "KNOWN"
    assert state == AdaptationState.OBSERVED
    assert engine.known_observations == 1


def test_engine_novelty_to_activation_flow():
    registry = ModelRegistry()
    model = create_sample_model()
    registry.register_model(model)

    config = AdaptationConfig(minimum_observations=2, minimum_sessions=2, minimum_followups=1, require_structural_validation=False)
    analyzer = HierarchicalAnalyzer(fast_path_model=model)
    engine = AdaptiveModelEngine(analyzer, registry, config=config)

    s1 = ProtocolSession("s1", messages=[ProtocolMessage("s1", 1, MessageDirection.CLIENT_TO_SERVER, "AUTH"), ProtocolMessage("s1", 2, MessageDirection.SERVER_TO_CLIENT, "GRANT")])
    s2 = ProtocolSession("s2", messages=[ProtocolMessage("s2", 1, MessageDirection.CLIENT_TO_SERVER, "AUTH"), ProtocolMessage("s2", 2, MessageDirection.SERVER_TO_CLIENT, "GRANT")])

    # 1st session: under review -> rejected due to min_sessions < 2
    _, nov1, state1 = engine.process_session(s1)
    assert state1 == AdaptationState.REJECTED

    # 2nd session: satisfies min_sessions == 2 -> activated!
    _, nov2, state2 = engine.process_session(s2)
    assert state2 == AdaptationState.ACTIVATED
    assert engine.active_model.version == "v2.0.0-adapted"
    assert len(engine.events_log) > 0

    metrics = engine.get_metrics_summary()
    assert metrics["accepted_candidates"] == 1
    assert metrics["active_model_version"] == "v2.0.0-adapted"
