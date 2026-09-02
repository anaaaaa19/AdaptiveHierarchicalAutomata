# Phase 6 Cybersecurity Experiments & Research Benchmarks

This directory contains reproducible controlled experiments evaluating the Phase 6 **Cybersecurity Layer** built on top of the Phase 1–5 Adaptive Hierarchical Automata Engine.

---

## 1. Research Hypotheses Evaluated

- **H1**: Hierarchical formal analysis detects protocol deviations more effectively than DFA-only analysis for behaviors requiring contextual/structural reasoning.
- **H2**: Adaptive modeling reduces false positives caused by legitimate protocol evolution compared with a static model.
- **H3**: Evidence-based adaptation is less susceptible to model poisoning than naive frequency-based adaptation.
- **H4**: A formal hierarchical system can detect previously unseen protocol deviations without requiring the exact attack pattern to be present during learning.
- **H5**: Hierarchical escalation reduces computational overhead compared with applying the most expressive formal model to every input.

---

## 2. Experiment Runners

| Script | Purpose | Hypotheses Tested |
| :--- | :--- | :---: |
| `run_baselines.py` | Compares Baselines 1–4 across Precision, Recall, F1, FPR, FNR, and Latency | **H1, H5** |
| `run_zero_day.py` | Evaluates previously unseen zero-day attack detection (withheld from training) | **H4** |
| `run_evolution.py` | Evaluates legitimate protocol evolution (`CAPABILITIES`) vs malicious attacks | **H2** |
| `run_poisoning.py` | Evaluates single-session high-frequency poisoning attack resilience | **H3** |
| `run_performance.py` | Evaluates DFA/PDA/CFG escalation percentages and P50/P95 latency statistics | **H5** |

---

## 3. Running All Phase 6 Experiments

Run each experiment script using Python:

```powershell
$env:PYTHONPATH="src;experiments/phase6"; python experiments/phase6/run_baselines.py
$env:PYTHONPATH="src;experiments/phase6"; python experiments/phase6/run_zero_day.py
$env:PYTHONPATH="src;experiments/phase6"; python experiments/phase6/run_evolution.py
$env:PYTHONPATH="src;experiments/phase6"; python experiments/phase6/run_poisoning.py
$env:PYTHONPATH="src;experiments/phase6"; python experiments/phase6/run_performance.py
```

Generated outputs will be saved to `results/phase6/`.
