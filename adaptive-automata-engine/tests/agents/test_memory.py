"""Unit tests for AgentMemory."""

from adaptive_automata.agents import AgentMemory, InvestigationResult


def test_agent_memory_store_and_retrieve():
    memory = AgentMemory()
    res = InvestigationResult(
        investigation_id="INV-MEM-1",
        event_type="SECURITY_ALERT",
        classification="SUSPICIOUS",
    )

    memory.store_result(res)
    rec = memory.get_or_create_record("INV-MEM-1")

    assert rec.investigation_id == "INV-MEM-1"
    assert rec.final_result is not None
    assert rec.final_result.classification == "SUSPICIOUS"
