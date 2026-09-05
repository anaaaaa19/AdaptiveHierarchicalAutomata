"""
Integration tests for ExperimentRunner end-to-end multi-seed execution and JSON auditing.
"""

import os
from adaptive_automata.evaluation.config import ExperimentConfig
from adaptive_automata.evaluation.runner import ExperimentRunner


def test_experiment_runner_execution(tmp_path):
    out_dir = str(tmp_path / "results")

    config = ExperimentConfig(
        name="test_run",
        seeds=[1, 2],
        dataset_params={
            "protocol": "toy_protocol",
            "train_size": 50,
            "validation_size": 10,
            "test_size": 20,
        },
        models=["static_dfa", "proposed"],
        output_dir=out_dir,
    )

    runner = ExperimentRunner(config)
    results = runner.run()

    assert results["experiment"] == "test_run"
    assert "static_dfa" in results["summary"]
    assert "proposed" in results["summary"]

    res_file = os.path.join(out_dir, "test_run_results.json")
    assert os.path.exists(res_file)
