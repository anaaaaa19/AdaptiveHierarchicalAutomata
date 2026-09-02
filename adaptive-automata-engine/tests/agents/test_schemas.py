"""Unit tests for agent structured schemas."""

from adaptive_automata.agents import AgentHypothesis, AgentObservation, CandidateModelProposal, InvestigationResult


def test_agent_schemas_fact_hypothesis_separation():
    obs = AgentObservation(
        fact_id="fact_100",
        source_tool="run_dfa_analysis",
        description="Observed symbol CAPABILITIES at state q0.",
    )
    hyp = AgentHypothesis(
        hypothesis_id="hyp_100",
        statement="Symbol may represent valid protocol evolution.",
        confidence=0.85,
        supporting_fact_ids=["fact_100"],
    )

    prop = CandidateModelProposal(
        proposal_id="prop_100",
        parent_model_version="v1.0.0",
        proposed_transitions=[{"source": "q0", "symbol": "CAPABILITIES", "target": "q_capabilities"}],
        evidence_ids=["fact_100"],
        reason="Repeated observation",
    )

    res = InvestigationResult(
        investigation_id="INV-100",
        event_type="MODEL_EVOLUTION",
        classification="MODEL_EVOLUTION_CANDIDATE",
        observed_facts=[obs],
        ai_hypotheses=[hyp],
        proposal=prop,
    )

    assert res.investigation_id == "INV-100"
    assert res.observed_facts[0].fact_id == "fact_100"
    assert res.ai_hypotheses[0].hypothesis_id == "hyp_100"
    assert res.proposal.proposal_id == "prop_100"
