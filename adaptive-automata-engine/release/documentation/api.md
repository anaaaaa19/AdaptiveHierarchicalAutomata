# API Reference

## Health & Telemetry
- `GET /health`: Health status of capture, storage, pipeline, active model, and AI.
- `GET /status`: Live pipeline status and metrics summary.
- `GET /metrics`: Latency percentiles (P50, P95, P99), throughput, and escalation stats.

## Models
- `GET /models`: List all versioned models.
- `GET /models/active`: Details of current active version.
- `POST /models/{version}/activate`: Protected endpoint to request hot-reload activation.
- `POST /models/rollback`: Rollback to previous active model version.

## Sessions & Events
- `GET /sessions`: List active protocol sessions.
- `GET /events`: Paginated query of stored events.
- `WS /ws/stream`: Real-time WebSocket event stream.

## Alerts & Investigations
- `GET /alerts`: List security alerts.
- `POST /alerts/{alert_id}/status`: Update alert status.
- `POST /investigations/run`: Trigger asynchronous Phase 7 AI investigation.
