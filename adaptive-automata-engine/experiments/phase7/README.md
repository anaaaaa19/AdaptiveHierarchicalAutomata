# Phase 7 Agentic AI Orchestration Experiments & Benchmarks

This directory contains reproducible controlled experiments evaluating the Phase 7 **Agentic AI Orchestration Layer** built on top of the Phase 1–6 formal adaptive engine.

---

## 1. Research Hypotheses Evaluated

- **H1**: Agentic orchestration reduces manual investigation effort.
- **H2**: AI-assisted evidence synthesis improves investigation completeness without replacing formal analysis.
- **H3**: Formal verification guards can prevent invalid AI-generated model changes.
- **H4**: A constrained tool-based agent can operate safely on untrusted protocol data when privileged actions are separated from AI reasoning.
- **H5**: AI-assisted model proposals can accelerate identification of legitimate protocol evolution while preserving formal validation.
- **H6**: The underlying formal detection system remains operational and safe when the AI layer fails.

---

## 2. Experiment Runners

| Script | Purpose | Hypotheses Tested |
| :--- | :--- | :---: |
| `agent_vs_formal.py` | Compares Mode A (Formal Only) vs Mode B (Explanation) vs Mode C (Investigation) | **H1, H2** |
| `model_proposals.py` | Evaluates AI model proposals and FormalVerificationGuard validation | **H3, H5** |
| `prompt_injection.py` | Evaluates prompt injection defense resilience on untrusted network traffic | **H4** |
| `grounding.py` | Evaluates evidence grounding and hallucination rate under incomplete evidence | **H2** |
| `efficiency.py` | Evaluates investigation step efficiency, tool execution budget, and latency | **H1** |
| `failure_modes.py` | Evaluates safe fallback to non-AI formal pipeline when AI layer is disabled | **H6** |

---

## 3. Running All Phase 7 Experiments

Run each experiment script using Python:

```powershell
$env:PYTHONPATH="src;experiments/phase7"; python experiments/phase7/agent_vs_formal.py
$env:PYTHONPATH="src;experiments/phase7"; python experiments/phase7/model_proposals.py
$env:PYTHONPATH="src;experiments/phase7"; python experiments/phase7/prompt_injection.py
$env:PYTHONPATH="src;experiments/phase7"; python experiments/phase7/grounding.py
$env:PYTHONPATH="src;experiments/phase7"; python experiments/phase7/efficiency.py
$env:PYTHONPATH="src;experiments/phase7"; python experiments/phase7/failure_modes.py
```

Generated outputs will be saved to `results/phase7/`.
