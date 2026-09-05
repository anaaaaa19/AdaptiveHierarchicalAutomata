"""
Unit tests for ResearchReportGenerator and EvaluationPlotter.
"""

import os
from adaptive_automata.evaluation.plots import EvaluationPlotter
from adaptive_automata.evaluation.reporter import ResearchReportGenerator


def test_report_and_plot_generation(tmp_path):
    plot_dir = str(tmp_path / "plots")
    report_dir = str(tmp_path / "reports")

    mock_summary = {
        "static_dfa": {
            "precision": {"mean": 0.85, "std_dev": 0.02},
            "recall": {"mean": 0.75, "std_dev": 0.03},
            "f1": {"mean": 0.796, "std_dev": 0.025},
            "fpr": {"mean": 0.05, "std_dev": 0.01},
            "dfa_resolution_pct": {"mean": 100.0, "std_dev": 0.0},
            "pda_escalation_pct": {"mean": 0.0, "std_dev": 0.0},
            "cfg_escalation_pct": {"mean": 0.0, "std_dev": 0.0},
            "mean_latency_ms": {"mean": 0.05, "std_dev": 0.005},
            "p95_latency_ms": {"mean": 0.08, "std_dev": 0.008},
            "rejection_rate": {"mean": 0.0, "std_dev": 0.0},
        },
        "proposed": {
            "precision": {"mean": 0.95, "std_dev": 0.01},
            "recall": {"mean": 0.94, "std_dev": 0.01},
            "f1": {"mean": 0.945, "std_dev": 0.01},
            "fpr": {"mean": 0.01, "std_dev": 0.005},
            "dfa_resolution_pct": {"mean": 82.0, "std_dev": 1.2},
            "pda_escalation_pct": {"mean": 12.0, "std_dev": 0.8},
            "cfg_escalation_pct": {"mean": 6.0, "std_dev": 0.4},
            "mean_latency_ms": {"mean": 0.12, "std_dev": 0.01},
            "p95_latency_ms": {"mean": 0.25, "std_dev": 0.02},
            "rejection_rate": {"mean": 1.0, "std_dev": 0.0},
        },
    }

    mock_data = {
        "experiment": "unit_test_report",
        "timestamp": "2026-09-05T00:00:00Z",
        "seeds": [1, 2, 3],
        "configuration": {"dataset_params": {"protocol": "toy"}},
        "summary": mock_summary,
    }

    # Test plotter
    plotter = EvaluationPlotter(output_dir=plot_dir)
    plots = plotter.generate_all_plots(mock_data)
    assert len(plots) >= 4
    for p in plots:
        assert os.path.exists(p)

    # Test report generator
    reporter = ResearchReportGenerator(output_dir=report_dir)
    rep_path = reporter.generate_report(mock_data)
    assert os.path.exists(rep_path)
    with open(rep_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Research Report: Unit Test Report" in content
        assert "proposed" in content
