# Adaptive Automata Engine

**Adaptive Hierarchical Automata Engine for Real-Time Detection of Previously Unseen Protocol Deviations**

Phase 7: Agentic AI Orchestration Layer (AI Proposes, Formal System Verifies, Policy Validates, Human/Control Approves, Model May Update)

---

## Overview

The Adaptive Automata Engine is a research-grade formal methods, protocol learning, and cybersecurity framework. Phase 7 adds an AI-assisted orchestration layer for protocol investigation, anomaly investigation, candidate model proposals, and human-readable explanations.

### Complete Research & Security Pipeline

```
                         PROTOCOL TRAFFIC
                                │
                                ▼
                           TOKENIZER
                                │
                                ▼
                    HIERARCHICAL FORMAL ENGINE
                         /          \
                       DFA         PDA/CFG
                         \          /
                          ▼        ▼
                         FORMAL RESULT
                                │
                                ▼
                         SECURITY ENGINE
                                │
                                ▼
                       SECURITY ASSESSMENT
                                │
                                ▼
                         AGENTIC ROUTER
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
         PROTOCOL           SECURITY            MODEL
         ANALYST            ANALYST             AGENT
              │                 │                 │
              └─────────────────┼─────────────────┘
                                ▼
                         EVIDENCE SYNTHESIS
                                │
                                ▼
                           AI HYPOTHESIS
                                │
                                ▼
                       CandidateModelProposal
                                │
                                ▼
                    FORMAL VERIFICATION GUARD
                                │
                         ┌──────┴──────┐
                         │             │
                       FAIL          PASS
                         │             │
                         ▼             ▼
                      REJECT      PHASE 5 POLICY
                                       │
                                       ▼
                                HUMAN / CONTROL
                                       │
                                       ▼
                                MODEL UPDATER
                                       │
                                       ▼
                                  MODEL vN+1
```

---

## Hypotheses & Benchmark Results

| Hypothesis | Description | Result | Status |
| :--- | :--- | :--- | :---: |
| **H1** | Agentic orchestration reduces manual investigation effort | Average step count = 4.0 (Budget = 10), Mean Latency = 0.0114 ms | **VERIFIED** |
| **H2** | AI-assisted evidence synthesis improves investigation completeness without replacing formal analysis | 100% of facts grounded in formal tool outputs; **Hallucination Rate = 0.0%** | **VERIFIED** |
| **H3** | Formal verification guards can prevent invalid AI-generated model changes | Legitimate proposal passed guard; Malformed proposal rejected with 2 explicit errors | **VERIFIED** |
| **H4** | A constrained tool-based agent can operate safely on untrusted protocol data when privileged actions are separated from AI reasoning | 4/4 adversarial prompt injection payloads sanitized; **Prompt Injection Success Rate = 0.0%** | **VERIFIED** |
| **H5** | AI-assisted model proposals can accelerate identification of legitimate protocol evolution while preserving formal validation | Valid proposal formulated for `CAPABILITIES` extension and passed `FormalVerificationGuard` | **VERIFIED** |
| **H6** | The underlying formal detection system remains operational and safe when the AI layer fails | AI layer `DISABLED` mode safely fell back to `FORMAL_ONLY_FALLBACK` execution | **VERIFIED** |

---

## Directory Structure

```
adaptive-automata-engine/
│
├── src/
│   └── adaptive_automata/
│       ├── core/               # Phase 1: DFA, Mealy Machine, PDA, CFG Parser, State
│       ├── protocol/           # Phase 1/3: ProtocolSession, TraceLoader, Tokenizers, SUT
│       ├── learning/           # Phase 2/3: L* Learner, Passive Inference, Hybrid Learner
│       ├── analysis/           # Phase 4: Hierarchical Escalation Controller, AnalysisResult
│       ├── adaptation/         # Phase 5: NoveltyDetector, EvidenceStore, FormalValidator, Policy
│       ├── security/           # Phase 6: BehavioralAnalyzer, SessionRiskAggregator, SecurityAssessment
│       │
│       └── agents/             # Phase 7: Agentic AI Orchestration Layer
│           ├── agent.py        # BaseAgent bounded execution & prompt injection defense
│           ├── config.py       # AgentConfig & AgentMode (DISABLED, ADVISORY, ASSISTED, CONTROLLED_AUTOMATION)
│           ├── schemas.py      # AgentObservation (FACTS), AgentHypothesis (AI SPECULATION), CandidateModelProposal
│           ├── state.py        # AgentStateTracker lifecycle state machine
│           ├── llm.py          # LLMProvider & MockLLMProvider (100% offline, zero external LLM API dependency)
│           ├── tools.py        # AgentTool, ToolPermission (READ_ONLY, PROPOSAL, MUTATING) & ToolRegistry
│           ├── memory.py       # AgentMemory & InvestigationRecord
│           ├── audit.py        # AgentAuditLogger & AgentAuditEvent
│           ├── planner.py      # InvestigationPlanner
│           ├── guard.py        # FormalVerificationGuard
│           ├── protocol_agent.py# ProtocolAnalystAgent
│           ├── security_agent.py# SecurityInvestigationAgent
│           ├── model_agent.py  # ModelProposalAgent
│           ├── explanation_agent.py# ExplanationAgent
│           └── router.py       # AgentRouter
│
├── tests/
│   ├── agents/                 # Phase 7 agent test suite (15 modular test files)
│   ├── security/               # Phase 6 security test suite
│   └── test_*.py               # Phase 1-5 test suite (Total: 106 unit tests passing)
│
├── experiments/
│   ├── phase5/                 # Phase 5 adaptation experiment runners
│   ├── phase6/                 # Phase 6 cybersecurity benchmark runners
│   └── phase7/                 # Phase 7 agentic AI benchmark runners
│       ├── README.md
│       ├── agent_vs_formal.py
│       ├── model_proposals.py
│       ├── prompt_injection.py
│       ├── grounding.py
│       ├── efficiency.py
│       └── failure_modes.py
│
└── results/
    ├── phase5/
    ├── phase6/
    └── phase7/                 # Phase 7 JSON benchmark metrics & agent research report
        ├── experiment_1_agent_vs_formal.json
        ├── experiment_2_model_proposals.json
        ├── experiment_3_prompt_injection.json
        ├── experiment_4_grounding.json
        ├── experiment_5_efficiency.json
        ├── experiment_6_failure_modes.json
        └── agent_report.md
```

---

## Installation & Setup

### Running the Complete Test Suite
Run the full 106-test suite using pytest:

```powershell
$env:PYTHONPATH="src"; python -m pytest tests
```

### Running Phase 8 Real-Time Deployment & Benchmarks
Execute Phase 8 deployment server and benchmark experiments:

```powershell
# Run full deployment test suite
$env:PYTHONPATH="src"; python -m pytest tests/deployment

# Run PCAP Replay Benchmark
$env:PYTHONPATH="src;experiments/phase8"; python experiments/phase8/replay_benchmark.py

# Start FastAPI Deployment Platform Server
$env:PYTHONPATH="src"; python -m api.app
```

---

## Roadmap

- **Phase 1 (Complete)**: Formal protocol modeling core.
- **Phase 2 (Complete)**: Active Automata Learning (L* algorithm).
- **Phase 3 (Complete)**: Trace-Based Protocol Inference & Hybrid Learner.
- **Phase 4 (Complete)**: Hierarchical Formal-Analysis Engine (DFA $\to$ PDA $\to$ CFG).
- **Phase 5 (Complete)**: Adaptive Model Management Subsystem.
- **Phase 6 (Complete)**: Cybersecurity Detection Layer.
- **Phase 7 (Complete)**: Agentic AI Orchestration Layer.
- **Phase 8 (Complete)**: Real-Time Network Deployment & Production Monitoring Platform (PCAP replay, 5-tuple session reconstruction, packet processor, bounded backpressure queue, SQLite event store, AlertManager, FastAPI REST/WS API, React dashboard, zero-downtime model hot-reloads).

