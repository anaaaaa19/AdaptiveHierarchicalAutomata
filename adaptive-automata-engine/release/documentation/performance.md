# Performance Strategy & Benchmarking

## Micro-benchmarks
- **Level 1 Fast Path**: $O(1)$ state transduction lookup ($<0.01\text{ms}$).
- **Level 2 PDA & Level 3 CFG**: Escalated only when fast-path Mealy transducer encounters a deviation.
- **Processing Latency**: P50 $<0.05\text{ms}$, P95 $<0.15\text{ms}$ per message.
- **Throughput**: $>10,000$ events/second on single-core Python evaluation thread with memory-bounded queue.

## Backpressure Policies
- `DROP_OLDEST` (Default): Evicts oldest queued packets when queue utilization reaches $100\%$.
- `DROP_NEWEST`: Drops incoming packets under spike conditions.
- `BLOCK`: Blocks producer thread.
