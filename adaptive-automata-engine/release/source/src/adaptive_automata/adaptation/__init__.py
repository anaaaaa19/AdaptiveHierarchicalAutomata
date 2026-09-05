"""Adaptive Model Management Subsystem package."""

from .config import AdaptationConfig
from .lifecycle import AdaptationState, AdaptationStateTracker, InvalidStateTransitionError
from .novelty import NoveltyStatus, NoveltyResult, NoveltyDetector
from .evidence import BehaviorEvidence, EvidenceStore
from .drift import DriftConfig, DriftResult, ConceptDriftDetector
from .candidate import AdaptationEvent, CandidateModel
from .validator import ValidationResult, FormalValidator
from .policy import EvidenceStrength, AdaptationPolicy
from .updater import ModelUpdater
from .rollback import RollbackEvent, ModelRollbackManager
from .engine import AdaptiveModelEngine

__all__ = [
    "AdaptationConfig",
    "AdaptationState",
    "AdaptationStateTracker",
    "InvalidStateTransitionError",
    "NoveltyStatus",
    "NoveltyResult",
    "NoveltyDetector",
    "BehaviorEvidence",
    "EvidenceStore",
    "DriftConfig",
    "DriftResult",
    "ConceptDriftDetector",
    "AdaptationEvent",
    "CandidateModel",
    "ValidationResult",
    "FormalValidator",
    "EvidenceStrength",
    "AdaptationPolicy",
    "ModelUpdater",
    "RollbackEvent",
    "ModelRollbackManager",
    "AdaptiveModelEngine",
]
