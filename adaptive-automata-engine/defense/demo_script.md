# Research Defense: Final Demonstration Script

To execute the interactive 6-scenario demonstration:
```bash
$env:PYTHONPATH="src"; python examples/final_demo.py
```

### Demonstration Scenarios Overview
1. **Scenario 1**: Known valid protocol sequence $\rightarrow$ Resolved at DFA fast path ($<0.1\text{ms}$).
2. **Scenario 2**: Unseen legitimate behavior (Protocol v2) $\rightarrow$ Escalated & evidence collected.
3. **Scenario 3**: Confirmed structural anomaly $\rightarrow$ Anomaly flagged & security alert logged.
4. **Scenario 4**: Malicious transition injection attack $\rightarrow$ Poisoning attempts blocked ($100\%$ rejection).
5. **Scenario 5**: Validated model evolution $\rightarrow$ Threshold met, candidate validated, model promoted to v2.0.0.
6. **Scenario 6**: AI investigation failure fallback $\rightarrow$ Agent layer isolated; formal engine operates uninterrupted.
