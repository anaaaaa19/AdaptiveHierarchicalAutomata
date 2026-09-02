"""Unit and integration tests for Active/Passive Hybrid Learning."""

import pytest
from adaptive_automata.protocol import TraceLoader, create_toy_protocol_sut
from adaptive_automata.learning import PassiveInferenceEngine, HybridActiveLearner, ConfidenceLevel


def test_hybrid_active_learner():
    json_data = """
    {
        "sessions": [
            {
                "session_id": "s1",
                "messages": [
                    {"sequence_number": 1, "direction": "INBOUND", "message_type": "SYN"},
                    {"sequence_number": 2, "direction": "OUTBOUND", "message_type": "SEND_SYN_ACK"},
                    {"sequence_number": 3, "direction": "INBOUND", "message_type": "ACK"},
                    {"sequence_number": 4, "direction": "OUTBOUND", "message_type": "ALLOCATE_SESSION"}
                ]
            }
        ]
    }
    """
    sessions = TraceLoader.load_from_json(json_data)
    passive_engine = PassiveInferenceEngine()
    passive_model = passive_engine.infer_model(sessions, model_id="ToyHybrid", version="v1.0.0-passive")

    sut = create_toy_protocol_sut()
    hybrid_learner = HybridActiveLearner[str, str]()

    refined_model = hybrid_learner.refine_model(passive_model, sut, new_version="v1.1.0-hybrid")

    assert refined_model.version == "v1.1.0-hybrid"
    assert refined_model.num_states == 4
    assert refined_model.metrics["hybrid_active_queries"] > 0

    # Verify transition statuses upgraded to ACTIVE_VERIFIED
    for meta in refined_model.transition_metadata.values():
        assert meta.status == ConfidenceLevel.ACTIVE_VERIFIED
        assert meta.confidence_score == 1.0
