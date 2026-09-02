"""Unit tests for CandidateModel and AdaptationEvent audit containers."""

from adaptive_automata.adaptation.candidate import AdaptationEvent, CandidateModel
from adaptive_automata.adaptation.evidence import BehaviorEvidence
from adaptive_automata.adaptation.lifecycle import AdaptationState


def test_candidate_model_creation():
    ev = BehaviorEvidence(behavior_id="q0:AUTH", source_state="q0", input_symbol="AUTH", observation_count=5)
    cand = CandidateModel(
        candidate_id="cand_q0_AUTH_5",
        parent_version="v1.0.0",
        proposed_transitions=[("q0", "AUTH", "q1", "GRANT")],
        supporting_evidence=ev,
    )

    assert cand.candidate_id == "cand_q0_AUTH_5"
    assert cand.parent_version == "v1.0.0"
    assert cand.lifecycle_state == AdaptationState.CANDIDATE
    assert len(cand.proposed_transitions) == 1


def test_adaptation_event_creation():
    event = AdaptationEvent(
        event_id="evt_1",
        timestamp="2026-09-02T12:00:00Z",
        session_id="sess_100",
        event_type="NOVELTY_DETECTED",
        state_from="OBSERVED",
        state_to="NOVEL",
        explanation="Novel transition observed at q0 on AUTH.",
        model_version="v1.0.0",
    )

    assert event.event_id == "evt_1"
    assert event.event_type == "NOVELTY_DETECTED"
    assert event.state_from == "OBSERVED"
    assert event.state_to == "NOVEL"
    assert "Novel transition" in event.explanation
