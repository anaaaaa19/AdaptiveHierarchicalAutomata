"""
Unified Metrics Engine for Detection, Novelty, Adaptation, Hierarchy, and Latency Metrics.
"""

from dataclasses import dataclass, field
import numpy as np
from typing import Dict, List, Optional, Tuple

from .baselines import EvalResult
from .dataset import ProtocolSample


@dataclass
class EvaluationMetrics:
    # Classification / Detection Metrics
    tp: int = 0
    tn: int = 0
    fp: int = 0
    fn: int = 0
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    accuracy: float = 0.0
    fpr: float = 0.0
    fnr: float = 0.0

    # Novelty Metrics
    unseen_behavior_detection_rate: float = 0.0
    legitimate_novelty_recognition: float = 0.0

    # Adaptation Metrics
    adaptation_precision: float = 0.0
    incorrect_adaptation_rate: float = 0.0
    candidate_acceptance_rate: float = 0.0
    rejection_rate: float = 0.0
    rollback_rate: float = 0.0

    # Hierarchy Metrics
    dfa_resolution_pct: float = 0.0
    pda_escalation_pct: float = 0.0
    cfg_escalation_pct: float = 0.0
    escalation_rate: float = 0.0

    # Performance Metrics
    throughput_msgs_sec: float = 0.0
    mean_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0


class MetricsEngine:
    """Computes unified empirical evaluation metrics over experimental runs."""

    @staticmethod
    def compute_metrics(
        eval_pairs: List[Tuple[ProtocolSample, EvalResult]],
        adaptation_stats: Optional[Dict] = None,
    ) -> EvaluationMetrics:
        if not eval_pairs:
            return EvaluationMetrics()

        tp = tn = fp = fn = 0
        dfa_count = pda_count = cfg_count = reject_count = 0

        unseen_total = 0
        unseen_detected = 0

        evolved_total = 0
        evolved_recognized = 0

        latencies_ms: List[float] = []

        for sample, res in eval_pairs:
            latencies_ms.append(res.execution_time_ms)

            # Ground truth: Is this sequence abnormal / attack / anomaly / poisoning?
            is_ground_truth_anomaly = sample.expected_label in (
                "anomalous",
                "attack",
                "poisoning",
                "structural_anomaly",
                "behavioral_anomaly",
                "unseen",
            )

            # System prediction: Did model flag it as anomaly or reject?
            predicted_anomaly = res.is_anomaly or not res.is_accepted

            if is_ground_truth_anomaly and predicted_anomaly:
                tp += 1
            elif not is_ground_truth_anomaly and not predicted_anomaly:
                tn += 1
            elif not is_ground_truth_anomaly and predicted_anomaly:
                fp += 1
            elif is_ground_truth_anomaly and not predicted_anomaly:
                fn += 1

            # Hierarchy escalation tracking
            esc = res.escalation_level
            if esc == "DFA":
                dfa_count += 1
            elif esc == "PDA":
                pda_count += 1
            elif esc == "CFG":
                cfg_count += 1
            else:
                reject_count += 1

            # Novelty tracking
            if sample.category in ("unseen", "zero_day_exploit") or sample.expected_label == "attack":
                unseen_total += 1
                if predicted_anomaly or res.is_novel:
                    unseen_detected += 1

            if sample.category in ("legitimate_evolution", "evolved") or sample.expected_label == "evolved":
                evolved_total += 1
                if res.is_novel or not predicted_anomaly:
                    evolved_recognized += 1

        # Calculate standard detection metrics
        total = tp + tn + fp + fn
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = (tp + tn) / total if total > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

        # Hierarchy percentages
        dfa_pct = (dfa_count / total * 100.0) if total > 0 else 0.0
        pda_pct = (pda_count / total * 100.0) if total > 0 else 0.0
        cfg_pct = (cfg_count / total * 100.0) if total > 0 else 0.0
        esc_rate = ((pda_count + cfg_count) / total * 100.0) if total > 0 else 0.0

        # Novelty rates
        unseen_rate = (unseen_detected / unseen_total) if unseen_total > 0 else 0.0
        evolved_rate = (evolved_recognized / evolved_total) if evolved_total > 0 else 0.0

        # Adaptation metrics
        ad_stats = adaptation_stats or {}
        correct_adaptations = ad_stats.get("correct_adaptations", 0)
        total_adaptations = ad_stats.get("total_adaptations", 0)
        poison_attempts = ad_stats.get("poisoning_attempts", 0)
        blocked_poison = ad_stats.get("blocked_poisoning_attempts", 0)

        ad_prec = (correct_adaptations / total_adaptations) if total_adaptations > 0 else (1.0 if total_adaptations == 0 else 0.0)
        inc_ad_rate = 1.0 - ad_prec
        rej_rate = (blocked_poison / poison_attempts) if poison_attempts > 0 else 1.0

        # Latency statistics
        arr_lat = np.array(latencies_ms) if latencies_ms else np.array([0.0])
        mean_lat = float(np.mean(arr_lat))
        p50_lat = float(np.percentile(arr_lat, 50))
        p95_lat = float(np.percentile(arr_lat, 95))
        p99_lat = float(np.percentile(arr_lat, 99))
        tot_time_sec = float(np.sum(arr_lat)) / 1000.0
        throughput = (total / tot_time_sec) if tot_time_sec > 0 else 0.0

        return EvaluationMetrics(
            tp=tp,
            tn=tn,
            fp=fp,
            fn=fn,
            precision=precision,
            recall=recall,
            f1=f1,
            accuracy=accuracy,
            fpr=fpr,
            fnr=fnr,
            unseen_behavior_detection_rate=unseen_rate,
            legitimate_novelty_recognition=evolved_rate,
            adaptation_precision=ad_prec,
            incorrect_adaptation_rate=inc_ad_rate,
            candidate_acceptance_rate=float(total_adaptations > 0),
            rejection_rate=rej_rate,
            rollback_rate=0.0,
            dfa_resolution_pct=dfa_pct,
            pda_escalation_pct=pda_pct,
            cfg_escalation_pct=cfg_pct,
            escalation_rate=esc_rate,
            throughput_msgs_sec=throughput,
            mean_latency_ms=mean_lat,
            p50_latency_ms=p50_lat,
            p95_latency_ms=p95_lat,
            p99_latency_ms=p99_lat,
        )
