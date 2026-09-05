"""
Experiment Runner Engine for Reproducible Benchmarks.
"""

from dataclasses import asdict
import datetime
import json
import os
from typing import Dict, List, Set, Tuple

from .baselines import (
    BaseEvaluatorModel,
    StaticDFABaseline,
    StaticHierarchicalBaseline,
    NaiveAdaptiveBaseline,
    ProposedAdaptiveHierarchicalModel,
    EvalResult,
)
from .config import ExperimentConfig
from .dataset import SyntheticDatasetGenerator, DatasetSplit, ProtocolSample
from .metrics import MetricsEngine, EvaluationMetrics
from .statistics import StatisticalAnalyzer, SummaryStats


class ExperimentRunner:
    """Executes multi-seed experiment configurations over baselines and proposed models."""

    def __init__(self, config: ExperimentConfig):
        self.config = config

    def run(self) -> Dict:
        results_by_model: Dict[str, List[EvaluationMetrics]] = {m: [] for m in self.config.models}

        for seed in self.config.seeds:
            # 1. Generate seed-deterministic dataset
            gen = SyntheticDatasetGenerator(seed=seed)
            ds_params = self.config.dataset_params
            split = gen.generate_dataset(
                protocol=ds_params.get("protocol", "toy_protocol"),
                train_size=ds_params.get("train_size", 1000),
                validation_size=ds_params.get("validation_size", 200),
                test_size=ds_params.get("test_size", 500),
                categories=ds_params.get("categories", None),
                seed=seed,
            )

            # Extract base sequence sets from training split
            dfa_seqs, pda_seqs, cfg_seqs = self._extract_knowledge_base(split.train)

            # 2. Evaluate each target model
            for model_name in self.config.models:
                model = self._instantiate_model(model_name, dfa_seqs, pda_seqs, cfg_seqs)

                # Adaptation / Warmup Phase on Train + Validation
                for sample in split.train + split.validation:
                    if sample.expected_label in ("normal", "evolved"):
                        model.adapt_on_sequence(sample.sequence, label=sample.expected_label)
                    elif sample.expected_label == "poisoning":
                        model.adapt_on_sequence(sample.sequence, label="poisoning")

                # Test Evaluation Phase
                eval_pairs: List[Tuple[ProtocolSample, EvalResult]] = []
                for sample in split.test:
                    res = model.process_sequence(sample.sequence)
                    eval_pairs.append((sample, res))

                # Collect adaptation stats if available
                ad_stats = {}
                if isinstance(model, ProposedAdaptiveHierarchicalModel):
                    ad_stats = {
                        "total_adaptations": model.model_versions - 1,
                        "correct_adaptations": max(0, model.model_versions - 1 - model.poisoning_attempts),
                        "poisoning_attempts": model.poisoning_attempts,
                        "blocked_poisoning_attempts": model.blocked_poisoning_attempts,
                    }

                metrics = MetricsEngine.compute_metrics(eval_pairs, adaptation_stats=ad_stats)
                results_by_model[model_name].append(metrics)

        # 3. Aggregate Statistical Results
        aggregated_summary = self._aggregate_statistics(results_by_model)

        # 4. Save audit trail JSON
        output_payload = {
            "experiment": self.config.name,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "seeds": self.config.seeds,
            "configuration": asdict(self.config),
            "summary": aggregated_summary,
        }

        os.makedirs(self.config.output_dir, exist_ok=True)
        out_file = os.path.join(self.config.output_dir, f"{self.config.name}_results.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(output_payload, f, indent=2)

        return output_payload

    def _extract_knowledge_base(
        self, train_samples: List[ProtocolSample]
    ) -> Tuple[Set[Tuple[str, ...]], Set[Tuple[str, ...]], Set[Tuple[str, ...]]]:
        dfa_seqs: Set[Tuple[str, ...]] = set()
        pda_seqs: Set[Tuple[str, ...]] = set()
        cfg_seqs: Set[Tuple[str, ...]] = set()

        for s in train_samples:
            if s.expected_label == "normal":
                seq_t = tuple(s.sequence)
                if len(s.sequence) <= 5:
                    dfa_seqs.add(seq_t)
                elif len(s.sequence) <= 8:
                    pda_seqs.add(seq_t)
                else:
                    cfg_seqs.add(seq_t)

        return dfa_seqs, pda_seqs, cfg_seqs

    def _instantiate_model(
        self,
        model_name: str,
        dfa_seqs: Set[Tuple[str, ...]],
        pda_seqs: Set[Tuple[str, ...]],
        cfg_seqs: Set[Tuple[str, ...]],
    ) -> BaseEvaluatorModel:
        ab = self.config.ablation_params

        if model_name == "static_dfa":
            return StaticDFABaseline(valid_sequences=dfa_seqs)
        elif model_name == "static_hierarchical":
            return StaticHierarchicalBaseline(dfa_sequences=dfa_seqs, pda_sequences=pda_seqs, cfg_sequences=cfg_seqs)
        elif model_name == "naive_adaptive":
            return NaiveAdaptiveBaseline(initial_valid=dfa_seqs, frequency_threshold=3)
        elif model_name == "proposed":
            return ProposedAdaptiveHierarchicalModel(
                dfa_sequences=dfa_seqs,
                pda_sequences=pda_seqs,
                cfg_sequences=cfg_seqs,
                evidence_threshold=5,
                disable_hierarchy=ab.get("disable_hierarchy", False),
                disable_drift=ab.get("disable_drift", False),
                disable_evidence=ab.get("disable_evidence", False),
                disable_validation=ab.get("disable_validation", False),
                disable_poisoning_protection=ab.get("disable_poisoning_protection", False),
                disable_versioning=ab.get("disable_versioning", False),
            )
        else:
            raise ValueError(f"Unknown baseline model requested: {model_name}")

    def _aggregate_statistics(self, results: Dict[str, List[EvaluationMetrics]]) -> Dict:
        summary = {}

        metric_fields = [
            "precision",
            "recall",
            "f1",
            "accuracy",
            "fpr",
            "unseen_behavior_detection_rate",
            "legitimate_novelty_recognition",
            "adaptation_precision",
            "rejection_rate",
            "dfa_resolution_pct",
            "pda_escalation_pct",
            "cfg_escalation_pct",
            "mean_latency_ms",
            "p95_latency_ms",
            "throughput_msgs_sec",
        ]

        for model_name, metrics_list in results.items():
            model_sum = {}
            for field_name in metric_fields:
                vals = [getattr(m, field_name) for m in metrics_list]
                stats: SummaryStats = StatisticalAnalyzer.summarize(vals)
                model_sum[field_name] = asdict(stats)
            summary[model_name] = model_sum

        return summary
