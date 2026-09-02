"""
Phase 8 PCAP and Trace Replay Benchmark Runner.
"""

import time
from adaptive_automata.analysis.analyzer import HierarchicalAnalyzer
from adaptive_automata.core.mealy import MealyMachine, State
from adaptive_automata.deployment.capture.replay import ReplayCaptureSource
from adaptive_automata.deployment.config.settings import DeploymentConfig
from adaptive_automata.deployment.models.registry import DeploymentModelRegistry
from adaptive_automata.deployment.pipeline.realtime import RealTimePipeline
from adaptive_automata.deployment.storage.sqlite import InMemoryEventStore
from adaptive_automata.models.versioning import ModelRegistry, VersionedProtocolModel, ModelSource


def run_replay_benchmark(num_packets: int = 1000) -> dict:
    q0 = State("q0", is_initial=True)
    q1 = State("q1")
    mealy = MealyMachine[str, str]()
    mealy.add_transition(q0, "SYN", q1, "SYN-ACK")
    mealy.add_transition(q1, "ACK", q0, "READY")

    init_model = VersionedProtocolModel[str, str](
        model_id="toy_protocol_model",
        version="v1.0.0",
        source=ModelSource.PASSIVE_INFERENCE,
        mealy_machine=mealy,
    )

    model_reg = ModelRegistry()
    model_reg.register_model(init_model)
    dep_model_reg = DeploymentModelRegistry(registry=model_reg, model_id="toy_protocol_model")
    dep_model_reg.set_active_model("v1.0.0")

    analyzer = HierarchicalAnalyzer(fast_path_model=init_model)
    capture = ReplayCaptureSource()

    # Add synthetic replay packets
    for i in range(num_packets):
        cmd = "SYN" if i % 2 == 0 else "ACK"
        capture.add_packet("192.168.1.10", 5000 + (i % 100), "192.168.1.20", 80, "TCP", f"CONNECT:{cmd}")

    event_store = InMemoryEventStore()
    pipeline = RealTimePipeline(
        capture_source=capture,
        analyzer=analyzer,
        model_registry=dep_model_reg,
        config=DeploymentConfig(),
        event_store=event_store,
    )

    start_t = time.time()
    events = pipeline.run_replay()
    elapsed = max(0.0001, time.time() - start_t)

    summary = pipeline.metrics.get_summary()
    summary["benchmark_packets"] = num_packets
    summary["benchmark_events_generated"] = len(events)
    summary["total_time_seconds"] = round(elapsed, 4)
    summary["events_per_second"] = round(len(events) / elapsed, 2)

    return summary


if __name__ == "__main__":
    res = run_replay_benchmark(1000)
    print("Replay Benchmark Summary:", res)
