# Research Reproducibility Guide

This guide details how to execute reproducible benchmarks, generate figures, and compile research reports for the **Adaptive Hierarchical Automata Engine**.

---

## 1. Directory Structure

```
adaptive-automata-engine/
├── configs/                  # Experiment YAML configurations
│   ├── baseline_comparison.yaml
│   ├── unseen_behavior.yaml
│   ├── legitimate_evolution.yaml
│   ├── poisoning_resistance.yaml
│   ├── hierarchical_efficiency.yaml
│   └── ablation_study.yaml
├── experiments/
│   ├── run.py                # CLI runner script
│   ├── results/              # JSON raw result audit trails
│   ├── plots/                # Publication-quality figures (.png)
│   └── reports/              # Markdown research reports (.md)
└── src/adaptive_automata/evaluation/  # Unified metrics & evaluation engine
```

---

## 2. Running Experiments

### Running a Specific Experiment Configuration
To run a single experiment configuration:
```bash
python -m experiments.run --config configs/baseline_comparison.yaml
```

### Running All Benchmarks Sequentially
To execute the complete benchmark suite:
```bash
python -m experiments.run --all
```

---

## 3. Output Artifacts

Upon execution, the framework automatically produces three types of artifacts:

1. **Audit Trail JSON (`experiments/results/<exp_name>_results.json`)**:
   Contains raw seed outputs, exact configuration, and statistical metrics (`mean`, `std_dev`, 95% CIs).
2. **Publication Figures (`experiments/plots/`)**:
   High-resolution charts including `baseline_f1_comparison.png`, `precision_recall_comparison.png`, `hierarchy_escalation_distribution.png`, `latency_vs_throughput.png`, and `poisoning_resistance_comparison.png`.
3. **Research Reports (`experiments/reports/<exp_name>_report.md`)**:
   Comprehensive Markdown reports detailing the objective, setup, quantitative findings, scientific analysis, and limitations.

---

## 4. Determinism & Seeding

Every dataset sample generation and evaluation run is seeded using standard random seeds (e.g. `[1, 2, 3, 4, 5]`). Running the same configuration with the same seeds will produce mathematically identical results.
