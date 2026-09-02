"""Unit tests for SecurityInvestigationAgent."""

from adaptive_automata.agents import SecurityInvestigationAgent


def test_security_investigation_agent_advisory():
    agent = SecurityInvestigationAgent()
    res = agent.run_investigation({
        "session_id": "sec_sess_99",
        "reason_codes": ["UNKNOWN_TRANSITION", "STRUCTURAL_VIOLATION"],
        "severity": "HIGH",
    })

    assert res.event_type == "SECURITY_ALERT_INVESTIGATION"
    assert res.classification == "SUSPICIOUS_PROTOCOL_BEHAVIOR"
    assert res.severity_recommendation == "HIGH"
    assert "Authoritative Severity: HIGH" in res.explanation
