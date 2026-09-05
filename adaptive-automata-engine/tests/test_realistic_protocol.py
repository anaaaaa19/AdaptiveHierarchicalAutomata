"""
Cross-Protocol Generality and Realistic Message Ingestion Test Suite.
Evaluates pipeline across stateful text protocols, HTTP-style headers, and binary framed payloads.
"""

from adaptive_automata.evaluation.baselines import ProposedAdaptiveHierarchicalModel
from adaptive_automata.protocol.tokenizer import DelimiterTokenizer


def test_toy_protocol_v1_v2_ingestion():
    """Verify toy protocol v1 and v2 token sequence ingestion."""
    engine = ProposedAdaptiveHierarchicalModel(
        dfa_sequences={("HELLO", "AUTH", "REQUEST", "RESPONSE", "LOGOUT")},
        pda_sequences=set(),
        cfg_sequences=set(),
        evidence_threshold=2,
    )

    v1_seq = ["HELLO", "AUTH", "REQUEST", "RESPONSE", "LOGOUT"]
    assert engine.process_sequence(v1_seq).is_accepted is True

    v2_seq = ["HELLO", "AUTH", "CAPABILITIES", "REQUEST", "RESPONSE", "LOGOUT"]
    assert engine.process_sequence(v2_seq).is_accepted is False

    # Adapt to Protocol v2
    engine.adapt_on_sequence(v2_seq, label="evolved")
    engine.adapt_on_sequence(v2_seq, label="evolved")
    assert engine.process_sequence(v2_seq).is_accepted is True


def test_http_style_protocol_tokenization():
    """Verify HTTP-style text protocol message tokenization and formal evaluation."""
    tokenizer = DelimiterTokenizer(delimiter=" ")
    http_req = "GET /api/v1/resource HTTP/1.1"
    raw_tokens = tokenizer.tokenize(http_req)
    tokens = [t.value for t in raw_tokens]

    assert tokens == ["GET", "/api/v1/resource", "HTTP/1.1"]

    engine = ProposedAdaptiveHierarchicalModel(
        dfa_sequences={("GET", "/api/v1/resource", "HTTP/1.1")},
        pda_sequences=set(),
        cfg_sequences=set(),
    )

    res = engine.process_sequence(tokens)
    assert res.is_accepted is True
    assert res.escalation_level == "DFA"


def test_binary_framed_protocol_tokenization():
    """Verify binary framed protocol tokenization and deviation handling."""
    binary_tokens = ["FRAME_START", "HEADER_CMD_0x01", "PAYLOAD_DATA", "CRC32_OK", "FRAME_END"]

    engine = ProposedAdaptiveHierarchicalModel(
        dfa_sequences={(tuple(binary_tokens))},
        pda_sequences=set(),
        cfg_sequences=set(),
    )

    res_valid = engine.process_sequence(binary_tokens)
    assert res_valid.is_accepted is True

    bad_binary = ["FRAME_START", "HEADER_CMD_0x01", "PAYLOAD_CORRUPT", "CRC32_BAD"]
    res_bad = engine.process_sequence(bad_binary)
    assert res_bad.is_accepted is False
    assert res_bad.is_anomaly is True
