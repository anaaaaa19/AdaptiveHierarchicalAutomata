# System Threat Model & Security Architecture

This document defines the formal security threat model for the **Adaptive Hierarchical Automata Engine**, detailing assets, attacker capabilities, attack surfaces, trusted boundaries, and mitigation mechanisms.

---

## 1. System Assets & Security Boundaries

### Protected Assets
1. **Automata State Models**: Active DFA/Mealy, PDA, and CFG transition graphs stored in `ModelRegistry`.
2. **Detection Integrity**: Ability to detect protocol deviations, structural anomalies, and zero-day exploits without false negatives.
3. **Engine Availability**: Continuous real-time packet ingestion and detection processing without memory exhaustion or CPU starvation.
4. **Alert & Forensic Integrity**: Uncorrupted security event logs and investigation reports.

### Trust Boundaries
- **Trusted Core**: Automata transition engines (`core/`), Hierarchical Analyzer (`analysis/`), Adaptation Engine (`adaptation/`), Security Analyzer (`security/`), and Model Registry (`models/`).
- **Untrusted External Inputs**: Live network packet payloads, raw protocol token streams, REST API client requests, and third-party AI provider API responses.

---

## 2. Attacker Capabilities & Threat Profiles

| Threat Category | Attacker Capability | Attacker Goal | Target Subsystem |
|---|---|---|---|
| **Model Poisoning** | Sends repeated malicious transition patterns mixed into normal session traffic. | Trick adaptive model into learning and accepting malicious sequence paths. | `AdaptationEngine`, `EvidenceStore` |
| **Novelty Flooding** | Generates a high volume of random, unique unknown protocol token sequences. | Deplete evidence store memory and trigger excessive candidate generation. | `NoveltyDetector`, `EvidenceStore` |
| **Session Flooding** | Spawns thousands of concurrent unclosed network sessions. | Deplete memory (`MAX_SESSIONS`) and cause denial of service. | `SessionManager`, `RealTimePipeline` |
| **Deep Structural Attack** | Injects deeply nested or extremely long protocol message sequences. | Cause stack overflow or algorithmic complexity explosion during CFG parsing. | `PushdownAutomaton`, `CFGParser` |
| **Prompt Injection** | Injects adversarial text instructions inside protocol token strings (e.g. `"HELLO; DROP ALERTS"`). | Manipulate LLM investigation agents into suppressing alerts. | `AIInvestigationAgent`, `AgenticLayer` |
| **Invalid Activation** | Attempts to force activation of an unvalidated or corrupt candidate model via API. | Disable formal detection or introduce backdoors. | `ModelRegistry`, `DeploymentPipeline` |

---

## 3. Mitigation Mechanisms & Safety Enforcements

### 3.1 Poisoning Resistance
- **Multi-Session Diversity Requirement**: Adaptation requires evidence accumulated across multiple distinct session IDs.
- **Formal Model Checker (`FormalValidator`)**: Candidate models must pass bounded state invariants. Injected transitions breaking state invariants are rejected regardless of presentation frequency.
- **Threat Score Gate**: Behavioral threat scores above threshold automatically block candidate generation.

### 3.2 Resource Bounding & Flood Defense
- **Strict Configuration Bounds**:
  - `MAX_SESSIONS = 10,000` concurrent active sessions.
  - `MAX_SESSION_DURATION = 3,600` seconds timeout.
  - `MAX_MESSAGE_SIZE = 65,536` bytes per message.
  - `MAX_QUEUE_SIZE = 5,000` events queue depth.
  - `MAX_EVENTS_IN_MEMORY = 50,000` stored events.
- Session pruning automatically evicts stale/inactive sessions.

### 3.3 AI Agent Containment & Fallback Isolation
- **Read-Only Formal Interface**: AI agents cannot directly alter DFA/PDA/CFG transition tables.
- **Sanitization**: Protocol tokens passed to AI prompts are sanitized and enclosed in strict data blocks.
- **Provider Failure Isolation**: If the AI provider times out or returns an error, formal automata detection continues running at 100% capacity and generates standard formal alerts.

---

## 4. Out-of-Scope Threats

1. **Hardware-Level Side Channels**: Physical probe attacks or CPU cache timing side channels.
2. **Kernel / Hypervisor Compromise**: Direct memory modification of Python runtime memory by root-level OS malware.
3. **Network Physical Layer Jamming**: Physical Ethernet/Wireless layer denial of service.
