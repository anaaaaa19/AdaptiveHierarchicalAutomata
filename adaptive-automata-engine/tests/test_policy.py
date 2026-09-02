"""Unit tests for AdaptationPolicy and Poisoning Defense."""

from adaptive_automata.adaptation.config import AdaptationConfig
from adaptive_automata.adaptation.evidence import BehaviorEvidence, EvidenceStore
from adaptive_automata.adaptation.policy import AdaptationPolicy, EvidenceStrength


def test_policy_low_evidence():
    policy = AdaptationPolicy(min_observations=5, min_unique_sessions=3, min_successful_followups=2)
    ev = BehaviorEvidence("q0:AUTH", "q0", "AUTH", observation_count=1, unique_session_count=1)

    assert policy.evaluate_evidence_strength(ev) == EvidenceStrength.LOW
    should_propose, reason = policy.should_propose_candidate(ev)
    assert not should_propose
    assert "Insufficient observation count" in reason


def test_poisoning_like_high_frequency_single_session_rejected():
    policy = AdaptationPolicy(min_observations=5, min_unique_sessions=3, min_successful_followups=2)
    store = EvidenceStore()

    # Attacker spams 100 times in 1 single session
    for _ in range(100):
        ev = store.record_observation("attacker_session_1", "q0", "MALICIOUS_SYM", follows_up_successfully=True)

    # Frequency alone is NOT sufficient! Poisoning defense MUST reject single-session spam attacks!
    should_propose, reason = policy.should_propose_candidate(ev)
    assert not should_propose
    assert "Poisoning Defense Triggered" in reason
    assert "Insufficient session diversity" in reason


def test_policy_multi_dimensional_evidence_accepted():
    policy = AdaptationPolicy(min_observations=5, min_unique_sessions=3, min_successful_followups=2)
    store = EvidenceStore()

    # Legitimate behavior observed across 3 distinct sessions with successful follow-ups
    store.record_observation("sess_1", "q0", "CAPABILITIES", follows_up_successfully=True, structurally_valid=True)
    store.record_observation("sess_1", "q0", "CAPABILITIES", follows_up_successfully=True, structurally_valid=True)
    store.record_observation("sess_2", "q0", "CAPABILITIES", follows_up_successfully=True, structurally_valid=True)
    store.record_observation("sess_2", "q0", "CAPABILITIES", follows_up_successfully=True, structurally_valid=True)
    ev = store.record_observation("sess_3", "q0", "CAPABILITIES", follows_up_successfully=True, structurally_valid=True)

    assert ev.observation_count == 5
    assert ev.unique_session_count == 3
    assert ev.successful_followup_count == 5

    should_propose, reason = policy.should_propose_candidate(ev)
    assert should_propose
    assert "Multi-dimensional evidence criteria satisfied" in reason
