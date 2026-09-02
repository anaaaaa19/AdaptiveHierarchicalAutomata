"""
Tests for RealTimePipeline synchronous and asynchronous execution.
"""

from adaptive_automata.analysis.analyzer import HierarchicalAnalyzer
from adaptive_automata.core.mealy import MealyMachine, State
from adaptive_automata.deployment.capture.replay import ReplayCaptureSource
from adaptive_automata.deployment.models.registry import DeploymentModelRegistry
from adaptive_automata.deployment.pipeline.realtime import RealTimePipeline
from adaptive_automata.models.versioning import ModelRegistry, VersionedProtocolModel, ModelSource


def test_realtime_pipeline_synchronous_processing():
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
    capture = ReplayCaptureSource()
    capture.add_packet("10.0.0.1", 1000, "10.0.0.2", 80, "TCP", "SYN")

    pipeline = RealTimePipeline(capture_source=capture, analyzer=analyzer, model_registry=dep_reg)
    events = pipeline.run_replay()

    assert len(events) > 0
    assert events[0].symbol == "SYN"
    assert events[0].formal_state == "q1"
