# Protocol Inference & Automata Learning Specification

This document details the active and passive protocol learning architecture implemented in `adaptive_automata.learning`.

---

## 1. Active Learning (L* Algorithm & Mealy Inference)

The system implements Angluin's $L^*$ active learning algorithm adapted for stateful Mealy Machines:
- **Observation Table $(S, E, T)$**: Maintains prefix set $S$, suffix set $E$, and transition observation entries $T(s \cdot a, e)$.
- **Closedness & Consistency**: Ensures table satisfies closedness ($\forall t \in S \cdot \Sigma, \exists s \in S : T(t) = T(s)$) and consistency.
- **Equivalence Oracles**: Supports $W$-method, random sequence walks, and exact state comparison oracles to discover counterexamples.

---

## 2. Passive Inference

For offline trace analysis, `PassiveInferenceEngine` reconstructs state transition graphs from recorded session logs:
- Merges equivalent prefixes into prefix tree acceptors (PTA).
- Applies state merging heuristics based on local k-context equivalence.
