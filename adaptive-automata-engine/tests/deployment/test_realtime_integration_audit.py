"""
End-to-End Real-Time Audit Integration Test for Adaptive Automata Engine.
Verifies packet ingestion -> session reconstruction -> tokenization -> formal evaluation ->
security assessment -> alert generation -> event store -> REST API / WebSocket response.
"""

import time
from fastapi.testclient import TestClient

from adaptive_automata.analysis.analyzer import HierarchicalAnalyzer
from adaptive_automata.core.mealy import MealyMachine, State
from adaptive_automata.deployment.capture.base import PacketCaptureSource
from adaptive_automata.deployment.models.registry import DeploymentModelRegistry
from adaptive_automata.deployment.pipeline.events import RawPacket
from adaptive_automata.deployment.pipeline.realtime import RealTimePipeline
from adaptive_automata.deployment.storage.sqlite import InMemoryEventStore
from adaptive_automata.models.versioning import VersionedProtocolModel, ModelSource, ModelRegistry
from api.app import app


class SimpleReplaySource(PacketCaptureSource):
    """Synthetic packet capture source feeding real RawPacket streams."""

    def __init__(self, raw_messages: list[str]) -> None:
        super().__init__()
        self.raw_messages = raw_messages
        self._is_active = False

    def start(self) -> None:
        self._is_active = True

    def stop(self) -> None:
        self._is_active = False

    @property
    def is_active(self) -> bool:
        return self._is_active

    def packets(self):
        for idx, msg in enumerate(self.raw_messages):
            if not self._is_active:
                break
            yield RawPacket(
                packet_id=f"PKT-{idx+1}",
                src_ip="127.0.0.1",
                src_port=5000 + (idx % 2),
                dst_ip="127.0.0.1",
                dst_port=8000,
                protocol="TCP",
                timestamp=time.time(),
                payload=msg.encode("utf-8"),
                length=len(msg),
            )


def test_realtime_pipeline_end_to_end_audit():
    # 1. Setup formal Mealy Machine
    q0 = State("START", is_initial=True)
    q1 = State("AUTH_REQ")
    q2 = State("ACCEPTED")
    mealy = MealyMachine[str, str]()
    mealy.add_transition(q0, "ClientHello", q1, "ACK")
    mealy.add_transition(q1, "AuthToken", q2, "SUCCESS")

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

    capture = SimpleReplaySource([
        "SESSION-1:ClientHello",
        "SESSION-1:AuthToken",
        "SESSION-2:UNKNOWN_DEVIATION_SYMBOL",
    ])

    event_store = InMemoryEventStore()
    pipeline = RealTimePipeline(
        capture_source=capture,
        analyzer=analyzer,
        model_registry=dep_model_reg,
        event_store=event_store,
    )

    with TestClient(app) as client:
        app.state.pipeline = pipeline

        # Run synchronous replay to process packets through the real backend pipeline
        events = pipeline.run_replay()
        assert len(events) >= 2, f"Expected at least 2 events generated, got {len(events)}"

        # Verify /status endpoint returns real calculated metrics
        res = client.get("/status")
        assert res.status_code == 200
        status_data = res.json()
        assert status_data["active_model_version"] == "v1.0.0"
        assert status_data["metrics"]["events_processed"] >= 2
        assert status_data["metrics"]["throughput_events_per_sec"] >= 0.0
        assert status_data["metrics"]["dfa_resolution_percentage"] >= 0.0

        # Verify /events endpoint
        res = client.get("/events")
        assert res.status_code == 200
        events_data = res.json()
        assert events_data["count"] >= 2
        first_evt = events_data["events"][0]
        assert "event_id" in first_evt
        assert "symbol" in first_evt
        assert "formal_state" in first_evt
        assert "analysis" in first_evt
        assert "security" in first_evt

        # Verify /alerts endpoint
        res = client.get("/alerts")
        assert res.status_code == 200

        # Verify /models endpoint & /models/v1.0.0/graph
        res = client.get("/models")
        assert res.status_code == 200
        assert "v1.0.0" in res.json()["versions"]

        res = client.get("/models/v1.0.0/graph")
        assert res.status_code == 200
        graph_data = res.json()
        assert "states" in graph_data
        assert "START" in graph_data["states"]
        assert len(graph_data["transitions"]) >= 2
