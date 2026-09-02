"""Unit tests for Passive Protocol Inference Engine."""

import pytest
from adaptive_automata.protocol import TraceLoader
from adaptive_automata.learning.passive import PassiveInferenceEngine
from adaptive_automata.learning.confidence import ConfidenceLevel


def test_passive_inference_engine():
    json_data = """
    {
        "sessions": [
            {
                "session_id": "s1",
                "messages": [
                    {"sequence_number": 1, "direction": "INBOUND", "message_type": "SYN"},
                    {"sequence_number": 2, "direction": "OUTBOUND", "message_type": "SYN_ACK"},
                    {"sequence_number": 3, "direction": "INBOUND", "message_type": "ACK"},
                    {"sequence_number": 4, "direction": "OUTBOUND", "message_type": "ALLOC"}
                ]
            }
        ]
    }
    """
    sessions = TraceLoader.load_from_json(json_data)
    engine = PassiveInferenceEngine()

    model = engine.infer_model(sessions, model_id="TestPassive", version="v1.0.0")

    assert model.model_id == "TestPassive"
    assert model.version == "v1.0.0"
    assert model.num_states >= 2
    assert model.metrics["num_traces"] == 1
    assert model.metrics["num_symbols"] == 2

    # Verify transition metadata
    meta = model.transition_metadata.get(("q0", "SYN"))
    assert meta is not None
    assert meta.observation_count == 1
    assert meta.output_symbol == "SYN_ACK"
