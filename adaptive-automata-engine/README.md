# Adaptive Automata Engine

**Adaptive Hierarchical Automata Engine for Real-Time Detection of Previously Unseen Protocol Deviations**

Phase 2: Active Automata Learning Framework (L* Mealy Machine Learner)

---

## Overview

The Adaptive Automata Engine is a research-grade framework designed to detect zero-day and unseen protocol anomalies in network traffic and communication streams.

### Phase 1 Capabilities
- **Deterministic Finite Automata (DFA)**: Deterministic state tracking, sequence acceptance/rejection, trace execution.
- **Mealy Machine Transducers**: Transducer state machines ($\delta: Q \times \Sigma \to Q, \lambda: Q \times \Sigma \to \Gamma$).
- **Protocol Tokenizer**: Abstraction layer transforming raw protocol message streams into discrete tokens.

### Phase 2 Capabilities (New)
- **Membership Query Abstraction (`SystemUnderTest`)**: Clean interface executing input symbol sequences and recording output transductions and query budgets.
- **Black-Box SUT Simulator (`MealyMachineSUT`)**: Protocol simulator encapsulating Phase 1 Mealy Machines as black boxes.
- **Observation Table (`ObservationTable`)**: Prefix set $S$, extended prefix set $S \cdot \Sigma$, suffix set $E$, observation matrix $T$, closedness & consistency checking.
- **Hypothesis Construction**: Direct Mealy machine extraction from closed and consistent observation tables.
- **Equivalence Oracles (`EquivalenceOracle`)**: Bounded random sequence testing, W-method testing, and exact state graph comparison.
- **L* Learning Algorithm (`LStarLearner`)**: Complete active learning loop with counterexample processing and metrics tracking.

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
│       │   ├── sut.py
│       │   └── tokenizer.py
│       │
│       └── learning/
│           ├── __init__.py
│           ├── equivalence.py
│           ├── lstar.py
│           └── observation_table.py
│
├── tests/
│   ├── test_dfa.py
│   ├── test_equivalence.py
│   ├── test_lstar.py
│   ├── test_mealy.py
│   ├── test_observation_table.py
│   ├── test_sut.py
│   └── test_tokenizer.py
│
├── examples/
│   ├── lstar_mealy_example.py
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
Run the test suite using pytest:

```powershell
$env:PYTHONPATH="src"; python -m pytest tests
```

### Running Examples
Execute the Phase 2 L* Active Learning demonstration script:

```powershell
$env:PYTHONPATH="src"; python examples/lstar_mealy_example.py
```

---

## Mathematical Correspondence (L* Algorithm)

| Implementation Component | Formal L* Concept | Mathematical Definition |
| :--- | :--- | :--- |
| `SystemUnderTest` | Membership Oracle $\mathcal{O}_{MQ}$ | Transduction function $\mathcal{O}_{MQ}: \Sigma^* \to \Gamma^*$ |
| `ObservationTable.S` | Access sequence set $S$ | Prefixes representing candidate states $Q \cong \{ row(s) \mid s \in S \}$ |
| `ObservationTable.E` | Distinguishing suffix set $E$ | Sequences $e \in \Sigma^+$ used to differentiate states |
| `ObservationTable.T` | Observation matrix $T$ | $T: (S \cup S \cdot \Sigma) \times E \to \Gamma^*$, where $T(s, e) = \text{SUT}(s \cdot e)[|s|:]$ |
| `is_closed()` | Table Closedness Property | $\forall t \in S \cdot \Sigma, \exists s \in S : row(t) = row(s)$ |
| `is_consistent()` | Table Consistency Property | $\forall s_1, s_2 \in S, (row(s_1) = row(s_2) \implies \forall a \in \Sigma, row(s_1 \cdot a) = row(s_2 \cdot a))$ |
| `to_mealy_machine()` | Hypothesis Construction $\mathcal{H}$ | $Q = \{ row(s) \}, q_0 = row(\varepsilon), \delta(row(s), a) = row(s \cdot a), \lambda(row(s), a) = T(s, (a,))[0]$ |
| `EquivalenceOracle` | Equivalence Oracle $\mathcal{O}_{EQ}$ | Given hypothesis $\mathcal{H}$, finds $x \in \Sigma^*$ where $\mathcal{H}(x) \neq \text{SUT}(x)$ or returns $\emptyset$ |

---

## Roadmap

- **Phase 1 (Complete)**: Formal protocol modeling core (State, Transition, DFA, Mealy Machine, Tokenizer).
- **Phase 2 (Complete)**: Active Automata Learning (L* algorithm, Observation Tables, Equivalence/Membership Oracles).
- **Phase 3**: Hierarchical Parsing (Pushdown Automata / Context-Free Grammars for nested framing).
- **Phase 4**: Anomaly Detection & Adaptive Learning with Poisoning Protection.
- **Phase 5**: Agentic AI Orchestration Layer.
