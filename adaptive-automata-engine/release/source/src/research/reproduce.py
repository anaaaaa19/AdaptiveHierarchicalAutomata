"""
Independent Reproduction and Metric Comparison Utility.
Executable via: python -m research.reproduce
"""

import argparse
import json
import os
import sys
from typing import Dict

from adaptive_automata.evaluation.config import load_experiment_config
from adaptive_automata.evaluation.runner import ExperimentRunner


def compare_results(original_path: str, reproduced_path: str, tolerance: float = 0.05) -> Dict:
    with open(original_path, "r", encoding="utf-8") as f:
        orig_data = json.load(f)

    with open(reproduced_path, "r", encoding="utf-8") as f:
        repro_data = json.load(f)

    orig_summary = orig_data.get("summary", {})
    repro_summary = repro_data.get("summary", {})

    comparison_report = {
        "original_file": original_path,
        "reproduced_file": reproduced_path,
        "metrics_compared": [],
        "overall_status": "PASS",
    }

    print("\n==================================================")
    print("INDEPENDENT REPRODUCTION METRIC COMPARISON AUDIT")
    print("==================================================")
    print(f"{'Model':<20} | {'Metric':<25} | {'Orig Mean':<10} | {'Repro Mean':<10} | {'Abs Diff':<10} | {'Status':<15}")
    print("-" * 100)

    has_fail = False
    has_minor = False

    for model_name, metrics_dict in orig_summary.items():
        if model_name not in repro_summary:
            print(f"Warning: Model '{model_name}' missing in reproduced results.")
            continue

        for metric_name, orig_stats in metrics_dict.items():
            if metric_name not in repro_summary[model_name]:
                continue

            orig_mean = orig_stats["mean"]
            repro_mean = repro_summary[model_name][metric_name]["mean"]
            abs_diff = abs(orig_mean - repro_mean)

            # Determine tolerance context
            metric_tol = tolerance
            if "latency" in metric_name:
                metric_tol = 5.0  # 5ms tolerance for latency jitter

            if abs_diff <= metric_tol:
                status = "PASS"
            elif abs_diff <= metric_tol * 2:
                status = "MINOR_VARIATION"
                has_minor = True
            else:
                status = "FAIL"
                has_fail = True

            entry = {
                "model": model_name,
                "metric": metric_name,
                "original_mean": orig_mean,
                "reproduced_mean": repro_mean,
                "absolute_difference": round(abs_diff, 6),
                "tolerance": metric_tol,
                "status": status,
            }
            comparison_report["metrics_compared"].append(entry)

            print(f"{model_name:<20} | {metric_name:<25} | {orig_mean:<10.4f} | {repro_mean:<10.4f} | {abs_diff:<10.4f} | {status:<15}")

    if has_fail:
        comparison_report["overall_status"] = "FAIL"
    elif has_minor:
        comparison_report["overall_status"] = "MINOR_VARIATION"

    print("-" * 100)
    print(f"OVERALL REPRODUCTION AUDIT STATUS: {comparison_report['overall_status']}")
    print("==================================================\n")

    return comparison_report


def main():
    parser = argparse.ArgumentParser(description="Independent Reproduction & Comparison Tool")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run reproduction experiment")
    run_parser.add_argument("--config", type=str, required=True, help="Path to experiment config YAML")

    comp_parser = subparsers.add_parser("compare", help="Compare original vs reproduced result JSONs")
    comp_parser.add_argument("--original", type=str, required=True, help="Path to original result JSON")
    comp_parser.add_argument("--reproduced", type=str, required=True, help="Path to reproduced result JSON")
    comp_parser.add_argument("--tolerance", type=float, default=0.05, help="Acceptance tolerance threshold")

    args = parser.parse_args()

    if args.command == "run":
        config = load_experiment_config(args.config)
        runner = ExperimentRunner(config)
        results = runner.run()
        print(f"Reproduction run completed for experiment: {config.name}")
    elif args.command == "compare":
        compare_results(args.original, args.reproduced, tolerance=args.tolerance)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
