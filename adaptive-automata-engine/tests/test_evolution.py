"""Unit tests for Protocol Evolution Analyzer."""

import pytest
from adaptive_automata.protocol import TraceLoader
from adaptive_automata.learning import PassiveInferenceEngine, ProtocolEvolutionAnalyzer


def test_protocol_evolution_analysis():
    v1_json = """
    {
        "sessions": [
            {
                "session_id": "v1",
                "messages": [
                    {"sequence_number": 1, "direction": "INBOUND", "message_type": "SYN"},
                    {"sequence_number": 2, "direction": "OUTBOUND", "message_type": "SYN_ACK"}
                ]
            }
        ]
    }
    """
    v2_json = """
    {
        "sessions": [
            {
                "session_id": "v2",
                "messages": [
                    {"sequence_number": 1, "direction": "INBOUND", "message_type": "SYN"},
                    {"sequence_number": 2, "direction": "OUTBOUND", "message_type": "SYN_ACK"},
                    {"sequence_number": 3, "direction": "INBOUND", "message_type": "PING"},
                    {"sequence_number": 4, "direction": "OUTBOUND", "message_type": "PONG"}
                ]
            }
        ]
    }
    """
    v1_sessions = TraceLoader.load_from_json(v1_json)
    v2_sessions = TraceLoader.load_from_json(v2_json)

    engine = PassiveInferenceEngine()
    baseline = engine.infer_model(v1_sessions, model_id="ProtoEvol", version="v1.0.0")

    analyzer = ProtocolEvolutionAnalyzer(passive_engine=engine)
    evolved_model, eval_result = analyzer.analyze_evolution(baseline, v2_sessions, new_version="v2.0.0")

    assert eval_result.is_valid_protocol_extension
    assert len(eval_result.new_valid_transitions) >= 1
    assert evolved_model.version == "v2.0.0"
    assert evolved_model.metrics["new_transitions_added"] >= 1
