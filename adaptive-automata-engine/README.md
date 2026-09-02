# Adaptive Automata Engine

**Adaptive Hierarchical Automata Engine for Real-Time Detection of Previously Unseen Protocol Deviations**

Phase 4: Hierarchical Formal-Analysis Engine (DFA $\to$ PDA $\to$ CFG Formal Escalation)

---

## Overview

The Adaptive Automata Engine is a research-grade framework designed to detect zero-day and unseen protocol anomalies in network traffic and communication streams.

### Central Design Principle
> *"Use the least expressive formal model capable of explaining the observed behavior, and escalate only when the simpler model fails."*

### Multi-Tiered Formal Model Hierarchy

```
Incoming Trace
      │
      ▼
Tokenizer
      │
      ▼
┌────────────────────────────────────────┐
│ Level 1: Fast-Path DFA / Mealy Machine │
└───────────────────┬────────────────────┘
                    │
           ┌────────┴────────┐
      (Recognized)     (Deviation)
           │                 │
           ▼                 ▼
     [ Status.KNOWN ]  [ DeviationEvent ]
                             │
                             ▼
                  [ EscalationController ]
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
┌─────────────────────────┐       ┌─────────────────────────┐
│ Level 2: Pushdown (PDA) │       │ Level 3: Context-Free   │
└───────────┬─────────────┘       │          (CFG Parser)   │
            │                     └───────────┬─────────────┘
            └────────────────┬────────────────┘
                             │
                             ▼
                  [ Unified AnalysisResult ]
                 - KNOWN
                 - NOVEL_BUT_VALID
                 - STRUCTURAL_VIOLATION
                 - ANOMALOUS
                 - UNKNOWN
```

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
Run the complete 40-test suite using pytest:

```powershell
$env:PYTHONPATH="src"; python -m pytest tests
```

### Running Phase 4 Demonstration
Execute the Phase 4 Hierarchical Formal Analysis demonstration script:

```powershell
$env:PYTHONPATH="src"; python examples/phase4_hierarchical_example.py
```

---

## Roadmap

- **Phase 1 (Complete)**: Formal protocol modeling core (State, Transition, DFA, Mealy Machine, Tokenizer).
- **Phase 2 (Complete)**: Active Automata Learning (L* algorithm, Observation Tables, Equivalence/Membership Oracles).
- **Phase 3 (Complete)**: Trace-Based Protocol Inference & Hybrid Active/Passive Engine.
- **Phase 4 (Complete)**: Hierarchical Formal-Analysis Engine (DFA fast-path, PDA nested context, CFG parser, EscalationController, AnalysisResult).
- **Phase 5**: Adaptive Learning with Anomaly Detection, Poisoning Protection, and Agentic AI.
