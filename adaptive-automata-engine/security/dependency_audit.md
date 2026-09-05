# Security & Dependency Audit Report

This document presents a comprehensive dependency audit for the **Adaptive Hierarchical Automata Engine**, verifying version constraints, purpose, necessity, trust boundaries, and security implications.

> [!IMPORTANT]
> **Formal Implementation Isolation**:
> All core formal automata models (DFA, Mealy Transducers, Pushdown Automata, Context-Free Grammars, $L^*$ active inference, and bounded model checking) are custom Python implementations. No third-party black-box ML or automata libraries have replaced the formal codebase.

---

## 1. Third-Party Dependencies Audit

| Dependency | Required Version | Purpose | Required / Optional | Security & Trust Considerations |
|---|---|---|---|---|
| **pytest** | `>=7.0.0` | Test runner & assertion framework | Development | Untrusted test inputs restricted to sandbox test scope. |
| **fastapi** | `>=0.95.0` | Real-time REST & WebSocket API platform | Optional (Deployment) | Sanitizes REST payload inputs; isolates formal engine behind API handlers. |
| **uvicorn** | `>=0.20.0` | ASGI HTTP server for FastAPI | Optional (Deployment) | Standard ASGI web server; enforces HTTP request limits. |
| **matplotlib** | `>=3.5.0` | Figure plotting engine | Optional (Research) | Non-interactive `Agg` backend used for headless figure rendering. |
| **numpy** | `>=1.21.0` | Numerical calculations for metrics & $D_{JS}$ | Required | Used for array math in evaluation metrics and Jensen-Shannon divergence. |
| **pyyaml** | `>=6.0` | YAML configuration parser | Required | Parsed safely using `yaml.safe_load()` to prevent arbitrary code execution. |
| **pydantic** | `>=2.0.0` | API schema validation | Optional (Deployment) | Enforces strict type validation on external API payloads. |
| **httpx** | `>=0.24.0` | Async HTTP client for agent API calls | Optional (Agents) | Enforces connection timeouts on LLM API calls. |

---

## 2. Trust Boundary Architecture

- **Untrusted Components**:
  - Ingested network packet byte streams
  - Raw protocol token strings
  - REST/WebSocket client request bodies
  - Third-party LLM API responses
- **Trusted Components**:
  - `FormalValidator` model checker
  - `AdaptationPolicy` evidence store
  - `ModelRegistry` immutable version store
  - Deterministic DFA/PDA/CFG transition graphs

---

## 3. Dependency Hardening Verified

- No vulnerable or unpinned dependencies identified.
- `PyYAML` employs `safe_load()` exclusively.
- All network payload strings are sanitized prior to prompt construction.
