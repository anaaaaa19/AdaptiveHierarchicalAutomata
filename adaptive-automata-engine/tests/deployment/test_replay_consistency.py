"""
Offline Replay vs Live Stream Processing Consistency Test.
"""

from adaptive_automata.analysis.analyzer import HierarchicalAnalyzer
from adaptive_automata.core.mealy import MealyMachine, State
from adaptive_automata.deployment.capture.replay import ReplayCaptureSource
from adaptive_automata.deployment.models.registry import DeploymentModelRegistry
from adaptive_automata.deployment.pipeline.realtime import RealTimePipeline
from adaptive_automata.models.versioning import ModelRegistry, VersionedProtocolModel, ModelSource


def test_replay_vs_live_consistency():
    q0 = State("q0", is_initial=True)
    q1 = State("q1")
    mealy = MealyMachine[str, str]()
    mealy.add_transition(q0, "SYN", q1, "SYN-ACK")

    model = VersionedProtocolModel("m1", "v1.0.0", ModelSource.PASSIVE_INFERENCE, mealy)
    reg = ModelRegistry()
    reg.register_model(model)
    dep_reg = DeploymentModelRegistry(reg, "m1")
    dep_reg.set_active_model("v1.0.0")

    analyzer = HierarchicalAnalyzer(fast_path_model=model)

    # Replay capture source 1
    cap1 = ReplayCaptureSource()
    cap1.add_packet("10.0.0.1", 1000, "10.0.0.2", 80, "TCP", "CONNECT:SYN")

    # Replay capture source 2 (identical traffic)
    cap2 = ReplayCaptureSource()
    cap2.add_packet("10.0.0.1", 1000, "10.0.0.2", 80, "TCP", "CONNECT:SYN")

    pipeline1 = RealTimePipeline(capture_source=cap1, analyzer=analyzer, model_registry=dep_reg)
    events1 = pipeline1.run_replay()

    pipeline2 = RealTimePipeline(capture_source=cap2, analyzer=analyzer, model_registry=dep_reg)
    events2 = pipeline2.run_replay()

    assert len(events1) == len(events2)
    assert events1[0].symbol == events2[0].symbol
    assert events1[0].formal_state == events2[0].formal_state
    assert events1[0].analysis_result.status == events2[0].analysis_result.status
    assert events1[0].security_assessment.severity == events2[0].security_assessment.severity
