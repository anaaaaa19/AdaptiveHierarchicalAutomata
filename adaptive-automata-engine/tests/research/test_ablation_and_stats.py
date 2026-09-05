"""
Unit tests for StatisticalAnalyzer and Ablation study toggles.
"""

from adaptive_automata.evaluation.baselines import ProposedAdaptiveHierarchicalModel
from adaptive_automata.evaluation.statistics import StatisticalAnalyzer, SummaryStats


def test_statistical_analyzer():
    values = [0.80, 0.82, 0.84, 0.81, 0.83]
    stats: SummaryStats = StatisticalAnalyzer.summarize(values)

    assert abs(stats.mean - 0.82) < 1e-4
    assert stats.sample_size == 5
    assert stats.ci95_lower < stats.mean < stats.ci95_upper


def test_ablation_toggles():
    # Ablation: Disable formal validation & disable hierarchy
    model = ProposedAdaptiveHierarchicalModel(
        dfa_sequences={("HELLO", "LOGOUT")},
        pda_sequences={("HELLO", "AUTH", "LOGOUT")},
        cfg_sequences=set(),
        disable_hierarchy=True,
        disable_validation=True,
        disable_poisoning_protection=True,
    )

    # With hierarchy disabled, PDA sequence resolves as REJECT
    res = model.process_sequence(["HELLO", "AUTH", "LOGOUT"])
    assert res.escalation_level == "REJECT"
