"""Unit tests for BehavioralAnalyzer."""

from adaptive_automata.analysis import AnalysisLevel, AnalysisResult, AnalysisStatus
from adaptive_automata.adaptation import NoveltyResult, NoveltyStatus
from adaptive_automata.protocol import MessageDirection, ProtocolMessage, ProtocolSession
from adaptive_automata.security import BehavioralAnalyzer, BehavioralClassification, ReasonCode, SeverityLevel


def test_behavioral_analyzer_known():
    analyzer = BehavioralAnalyzer()
    sess = ProtocolSession("sess_known", messages=[ProtocolMessage("sess_known", 1, MessageDirection.CLIENT_TO_SERVER, "SYN")])

    an_res = AnalysisResult(
        status=AnalysisStatus.KNOWN,
        level_used=AnalysisLevel.DFA_MEALY,
        reason="Recognized",
        state="q1",
        symbol="SYN",
        confidence_score=1.0,
        model_version="v1.0.0",
    )
    nov_res = NoveltyResult(status=NoveltyStatus.KNOWN, state="q1", symbol="SYN", hierarchical_level=AnalysisLevel.DFA_MEALY)

    assessment = analyzer.analyze_security(sess, an_res, nov_res)
    assert assessment.severity == SeverityLevel.BENIGN
    assert assessment.behavioral_classification == BehavioralClassification.KNOWN
    assert assessment.risk_score == 0.0


def test_behavioral_analyzer_structural_violation():
    analyzer = BehavioralAnalyzer()
    sess = ProtocolSession("sess_attack", messages=[ProtocolMessage("sess_attack", 1, MessageDirection.CLIENT_TO_SERVER, "MALFORMED")])

    an_res = AnalysisResult(
        status=AnalysisStatus.STRUCTURAL_VIOLATION,
        level_used=AnalysisLevel.CFG,
        reason="CFG parse failed",
        state="q0",
        symbol="MALFORMED",
        confidence_score=0.0,
        model_version="v1.0.0",
    )
    nov_res = NoveltyResult(status=NoveltyStatus.NOVEL, state="q0", symbol="MALFORMED", hierarchical_level=AnalysisLevel.CFG)

    assessment = analyzer.analyze_security(sess, an_res, nov_res)
    assert assessment.severity in (SeverityLevel.MEDIUM, SeverityLevel.HIGH, SeverityLevel.CRITICAL)
    assert ReasonCode.STRUCTURAL_VIOLATION in assessment.reason_codes
