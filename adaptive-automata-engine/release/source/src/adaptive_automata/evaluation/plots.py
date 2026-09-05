"""
Publication-Quality Figure and Plot Generator.
"""

import os
from typing import Dict

import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
import numpy as np


class EvaluationPlotter:
    """Generates publication-quality charts from experiment results."""

    def __init__(self, output_dir: str = "experiments/plots"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_all_plots(self, results_data: Dict) -> List[str]:
        generated_files = []

        summary = results_data.get("summary", {})
        models = list(summary.keys())

        if not models:
            return []

        # 1. Baseline F1 Comparison
        f1_path = self.plot_baseline_f1(summary)
        if f1_path:
            generated_files.append(f1_path)

        # 2. Precision/Recall/F1 Grouped Bar Chart
        pr_path = self.plot_precision_recall(summary)
        if pr_path:
            generated_files.append(pr_path)

        # 3. Hierarchy Escalation Distribution
        esc_path = self.plot_hierarchy_escalation(summary)
        if esc_path:
            generated_files.append(esc_path)

        # 4. Latency vs Throughput
        lat_path = self.plot_latency_performance(summary)
        if lat_path:
            generated_files.append(lat_path)

        # 5. Poisoning Resistance
        pois_path = self.plot_poisoning_resistance(summary)
        if pois_path:
            generated_files.append(pois_path)

        return generated_files

    def plot_baseline_f1(self, summary: Dict) -> str:
        models = list(summary.keys())
        f1_means = [summary[m]["f1"]["mean"] for m in models]
        f1_stds = [summary[m]["f1"]["std_dev"] for m in models]

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(models, f1_means, yerr=f1_stds, capsize=5, color=["#4C72B0", "#55A868", "#C44E52", "#8172B0"])
        ax.set_ylabel("F1 Score (Mean ± Std)")
        ax.set_title("Baseline Comparison — Detection F1 Score")
        ax.set_ylim(0, 1.1)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"{height:.2f}",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha="center", va="bottom")

        path = os.path.join(self.output_dir, "baseline_f1_comparison.png")
        plt.tight_layout()
        plt.savefig(path, dpi=300)
        plt.close()
        return path

    def plot_precision_recall(self, summary: Dict) -> str:
        models = list(summary.keys())
        prec_means = [summary[m]["precision"]["mean"] for m in models]
        rec_means = [summary[m]["recall"]["mean"] for m in models]
        f1_means = [summary[m]["f1"]["mean"] for m in models]

        x = np.arange(len(models))
        width = 0.25

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.bar(x - width, prec_means, width, label="Precision", color="#4C72B0")
        ax.bar(x, rec_means, width, label="Recall", color="#55A868")
        ax.bar(x + width, f1_means, width, label="F1 Score", color="#8172B0")

        ax.set_ylabel("Score")
        ax.set_title("Precision, Recall, and F1 across Baselines")
        ax.set_xticks(x)
        ax.set_xticklabels(models)
        ax.set_ylim(0, 1.15)
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        path = os.path.join(self.output_dir, "precision_recall_comparison.png")
        plt.tight_layout()
        plt.savefig(path, dpi=300)
        plt.close()
        return path

    def plot_hierarchy_escalation(self, summary: Dict) -> str:
        models = list(summary.keys())
        dfa_pcts = [summary[m]["dfa_resolution_pct"]["mean"] for m in models]
        pda_pcts = [summary[m]["pda_escalation_pct"]["mean"] for m in models]
        cfg_pcts = [summary[m]["cfg_escalation_pct"]["mean"] for m in models]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(models, dfa_pcts, label="DFA Resolution", color="#55A868")
        ax.bar(models, pda_pcts, bottom=dfa_pcts, label="PDA Escalation", color="#4C72B0")
        
        bottom_cfg = np.array(dfa_pcts) + np.array(pda_pcts)
        ax.bar(models, cfg_pcts, bottom=bottom_cfg, label="CFG Escalation", color="#C44E52")

        ax.set_ylabel("Resolution Percentage (%)")
        ax.set_title("Hierarchical Escalation Breakdown per Model")
        ax.set_ylim(0, 110)
        ax.legend(loc="upper right")
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        path = os.path.join(self.output_dir, "hierarchy_escalation_distribution.png")
        plt.tight_layout()
        plt.savefig(path, dpi=300)
        plt.close()
        return path

    def plot_latency_performance(self, summary: Dict) -> str:
        models = list(summary.keys())
        mean_lat = [summary[m]["mean_latency_ms"]["mean"] for m in models]
        p95_lat = [summary[m]["p95_latency_ms"]["mean"] for m in models]

        x = np.arange(len(models))
        width = 0.35

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(x - width/2, mean_lat, width, label="Mean Latency (ms)", color="#4C72B0")
        ax.bar(x + width/2, p95_lat, width, label="P95 Latency (ms)", color="#C44E52")

        ax.set_ylabel("Latency (ms)")
        ax.set_title("Processing Latency Profiles across Models")
        ax.set_xticks(x)
        ax.set_xticklabels(models)
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        path = os.path.join(self.output_dir, "latency_vs_throughput.png")
        plt.tight_layout()
        plt.savefig(path, dpi=300)
        plt.close()
        return path

    def plot_poisoning_resistance(self, summary: Dict) -> str:
        models = list(summary.keys())
        rej_rates = [summary[m]["rejection_rate"]["mean"] * 100.0 for m in models]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(models, rej_rates, color=["#C44E52", "#C44E52", "#C44E52", "#55A868"])
        ax.set_ylabel("Poisoning Block Rate (%)")
        ax.set_title("Poisoning Attempt Rejection Rate")
        ax.set_ylim(0, 110)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        path = os.path.join(self.output_dir, "poisoning_resistance_comparison.png")
        plt.tight_layout()
        plt.savefig(path, dpi=300)
        plt.close()
        return path
