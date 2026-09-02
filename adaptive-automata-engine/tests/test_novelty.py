"""Unit tests for NoveltyDetector."""

from adaptive_automata.analysis.escalation import AnalysisLevel, AnalysisResult, AnalysisStatus
from adaptive_automata.core import State, MealyMachine
from adaptive_automata.models import ModelSource, VersionedProtocolModel
from adaptive_automata.adaptation.novelty import NoveltyDetector, NoveltyStatus


def create_mock_model() -> VersionedProtocolModel[str, str]:
    s0 = State("q0", is_initial=True)
    mealy = MealyMachine[str, str]("TestModel")
    mealy.add_state(s0)
    return VersionedProtocolModel[str, str](
        model_id="TestModel",
        version="v1.0.0",
        source=ModelSource.ACTIVE_HYBRID,
        mealy_machine=mealy,
    )


def test_novelty_detector_known():
    detector = NoveltyDetector()
    model = create_mock_model()

    known_analysis = AnalysisResult(
        status=AnalysisStatus.KNOWN,
        level_used=AnalysisLevel.DFA_MEALY,
        reason="Recognized",
        state="q0",
        symbol="SYN",
        confidence_score=1.0,
        model_version="v1.0.0",
    )
    result = detector.detect_novelty(known_analysis, model)
    assert result.status == NoveltyStatus.KNOWN
    assert result.state == "q0"
    assert result.symbol == "SYN"


def test_novelty_detector_novel():
    detector = NoveltyDetector()
    model = create_mock_model()

    novel_analysis = AnalysisResult(
        status=AnalysisStatus.NOVEL_BUT_VALID,
        level_used=AnalysisLevel.PDA,
        reason="Validated by Pushdown Automaton",
        state="q0",
        symbol="NESTED_OPEN",
        confidence_score=0.9,
        model_version="v1.0.0",
    )
    result = detector.detect_novelty(novel_analysis, model)
    assert result.status == NoveltyStatus.NOVEL
    assert result.hierarchical_level == AnalysisLevel.PDA


def test_novelty_detector_unknown():
    detector = NoveltyDetector()
    model = create_mock_model()

    unknown_analysis = AnalysisResult(
        status=AnalysisStatus.UNKNOWN,
        level_used=AnalysisLevel.CFG,
        reason="CFG parse failed",
        state="q0",
        symbol="GARBAGE",
        confidence_score=0.0,
        model_version="v1.0.0",
    )
    result = detector.detect_novelty(unknown_analysis, model)
    assert result.status == NoveltyStatus.UNKNOWN
