"""
Phase 8 Processing Latency Percentiles Test.
"""

from experiments.phase8.replay_benchmark import run_replay_benchmark


def run_latency_test():
    print("Running Latency Percentiles Evaluation...")
    res = run_replay_benchmark(2000)
    print("Latency Percentiles (ms):")
    print(f"  P50: {res['latency_ms']['p50']} ms")
    print(f"  P95: {res['latency_ms']['p95']} ms")
    print(f"  P99: {res['latency_ms']['p99']} ms")
    return res


if __name__ == "__main__":
    run_latency_test()
