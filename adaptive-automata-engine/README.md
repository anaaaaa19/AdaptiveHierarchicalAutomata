# Adaptive Automata Engine

**Adaptive Hierarchical Automata Engine for Real-Time Detection of Previously Unseen Protocol Deviations**

Phase 5: Adaptive Model Management Subsystem (Safety-Guaranteed Model Adaptation & Poisoning Protection)

---

## Overview

The Adaptive Automata Engine is a research-grade framework designed to detect zero-day and unseen protocol anomalies in network traffic and communication streams.

### Core Research Principle (Phase 5)
$$\text{OBSERVE} \to \text{DETECT NOVELTY} \to \text{ACCUMULATE EVIDENCE} \to \text{ANALYZE CONTEXT} \to \text{DETECT DRIFT} \to \text{GENERATE CANDIDATE} \to \text{FORMALLY VALIDATE} \to \text{ACCEPT/REJECT} \to \text{UPDATE VERSION} \to \text{ACTIVATE/ROLLBACK}$$

The system enforces strict research invariants:
- **No direct mutation**: New observed behavior NEVER directly mutates the active protocol model.
- **Strict distinctions**: $\text{NEW BEHAVIOR} \neq \text{MALICIOUS}$, $\text{NEW BEHAVIOR} \neq \text{LEGITIMATE}$, $\text{FREQUENT BEHAVIOR} \neq \text{LEGITIMATE}$.
- **Poisoning resistance**: Frequency alone is NEVER sufficient to cause a model update. Multiple independent evidence dimensions (frequency + session diversity + successful follow-ups + structural validity) are required.

---

## Directory Structure

```
adaptive-automata-engine/
│
├── src/
│   └── adaptive_automata/
│       ├── core/
│       │   ├── __init__.py
│       │   ├── cfg.py
│       │   ├── dfa.py
│       │   ├── mealy.py
│       │   ├── pda.py
│       │   ├── state.py
│       │   └── transition.py
│       │
│       ├── analysis/
│       │   ├── __init__.py
│       │   ├── analyzer.py
│       │   ├── escalation.py
│       │   └── event.py
│       │
│       ├── adaptation/
│       │   ├── __init__.py
│       │   ├── candidate.py
│       │   ├── drift.py
│       │   ├── engine.py
│       │   ├── evidence.py
│       │   ├── lifecycle.py
│       │   ├── novelty.py
│       │   ├── policy.py
│       │   ├── rollback.py
│       │   ├── updater.py
│       │   └── validator.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   └── versioning.py
│       │
│       ├── protocol/
│       │   ├── __init__.py
│       │   ├── session.py
│       │   ├── sut.py
│       │   ├── tokenizer.py
│       │   └── trace.py
│       │
│       └── learning/
│           ├── __init__.py
│           ├── confidence.py
│           ├── equivalence.py
│           ├── evolution.py
│           ├── hybrid.py
│           ├── lstar.py
│           ├── observation_table.py
│           └── passive.py
│
├── tests/
│   ├── test_adaptation.py
│   ├── test_cfg.py
│   ├── test_dfa.py
│   ├── test_equivalence.py
│   ├── test_evolution.py
│   ├── test_hierarchical.py
│   ├── test_hybrid.py
│   ├── test_lstar.py
│   ├── test_mealy.py
│   ├── test_observation_table.py
│   ├── test_passive.py
│   ├── test_pda.py
│   ├── test_sut.py
│   ├── test_tokenizer.py
│   ├── test_trace.py
│   └── test_versioning.py
│
├── examples/
│   ├── data/
│   │   ├── toy_protocol_v1.json
│   │   └── toy_protocol_v2.json
│   ├── lstar_mealy_example.py
│   ├── phase3_pipeline_example.py
│   ├── phase4_hierarchical_example.py
│   ├── phase5_adaptation_example.py
│   └── toy_protocol.py
│
├── requirements.txt
├── README.md
├── .gitignore
└── pyproject.toml
```

---

## Installation & Setup

### Prerequisites
- Python 3.11+

### Running Tests
Run the complete 48-test suite using pytest:

```powershell
$env:PYTHONPATH="src"; python -m pytest tests
```

### Running Phase 5 Demonstration
Execute the Phase 5 Adaptive Model Management demonstration script:

```powershell
$env:PYTHONPATH="src"; python examples/phase5_adaptation_example.py
```

---

## Roadmap

- **Phase 1 (Complete)**: Formal protocol modeling core (State, Transition, DFA, Mealy Machine, Tokenizer).
- **Phase 2 (Complete)**: Active Automata Learning (L* algorithm, Observation Tables, Equivalence/Membership Oracles).
- **Phase 3 (Complete)**: Trace-Based Protocol Inference & Hybrid Active/Passive Engine.
- **Phase 4 (Complete)**: Hierarchical Formal-Analysis Engine (DFA fast-path, PDA nested context, CFG parser, EscalationController, AnalysisResult).
- **Phase 5 (Complete)**: Adaptive Model Management Subsystem (Novelty detection, evidence store, concept drift, candidate generation, formal validation, model updating, rollback manager, poisoning defense policy).
- **Phase 6**: Protocol Anomaly Detection & Cybersecurity Classification (Attack scenarios, zero-day threat tagging, fuzzing).
- **Phase 7**: Agentic AI Orchestration Layer.
- **Phase 8**: Real-Time Network Deployment.
