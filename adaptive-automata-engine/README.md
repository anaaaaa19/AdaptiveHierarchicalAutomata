# Adaptive Automata Engine

**Adaptive Hierarchical Automata Engine for Real-Time Detection of Previously Unseen Protocol Deviations**

Phase 3: Trace-Based Protocol Inference & Active/Passive Hybrid Framework

---

## Overview

The Adaptive Automata Engine is a research-grade framework designed to detect zero-day and unseen protocol anomalies in network traffic and communication streams.

### Phase 1 Capabilities
- **Deterministic Finite Automata (DFA)**: State tracking, sequence acceptance/rejection, trace execution.
- **Mealy Machine Transducers**: Transducer state machines ($\delta: Q \times \Sigma \to Q, \lambda: Q \times \Sigma \to \Gamma$).
- **Protocol Tokenizer**: Abstraction layer transforming raw protocol message streams into discrete tokens.

### Phase 2 Capabilities
- **Membership Query Abstraction (`SystemUnderTest`)**: Interface executing input sequences and recording output transductions.
- **Black-Box SUT Simulator (`MealyMachineSUT`)**: Protocol simulator encapsulating Mealy Machines as black boxes.
- **Observation Table (`ObservationTable`)**: Prefix set $S$, extended prefix set $S \cdot \Sigma$, suffix set $E$, observation matrix $T$, closedness & consistency checking.
- **L* Learning Algorithm (`LStarLearner`)**: Active learning loop with counterexample processing and metrics tracking.

### Phase 3 Capabilities (New)
- **Trace Representation & Loader (`TraceLoader`)**: Parses and validates JSON protocol logs into structured `ProtocolSession` and `ProtocolMessage` instances.
- **Session Reconstruction (`SessionReconstructor`)**: Abstract session grouping interface supporting pre-grouped streams and prepared for live/PCAP streams.
- **Modular Message Tokenization (`JSONMessageTokenizer`, `HeaderCommandTokenizer`)**: Separates message structure/headers from dynamic payloads.
- **Passive Inference Engine (`PassiveInferenceEngine`)**: Prefix Tree Acceptor (PTA) construction, state merging, transition frequency tracking, and Laplace-smoothed confidence calculation.
- **Active/Passive Hybrid Engine (`HybridActiveLearner`)**: Bridges passive models with Phase 2 active learning by seeding `ObservationTable` with access sequences and querying unexplored transitions on an active SUT.
- **Model Versioning & Immutability (`ModelRegistry`)**: Versioned model packaging (`VersionedProtocolModel`) with strict overwrite protection.
- **Protocol Evolution Analysis (`ProtocolEvolutionAnalyzer`)**: Evaluates version upgrades ($v1 \to v2$) to classify legitimate protocol extensions without false anomaly flags.

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
│   ├── test_dfa.py
│   ├── test_equivalence.py
│   ├── test_evolution.py
│   ├── test_hybrid.py
│   ├── test_lstar.py
│   ├── test_mealy.py
│   ├── test_observation_table.py
│   ├── test_passive.py
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
Run the complete test suite using pytest:

```powershell
$env:PYTHONPATH="src"; python -m pytest tests
```

### Running Phase 3 Pipeline Demonstration
Execute the Phase 3 trace inference and hybrid learning demonstration script:

```powershell
$env:PYTHONPATH="src"; python examples/phase3_pipeline_example.py
```

---

## Architecture Flow

```
[ Recorded JSON Traces ]
         │
         ▼
 1. Trace Loader & Validation (`TraceLoader`)
         │
         ▼
 2. Session Reconstruction (`SessionReconstructor`)
         │
         ▼
 3. Protocol Tokenization (`JSONMessageTokenizer`)
         │
         ▼
 4. Passive Inference Engine (`PassiveInferenceEngine`)
         │  └── Constructs PTA & Merged Mealy Machine
         │  └── Computes Transition Observation Counts & Confidence Metrics
         ▼
 5. Initial Versioned Model (`VersionedProtocolModel v1.0.0-passive`)
         │
         ▼
 6. Hybrid Active/Passive Learner (`HybridActiveLearner`)
         │  └── Identifies UNKNOWN / UNCERTAIN transitions (N_obs == 0)
         │  └── Seeds Phase 2 ObservationTable with passive access sequences
         │  └── Queries Active SUT via Phase 2 `LStarLearner` for unexplored paths
         ▼
 7. Refined Versioned Model (`VersionedProtocolModel v1.1.0-hybrid`)
         │
         ▼
 8. Protocol Evolution Analyzer (`ProtocolEvolutionAnalyzer`)
            └── Compares v1 model with new v2 protocol traces
            └── Identifies valid protocol extensions without false malicious flags
```

---

## Roadmap

- **Phase 1 (Complete)**: Formal protocol modeling core (State, Transition, DFA, Mealy Machine, Tokenizer).
- **Phase 2 (Complete)**: Active Automata Learning (L* algorithm, Observation Tables, Equivalence/Membership Oracles).
- **Phase 3 (Complete)**: Trace-Based Protocol Inference & Hybrid Active/Passive Engine.
- **Phase 4**: Anomaly Detection Engine (Hierarchical DFA/PDA/CFG detection, adaptive learning, poisoning protection).
- **Phase 5**: Agentic AI Orchestration Layer.
