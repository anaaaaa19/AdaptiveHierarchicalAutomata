# Adaptive Automata Engine

**Adaptive Hierarchical Automata Engine for Real-Time Detection of Previously Unseen Protocol Deviations**

Phase 6: Cybersecurity Layer (Behavioral Security Assessment, Zero-Day Detection, Poisoning Resilience & Hypotheses Benchmark Framework)

---

## Overview

The Adaptive Automata Engine is a research-grade formal methods and cybersecurity framework designed to detect zero-day protocol anomalies, evaluate protocol deviations, and manage active protocol model evolution safely.

### Complete Research & Security Pipeline

```
           PROTOCOL TRAFFIC
                  │
                  ▼
             TOKENIZER
                  │
                  ▼
        DFA / MEALY FAST PATH
                  │
          ┌───────┴───────┐
          │               │
        KNOWN          DEVIATION
          │               │
          │               ▼
          │          PDA / CFG
          │               │
          └───────┬───────┘
                  ▼
           FORMAL RESULT (AnalysisResult)
                  │
                  ▼
          NOVELTY ANALYSIS (NoveltyDetector)
                  │
                  ▼
        BEHAVIORAL ANALYSIS (BehavioralAnalyzer)
                  │
                  ▼
        SESSION RISK ANALYSIS (SessionRiskAggregator)
                  │
                  ▼
        SECURITY ASSESSMENT (SecurityAssessment)
                  │
         ┌────────┴────────┐
         │                 │
       BENIGN           SUSPICIOUS
         │                 │
         ▼                 ▼
       RECORD             ALERT
                            │
                            ▼
                   Phase 5 adaptation
                   (Only when evidence criteria met)
                            │
                            ▼
                   candidate update
                            │
                            ▼
                   formal validation
                            │
                            ▼
                   new model version (vN+1)
```

---

## Hypotheses & Benchmark Results

| Hypothesis | Description | Result | Status |
| :--- | :--- | :--- | :---: |
| **H1** | Hierarchical formal analysis detects protocol deviations more effectively than DFA-only analysis for behaviors requiring contextual/structural reasoning | DFA resolved 70%, PDA 15% (nested framing), CFG 15% (recursive tags) | **VERIFIED** |
| **H2** | Adaptive modeling reduces false positives caused by legitimate protocol evolution compared with a static model | 0 False Alerts on evolution; Legitimate `v2.0.0-adapted` model published cleanly | **VERIFIED** |
| **H3** | Evidence-based adaptation is less susceptible to model poisoning than naive frequency-based adaptation | Baseline 3 Naive Model updated 46 times on single-session spam; Proposed System 0 incorrect updates | **VERIFIED** |
| **H4** | A formal hierarchical system can detect previously unseen protocol deviations without requiring the exact attack pattern to be present during learning | **100.0% Unseen Zero-Day Attack Detection Rate** (10/10 detected, FPR = 0.0000) | **VERIFIED** |
| **H5** | Hierarchical escalation reduces computational overhead compared with applying the most expressive formal model to every input | DFA Fast-Path Mean Latency = 0.0126 ms vs CFG Heavy Parser = 0.0216 ms (Overall Mean: 0.0135 ms) | **VERIFIED** |

---

## Directory Structure

```
adaptive-automata-engine/
│
├── src/
│   └── adaptive_automata/
│       ├── core/
│       │   ├── cfg.py, dfa.py, mealy.py, pda.py, state.py, transition.py
│       │
│       ├── analysis/
│       │   ├── analyzer.py, escalation.py, event.py
│       │
│       ├── adaptation/
│       │   ├── candidate.py, config.py, drift.py, engine.py, evidence.py
│       │   ├── lifecycle.py, novelty.py, policy.py, rollback.py, updater.py, validator.py
│       │
│       ├── security/
│       │   ├── alerts.py, assessment.py, behavioral.py, config.py, context.py
│       │   ├── dataset.py, evaluation.py, metrics.py, risk.py
│       │
│       ├── models/
│       │   └── versioning.py
│       │
│       ├── protocol/
│       │   ├── session.py, sut.py, tokenizer.py, trace.py
│       │
│       └── learning/
│           ├── confidence.py, equivalence.py, evolution.py, hybrid.py, lstar.py, passive.py
│
├── tests/
│   ├── security/               # Phase 6 security test suite
│   │   ├── test_alerts.py, test_behavioral_analyzer.py, test_evolution_detection.py
│   │   ├── test_metrics.py, test_poisoning.py, test_security_assessment.py
│   │   ├── test_session_risk.py, test_zero_day.py
│   ├── test_adaptation.py, test_adaptive_engine.py, test_candidate.py
│   ├── test_cfg.py, test_dfa.py, test_drift.py, test_equivalence.py, test_evidence.py
│   ├── test_evolution.py, test_hierarchical.py, test_hybrid.py, test_lstar.py
│   ├── test_mealy.py, test_novelty.py, test_observation_table.py, test_passive.py
│   ├── test_pda.py, test_policy.py, test_rollback.py, test_sut.py, test_tokenizer.py
│   ├── test_trace.py, test_updater.py, test_validator.py, test_versioning.py
│
├── experiments/
│   ├── phase5/                 # Phase 5 adaptation experiment runners
│   └── phase6/                 # Phase 6 cybersecurity benchmark runners
│       ├── README.md
│       ├── run_baselines.py, run_zero_day.py, run_evolution.py
│       ├── run_poisoning.py, run_performance.py
│
└── results/
    ├── phase5/
    └── phase6/                 # Phase 6 JSON benchmark metrics & security report
        ├── experiment_1_baselines.json
        ├── experiment_2_zero_day.json
        ├── experiment_3_evolution.json
        ├── experiment_4_poisoning.json
        ├── experiment_5_performance.json
        └── security_report.md
```

---

## Installation & Setup

### Prerequisites
- Python 3.11+

### Running the Complete Test Suite
Run the full 84-test suite using pytest:

```powershell
$env:PYTHONPATH="src"; python -m pytest tests
```

### Running Phase 6 Benchmark Experiments
Execute individual Phase 6 experiment runners:

```powershell
$env:PYTHONPATH="src;experiments/phase6"; python experiments/phase6/run_baselines.py
$env:PYTHONPATH="src;experiments/phase6"; python experiments/phase6/run_zero_day.py
$env:PYTHONPATH="src;experiments/phase6"; python experiments/phase6/run_evolution.py
$env:PYTHONPATH="src;experiments/phase6"; python experiments/phase6/run_poisoning.py
$env:PYTHONPATH="src;experiments/phase6"; python experiments/phase6/run_performance.py
```

Generated outputs will be saved to `results/phase6/`.

---

## Roadmap

- **Phase 1 (Complete)**: Formal protocol modeling core (State, Transition, DFA, Mealy Machine, Tokenizer).
- **Phase 2 (Complete)**: Active Automata Learning (L* algorithm, Observation Tables, Equivalence/Membership Oracles).
- **Phase 3 (Complete)**: Trace-Based Protocol Inference & Hybrid Active/Passive Engine.
- **Phase 4 (Complete)**: Hierarchical Formal-Analysis Engine (DFA fast-path, PDA nested context, CFG parser).
- **Phase 5 (Complete)**: Adaptive Model Management Subsystem (Novelty detection, evidence store, concept drift, candidate generation, formal validation, model updater, rollback manager, poisoning defense policy).
- **Phase 6 (Complete)**: Cybersecurity Layer (Behavioral security assessment, zero-day detection, session risk aggregation, human-readable alerts, synthetic dataset generators, baselines 1-4, empirical hypothesis verification H1–H5).
- **Phase 7**: Agentic AI Orchestration Layer.
- **Phase 8**: Real-Time Network Deployment.
