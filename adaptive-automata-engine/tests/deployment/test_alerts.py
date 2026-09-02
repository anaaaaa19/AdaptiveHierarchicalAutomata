"""
Tests for AlertManager deduplication and lifecycle state.
"""

from adaptive_automata.analysis.escalation import AnalysisStatus
from adaptive_automata.deployment.alerts.manager import AlertManager, AlertState
from adaptive_automata.security.assessment import BehavioralClassification, ReasonCode, SecurityAssessment, SeverityLevel


def test_alert_manager_deduplication():
    am = AlertManager(dedup_window_sec=60.0)
    sec1 = SecurityAssessment("s1", "v1.0.0", AnalysisStatus.STRUCTURAL_VIOLATION, "NOVEL", "INVALID", BehavioralClassification.POTENTIAL_ATTACK, SeverityLevel.HIGH, 0.9, [ReasonCode.STRUCTURAL_VIOLATION])
    sec2 = SecurityAssessment("s1", "v1.0.0", AnalysisStatus.STRUCTURAL_VIOLATION, "NOVEL", "INVALID", BehavioralClassification.POTENTIAL_ATTACK, SeverityLevel.HIGH, 0.9, [ReasonCode.STRUCTURAL_VIOLATION])

    alt1 = am.process_security_assessment(sec1, symbol="BAD_SYM", state="q0")
    alt2 = am.process_security_assessment(sec2, symbol="BAD_SYM", state="q0")

    assert alt1 is not None
    assert alt2 is not None
    assert alt1.alert_id == alt2.alert_id
    assert alt2.count == 2

    updated = am.update_alert_status(alt1.alert_id, AlertState.ACKNOWLEDGED)
    assert am.get_alert_status(alt1.alert_id) == AlertState.ACKNOWLEDGED
