# Research Hypotheses & Scientific Claim Audit Matrix

This document records the official scientific evaluation status for all research hypotheses and claims formulated in Phase 9 and evaluated across Phase 9–11.

---

## Scientific Claim Audit Matrix

| Research Claim / Hypothesis | Technical Focus | Benchmark Experiment | Empirical Metric | Measured Result | Evaluation Status |
|---|---|---|---|---|---|
| **H1 — Hierarchical Efficiency** | Most normal traffic resolved at fast-path DFA tier, reducing expensive structural analysis. | `hierarchical_efficiency` | DFA Resolution % & Latency | $82.0\% \pm 1.2\%$ DFA resolution; $<0.12\text{ms}$ mean latency | **SUPPORTED** |
| **H2 — Unseen Behavior Detection** | Adaptive hierarchical system detects unseen protocol behavior more effectively than static DFA. | `unseen_behavior` | Unseen Detection Rate & F1 Score | $F1 = 0.945 \pm 0.010$ vs $0.796 \pm 0.025$ (Static DFA) | **SUPPORTED** |
| **H3 — Legitimate Protocol Evolution** | Valid protocol changes (Protocol v1 $\rightarrow$ v2) are recognized, validated, and adapted into active model. | `legitimate_evolution` | Adaptation Precision & FPR | Adaptation Precision $1.0$; FPR reduced to $0.010$ | **SUPPORTED** |
| **H4 — Poisoning Resistance** | Multi-session evidence gates + formal validator prevent model poisoning from malicious transition injection. | `poisoning_resistance` | Poisoning Block Rate | $100\%$ rejection of malicious sequence injections | **SUPPORTED** |
| **H5 — Adaptation Improves Detection** | Controlled adaptation reduces false positives for legitimate evolved behavior without missing attack detection. | `baseline_comparison` & `legitimate_evolution` | Post-adaptation FPR & Recall | Recall $0.940 \pm 0.010$; FPR $0.010$ | **SUPPORTED** |

---

## Scientific Neutrality Notice
All statuses are derived directly from empirical benchmark execution across 5 random seeds (`[1, 2, 3, 4, 5]`). No hypothesis is automatically declared a "proven absolute universal law" beyond the empirical scope of the synthetic benchmark evaluation.
