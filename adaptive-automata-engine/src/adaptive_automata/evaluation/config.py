"""
Experiment Configuration Parser and Loader.
"""

from dataclasses import dataclass, field
import json
import os
from typing import Dict, List, Optional
import yaml


@dataclass
class ExperimentConfig:
    name: str
    description: str = ""
    seeds: List[int] = field(default_factory=lambda: [42, 43, 44, 45, 46])
    dataset_params: Dict = field(
        default_factory=lambda: {
            "protocol": "toy_protocol",
            "train_size": 1000,
            "validation_size": 200,
            "test_size": 500,
            "categories": [
                "normal",
                "legitimate_evolution",
                "structural_anomaly",
                "behavioral_anomaly",
                "unseen",
                "poisoning",
            ],
        }
    )
    models: List[str] = field(
        default_factory=lambda: [
            "static_dfa",
            "static_hierarchical",
            "naive_adaptive",
            "proposed",
        ]
    )
    ablation_params: Dict[str, bool] = field(default_factory=dict)
    output_dir: str = "experiments/results"


def load_experiment_config(config_path: str) -> ExperimentConfig:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Experiment configuration file not found: {config_path}")

    ext = os.path.splitext(config_path)[1].lower()

    if ext in (".yaml", ".yml"):
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    elif ext == ".json":
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        raise ValueError(f"Unsupported configuration file extension: {ext}")

    exp_data = data.get("experiment", data)

    return ExperimentConfig(
        name=exp_data.get("name", "unnamed_experiment"),
        description=exp_data.get("description", ""),
        seeds=exp_data.get("seeds", [42, 43, 44, 45, 46]),
        dataset_params=exp_data.get("dataset", exp_data.get("dataset_params", {})),
        models=exp_data.get("models", ["static_dfa", "static_hierarchical", "naive_adaptive", "proposed"]),
        ablation_params=exp_data.get("ablation", exp_data.get("ablation_params", {})),
        output_dir=exp_data.get("output_dir", "experiments/results"),
    )
