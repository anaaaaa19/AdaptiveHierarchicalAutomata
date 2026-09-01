# Adaptive Automata Engine

**Adaptive Hierarchical Automata Engine for Real-Time Detection of Previously Unseen Protocol Deviations**

Phase 1: Formal Protocol-Modeling Core

---

## Overview

The Adaptive Automata Engine is a research-grade framework designed to detect zero-day and unseen protocol anomalies in network traffic and communication streams.

Phase 1 establishes the mathematical foundation:
- **Deterministic Finite Automata (DFA)**: Deterministic state tracking, sequence acceptance/rejection, trace execution.
- **Mealy Machine Transducers**: State machines with input symbol to output symbol transductions ($\delta: Q \times \Sigma \to Q, \lambda: Q \times \Sigma \to \Gamma$).
- **Protocol Tokenizer**: Abstraction layer transforming raw protocol message streams into formal discrete tokens.

---

## Directory Structure

```
adaptive-automata-engine/
│
├── src/
│   └── adaptive_automata/
│       ├── core/
│       │   ├── __init__.py
│       │   ├── state.py
│       │   ├── transition.py
│       │   ├── dfa.py
│       │   └── mealy.py
│       │
│       ├── protocol/
│       │   ├── __init__.py
│       │   └── tokenizer.py
│       │
│       └── learning/
│           └── __init__.py
│
├── tests/
│   ├── test_dfa.py
│   ├── test_mealy.py
│   └── test_tokenizer.py
│
├── examples/
│   └── toy_protocol.py
│
├── notebooks/
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
Run the test suite using pytest:

```bash
python -m pytest adaptive-automata-engine/tests
```

### Running Examples
Execute the toy protocol demonstration script:

```bash
python adaptive-automata-engine/examples/toy_protocol.py
```

---

## Roadmap

- **Phase 1 (Current)**: Formal protocol modeling core (State, Transition, DFA, Mealy Machine, Tokenizer).
- **Phase 2**: Active Automata Learning (L* algorithm, Observation Tables, Equivalence/Membership Oracles).
- **Phase 3**: Hierarchical Parsing (Pushdown Automata / Context-Free Grammars for nested framing).
- **Phase 4**: Anomaly Detection & Adaptive Learning with Poisoning Protection.
- **Phase 5**: Agentic AI Orchestration Layer.
