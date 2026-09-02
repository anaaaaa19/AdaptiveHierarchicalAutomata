"""Unit tests for AgentAuditLogger."""

from adaptive_automata.agents import AgentAuditLogger


def test_agent_audit_logger_event_logging():
    logger = AgentAuditLogger()
    evt = logger.log_event(
        investigation_id="INV-AUDIT-1",
        agent_name="ProtocolAnalystAgent",
        action_type="RUN_TOOL",
        tool_name="run_dfa_analysis",
        decision="FACT_RECORDED",
    )

    assert evt.audit_id == "AUD-000001"
    assert evt.investigation_id == "INV-AUDIT-1"
    assert evt.agent_name == "ProtocolAnalystAgent"

    events = logger.get_events_for_investigation("INV-AUDIT-1")
    assert len(events) == 1
