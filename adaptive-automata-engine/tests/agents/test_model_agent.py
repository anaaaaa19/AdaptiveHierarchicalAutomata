"""Unit tests for ModelProposalAgent."""

from adaptive_automata.agents import ModelProposalAgent


def test_model_proposal_agent_proposal_formulation():
    agent = ModelProposalAgent()
    res = agent.run_investigation({
        "session_id": "mod_sess_77",
        "symbol": "CAPABILITIES",
        "model_version": "v1.1.0",
    })

    assert res.event_type == "MODEL_PROPOSAL_GENERATION"
    assert res.proposal is not None
    assert res.proposal.parent_model_version == "v1.1.0"
    assert res.proposal.proposed_transitions[0]["symbol"] == "CAPABILITIES"
