"""Unit tests for Protocol Trace Loading, Session Reconstruction, and Tokenization."""

import pytest
from adaptive_automata.protocol import (
    MessageDirection,
    ProtocolMessage,
    ProtocolSession,
    TraceLoader,
    MalformedTraceError,
    PreGroupedSessionReconstructor,
    HeaderCommandTokenizer,
    JSONMessageTokenizer,
)


def test_trace_loader_valid_json():
    json_data = """
    {
        "sessions": [
            {
                "session_id": "s1",
                "messages": [
                    {"sequence_number": 1, "direction": "INBOUND", "message_type": "SYN", "payload": {}},
                    {"sequence_number": 2, "direction": "OUTBOUND", "message_type": "SYN_ACK", "payload": {}}
                ]
            }
        ]
    }
    """
    sessions = TraceLoader.load_from_json(json_data)
    assert len(sessions) == 1
    assert sessions[0].session_id == "s1"
    assert len(sessions[0].messages) == 2
    assert sessions[0].messages[0].direction == MessageDirection.CLIENT_TO_SERVER
    assert sessions[0].messages[1].direction == MessageDirection.SERVER_TO_CLIENT


def test_trace_loader_malformed_json():
    with pytest.raises(MalformedTraceError):
        TraceLoader.load_from_json("INVALID JSON {")

    with pytest.raises(MalformedTraceError):
        TraceLoader.load_from_json('{"sessions": [{"messages": [{"direction": "INBOUND"}]}]}')


def test_session_reconstructor():
    reconstructor = PreGroupedSessionReconstructor()
    data = [
        {
            "session_id": "sess_rec",
            "messages": [
                {"sequence_number": 1, "direction": "C2S", "message_type": "AUTH"},
                {"sequence_number": 2, "direction": "S2C", "message_type": "GRANT"}
            ]
        }
    ]
    sessions = reconstructor.reconstruct_sessions(data)
    assert len(sessions) == 1
    assert sessions[0].session_id == "sess_rec"


def test_message_tokenizers():
    sess = ProtocolSession(
        session_id="test",
        messages=[
            ProtocolMessage("test", 1, MessageDirection.CLIENT_TO_SERVER, "AUTH", {"cmd": "LOGIN"}),
            ProtocolMessage("test", 2, MessageDirection.SERVER_TO_CLIENT, "GRANT", {"code": 200}),
        ]
    )

    tok_header = HeaderCommandTokenizer()
    pairs_header = tok_header.tokenize_session(sess)
    assert pairs_header == [("AUTH", "GRANT")]

    tok_json = JSONMessageTokenizer(header_field="cmd")
    pairs_json = tok_json.tokenize_session(sess)
    assert pairs_json == [("LOGIN", "GRANT")]
