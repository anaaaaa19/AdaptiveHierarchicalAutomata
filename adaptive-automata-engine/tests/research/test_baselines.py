"""
Unit tests for baseline models (StaticDFA, StaticHierarchical, NaiveAdaptive, ProposedAdaptiveHierarchical).
"""

from adaptive_automata.evaluation.baselines import (
    StaticDFABaseline,
    StaticHierarchicalBaseline,
    NaiveAdaptiveBaseline,
    ProposedAdaptiveHierarchicalModel,
)


def test_static_dfa_baseline():
    valid = {("HELLO", "AUTH", "LOGOUT")}
    model = StaticDFABaseline(valid_sequences=valid)

    res_valid = model.process_sequence(["HELLO", "AUTH", "LOGOUT"])
    assert res_valid.is_accepted is True
    assert res_valid.is_anomaly is False
    assert res_valid.escalation_level == "DFA"

    res_invalid = model.process_sequence(["HELLO", "LOGOUT"])
    assert res_invalid.is_accepted is False
    assert res_invalid.is_anomaly is True
    assert res_invalid.escalation_level == "REJECT"

    # Static model must not adapt
    assert model.adapt_on_sequence(["HELLO", "LOGOUT"]) is False


def test_static_hierarchical_baseline():
    dfa_seqs = {("HELLO", "LOGOUT")}
    pda_seqs = {("HELLO", "AUTH", "LOGOUT")}
    cfg_seqs = {("HELLO", "AUTH", "REQ", "RESP", "LOGOUT")}

    model = StaticHierarchicalBaseline(dfa_seqs, pda_seqs, cfg_seqs)

    assert model.process_sequence(["HELLO", "LOGOUT"]).escalation_level == "DFA"
    assert model.process_sequence(["HELLO", "AUTH", "LOGOUT"]).escalation_level == "PDA"
    assert model.process_sequence(["HELLO", "AUTH", "REQ", "RESP", "LOGOUT"]).escalation_level == "CFG"
    assert model.process_sequence(["INVALID"]).escalation_level == "REJECT"


def test_naive_adaptive_baseline():
    initial = {("HELLO", "LOGOUT")}
    model = NaiveAdaptiveBaseline(initial_valid=initial, frequency_threshold=3)

    novel = ["HELLO", "NEW_STEP", "LOGOUT"]
    assert model.process_sequence(novel).is_accepted is False

    # Adapt 2 times (below threshold 3)
    assert model.adapt_on_sequence(novel) is False
    assert model.adapt_on_sequence(novel) is False
    # 3rd time reaches threshold -> adapts
    assert model.adapt_on_sequence(novel) is True

    # Now accepts
    assert model.process_sequence(novel).is_accepted is True


def test_proposed_adaptive_model():
    dfa_seqs = {("HELLO", "LOGOUT")}
    pda_seqs = {("HELLO", "AUTH", "LOGOUT")}
    cfg_seqs = set()

    model = ProposedAdaptiveHierarchicalModel(
        dfa_sequences=dfa_seqs,
        pda_sequences=pda_seqs,
        cfg_sequences=cfg_seqs,
        evidence_threshold=3,
    )

    # Standard hierarchy check
    assert model.process_sequence(["HELLO", "LOGOUT"]).escalation_level == "DFA"
    assert model.process_sequence(["HELLO", "AUTH", "LOGOUT"]).escalation_level == "PDA"

    # Poisoning attack rejection test
    poison_seq = ["HELLO", "MALICIOUS", "LOGOUT"]
    for _ in range(5):
        adapted = model.adapt_on_sequence(poison_seq, label="poisoning")
        assert adapted is False

    assert model.poisoning_attempts > 0
    assert model.blocked_poisoning_attempts > 0
