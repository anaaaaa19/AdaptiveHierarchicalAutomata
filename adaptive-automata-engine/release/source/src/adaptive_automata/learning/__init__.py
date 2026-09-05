"""Active and Passive Automata Learning package based on L* and trace inference."""

from .observation_table import ObservationTable
from .equivalence import (
    EquivalenceOracle,
    RandomSequenceEquivalenceOracle,
    WMethodEquivalenceOracle,
    ExactMealyEquivalenceOracle,
)
from .lstar import LStarLearner, LearningResult
from .confidence import ConfidenceLevel, TransitionMetadata, ConfidenceCalculator
from .passive import PassiveInferenceEngine
from .hybrid import HybridActiveLearner
from .evolution import ProtocolEvolutionAnalyzer, ProtocolEvolutionResult

__all__ = [
    "ObservationTable",
    "EquivalenceOracle",
    "RandomSequenceEquivalenceOracle",
    "WMethodEquivalenceOracle",
    "ExactMealyEquivalenceOracle",
    "LStarLearner",
    "LearningResult",
    "ConfidenceLevel",
    "TransitionMetadata",
    "ConfidenceCalculator",
    "PassiveInferenceEngine",
    "HybridActiveLearner",
    "ProtocolEvolutionAnalyzer",
    "ProtocolEvolutionResult",
]
