"""Unit tests for Zero-Day Unseen Behavior Detection."""

from adaptive_automata.analysis import HierarchicalAnalyzer
from adaptive_automata.core import State, MealyMachine
from adaptive_automata.models import ModelSource, VersionedProtocolModel
from adaptive_automata.adaptation import NoveltyDetector
from adaptive_automata.security import BehavioralAnalyzer, BehavioralClassification, SyntheticDatasetGenerator


def create_baseline_model() -> VersionedProtocolModel[str, str]:
    s0 = State("q0", is_initial=True)
    s1 = State("q1")
    mealy = MealyMachine[str, str]("ZeroDayProto")
    mealy.add_transition(s0, "SYN", s1, "SEND_SYN_ACK")
    mealy.validate()

    return VersionedProtocolModel[str, str](
        model_id="ZeroDayProto",
        version="v1.0.0",
        source=ModelSource.ACTIVE_HYBRID,
        mealy_machine=mealy,
    )


def test_zero_day_unseen_behavior_detection():
    model = create_baseline_model()
    analyzer = HierarchicalAnalyzer(fast_path_model=model)
    novelty_det = NoveltyDetector()
    sec_analyzer = BehavioralAnalyzer()

    # Generate synthetic zero-day attack sessions (withheld during training)
    zero_day_sessions = SyntheticDatasetGenerator.generate_unseen_zero_day_deviations(count=3)

    detected_count = 0
    for sess, is_attack in zero_day_sessions:
        an_res = analyzer.analyze_session(sess)
        nov_res = novelty_det.detect_novelty(an_res, model)
        assessment = sec_analyzer.analyze_security(sess, an_res, nov_res)

        if assessment.behavioral_classification in (BehavioralClassification.POTENTIAL_ATTACK, BehavioralClassification.SUSPICIOUS, BehavioralClassification.PROTOCOL_VIOLATION):
            detected_count += 1

    # Unseen Zero-Day Attack Detection Rate MUST be 100% on unseen attack sequences!
    assert detected_count == len(zero_day_sessions)
