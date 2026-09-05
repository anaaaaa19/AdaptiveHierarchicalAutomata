"""
Security Layer Configuration.

Provides SecurityConfig container to manage configurable parameters across cybersecurity assessment,
session risk aggregation, alerts, and evaluation.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class SecurityConfig:
    """
    Configuration parameters for the Phase 6 Cybersecurity Layer.
    """
    risk_weights: dict[str, float] = field(default_factory=lambda: {
        "unknown_transition": 0.2,
        "structural_violation": 0.4,
        "invalid_state_sequence": 0.3,
        "unexpected_nesting": 0.3,
        "repeated_deviation": 0.25,
        "poisoning_suspected": 0.5,
    })
    low_severity_threshold: float = 0.2
    medium_severity_threshold: float = 0.5
    high_severity_threshold: float = 0.75
    repetition_threshold: int = 3
    session_timeout_seconds: float = 300.0

    def __repr__(self) -> str:
        return (
            f"SecurityConfig(low_thresh={self.low_severity_threshold}, "
            f"med_thresh={self.medium_severity_threshold}, "
            f"high_thresh={self.high_severity_threshold}, "
            f"repeat_thresh={self.repetition_threshold})"
        )
