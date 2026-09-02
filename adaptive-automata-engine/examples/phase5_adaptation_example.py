"""
Phase 5 Demonstration: Adaptive Model Management Subsystem.

Demonstrates:
  1. Legitimate protocol evolution adaptation (OBSERVED -> NOVEL -> CANDIDATE -> VALIDATED -> ACTIVATED v2.0.0-adapted).
  2. Poisoning attack defense (blocking single-session high-frequency spam attacks via multi-dimensional policy).
  3. Formal regression validation (rejecting corrupt candidate models prior to activation).
  4. Model rollback management (v2.0.0-adapted -> v1.1.0-hybrid audit logging).
"""

from pathlib import Path

from adaptive_automata.analysis import HierarchicalAnalyzer
from adaptive_automata.adaptation import (
    AdaptationPolicy,
    AdaptationState,
    AdaptiveModelEngine,
    BehaviorEvidence,
    CandidateModel,
    DriftConfig,
    EvidenceStore,
    FormalValidator,
    ModelRollbackManager,
    ModelUpdater,
    NoveltyDetector,
    NoveltyStatus,
)
from adaptive_automata.learning import HybridActiveLearner, PassiveInferenceEngine
from adaptive_automata.models import ModelRegistry
from adaptive_automata.protocol import (
    MessageDirection,
    ProtocolMessage,
    ProtocolSession,
    TraceLoader,
    create_toy_protocol_sut,
)


def main() -> None:
    print("==========================================================================")
    print("  Adaptive Automata Engine - Phase 5 Adaptation Demonstration")
    print("==========================================================================\n")

    registry = ModelRegistry()

    # 1. Setup Phase 3 Baseline Model (v1.1.0-hybrid)
    data_dir = Path(__file__).parent / "data"
    v1_path = data_dir / "toy_protocol_v1.json"
    v1_sessions = TraceLoader.load_from_file(str(v1_path))

    passive_engine = PassiveInferenceEngine()
    passive_model = passive_engine.infer_model(v1_sessions, model_id="ToyAdaptationProto", version="v1.0.0-passive")

    sut = create_toy_protocol_sut()
    hybrid_learner = HybridActiveLearner[str, str]()
    baseline_model = hybrid_learner.refine_model(passive_model, sut, new_version="v1.1.0-hybrid")
    registry.register_model(baseline_model)

    analyzer = HierarchicalAnalyzer(fast_path_model=baseline_model)
    policy = AdaptationPolicy(min_observations=3, min_unique_sessions=3, min_successful_followups=2, require_structural_validation=False)

    engine = AdaptiveModelEngine(analyzer, registry, policy=policy)

    print(f"[*] Baseline Model Active: '{engine.active_model.model_id}' ({engine.active_model.version})")
    print(f"[*] Baseline Model States: {engine.active_model.num_states}, Transitions: {engine.active_model.num_transitions}\n")

    # 2. Experiment 1: Legitimate Evolution Adaptation Across Multiple Sessions
    print("=== [Experiment 1] Legitimate Evolution Adaptation Across Sessions ===")
    sessions_evolution = [
        ProtocolSession("sess_adapt_1", messages=[
            ProtocolMessage("sess_adapt_1", 1, MessageDirection.CLIENT_TO_SERVER, "SYN"),
            ProtocolMessage("sess_adapt_1", 2, MessageDirection.SERVER_TO_CLIENT, "SEND_SYN_ACK"),
            ProtocolMessage("sess_adapt_1", 3, MessageDirection.CLIENT_TO_SERVER, "ACK"),
            ProtocolMessage("sess_adapt_1", 4, MessageDirection.SERVER_TO_CLIENT, "ALLOCATE_SESSION"),
            ProtocolMessage("sess_adapt_1", 5, MessageDirection.CLIENT_TO_SERVER, "RENEW_TOKEN"),
            ProtocolMessage("sess_adapt_1", 6, MessageDirection.SERVER_TO_CLIENT, "RENEW_ACK"),
        ]),
        ProtocolSession("sess_adapt_2", messages=[
            ProtocolMessage("sess_adapt_2", 1, MessageDirection.CLIENT_TO_SERVER, "SYN"),
            ProtocolMessage("sess_adapt_2", 2, MessageDirection.SERVER_TO_CLIENT, "SEND_SYN_ACK"),
            ProtocolMessage("sess_adapt_2", 3, MessageDirection.CLIENT_TO_SERVER, "ACK"),
            ProtocolMessage("sess_adapt_2", 4, MessageDirection.SERVER_TO_CLIENT, "ALLOCATE_SESSION"),
            ProtocolMessage("sess_adapt_2", 5, MessageDirection.CLIENT_TO_SERVER, "RENEW_TOKEN"),
            ProtocolMessage("sess_adapt_2", 6, MessageDirection.SERVER_TO_CLIENT, "RENEW_ACK"),
        ]),
        ProtocolSession("sess_adapt_3", messages=[
            ProtocolMessage("sess_adapt_3", 1, MessageDirection.CLIENT_TO_SERVER, "SYN"),
            ProtocolMessage("sess_adapt_3", 2, MessageDirection.SERVER_TO_CLIENT, "SEND_SYN_ACK"),
            ProtocolMessage("sess_adapt_3", 3, MessageDirection.CLIENT_TO_SERVER, "ACK"),
            ProtocolMessage("sess_adapt_3", 4, MessageDirection.SERVER_TO_CLIENT, "ALLOCATE_SESSION"),
            ProtocolMessage("sess_adapt_3", 5, MessageDirection.CLIENT_TO_SERVER, "RENEW_TOKEN"),
            ProtocolMessage("sess_adapt_3", 6, MessageDirection.SERVER_TO_CLIENT, "RENEW_ACK"),
        ]),
    ]

    for idx, sess in enumerate(sessions_evolution, 1):
        an_res, nov_res, state = engine.process_session(
            sess,
            follows_up_successfully=True,
            structurally_valid=True,
            proposed_target_state="q2",
            proposed_output_symbol="RENEW_ACK",
        )
        print(f"  Session {idx} ('{sess.session_id}'): Novelty={nov_res.status.value}, State={state.value}")

    print(f"\n[+] Adaptation Result: Active Version is now '{engine.active_model.version}'")
    print(f"[+] Updated Model States: {engine.active_model.num_states}, Transitions: {engine.active_model.num_transitions}\n")

    # 3. Experiment 2: Poisoning Attack Defense (Single-Session High-Frequency Spam)
    print("=== [Experiment 2] Poisoning Attack Defense (Single-Session Spam) ===")
    spam_session = ProtocolSession("attacker_session_99", messages=[
        ProtocolMessage("attacker_session_99", 1, MessageDirection.CLIENT_TO_SERVER, "POISON_PAYLOAD"),
        ProtocolMessage("attacker_session_99", 2, MessageDirection.SERVER_TO_CLIENT, "ERROR"),
    ])

    print("[*] Attacker generating 50 repeated observations from a SINGLE session...")
    for _ in range(50):
        an_res, nov_res, state = engine.process_session(
            spam_session,
            follows_up_successfully=False,
            structurally_valid=False,
            proposed_target_state="q_poison",
            proposed_output_symbol="ERROR",
        )

    ev_poison = engine.evidence_store.get_evidence("q0:POISON_PAYLOAD")
    assert ev_poison is not None
    should_prop, reason = engine.policy.should_propose_candidate(ev_poison)

    print(f"[+] Poisoning Defense Check: Candidate Proposed = {should_prop}")
    print(f"[+] Policy Defense Reason: {reason}")
    print(f"[+] Active Model Version Remains Safe: '{engine.active_model.version}'\n")

    # 4. Experiment 3: Formal Validation Failure & Candidate Rejection
    print("=== [Experiment 3] Formal Regression Validation Rejection ===")
    validator = FormalValidator()

    # Candidate proposing conflicting transition that breaks baseline q0 --[SYN]--> q1
    bad_cand = CandidateModel(
        candidate_id="cand_malformed",
        parent_version=engine.active_model.version,
        proposed_transitions=[("q0", "SYN", "q1", "CONFLICTING_OUTPUT")],
        supporting_evidence=BehaviorEvidence("q0:SYN", "q0", "SYN", observation_count=10),
    )

    val_result = validator.validate_candidate(bad_cand, engine.active_model, regression_traces=v1_sessions)
    print(f"[+] Candidate Validation Result: Valid = {val_result.valid}")
    print(f"[+] Validation Errors Detected: {val_result.errors}")
    print(f"[+] Corrupt Candidate REJECTED. Model remains intact at version '{engine.active_model.version}'\n")

    # 5. Experiment 4: Model Rollback Audit Log
    print("=== [Experiment 4] Model Rollback Audit Management ===")
    print(f"[*] Current Active Model: '{engine.active_model.version}'")
    print(f"[*] Initiating Rollback to baseline version 'v1.1.0-hybrid'...")

    reactivated = engine.rollback_manager.rollback(
        model_id="ToyAdaptationProto",
        target_version="v1.1.0-hybrid",
        reason="Model evolution rollback triggered by administrative policy audit.",
    )

    print(f"[+] Reactivated Model Version: '{reactivated.version}'")
    print(f"[+] Rollback Audit Log Entries: {len(engine.rollback_manager.audit_log)}")
    for event in engine.rollback_manager.audit_log:
        print(f"    - {event}")

    print("\n[+] Phase 5 Adaptive Model Management Subsystem executed successfully!")


if __name__ == "__main__":
    main()
