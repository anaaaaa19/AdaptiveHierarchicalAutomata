# Methodological Limitations & Empirical Scope

This document provides a transparent, scientifically rigorous statement of limitations for the **Adaptive Hierarchical Automata Engine**.

---

## 1. Synthetic Dataset Scope

- **State Space Simplification**: Experiments in Phase 9 use controlled synthetic protocol state machines (e.g. Toy Protocol v1/v2, nested structures). Real-world enterprise protocols (e.g. TLS 1.3, BGP, HTTP/2) feature larger state spaces and implementation-specific quirks.
- **Deterministic Tokenization**: The benchmark dataset generator assumes clean message boundaries. Noise, packet fragmentation, and out-of-order IP reassembly overhead are abstracted in synthetic tests.

---

## 2. Theoretical & Automata Boundaries

- **Bounded Equivalence Queries**: Active automata learning via L* relies on bounded equivalence oracles ($W$-method / random sequence walks). While effective for standard protocols, minimal counterexamples for extremely large state spaces may require extended query budgets.
- **CFG Computational Complexity**: Context-Free Grammar parsing exhibits $O(n^3)$ worst-case time complexity (Earley / CYK parsing). Although high-throughput normal traffic is resolved at the $O(n)$ DFA fast path, sustained high volumes of PDA/CFG-escalating traffic will decrease overall throughput.

---

## 3. Adaptive Learning & Latency Assumptions

- **Evidence Window Delay**: Adaptation to legitimate protocol evolution is intentionally non-instantaneous to prevent model poisoning. Valid novel protocol extensions must accumulate sufficient multi-session evidence before activation.
- **Drift Distribution Requirements**: Jensen-Shannon Divergence concept drift detection assumes stationary or slowly evolving transition distributions. Sudden, radical multi-step protocol rewrites may require manual policy approval.

---

## 4. Agentic Layer & LLM Dependencies

- **AI Hallucination Risk**: Large Language Model investigation reports produced in Phase 7 are advisory. AI agents may generate plausible but unverified explanatory hypotheses.
- **Formal Decoupling**: AI agents are strictly isolated from mutating core formal models. AI investigations cannot override formal security alert classifications.

---

## 5. Deployment & Hardware Dependencies

- **Python Runtime Overhead**: The engine is implemented in Python 3.14. Performance benchmarks (e.g. P95 latency $<1\text{ms}$) depend on host CPU clock speed, RAM bandwidth, and available worker threads. Production deployments at multi-gigabit line speeds would require C/C++ native acceleration wrappers for packet tokenization.
