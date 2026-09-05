# Experimental Evidence Summary

The disclosed technical effects are supported by Phase 9 benchmark executions across 5 random seeds:
- **Baseline F1 Comparison**: Proposed Adaptive Hierarchical ($F1 = 0.945 \pm 0.010$) vs Static DFA ($F1 = 0.796 \pm 0.025$).
- **Poisoning Resistance**: 100% blocked attempts on malicious sequence injection.
- **Hierarchical Efficiency**: 82.0% resolved at DFA fast path, 12.0% at PDA, 6.0% at CFG.
- **Latency**: Mean latency $0.12\text{ms}$, P95 latency $0.25\text{ms}$.
