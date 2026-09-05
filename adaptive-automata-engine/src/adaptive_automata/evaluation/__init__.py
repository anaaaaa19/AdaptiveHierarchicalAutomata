"""
Evaluation and Research Framework for Adaptive Hierarchical Automata.
"""

from .baselines import (
    BaseEvaluatorModel,
    StaticDFABaseline,
    StaticHierarchicalBaseline,
    NaiveAdaptiveBaseline,
    ProposedAdaptiveHierarchicalModel,
)
from .dataset import SyntheticDatasetGenerator, ProtocolSample, DatasetSplit
from .metrics import MetricsEngine, EvaluationMetrics
from .statistics import StatisticalAnalyzer, SummaryStats
from .config import ExperimentConfig, load_experiment_config
from .runner import ExperimentRunner
from .plots import EvaluationPlotter
from .reporter import ResearchReportGenerator

__all__ = [
    "BaseEvaluatorModel",
    "StaticDFABaseline",
    "StaticHierarchicalBaseline",
    "NaiveAdaptiveBaseline",
    "ProposedAdaptiveHierarchicalModel",
    "SyntheticDatasetGenerator",
    "ProtocolSample",
    "DatasetSplit",
    "MetricsEngine",
    "EvaluationMetrics",
    "StatisticalAnalyzer",
    "SummaryStats",
    "ExperimentConfig",
    "load_experiment_config",
    "ExperimentRunner",
    "EvaluationPlotter",
    "ResearchReportGenerator",
]
