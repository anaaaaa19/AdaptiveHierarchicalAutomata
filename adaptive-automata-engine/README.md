# Adaptive Automata Engine

**Adaptive Hierarchical Automata Engine for Real-Time Detection of Previously Unseen Protocol Deviations**

Phase 5: Adaptive Model Management Subsystem (Safety-Guaranteed Model Adaptation, Audit Logging & Research Benchmarks)

---

## Overview

The Adaptive Automata Engine is a research-grade formal methods framework designed to detect zero-day protocol deviations and manage active protocol model evolution safely.

### Central Research Adaptation Loop

```
         OLD MODEL (vN)
             │
             ▼
      OBSERVED TRAFFIC
             │
             ▼
    HIERARCHICAL ANALYSIS (DFA -> PDA -> CFG)
             │
             ▼
         NOVELTY?
             │
             ▼
   EVIDENCE ACCUMULATION (Multi-Dimensional)
             │
             ▼
  CONCEPT DRIFT? (Jensen-Shannon Divergence)
             │
             ▼
   ADAPTATION POLICY (Poisoning Defense)
             │
             ▼
      CANDIDATE MODEL
             │
             ▼
    FORMAL VALIDATION (Regression Testing)
         /         \
      FAIL         PASS
       │             │
       ▼             ▼
    REJECT       NEW VERSION (vN+1)
                     │
                     ▼
                  ACTIVATE
                     │
                     ▼
                  MONITOR
                     │
                     ▼
                  ROLLBACK (if necessary)
```

---

## Research Invariants & Disclaimers

The system strictly enforces formal research principles:
- **No Direct Mutation**: Observed novel behavior NEVER directly mutates active protocol models.
- **Explicit Invariant Distinctions**:
  - $\text{NEW BEHAVIOR} \neq \text{MALICIOUS}$
  - $\text{NEW BEHAVIOR} \neq \text{LEGITIMATE}$
  - $\text{FREQUENT BEHAVIOR} \neq \text{LEGITIMATE}$
- **Poisoning Resistance**: Frequency alone is **NEVER** sufficient for model updates. Multi-dimensional criteria (frequency + session diversity + successful follow-ups + structural validity) are required.

> [!IMPORTANT]
> **Research Limitations**:
> 1. The system does NOT equate novelty with maliciousness (cybersecurity classification is deferred to Phase 6).
> 2. The system does NOT guarantee 100% poisoning immunity under all threat models; it provides a multi-dimensional formal safety heuristic evaluated experimentally.
> 3. The system does NOT provide a mathematical proof of protocol legitimacy; empirical observation provides observational evidence.

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
│   ├── test_adaptation.py, test_adaptive_engine.py, test_candidate.py
│   ├── test_cfg.py, test_dfa.py, test_drift.py, test_equivalence.py
│   ├── test_evidence.py, test_evolution.py, test_hierarchical.py, test_hybrid.py
│   ├── test_lstar.py, test_mealy.py, test_novelty.py, test_observation_table.py
│   ├── test_passive.py, test_pda.py, test_policy.py, test_rollback.py
│   ├── test_sut.py, test_tokenizer.py, test_trace.py, test_updater.py, test_validator.py
│
├── experiments/
│   └── phase5/
│       ├── baselines.py        # Baselines 1, 2, 3 and Proposed model evaluators
│       ├── run_experiment.py   # Benchmark runner for Experiments A, B, C
│       └── README.md
│
└── results/
    └── phase5/
        ├── experiment_results.json
        └── benchmark_report.md
```

---

## Installation & Setup

### Prerequisites
- Python 3.11+

### Running the Complete Test Suite
Run the full 72-test suite:

```powershell
$env:PYTHONPATH="src"; python -m pytest tests
```

### Running Phase 5 Experiments & Benchmarks
Execute the reproducible experiment framework:

```powershell
$env:PYTHONPATH="src;experiments/phase5"; python experiments/phase5/run_experiment.py
```

---

## Benchmark Results Summary

| Modeling Engine | False Model Updates | Legitimate Evolution Adapted | Single-Session Poisoning Susceptibility | Model Version Preserved |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline 1: Static Model** | 0 | ❌ No | Low | ❌ Static (v1 only) |
| **Baseline 2: Hierarchical Model** | 0 | ❌ No | Low | ❌ Static (v1 only) |
| **Baseline 3: Naive Adaptive Model** | ❌ High | ✅ Yes | ❌ High (Vulnerable to Spam) | ❌ Overwritten |
| **Proposed: Phase 5 Engine** | **0** | **✅ Yes** | **Protected (Session Diversity Policy)** | **✅ Immutable Versioning** |

---

## Roadmap

- **Phase 1 (Complete)**: Formal protocol modeling core (State, Transition, DFA, Mealy Machine, Tokenizer).
- **Phase 2 (Complete)**: Active Automata Learning (L* algorithm, Observation Tables, Equivalence/Membership Oracles).
- **Phase 3 (Complete)**: Trace-Based Protocol Inference & Hybrid Active/Passive Engine.
- **Phase 4 (Complete)**: Hierarchical Formal-Analysis Engine (DFA fast-path, PDA nested context, CFG parser).
- **Phase 5 (Complete)**: Adaptive Model Management Subsystem (Novelty detection, evidence store, concept drift, candidate generation, formal validation, model updater, rollback manager, poisoning defense policy, reproducible benchmarks).
- **Phase 6**: Protocol Anomaly Detection & Cybersecurity Classification (Attack scenarios, zero-day threat tagging, fuzzing).
- **Phase 7**: Agentic AI Orchestration Layer.
- **Phase 8**: Real-Time Network Deployment.
