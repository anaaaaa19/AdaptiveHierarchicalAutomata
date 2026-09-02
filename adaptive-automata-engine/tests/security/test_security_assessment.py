"""Unit tests for SecurityAssessment and ReasonCode abstractions."""

from adaptive_automata.analysis import AnalysisStatus
from adaptive_automata.adaptation import NoveltyStatus
from adaptive_automata.security import BehavioralClassification, ReasonCode, SecurityAssessment, SeverityLevel


def test_security_assessment_creation():
    assessment = SecurityAssessment(
        session_id="sess_100",
        model_version="v1.0.0",
        analysis_status=AnalysisStatus.KNOWN,
        novelty_status=NoveltyStatus.KNOWN,
        structural_status="FULLY_VALID",
        behavioral_classification=BehavioralClassification.KNOWN,
        severity=SeverityLevel.BENIGN,
        risk_score=0.0,
        reason_codes=[],
    )

    assert assessment.session_id == "sess_100"
    assert assessment.severity == SeverityLevel.BENIGN
    assert assessment.behavioral_classification == BehavioralClassification.KNOWN
    assert assessment.risk_score == 0.0


def test_reason_codes_and_high_severity():
    assessment = SecurityAssessment(
        session_id="sess_attack",
        model_version="v1.0.0",
        analysis_status=AnalysisStatus.STRUCTURAL_VIOLATION,
        novelty_status=NoveltyStatus.UNKNOWN,
        structural_status="INVALID_GRAPH",
        behavioral_classification=BehavioralClassification.POTENTIAL_ATTACK,
        severity=SeverityLevel.HIGH,
        risk_score=0.85,
        reason_codes=[ReasonCode.UNKNOWN_TRANSITION, ReasonCode.STRUCTURAL_VIOLATION],
    )

    assert assessment.severity == SeverityLevel.HIGH
    assert ReasonCode.STRUCTURAL_VIOLATION in assessment.reason_codes
    assert ReasonCode.UNKNOWN_TRANSITION in assessment.reason_codes
