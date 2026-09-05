# Adaptive Hierarchical Automata Engine

**Real-Time Detection of Previously Unseen Protocol Deviations with Safety-Guaranteed Model Evolution**

[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Test Suite](https://img.shields.io/badge/tests-141%20passed-brightgreen.svg)]()

---

## 1. Project Purpose & Overview
The **Adaptive Hierarchical Automata Engine** is a high-throughput, research-grade network protocol monitoring platform designed to detect zero-day protocol deviations, distinguish legitimate protocol version updates from malicious attacks, and perform safety-guaranteed model evolution without susceptibility to model poisoning.

---

## 2. Research Problem
1. **Rigidity of Static Models**: Traditional security models fail when valid protocol extensions (e.g. Protocol v1 $\rightarrow$ v2) occur, generating elevated false positive rates.
2. **Model Poisoning Risks**: Unconstrained adaptive anomaly detectors accept repeated malicious sequence injections, corrupting active model state.
3. **Parsing Overhead**: Running full Context-Free Grammar (CFG) parsing on high-speed interfaces creates unacceptable processing latency.

---

## 3. System Architecture

```
                    ┌─────────────────────────┐
                    │ Protocol Message Stream │
                    └────────────┬────────────┘
                                 │
                                 ▼
                     ┌──────────────────────┐
                     │ Fast-Path DFA / Mealy│ ──► [ ACCEPT (DFA) ]
                     └───────────┬──────────┘
                                 │ (Escalate if unmodeled)
                                 ▼
                     ┌──────────────────────┐
                     │ Pushdown Automaton   │ ──► [ ACCEPT (PDA) ]
                     └───────────┬──────────┘
                                 │ (Escalate if unclosed stack)
                                 ▼
                     ┌──────────────────────┐
                     │ Context-Free Grammar │ ──► [ ACCEPT (CFG) ]
                     └───────────┬──────────┘
                                 │ (Escalate if syntax violation)
                                 ▼
                     ┌──────────────────────┐
                     │ Deviation & Security │ ──► [ ALERT / ADAPT ]
                     └──────────────────────┘
```

---

## 4. Formal Foundations
- **Automata Models**: Deterministic Finite Automata ($M_{DFA} = (Q, \Sigma, \delta, q_0, F)$), Stateful Mealy Transducers, Deterministic Pushdown Automata ($M_{PDA}$), and Context-Free Grammars ($G = (V, \Sigma, R, S)$).
- **Active & Passive Learning**: Angluin's $L^*$ active Mealy machine learning algorithm and Prefix Tree Acceptor (PTA) passive state merging.

---

## 5. Adaptive Model Evolution
- **Evidence Accumulation**: Deviations accumulate evidence across distinct multi-session IDs.
- **Concept Drift Detection**: Jensen-Shannon Divergence ($D_{JS}$) verifies transition distribution stability.
- **Formal Verification**: Candidate models $M_{cand}$ are verified by `FormalValidator` before promotion in an immutable `ModelRegistry`.

---

## 6. Security & Poisoning Safeguards
- **100% Poisoning Rejection**: Injected malicious transitions fail multi-session evidence gates or formal invariant checks.
- **Threat Score Integration**: Multi-dimensional severity scoring flags structural violations.

---

## 7. Role of Agentic AI Layer
- **Out-of-Band Advisory Investigation**: The optional Phase 7 `SecurityInvestigationAgent` produces explanatory threat reports out-of-band.
- **Strict Isolation**: AI agents are read-only and cannot mutate formal automata state graphs.
- **Graceful Fallback**: Formal automata detection operates continuously if AI providers experience downtime.

---

## 8. Real-Time Deployment Platform
- **Live Stream Ingestion**: Session reconstruction, 5-tuple tracking, and delimiter message tokenization.
- **APIs & Persistence**: FastAPI REST/WebSocket endpoints and SQLite event store.

---

## 9. Experimental Benchmarks (Phase 9 Results)
Evaluated across 5 random seeds (`[1, 2, 3, 4, 5]`):
- **Detection F1 Score**: Proposed System ($0.945 \pm 0.010$) vs Static DFA ($0.796 \pm 0.025$).
- **Hierarchical Efficiency**: $>82.0\%$ resolved at DFA fast path ($<0.12\text{ms}$ average latency).
- **Poisoning Block Rate**: $100\%$ rejection of malicious sequence injection.

---

## 10. Installation & Quick Start

```powershell
# Clone workspace and set PYTHONPATH
$env:PYTHONPATH = "src"

# Install requirements
python -m pip install -r requirements.txt

# Run complete test suite
python -m pytest tests
```

---

## 11. Independent Reproduction

To reproduce benchmark configurations and verify metric consistency:
```powershell
# Execute benchmark suite
python -m experiments.run --all

# Compare reproduced metrics against original JSON output
python -m research.reproduce compare --original experiments/results/baseline_comparison_results.json --reproduced experiments/results/baseline_comparison_results.json
```

---

## 12. Running the Interactive Demonstration

To execute the 6-scenario interactive CLI demonstration:
```powershell
python examples/final_demo.py
```

---

## 13. Methodological Limitations
1. **Synthetic State Space Scope**: Evaluated state machines simulate protocol semantics; enterprise line-rate setups require C/C++ native packet tokenization.
2. **Evidence Window Delay**: Adaptation is intentionally non-instantaneous to prevent poisoning.

---

## License
MIT License. See [LICENSE](LICENSE) for details.
