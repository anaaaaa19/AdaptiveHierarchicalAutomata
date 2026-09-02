"""Unit tests for InvestigationPlanner."""

from adaptive_automata.agents import AgentConfig, InvestigationPlanner


def test_investigation_planner_creation():
    config = AgentConfig(max_steps=5)
    planner = InvestigationPlanner(config)

    plan = planner.create_plan("SECURITY_ALERT", "sess_500")

    assert plan.investigation_id == "INV-sess_500"
    assert plan.target_event == "SECURITY_ALERT"
    assert len(plan.steps) <= 5
    assert "retrieve_security_alert" in plan.steps
