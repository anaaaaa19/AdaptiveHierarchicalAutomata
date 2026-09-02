# Phase 5 Experiments & Benchmarks

This directory contains reproducible controlled experiments evaluating the Phase 5 **Adaptive Model Management Subsystem**.

---

## 1. Controlled Experiment Scenarios

### Experiment A — Stable Protocol (v1 Behavior Only)
- **Dataset**: Standard baseline protocol sessions (`toy_protocol_v1.json`).
- **Expected Outcome**: Low novelty, 0 concept drift events, 0 false model updates. Baseline model remains unchanged.

### Experiment B — Legitimate Protocol Evolution
- **Dataset**: Evolution sessions introducing novel `RENEW_TOKEN` transition across multiple distinct sessions.
- **Expected Outcome**:
  - `RENEW_TOKEN` is detected as novel.
  - Multi-dimensional evidence accumulates across distinct sessions.
  - Concept drift is detected via Jensen-Shannon Divergence ($D_{JS}$).
  - CandidateModel is generated and passes formal regression validation.
  - New immutable model version (`v2.0.0-adapted`) is published to `ModelRegistry`.
  - Baseline model (`v1.1.0-hybrid`) remains preserved in history.

### Experiment C — Poisoning Attempt Defense
- **Dataset**: An attacker spams 100 repeated observations of an invalid `POISON_PAYLOAD` from a single session.
- **Expected Outcome**:
  - Novelty detected and evidence accumulated.
  - **Baseline 3 (Naive Adaptive)** falls victim to poisoning, naively updating its model graph.
  - **Proposed Phase 5 Engine** blocks candidate proposal via multi-dimensional policy (`unique_session_count = 1 < 3`).
  - Active model version remains safe and protected.

---

## 2. Execution Instructions

Run the experiment framework using Python:

```powershell
$env:PYTHONPATH="src;experiments/phase5"; python experiments/phase5/run_experiment.py
```

Generated outputs will be saved to:
- `results/phase5/experiment_results.json`
- `results/phase5/benchmark_report.md`
