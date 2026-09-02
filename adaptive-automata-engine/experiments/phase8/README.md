# Phase 8 Deployment Benchmark Suite

This directory contains empirical benchmark runners evaluating real-world throughput, end-to-end processing latency distributions, queue backpressure policies, zero-downtime model switches, and failure isolation.

## Benchmark Modules

1. **`replay_benchmark.py`**: Benchmarks offline PCAP and trace replay processing.
2. **`throughput_test.py`**: Measures maximum events/sec processing capability under high load.
3. **`latency_test.py`**: Computes P50, P95, and P99 latency distributions per processing stage.
4. **`queue_stress.py`**: Tests backpressure queue handling under extreme traffic bursts.
5. **`model_switch_test.py`**: Validates zero-downtime model hot-reloading and version consistency.
6. **`failure_test.py`**: Tests system failure isolation when AI or storage fails.
