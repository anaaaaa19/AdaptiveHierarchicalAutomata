"""
Metrics Collector Component for Real-Time Telemetry and Latency Percentiles.
"""

from dataclasses import dataclass, field
import math
import threading
import time
from typing import Any


class MetricsCollector:
    """
    Thread-safe Metrics Collector capturing packet rates, latency distributions (P50, P95, P99),
    queue depth, dropped events, and formal escalation statistics.
    """

    def __init__(self, history_size: int = 10000) -> None:
        self.history_size = history_size
        self._lock = threading.Lock()
        self.start_time: float = time.time()
        self.packets_processed: int = 0
        self.messages_processed: int = 0
        self.events_processed: int = 0
        self.alerts_generated: int = 0
        self.events_dropped: int = 0
        self.current_queue_depth: int = 0
        self.dfa_count: int = 0
        self.pda_count: int = 0
        self.cfg_count: int = 0
        self._latencies_ms: list[float] = []

    def record_event(
        self,
        latency_ms: float,
        level_used: str = "DFA_MEALY",
        is_alert: bool = False,
    ) -> None:
        with self._lock:
            self.events_processed += 1
            if is_alert:
                self.alerts_generated += 1

            if "DFA" in level_used:
                self.dfa_count += 1
            elif "PDA" in level_used:
                self.pda_count += 1
            elif "CFG" in level_used:
                self.cfg_count += 1

            self._latencies_ms.append(latency_ms)
            if len(self._latencies_ms) > self.history_size:
                self._latencies_ms.pop(0)

    def record_dropped_event(self, count: int = 1) -> None:
        with self._lock:
            self.events_dropped += count

    def set_queue_depth(self, depth: int) -> None:
        with self._lock:
            self.current_queue_depth = depth

    def get_summary(self) -> dict[str, Any]:
        with self._lock:
            elapsed = max(0.001, time.time() - self.start_time)
            sorted_lat = sorted(self._latencies_ms) if self._latencies_ms else [0.0]
            n = len(sorted_lat)

            p50 = sorted_lat[int(0.50 * (n - 1))]
            p95 = sorted_lat[int(0.95 * (n - 1))]
            p99 = sorted_lat[int(0.99 * (n - 1))]
            avg_lat = sum(sorted_lat) / n if n > 0 else 0.0

            total_esc = self.dfa_count + self.pda_count + self.cfg_count
            dfa_pct = round((self.dfa_count / total_esc) * 100, 1) if total_esc > 0 else 0.0
            pda_pct = round((self.pda_count / total_esc) * 100, 1) if total_esc > 0 else 0.0
            cfg_pct = round((self.cfg_count / total_esc) * 100, 1) if total_esc > 0 else 0.0

            return {
                "uptime_seconds": round(elapsed, 2),
                "packets_processed": self.packets_processed,
                "messages_processed": self.messages_processed,
                "events_processed": self.events_processed,
                "total_events_processed": self.events_processed,
                "throughput_events_per_sec": round(self.events_processed / elapsed, 2),
                "alerts_generated": self.alerts_generated,
                "events_dropped": self.events_dropped,
                "queue_depth": self.current_queue_depth,
                "dfa_resolution_percentage": dfa_pct,
                "pda_escalation_percentage": pda_pct,
                "cfg_escalation_percentage": cfg_pct,
                "latency_ms": {
                    "avg": round(avg_lat, 4),
                    "p50": round(p50, 4),
                    "p95": round(p95, 4),
                    "p99": round(p99, 4),
                },
                "escalations": {
                    "dfa_resolved": self.dfa_count,
                    "pda_escalations": self.pda_count,
                    "cfg_escalations": self.cfg_count,
                },
            }
