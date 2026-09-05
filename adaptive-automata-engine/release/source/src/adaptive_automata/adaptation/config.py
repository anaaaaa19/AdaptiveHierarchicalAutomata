"""
Adaptation System Configuration.

Provides AdaptationConfig container to avoid hard-coded thresholds across novelty detection,
evidence accumulation, concept drift, policy evaluation, formal validation, and rollbacks.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class AdaptationConfig:
    """
    Configuration parameters for the Phase 5 Adaptive Model Management Subsystem.
    """
    evidence_window: int = 50
    minimum_observations: int = 5
    minimum_sessions: int = 3
    minimum_followups: int = 2
    drift_threshold: float = 0.2
    require_structural_validation: bool = True
    enable_rollback_on_failure: bool = True

    def __repr__(self) -> str:
        return (
            f"AdaptationConfig(obs_window={self.evidence_window}, min_obs={self.minimum_observations}, "
            f"min_sessions={self.minimum_sessions}, min_followups={self.minimum_followups}, "
            f"drift_thresh={self.drift_threshold})"
        )
