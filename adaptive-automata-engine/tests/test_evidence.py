"""Unit tests for EvidenceStore and BehaviorEvidence abstraction."""

from adaptive_automata.adaptation.evidence import BehaviorEvidence, EvidenceStore


def test_first_observation():
    store = EvidenceStore()
    ev = store.record_observation(
        session_id="sess_1",
        source_state="q0",
        input_symbol="SYN",
        target_state="q1",
        output_symbol="ACK",
        follows_up_successfully=True,
    )
    assert ev.behavior_id == "q0:SYN"
    assert ev.observation_count == 1
    assert ev.unique_session_count == 1
    assert ev.successful_followup_count == 1
    assert "sess_1" in ev.session_ids


def test_repeated_observations_and_duplicate_sessions():
    store = EvidenceStore()
    # Repeated observation in the same session
    store.record_observation("sess_1", "q0", "DATA")
    store.record_observation("sess_1", "q0", "DATA")

    ev = store.get_evidence("q0:DATA")
    assert ev is not None
    assert ev.observation_count == 2
    assert ev.unique_session_count == 1

    # Observation in a second distinct session
    store.record_observation("sess_2", "q0", "DATA")
    assert ev.observation_count == 3
    assert ev.unique_session_count == 2


def test_no_evidence():
    store = EvidenceStore()
    assert store.get_evidence("non_existent") is None
    assert len(store.list_all_evidence()) == 0


def test_evidence_score_calculation():
    ev_empty = BehaviorEvidence(behavior_id="q0:X", source_state="q0", input_symbol="X", observation_count=0)
    assert ev_empty.calculate_evidence_score() == 0.0

    ev_high = BehaviorEvidence(
        behavior_id="q0:Y",
        source_state="q0",
        input_symbol="Y",
        observation_count=10,
        unique_session_count=5,
        successful_followup_count=10,
    )
    assert ev_high.calculate_evidence_score() >= 0.9
