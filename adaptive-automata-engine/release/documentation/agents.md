# Agentic AI Layer & Threat Investigation Architecture

This document describes the optional agentic investigation layer implemented in `adaptive_automata.agents`.

---

## 1. Agent Architecture

The agentic layer provides contextual threat investigation for formal security alerts:
- **`AIInvestigationAgent`**: Triggered on high-severity formal security alerts.
- **Tools**: Inspect session history, query model versions, analyze transition frequencies, format forensic summaries.
- **Isolation Principle**: The agentic layer operates strictly out-of-band and cannot mutate core formal automata state.
- **Graceful Fallback**: If LLM API fails or times out, formal alerts are logged directly without disruption.
