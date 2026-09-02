"""
Adaptive Model Engine Top-Level Orchestrator.

Orchestrates the formal adaptation flow:
  AnalysisResult -> NoveltyDetector -> EvidenceStore -> ConceptDriftDetector -> AdaptationPolicy -> CandidateModel -> FormalValidator -> ModelUpdater -> ModelRollbackManager.
Generates structured audit logs (AdaptationEvent) and telemetry metrics.
"""

from datetime import datetime, timezone
import time
from typing import Any, Sequence

from adaptive_automata.analysis.analyzer import HierarchicalAnalyzer
from adaptive_automata.analysis.escalation import AnalysisLevel, AnalysisResult, AnalysisStatus
from adaptive_automata.models.versioning import ModelRegistry, VersionedProtocolModel
from adaptive_automata.protocol.session import ProtocolSession
from adaptive_automata.protocol.tokenizer import BaseMessageTokenizer
from .candidate import AdaptationEvent, CandidateModel
from .config import AdaptationConfig
from .drift import ConceptDriftDetector, DriftConfig, DriftResult
from .evidence import BehaviorEvidence, EvidenceStore
from .lifecycle import AdaptationState, AdaptationStateTracker
from .novelty import NoveltyDetector, NoveltyResult, NoveltyStatus
from .policy import AdaptationPolicy
from .rollback import ModelRollbackManager
from .updater import ModelUpdater
from .validator import FormalValidator, ValidationResult


class AdaptiveModelEngine:
    """
    Top-level Orchestrator for formal, safety-guaranteed protocol model adaptation.
    """

    def __init__(
        self,
        analyzer: HierarchicalAnalyzer,
        registry: ModelRegistry,
        config: AdaptationConfig | None = None,
        policy: AdaptationPolicy | None = None,
    ) -> None:
        self.analyzer = analyzer
        self.registry = registry
        self.config = config or AdaptationConfig()
        self.novelty_detector = NoveltyDetector()
        self.evidence_store = EvidenceStore()
        
        drift_cfg = DriftConfig(window_size=self.config.evidence_window, threshold=self.config.drift_threshold)
        self.drift_detector = ConceptDriftDetector(drift_cfg)
        self.policy = policy or AdaptationPolicy(config=self.config)
        self.validator = FormalValidator()
        self.updater = ModelUpdater(registry)
        self.rollback_manager = ModelRollbackManager(registry)

        # Audit events log and metrics counters
        self.events_log: list[AdaptationEvent] = []
        self._history_symbols: list[str] = []

        # Telemetry metrics
        self.total_observations: int = 0
        self.known_observations: int = 0
        self.novel_observations: int = 0
        self.unique_novel_behaviors: set[str] = set()
        self.drift_events_count: int = 0
        self.candidate_models_count: int = 0
        self.accepted_candidates_count: int = 0
        self.rejected_candidates_count: int = 0
        self.validation_failures_count: int = 0
        self.dfa_resolved_count: int = 0
        self.pda_escalations_count: int = 0
        self.cfg_escalations_count: int = 0

        # Set active model pointer in rollback manager
        m_id = analyzer.fast_path_model.model_id
        m_ver = analyzer.fast_path_model.version
        self.rollback_manager.set_active_version(m_id, m_ver)

    @property
    def active_model(self) -> VersionedProtocolModel[str, str]:
        """Retrieve current active VersionedProtocolModel."""
        m_id = self.analyzer.fast_path_model.model_id
        return self.rollback_manager.get_active_model(m_id)

    def _log_event(
        self,
        session_id: str,
        event_type: str,
        state_from: str,
        state_to: str,
        explanation: str,
        evidence_summary: dict[str, Any] | None = None,
        drift_score: float | None = None,
        validation_errors: list[str] | None = None,
    ) -> AdaptationEvent:
        """Create and append a structured AdaptationEvent."""
        now_str = datetime.now(timezone.utc).isoformat()
        evt_id = f"evt_{len(self.events_log) + 1}_{int(time.time() * 1000)}"
        event = AdaptationEvent(
            event_id=evt_id,
            timestamp=now_str,
            session_id=session_id,
            event_type=event_type,
            state_from=state_from,
            state_to=state_to,
            explanation=explanation,
            evidence_summary=evidence_summary or {},
            drift_score=drift_score,
            validation_errors=validation_errors or [],
            model_version=self.active_model.version,
        )
        self.events_log.append(event)
        return event

    def process_session(
        self,
        session: ProtocolSession,
        tokenizer: BaseMessageTokenizer | None = None,
        follows_up_successfully: bool = True,
        structurally_valid: bool = True,
        proposed_target_state: str = "q_adapted",
        proposed_output_symbol: str = "ACK_ADAPTED",
    ) -> tuple[AnalysisResult, NoveltyResult, AdaptationState]:
        """
        Process a session through the complete adaptive model pipeline.

        Returns:
            Tuple of (AnalysisResult, NoveltyResult, final AdaptationState).
        """
        self.total_observations += 1

        # Ensure analyzer uses latest active model
        active_m = self.active_model
        self.analyzer.fast_path_model = active_m

        # Step 1: Hierarchical Formal Analysis
        analysis_res = self.analyzer.analyze_session(session, tokenizer=tokenizer)

        # Track Phase 4 escalations
        if analysis_res.level_used == AnalysisLevel.DFA_MEALY:
            self.dfa_resolved_count += 1
        elif analysis_res.level_used == AnalysisLevel.PDA:
            self.pda_escalations_count += 1
        elif analysis_res.level_used == AnalysisLevel.CFG:
            self.cfg_escalations_count += 1

        # Step 2: Novelty Detection
        novelty_res = self.novelty_detector.detect_novelty(analysis_res, active_m)

        if novelty_res.status == NoveltyStatus.KNOWN:
            self.known_observations += 1
            self._history_symbols.append(analysis_res.symbol)
            return analysis_res, novelty_res, AdaptationState.OBSERVED

        # Novel behavior handling
        self.novel_observations += 1
        beh_id = f"{analysis_res.state}:{analysis_res.symbol}"
        self.unique_novel_behaviors.add(beh_id)
        self._history_symbols.append(analysis_res.symbol)

        # Step 3: Lifecycle Initialization & Evidence Accumulation
        tracker = AdaptationStateTracker(AdaptationState.OBSERVED)
        tracker.transition_to(AdaptationState.NOVEL)

        self._log_event(
            session_id=session.session_id,
            event_type="NOVELTY_DETECTED",
            state_from=AdaptationState.OBSERVED.value,
            state_to=AdaptationState.NOVEL.value,
            explanation=f"Novel behavior detected at state '{analysis_res.state}' on symbol '{analysis_res.symbol}'.",
            evidence_summary={"behavior_id": beh_id, "analysis_level": analysis_res.level_used.value},
        )

        ev = self.evidence_store.record_observation(
            session_id=session.session_id,
            source_state=analysis_res.state,
            input_symbol=analysis_res.symbol,
            target_state=proposed_target_state,
            output_symbol=proposed_output_symbol,
            model_version=active_m.version,
            follows_up_successfully=follows_up_successfully,
            structurally_valid=structurally_valid,
        )

        tracker.transition_to(AdaptationState.UNDER_REVIEW)

        # Step 4: Concept Drift Detection
        drift_res: DriftResult | None = None
        if len(self._history_symbols) >= 10:
            baseline = list(active_m.mealy_machine.input_alphabet) or ["SYN", "ACK"]
            drift_res = self.drift_detector.detect_drift(self._history_symbols, baseline)
            if drift_res.detected:
                self.drift_events_count += 1

        # Step 5: Adaptation Policy Evaluation (Poisoning Defense)
        should_propose, reason = self.policy.should_propose_candidate(ev)
        if not should_propose:
            tracker.transition_to(AdaptationState.REJECTED)
            self.rejected_candidates_count += 1
            self._log_event(
                session_id=session.session_id,
                event_type="POLICY_REJECTION",
                state_from=AdaptationState.UNDER_REVIEW.value,
                state_to=AdaptationState.REJECTED.value,
                explanation=reason,
                evidence_summary={
                    "behavior_id": beh_id,
                    "observation_count": ev.observation_count,
                    "unique_sessions": ev.unique_session_count,
                    "evidence_score": ev.calculate_evidence_score(),
                },
                drift_score=drift_res.js_divergence_score if drift_res else None,
            )
            return analysis_res, novelty_res, tracker.current_state

        # Step 6: Candidate Model Generation
        tracker.transition_to(AdaptationState.CANDIDATE)
        self.candidate_models_count += 1

        cand_id = f"cand_{beh_id.replace(':', '_')}_{ev.observation_count}"
        proposed_trans = [(ev.source_state, ev.input_symbol, proposed_target_state, proposed_output_symbol)]

        candidate = CandidateModel(
            candidate_id=cand_id,
            parent_version=active_m.version,
            proposed_transitions=proposed_trans,
            supporting_evidence=ev,
            lifecycle_state=tracker.current_state,
        )

        self._log_event(
            session_id=session.session_id,
            event_type="CANDIDATE_PROPOSED",
            state_from=AdaptationState.UNDER_REVIEW.value,
            state_to=AdaptationState.CANDIDATE.value,
            explanation=f"CandidateModel '{cand_id}' proposed with transition {proposed_trans}.",
            evidence_summary={"candidate_id": cand_id, "evidence_score": ev.calculate_evidence_score()},
        )

        # Step 7: Formal Regression Validation
        tracker.transition_to(AdaptationState.VALIDATING)
        candidate.lifecycle_state = tracker.current_state

        val_res = self.validator.validate_candidate(candidate, active_m)
        if not val_res.valid:
            tracker.transition_to(AdaptationState.REJECTED)
            candidate.lifecycle_state = tracker.current_state
            candidate.validation_notes.extend(val_res.errors)
            self.validation_failures_count += 1
            self.rejected_candidates_count += 1

            self._log_event(
                session_id=session.session_id,
                event_type="FORMAL_VALIDATION_FAILED",
                state_from=AdaptationState.VALIDATING.value,
                state_to=AdaptationState.REJECTED.value,
                explanation="Candidate failed formal regression validation.",
                validation_errors=val_res.errors,
            )
            return analysis_res, novelty_res, tracker.current_state

        # Step 8: Validation Passed -> Activation
        tracker.transition_to(AdaptationState.VALIDATED)
        candidate.lifecycle_state = tracker.current_state

        v_clean = active_m.version.split("-")[0].replace("v", "")
        parts = v_clean.split(".")
        major = int(parts[0]) if parts else 1
        new_version_str = f"v{major + 1}.0.0-adapted"

        new_model = self.updater.apply_update(candidate, active_m, new_version_str)

        tracker.transition_to(AdaptationState.ACTIVATED)
        candidate.lifecycle_state = tracker.current_state
        self.accepted_candidates_count += 1

        self.rollback_manager.set_active_version(active_m.model_id, new_version_str)
        self.analyzer.fast_path_model = new_model

        self._log_event(
            session_id=session.session_id,
            event_type="MODEL_ACTIVATED",
            state_from=AdaptationState.VALIDATED.value,
            state_to=AdaptationState.ACTIVATED.value,
            explanation=f"New model version '{new_version_str}' activated cleanly.",
            evidence_summary={"candidate_id": cand_id, "new_version": new_version_str},
        )

        return analysis_res, novelty_res, tracker.current_state

    def get_metrics_summary(self) -> dict[str, Any]:
        """Retrieve aggregated experiment telemetry metrics."""
        return {
            "total_observations": self.total_observations,
            "known_observations": self.known_observations,
            "novel_observations": self.novel_observations,
            "unique_novel_behaviors": len(self.unique_novel_behaviors),
            "drift_events": self.drift_events_count,
            "candidate_models": self.candidate_models_count,
            "accepted_candidates": self.accepted_candidates_count,
            "rejected_candidates": self.rejected_candidates_count,
            "validation_failures": self.validation_failures_count,
            "active_model_version": self.active_model.version,
            "rollback_count": len(self.rollback_manager.audit_log),
            "dfa_resolved_events": self.dfa_resolved_count,
            "pda_escalations": self.pda_escalations_count,
            "cfg_escalations": self.cfg_escalations_count,
        }
