"""Unit tests for Context-Free Grammar (CFG) and Earley Parser."""

import pytest
from adaptive_automata.core import Grammar, Terminal, NonTerminal, ProductionRule, CFGParser, CFGValidationError


def test_cfg_grammar_and_parser():
    # Build grammar: S -> A B, A -> 'SYN', B -> 'ACK'
    S = NonTerminal("S")
    A = NonTerminal("A")
    B = NonTerminal("B")

    t_syn = Terminal("SYN")
    t_ack = Terminal("ACK")

    g = Grammar(start_symbol=S)
    g.add_rule(S, [A, B])
    g.add_rule(A, [t_syn])
    g.add_rule(B, [t_ack])

    g.validate()

    parser = CFGParser(g)

    # Valid parse
    res_valid = parser.parse(["SYN", "ACK"])
    assert res_valid.is_valid
    assert res_valid.error_position is None

    # Invalid parse
    res_invalid = parser.parse(["SYN", "SYN"])
    assert not res_invalid.is_valid
    assert res_invalid.error_position == 1


def test_cfg_recursive_grammar():
    # Grammar: S -> 'OPEN' S 'CLOSE' | 'DATA'
    S = NonTerminal("S")
    t_open = Terminal("OPEN")
    t_close = Terminal("CLOSE")
    t_data = Terminal("DATA")

    g = Grammar(start_symbol=S)
    g.add_rule(S, [t_open, S, t_close])
    g.add_rule(S, [t_data])
    g.validate()

    parser = CFGParser(g)

    # Nested depth 2 sequence: OPEN OPEN DATA CLOSE CLOSE
    res_nested = parser.parse(["OPEN", "OPEN", "DATA", "CLOSE", "CLOSE"])
    assert res_nested.is_valid

    # Unmatched sequence: OPEN DATA
    res_bad = parser.parse(["OPEN", "DATA"])
    assert not res_bad.is_valid
