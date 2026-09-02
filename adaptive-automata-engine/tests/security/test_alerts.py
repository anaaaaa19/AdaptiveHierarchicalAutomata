"""Unit tests for SecurityAlert."""

from adaptive_automata.analysis import AnalysisStatus
from adaptive_automata.adaptation import NoveltyStatus
from adaptive_automata.security import BehavioralClassification, ReasonCode, SecurityAlert, SecurityAssessment, SeverityLevel


def test_security_alert_explainable_text():
    assessment = SecurityAssessment(
        session_id="sess_alert_1",
        model_version="v1.0.0",
        analysis_status=AnalysisStatus.STRUCTURAL_VIOLATION,
        novelty_status=NoveltyStatus.UNKNOWN,
        structural_status="CFG_PARSE_FAIL",
        behavioral_classification=BehavioralClassification.POTENTIAL_ATTACK,
        severity=SeverityLevel.HIGH,
        risk_score=0.8,
        reason_codes=[ReasonCode.STRUCTURAL_VIOLATION, ReasonCode.UNKNOWN_TRANSITION],
    )

    alert = SecurityAlert.from_assessment(assessment, alert_id="alt_100", state="q0", symbol="MALFORMED_SYM", position=2, level="CFG")
    assert alert.alert_id == "alt_100"
    assert alert.severity == SeverityLevel.HIGH
    assert alert.triggering_symbol == "MALFORMED_SYM"

    exp_text = alert.to_explainable_text()
    assert "[ALERT alt_100] HIGH Severity" in exp_text
    assert "STRUCTURAL_VIOLATION" in exp_text
