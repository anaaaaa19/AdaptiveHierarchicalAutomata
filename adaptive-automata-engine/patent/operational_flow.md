# Operational Flow Specification

1. **Ingestion & Tokenization**: A raw message payload sequence $w$ is tokenized.
2. **DFA Fast-Path Evaluation**: $w$ is checked against active DFA/Mealy transitions. If accepted, return `(DFA, ACCEPT)` in $O(|w|)$ time.
3. **Escalation**: If unmodeled, evaluate at PDA tier (checking stack invariants) and CFG tier (parsing production rules).
4. **Deviation & Evidence**: If rejected across all tiers, record deviation event. Accumulate multi-session evidence $E(e)$.
5. **Drift & Formal Check**: If $E(e) \ge \tau_{ev}$ and $D_{JS} \le \tau_{drift}$, generate Candidate Model $M_{cand}$. Pass $M_{cand}$ to `FormalValidator`.
6. **Promotion**: If $V(M_{cand}) = 1$, register new model version $v_{k+1}$ in `ModelRegistry` and activate.
