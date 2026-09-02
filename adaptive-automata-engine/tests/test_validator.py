"""Unit tests for FormalValidator safety and regression checks."""

from adaptive_automata.core import State, MealyMachine
from adaptive_automata.models import ModelSource, VersionedProtocolModel
from adaptive_automata.adaptation.candidate import CandidateModel
from adaptive_automata.adaptation.evidence import BehaviorEvidence
from adaptive_automata.adaptation.validator import FormalValidator


def create_baseline_model() -> VersionedProtocolModel[str, str]:
    s0 = State("q0", is_initial=True)
    s1 = State("q1")
    mealy = MealyMachine[str, str]("TestModel")
    mealy.add_transition(s0, "SYN", s1, "SEND_SYN_ACK")
    mealy.validate()

    return VersionedProtocolModel[str, str](
        model_id="TestModel",
        version="v1.0.0",
        source=ModelSource.ACTIVE_HYBRID,
        mealy_machine=mealy,
    )


def test_validator_valid_candidate():
    validator = FormalValidator()
    baseline = create_baseline_model()
    ev = BehaviorEvidence("q1:AUTH", "q1", "AUTH", observation_count=5)

    valid_cand = CandidateModel(
        candidate_id="cand_valid",
        parent_version="v1.0.0",
        proposed_transitions=[("q1", "AUTH", "q2", "GRANT")],
        supporting_evidence=ev,
    )

    res = validator.validate_candidate(valid_cand, baseline)
    assert res.valid
    assert len(res.errors) == 0


def test_validator_candidate_breaks_existing_behavior():
    validator = FormalValidator()
    baseline = create_baseline_model()
    ev = BehaviorEvidence("q0:SYN", "q0", "SYN", observation_count=5)

    # Proposes transition that conflicts with existing q0 --[SYN]--> q1 / SEND_SYN_ACK
    conflicting_cand = CandidateModel(
        candidate_id="cand_corrupt",
        parent_version="v1.0.0",
        proposed_transitions=[("q0", "SYN", "q1", "WRONG_OUTPUT")],
        supporting_evidence=ev,
    )

    res = validator.validate_candidate(conflicting_cand, baseline)
    assert not res.valid
    assert len(res.errors) > 0
    assert "conflicts with baseline" in res.errors[0]


def test_validator_invalid_empty_state_definition():
    validator = FormalValidator()
    baseline = create_baseline_model()
    ev = BehaviorEvidence("invalid", "", "SYM")

    invalid_cand = CandidateModel(
        candidate_id="cand_invalid",
        parent_version="v1.0.0",
        proposed_transitions=[("", "SYM", "q1", "OUT")],
        supporting_evidence=ev,
    )

    res = validator.validate_candidate(invalid_cand, baseline)
    assert not res.valid
    assert len(res.errors) > 0
