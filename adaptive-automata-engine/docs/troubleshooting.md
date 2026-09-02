# Troubleshooting Guide

## Common Issues & Solutions

### 1. `ModuleNotFoundError: No module named 'adaptive_automata'`
Set `PYTHONPATH`:
```powershell
$env:PYTHONPATH="src"
```

### 2. High Event Dropping Metric
If `events_dropped` is increasing, check queue size in `DeploymentConfig`:
```python
config = DeploymentConfig(max_queue_size=10000, num_worker_threads=4)
```

### 3. AI Investigation Unavailable
If AI investigations report `FORMAL_ONLY_FALLBACK` or `UNAVAILABLE`, verify `AgentConfig.enabled` and ensure LLM provider is active or operating in Mock mode. Data plane packet monitoring will continue unaffected.
