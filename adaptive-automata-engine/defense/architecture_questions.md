# Research Defense: Architecture Q&A

### Q1: Why use a multi-tiered hierarchy (DFA -> PDA -> CFG) instead of a single parser?
**A**: Real-world high-throughput network traffic requires microsecond-level latency. Parsing every message with a Context-Free Grammar parser incurs $O(n^3)$ worst-case time complexity. By cascading evaluation, $>82\%$ of standard traffic is resolved at the fast $O(n)$ DFA tier in $<0.12\text{ms}$, while complex nested state structures escalate to PDA/CFG only when necessary.

### Q2: How does the system handle real-time pipeline bottlenecks?
**A**: The deployment platform uses a thread-safe 5-tuple session manager, bounded event queues (`MAX_QUEUE_SIZE = 5000`), and async FastAPI/ASGI event handling. Non-critical AI investigations run out-of-band on worker threads.
