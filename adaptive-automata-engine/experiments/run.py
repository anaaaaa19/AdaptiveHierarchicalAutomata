"""
CLI Entrypoint for Experiment Execution, Benchmarks, Plotting, and Report Generation.
"""

import argparse
import glob
import os
import sys

# Ensure src is in python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from adaptive_automata.evaluation.config import load_experiment_config, ExperimentConfig
from adaptive_automata.evaluation.runner import ExperimentRunner
from adaptive_automata.evaluation.plots import EvaluationPlotter
from adaptive_automata.evaluation.reporter import ResearchReportGenerator


def run_single_config(config_path: str, generate_plots: bool = True, generate_report: bool = True):
    print(f"\n==================================================")
    print(f"Executing Experiment Config: {config_path}")
    print(f"==================================================")

    config: ExperimentConfig = load_experiment_config(config_path)
    runner = ExperimentRunner(config)
    results = runner.run()

    print(f"Successfully executed experiment '{config.name}' across seeds: {config.seeds}")

    if generate_plots:
        plotter = EvaluationPlotter(output_dir=os.path.join("experiments", "plots"))
        plots = plotter.generate_all_plots(results)
        print(f"Generated {len(plots)} publication figures in experiments/plots/")

    if generate_report:
        reporter = ResearchReportGenerator(output_dir=os.path.join("experiments", "reports"))
        report_path = reporter.generate_report(results)
        print(f"Generated research report: {report_path}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Adaptive Automata Engine Phase 9 Experiment Runner")
    parser.add_argument("--config", type=str, help="Path to experiment configuration YAML/JSON file")
    parser.add_argument("--all", action="store_true", help="Run all configuration files in configs/")
    parser.add_argument("--no-plots", action="store_true", help="Disable figure generation")
    parser.add_argument("--no-report", action="store_true", help="Disable research report generation")

    args = parser.parse_args()

    if args.all:
        config_files = glob.glob("configs/*.yaml") + glob.glob("configs/*.yml")
        if not config_files:
            print("No YAML configs found in configs/ directory.")
            return

        for cfg_file in config_files:
            run_single_config(
                cfg_file,
                generate_plots=not args.no_plots,
                generate_report=not args.no_report,
            )
    elif args.config:
        run_single_config(
            args.config,
            generate_plots=not args.no_plots,
            generate_report=not args.no_report,
        )
    else:
        # Default run with baseline comparison config if no argument specified
        default_cfg = os.path.join("configs", "baseline_comparison.yaml")
        if os.path.exists(default_cfg):
            run_single_config(
                default_cfg,
                generate_plots=not args.no_plots,
                generate_report=not args.no_report,
            )
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
