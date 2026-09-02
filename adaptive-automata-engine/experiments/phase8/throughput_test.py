"""
Phase 8 High Throughput Stress Test.
"""

from experiments.phase8.replay_benchmark import run_replay_benchmark


def run_throughput_test():
    print("Running 5,000 packet throughput stress test...")
    res = run_replay_benchmark(5000)
    print(f"Throughput: {res['events_per_second']} events/sec")
    print(f"P95 Latency: {res['latency_ms']['p95']} ms")
    return res


if __name__ == "__main__":
    run_throughput_test()
