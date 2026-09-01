import pytest
from adaptive_automata.protocol import ProtocolToken, DelimiterTokenizer


def test_delimiter_tokenizer():
    tokenizer = DelimiterTokenizer(delimiter=" ")
    stream = "CONNECT AUTH_PASS REQ_DATA LOGOUT"
    tokens = tokenizer.tokenize(stream)

    assert len(tokens) == 4
    assert tokens[0] == ProtocolToken("CONNECT", "CONNECT", 0)
    assert tokens[1] == ProtocolToken("AUTH_PASS", "AUTH_PASS", 1)
    assert tokens[3] == ProtocolToken("LOGOUT", "LOGOUT", 3)


def test_tokenizer_type_error():
    tokenizer = DelimiterTokenizer()
    with pytest.raises(TypeError):
        tokenizer.tokenize(12345)  # type: ignore
