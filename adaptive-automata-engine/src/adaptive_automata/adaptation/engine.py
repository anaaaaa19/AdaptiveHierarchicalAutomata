"""
Adaptive Model Engine Top-Level Orchestrator.

Orchestrates the formal adaptation flow:
  AnalysisResult -> NoveltyDetector -> EvidenceStore -> ConceptDriftDetector -> AdaptationPolicy -> CandidateModel -> FormalValidator -> ModelUpdater -> ModelRollbackManager.
"""

from typing import Sequence

from adaptive_automata.analysis.analyzer import HierarchicalAnalyzer
from adaptive_automata.analysis.escalation import AnalysisResult
from adaptive_automata.models.versioning import ModelRegistry, VersionedProtocolModel
from adaptive_automata.protocol.session import ProtocolSession
from adaptive_automata.protocol.tokenizer import BaseMessageTokenizer
from .candidate import CandidateModel
from .drift import ConceptDriftDetector, DriftConfig
from .evidence import BehaviorEvidence, EvidenceStore
from .lifecycle import AdaptationState, AdaptationStateTracker
from .novelty import NoveltyDetector, NoveltyResult, NoveltyStatus
from .policy import AdaptationPolicy
from .rollback import ModelRollbackManager
from .updater import ModelUpdater
from .validator import FormalValidator


class AdaptiveModelEngine:
    """
    Top-level Orchestrator for formal, safety-guaranteed protocol model adaptation.
    """

    def __init__(
        self,
        analyzer: HierarchicalAnalyzer,
        registry: ModelRegistry,
        policy: AdaptationPolicy | None = None,
        drift_config: DriftConfig | None = None,
    ) -> None:
        self.analyzer = analyzer
        self.registry = registry
        self.novelty_detector = NoveltyDetector()
        self.evidence_store = EvidenceStore()
        self.drift_detector = ConceptDriftDetector(drift_config)
        self.policy = policy or AdaptationPolicy()
        self.validator = FormalValidator()
        self.updater = ModelUpdater(registry)
        self.rollback_manager = ModelRollbackManager(registry)

        # Set active model pointer in rollback manager
        m_id = analyzer.fast_path_model.model_id
        m_ver = analyzer.fast_path_model.version
        self.rollback_manager.set_active_version(m_id, m_ver)

    @property
    def active_model(self) -> VersionedProtocolModel[str, str]:
        """Retrieve current active VersionedProtocolModel."""
        m_id = self.analyzer.fast_path_model.model_id
        return self.rollback_manager.get_active_model(m_id)

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
        # Ensure analyzer uses latest active model
        active_m = self.active_model
        self.analyzer.fast_path_model = active_m

        # Step 1: Hierarchical Formal Analysis
        analysis_res = self.analyzer.analyze_session(session, tokenizer=tokenizer)

        # Step 2: Novelty Detection
        novelty_res = self.novelty_detector.detect_novelty(analysis_res, active_m)

        if novelty_res.status == NoveltyStatus.KNOWN:
            return analysis_res, novelty_res, AdaptationState.OBSERVED

        # Step 3: Lifecycle Initialization & Evidence Accumulation
        tracker = AdaptationStateTracker(AdaptationState.OBSERVED)
        tracker.transition_to(AdaptationState.NOVEL)

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

        # Step 4: Adaptation Policy Evaluation (Poisoning Defense)
        should_propose, reason = self.policy.should_propose_candidate(ev)
        if not should_propose:
            tracker.transition_to(AdaptationState.REJECTED)
            return analysis_res, novelty_res, tracker.current_state

        # Step 5: Candidate Model Generation
        tracker.transition_to(AdaptationState.CANDIDATE)

        cand_id = f"cand_{ev.behavior_id.replace(':', '_')}_{ev.observation_count}"
        proposed_trans = [(ev.source_state, ev.input_symbol, proposed_target_state, proposed_output_symbol)]

        candidate = CandidateModel(
            candidate_id=cand_id,
            parent_version=active_m.version,
            proposed_transitions=proposed_trans,
            supporting_evidence=ev,
            lifecycle_state=tracker.current_state,
        )

        # Step 6: Formal Regression Validation
        tracker.transition_to(AdaptationState.VALIDATING)
        candidate.lifecycle_state = tracker.current_state

        val_res = self.validator.validate_candidate(candidate, active_m)
        if not val_res.valid:
            tracker.transition_to(AdaptationState.REJECTED)
            candidate.lifecycle_state = tracker.current_state
            candidate.validation_notes.extend(val_res.errors)
            return analysis_res, novelty_res, tracker.current_state

        # Step 7: Validation Passed -> Activation
        tracker.transition_to(AdaptationState.VALIDATED)
        candidate.lifecycle_state = tracker.current_state

        # Determine next version string
        v_clean = active_m.version.split("-")[0].replace("v", "")
        parts = v_clean.split(".")
        major = int(parts[0]) if parts else 1
        new_version_str = f"v{major + 1}.0.0-adapted"

        new_model = self.updater.apply_update(candidate, active_m, new_version_str)

        tracker.transition_to(AdaptationState.ACTIVATED)
        candidate.lifecycle_state = tracker.current_state

        # Update active version pointer
        self.rollback_manager.set_active_version(active_m.model_id, new_version_str)
        self.analyzer.fast_path_model = new_model

        return analysis_res, novelty_res, tracker.current_state
