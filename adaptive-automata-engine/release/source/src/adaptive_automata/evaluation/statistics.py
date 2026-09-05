"""
Multi-Seed Statistical Analysis and Confidence Interval Utilities.
"""

from dataclasses import dataclass
import math
from typing import List, Tuple


@dataclass
class SummaryStats:
    mean: float
    std_dev: float
    ci95_lower: float
    ci95_upper: float
    sample_size: int
    min_val: float
    max_val: float


class StatisticalAnalyzer:
    """Statistical evaluation utilities for multi-seed experimental aggregation."""

    @staticmethod
    def summarize(values: List[float]) -> SummaryStats:
        if not values:
            return SummaryStats(
                mean=0.0,
                std_dev=0.0,
                ci95_lower=0.0,
                ci95_upper=0.0,
                sample_size=0,
                min_val=0.0,
                max_val=0.0,
            )

        n = len(values)
        mean_val = sum(values) / n

        if n > 1:
            variance = sum((x - mean_val) ** 2 for x in values) / (n - 1)
            std_dev = math.sqrt(variance)
        else:
            std_dev = 0.0

        # 95% confidence interval using Student-t margin approximation (z ~ 1.96 for n >= 5)
        stderr = std_dev / math.sqrt(n) if n > 0 else 0.0
        margin = 1.96 * stderr

        return SummaryStats(
            mean=mean_val,
            std_dev=std_dev,
            ci95_lower=mean_val - margin,
            ci95_upper=mean_val + margin,
            sample_size=n,
            min_val=min(values),
            max_val=max(values),
        )

    @staticmethod
    def compare_samples(sample1: List[float], sample2: List[float]) -> Tuple[float, float]:
        """
        Computes mean difference and Welch's t-statistic.
        Returns (mean_difference, t_statistic).
        """
        s1 = StatisticalAnalyzer.summarize(sample1)
        s2 = StatisticalAnalyzer.summarize(sample2)

        mean_diff = s2.mean - s1.mean
        n1, n2 = s1.sample_size, s2.sample_size
        if n1 < 2 or n2 < 2:
            return mean_diff, 0.0

        se = math.sqrt((s1.std_dev ** 2 / n1) + (s2.std_dev ** 2 / n2))
        t_stat = mean_diff / se if se > 0 else 0.0

        return mean_diff, t_stat
