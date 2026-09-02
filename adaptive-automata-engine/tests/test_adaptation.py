"""Unit and integration tests for Phase 5 Adaptive Model Management Subsystem."""

import pytest
from adaptive_automata.core import State, MealyMachine
from adaptive_automata.models import ModelSource, VersionedProtocolModel, ModelRegistry
from adaptive_automata.learning import ConfidenceLevel, TransitionMetadata
from adaptive_automata.analysis import HierarchicalAnalyzer, AnalysisResult, AnalysisStatus, AnalysisLevel
from adaptive_automata.protocol import ProtocolSession, ProtocolMessage, MessageDirection
from adaptive_automata.adaptation import (
    AdaptationState,
    AdaptationStateTracker,
    InvalidStateTransitionError,
    NoveltyStatus,
    NoveltyDetector,
    BehaviorEvidence,
    EvidenceStore,
    ConceptDriftDetector,
    AdaptationPolicy,
    CandidateModel,
    FormalValidator,
    ModelUpdater,
    ModelRollbackManager,
    AdaptiveModelEngine,
)


def create_sample_model(version: str = "v1.0.0") -> VersionedProtocolModel[str, str]:
    s0 = State("q0", is_initial=True)
    s1 = State("q1")
    mealy = MealyMachine[str, str]("TestProto")
    mealy.add_transition(s0, "SYN", s1, "SEND_SYN_ACK")
    mealy.validate()

    meta = {
        ("q0", "SYN"): TransitionMetadata("q0", "SYN", "q1", "SEND_SYN_ACK", 10, 1.0, ConfidenceLevel.ACTIVE_VERIFIED)
    }

    return VersionedProtocolModel[str, str](
        model_id="TestProto",
        version=version,
        source=ModelSource.ACTIVE_HYBRID,
        mealy_machine=mealy,
        transition_metadata=meta,
    )


def test_adaptation_lifecycle_legal_and_illegal_transitions():
    tracker = AdaptationStateTracker(AdaptationState.OBSERVED)
    assert tracker.current_state == AdaptationState.OBSERVED

    # Legal sequence: OBSERVED -> NOVEL -> UNDER_REVIEW -> CANDIDATE
    tracker.transition_to(AdaptationState.NOVEL)
    tracker.transition_to(AdaptationState.UNDER_REVIEW)
    tracker.transition_to(AdaptationState.CANDIDATE)
    assert tracker.current_state == AdaptationState.CANDIDATE

    # Illegal direct shortcut: CANDIDATE -> ACTIVATED must raise InvalidStateTransitionError
    with pytest.raises(InvalidStateTransitionError, match="Illegal adaptation state transition"):
        tracker.transition_to(AdaptationState.ACTIVATED)


def test_novelty_detector():
    model = create_sample_model()
    detector = NoveltyDetector()

    # Known result
    known_analysis = AnalysisResult(
        status=AnalysisStatus.KNOWN,
        level_used=AnalysisLevel.DFA_MEALY,
        reason="Recognized",
        state="q1",
        symbol="SYN",
        confidence_score=1.0,
        model_version=model.version,
    )
    nov_known = detector.detect_novelty(known_analysis, model)
    assert nov_known.status == NoveltyStatus.KNOWN

    # Novel result
    novel_analysis = AnalysisResult(
        status=AnalysisStatus.NOVEL_BUT_VALID,
        level_used=AnalysisLevel.PDA,
        reason="Validated by PDA",
        state="q1",
        symbol="RENEW_TOKEN",
        confidence_score=0.9,
        model_version=model.version,
    )
    nov_novel = detector.detect_novelty(novel_analysis, model)
    assert nov_novel.status == NoveltyStatus.NOVEL


def test_evidence_store_and_score():
    store = EvidenceStore()
    ev1 = store.record_observation("s1", "q1", "RENEW_TOKEN", "q2", "RENEW_ACK", follows_up_successfully=True)
    assert ev1.observation_count == 1
    assert ev1.unique_session_count == 1

    # Record 4 more observations across different sessions
    store.record_observation("s2", "q1", "RENEW_TOKEN", "q2", "RENEW_ACK", follows_up_successfully=True)
    store.record_observation("s3", "q1", "RENEW_TOKEN", "q2", "RENEW_ACK", follows_up_successfully=True)
    store.record_observation("s4", "q1", "RENEW_TOKEN", "q2", "RENEW_ACK", follows_up_successfully=True)
    ev5 = store.record_observation("s5", "q1", "RENEW_TOKEN", "q2", "RENEW_ACK", follows_up_successfully=True)

    assert ev5.observation_count == 5
    assert ev5.unique_session_count == 5
    assert ev5.calculate_evidence_score() > 0.5


def test_concept_drift_detector_jsd():
    drift_det = ConceptDriftDetector()
    base_syms = ["SYN", "ACK", "AUTH", "DATA", "FIN"] * 10
    recent_syms = ["RENEW_TOKEN", "RENEW_TOKEN", "RENEW_TOKEN"] * 10

    res = drift_det.detect_drift(recent_syms, base_syms)
    assert res.detected
    assert res.js_divergence_score > 0.2


def test_poisoning_resistant_adaptation_policy():
    policy = AdaptationPolicy(min_observations=5, min_unique_sessions=3, min_successful_followups=2)
    store = EvidenceStore()

    # Poisoning scenario: Single session spamming 100 times!
    for _ in range(100):
        ev = store.record_observation("attacker_session_1", "q0", "ATTACK_SYM", follows_up_successfully=False)

    should_propose, reason = policy.should_propose_candidate(ev)

    # Poisoning defense MUST block this update due to insufficient session diversity!
    assert not should_propose
    assert "Poisoning Defense" in reason or "unique_session_count" in reason or "Insufficient" in reason


def test_formal_validator_regression():
    model = create_sample_model()
    validator = FormalValidator()

    # Build valid candidate transition
    ev = BehaviorEvidence(behavior_id="q1:AUTH", source_state="q1", input_symbol="AUTH", observation_count=5)
    cand_valid = CandidateModel(
        candidate_id="cand_1",
        parent_version=model.version,
        proposed_transitions=[("q1", "AUTH", "q2", "GRANT_TOKEN")],
        supporting_evidence=ev,
    )

    val_res = validator.validate_candidate(cand_valid, model)
    assert val_res.valid

    # Build conflicting/corrupt candidate transition that breaks baseline
    cand_conflicting = CandidateModel(
        candidate_id="cand_conflict",
        parent_version=model.version,
        proposed_transitions=[("q0", "SYN", "q1", "WRONG_OUTPUT")],  # Conflicts with baseline q0 --[SYN]--> q1 / SEND_SYN_ACK
        supporting_evidence=ev,
    )

    val_conflict = validator.validate_candidate(cand_conflicting, model)
    assert not val_conflict.valid
    assert len(val_conflict.errors) > 0


def test_model_updater_and_rollback():
    registry = ModelRegistry()
    model_v1 = create_sample_model("v1.0.0")
    registry.register_model(model_v1)

    updater = ModelUpdater(registry)
    ev = BehaviorEvidence(behavior_id="q1:AUTH", source_state="q1", input_symbol="AUTH", observation_count=5)
    cand = CandidateModel(
        candidate_id="cand_1",
        parent_version="v1.0.0",
        proposed_transitions=[("q1", "AUTH", "q2", "GRANT_TOKEN")],
        supporting_evidence=ev,
        lifecycle_state=AdaptationState.VALIDATED,
    )

    model_v2 = updater.apply_update(cand, model_v1, "v2.0.0-adapted")
    assert registry.get_model("TestProto", "v2.0.0-adapted").version == "v2.0.0-adapted"

    rollback_mgr = ModelRollbackManager(registry)
    rollback_mgr.set_active_version("TestProto", "v2.0.0-adapted")
    assert rollback_mgr.get_active_version("TestProto") == "v2.0.0-adapted"

    # Rollback to v1.0.0
    reactivated = rollback_mgr.rollback("TestProto", "v1.0.0", reason="Candidate verification failed in production")
    assert reactivated.version == "v1.0.0"
    assert rollback_mgr.get_active_version("TestProto") == "v1.0.0"
    assert len(rollback_mgr.audit_log) == 1
    assert rollback_mgr.audit_log[0].from_version == "v2.0.0-adapted"
    assert rollback_mgr.audit_log[0].to_version == "v1.0.0"


def test_adaptive_model_engine_end_to_end():
    registry = ModelRegistry()
    model_v1 = create_sample_model("v1.0.0")
    registry.register_model(model_v1)

    analyzer = HierarchicalAnalyzer(fast_path_model=model_v1)
    policy = AdaptationPolicy(min_observations=2, min_unique_sessions=2, min_successful_followups=1, require_structural_validation=False)

    engine = AdaptiveModelEngine(analyzer, registry, policy=policy)

    # Sessions observing novel symbol AUTH paired with response GRANT across 2 distinct sessions
    sess1 = ProtocolSession(
        "sess_1",
        messages=[
            ProtocolMessage("sess_1", 1, MessageDirection.CLIENT_TO_SERVER, "AUTH"),
            ProtocolMessage("sess_1", 2, MessageDirection.SERVER_TO_CLIENT, "GRANT"),
        ]
    )
    sess2 = ProtocolSession(
        "sess_2",
        messages=[
            ProtocolMessage("sess_2", 1, MessageDirection.CLIENT_TO_SERVER, "AUTH"),
            ProtocolMessage("sess_2", 2, MessageDirection.SERVER_TO_CLIENT, "GRANT"),
        ]
    )

    # 1st session: accumulates evidence, under review
    _, nov1, state1 = engine.process_session(sess1, proposed_target_state="q2", proposed_output_symbol="GRANT")
    assert nov1.status in (NoveltyStatus.NOVEL, NoveltyStatus.UNKNOWN)
    assert state1 == AdaptationState.REJECTED  # Rejected initially due to min_unique_sessions < 2

    # 2nd session: satisfies session diversity policy, triggers model update!
    _, nov2, state2 = engine.process_session(sess2, proposed_target_state="q2", proposed_output_symbol="GRANT")
    assert nov2.status in (NoveltyStatus.NOVEL, NoveltyStatus.UNKNOWN)
    assert state2 == AdaptationState.ACTIVATED
    assert engine.active_model.version == "v2.0.0-adapted"
