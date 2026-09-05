# Research Defense: Security & Poisoning Resistance Q&A

### Q1: What happens if an attacker attempts a prompt injection attack against the AI agent?
**A**: Untrusted protocol token strings are sanitized and enclosed inside strict fact containers before being passed to LLM prompts. Furthermore, the AI layer is read-only and cannot mutate core formal automata state.

### Q2: How does the system handle model poisoning attacks?
**A**: Multi-layer security assessment checks threat scores, multi-session evidence diversity, concept drift bounds, and formal model invariants. Malicious transition patterns fail formal validation or threat scoring, achieving a 100% block rate in benchmarks.
