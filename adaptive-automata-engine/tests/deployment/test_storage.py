"""
Tests for SQLiteEventStore and InMemoryEventStore implementations.
"""

from adaptive_automata.analysis.escalation import AnalysisLevel, AnalysisResult, AnalysisStatus
from adaptive_automata.deployment.pipeline.events import ProtocolEvent
from adaptive_automata.deployment.storage.sqlite import InMemoryEventStore
from adaptive_automata.security.assessment import BehavioralClassification, ReasonCode, SecurityAssessment, SeverityLevel


def test_in_memory_event_store():
    store = InMemoryEventStore()
    an_res = AnalysisResult(AnalysisStatus.KNOWN, AnalysisLevel.DFA_MEALY, "Fast path", "q0", "SYN", 1.0, "v1.0.0")
    sec_assess = SecurityAssessment("s1", "v1.0.0", AnalysisStatus.KNOWN, "KNOWN", "VALID", BehavioralClassification.KNOWN, SeverityLevel.BENIGN, 0.0, [])
    evt = ProtocolEvent("e1", "s1", "TCP", "INBOUND", "SYN", "q0", "v1.0.0", an_res, sec_assess)

    store.store_event(evt)
    assert store.get_event_count() == 1

    retrieved = store.get_event("e1")
    assert retrieved is not None
    assert retrieved.session_id == "s1"
    assert retrieved.symbol == "SYN"
