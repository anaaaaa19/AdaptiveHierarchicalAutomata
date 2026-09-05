# Hierarchical Formal Analysis Specification

This document describes the multi-tier hierarchical evaluation pipeline implemented in `adaptive_automata.analysis`.

---

## 1. Multi-Tier Escalation Architecture

```
                    ┌─────────────────────────┐
                    │ Protocol Message Stream │
                    └────────────┬────────────┘
                                 │
                                 ▼
                     ┌──────────────────────┐
                     │ Fast-Path DFA / Mealy│ ──► [ ACCEPT (DFA) ]
                     └───────────┬──────────┘
                                 │ (Escalate if missing)
                                 ▼
                     ┌──────────────────────┐
                     │ Pushdown Automaton   │ ──► [ ACCEPT (PDA) ]
                     └───────────┬──────────┘
                                 │ (Escalate if unclosed stack)
                                 ▼
                     ┌──────────────────────┐
                     │ Context-Free Grammar │ ──► [ ACCEPT (CFG) ]
                     └───────────┬──────────┘
                                 │ (Escalate if invalid syntax)
                                 ▼
                     ┌──────────────────────┐
                     │ Deviation / Anomaly  │ ──► [ REJECT / ALERT ]
                     └──────────────────────┘
```

---

## 2. Evaluation Tiers

1. **DFA / Mealy Tier ($O(n)$)**: Validates strict state-transition paths. Resolves $\approx 80\%+$ of standard traffic.
2. **PDA Tier ($O(n)$ with stack)**: Evaluates structural depth, balanced message pairs, and pushdown stack invariants.
3. **CFG Tier ($O(n^3)$ worst-case)**: Evaluates complex context-free grammar production rules.
4. **Deviation Trigger**: Sequences failing all three tiers trigger a formal deviation event sent to the adaptive and security engines.
