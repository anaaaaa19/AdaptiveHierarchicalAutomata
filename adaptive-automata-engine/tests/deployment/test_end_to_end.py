"""
End-to-End System Test for Phase 8 Real-Time Deployment Platform.
"""

from adaptive_automata.analysis.analyzer import HierarchicalAnalyzer
from adaptive_automata.core.mealy import MealyMachine, State
from adaptive_automata.deployment.alerts.manager import AlertManager
from adaptive_automata.deployment.capture.replay import ReplayCaptureSource
from adaptive_automata.deployment.config.settings import DeploymentConfig
from adaptive_automata.deployment.models.registry import DeploymentModelRegistry
from adaptive_automata.deployment.pipeline.realtime import RealTimePipeline
from adaptive_automata.deployment.storage.sqlite import InMemoryEventStore
from adaptive_automata.models.versioning import ModelRegistry, VersionedProtocolModel, ModelSource


def test_full_end_to_end_pipeline():
    # 1. Initialize core formal model (Phase 1)
    q0 = State("q0", is_initial=True)
    q1 = State("q1")
    mealy = MealyMachine[str, str]()
    mealy.add_transition(q0, "SYN", q1, "SYN-ACK")

    model = VersionedProtocolModel("m1", "v1.0.0", ModelSource.PASSIVE_INFERENCE, mealy)
    reg = ModelRegistry()
    reg.register_model(model)
    dep_reg = DeploymentModelRegistry(reg, "m1")
    dep_reg.set_active_model("v1.0.0")

    # 2. Hierarchical analyzer (Phase 4)
    analyzer = HierarchicalAnalyzer(fast_path_model=model)

    # 3. Capture source & packet ingestion
    capture = ReplayCaptureSource()
    capture.add_packet("192.168.1.10", 1234, "192.168.1.20", 80, "TCP", "SYN")
    capture.add_packet("192.168.1.10", 1234, "192.168.1.20", 80, "TCP", "UNKNOWN_DEVIATION")

    # 4. Storage & Alert Manager
    event_store = InMemoryEventStore()
    alert_mgr = AlertManager(event_store=event_store)

    # 5. RealTimePipeline
    pipeline = RealTimePipeline(
        capture_source=capture,
        analyzer=analyzer,
        model_registry=dep_reg,
        config=DeploymentConfig(),
        event_store=event_store,
        alert_manager=alert_mgr,
    )

    events = pipeline.run_replay()

    # 6. Verify end-to-end provenance and outputs
    assert len(events) == 2
    assert events[0].symbol == "SYN"
    assert events[0].analysis_result.status == events[0].analysis_result.status.KNOWN

    # Deviation packet produces security alert
    assert events[1].symbol == "UNKNOWN_DEVIATION"
    assert events[1].security_assessment.severity.value in ("LOW", "MEDIUM", "HIGH")
    assert event_store.get_event_count() == 2
    assert alert_mgr.get_alert_status(events[1].session_id) is not None or len(alert_mgr.list_alerts()) >= 1

    print("End-to-End System Test completed with 100% success!")
