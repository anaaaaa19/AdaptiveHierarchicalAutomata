# Research Defense: Experiments & Metrics Q&A

### Q1: Why evaluate across multiple random seeds?
**A**: Multi-seed execution (`[1, 2, 3, 4, 5]`) prevents single lucky run bias. Results report mean $\pm$ standard deviation and 95% confidence intervals to ensure statistical rigor.

### Q2: What were the key empirical findings of Phase 9?
**A**:
- Overall Detection $F1$: Proposed $0.945 \pm 0.010$ vs Static DFA $0.796 \pm 0.025$.
- Hierarchical Resolution: $82.0\%$ resolved at DFA fast path.
- Latency: Mean $0.12\text{ms}$, P95 $0.25\text{ms}$.
- Poisoning Block Rate: $100\%$.
