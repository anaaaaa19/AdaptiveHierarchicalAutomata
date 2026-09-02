"""Unit tests for FormalVerificationGuard."""

from adaptive_automata.core import MealyMachine, State
from adaptive_automata.models import ModelSource, VersionedProtocolModel
from adaptive_automata.agents import CandidateModelProposal, FormalVerificationGuard


def create_base_model() -> VersionedProtocolModel[str, str]:
    s0 = State("q0", is_initial=True)
    s1 = State("q1")
    mealy = MealyMachine[str, str]("GuardTestProto")
    mealy.add_transition(s0, "SYN", s1, "SEND_SYN_ACK")
    mealy.validate()

    return VersionedProtocolModel[str, str](
        model_id="GuardTestProto",
        version="v1.0.0",
        source=ModelSource.ACTIVE_HYBRID,
        mealy_machine=mealy,
    )


def test_formal_verification_guard_valid_proposal():
    guard = FormalVerificationGuard()
    base_model = create_base_model()

    proposal = CandidateModelProposal(
        proposal_id="prop_valid",
        parent_model_version="v1.0.0",
        proposed_transitions=[{"source": "q0", "symbol": "CAPABILITIES", "target": "q2", "output": "ACK"}],
        reason="Legitimate extension",
    )

    result = guard.verify_proposal(proposal, base_model)
    assert result.is_valid is True
    assert len(result.rejection_reasons) == 0
    assert result.candidate_model is not None


def test_formal_verification_guard_malformed_proposal():
    guard = FormalVerificationGuard()
    base_model = create_base_model()

    proposal = CandidateModelProposal(
        proposal_id="",
        parent_model_version="",
        proposed_transitions=[],
    )

    result = guard.verify_proposal(proposal, base_model)
    assert result.is_valid is False
    assert len(result.rejection_reasons) >= 1
