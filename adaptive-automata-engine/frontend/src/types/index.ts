export interface ProtocolEventDTO {
  event_id: string;
  session_id: string;
  protocol: string;
  direction: string;
  symbol: string;
  formal_state: string;
  model_version: string;
  timestamp: string;
  processing_latency_ms: number;
  raw_payload_snippet: string;
  analysis: {
    status: string;
    level_used: string;
    reason: string;
    confidence_score: number;
  };
  security: {
    classification: string;
    severity: string;
    risk_score: number;
    reason_codes: string[];
  };
}

export interface SecurityAlertDTO {
  alert_id: string;
  session_id: string;
  model_version: string;
  severity: string;
  classification: string;
  status: string;
  risk_score: number;
  timestamp: string;
  representative_symbol: string;
  state: string;
  count: number;
}

export interface SystemStatusDTO {
  active_model_version: string;
  queue_depth: number;
  is_capture_active: boolean;
  active_sessions_count: number;
  metrics: {
    uptime_seconds: number;
    packets_processed: number;
    messages_processed: number;
    events_processed: number;
    throughput_events_per_sec: number;
    alerts_generated: number;
    events_dropped: number;
    queue_depth: number;
    latency_ms: {
      avg: number;
      p50: number;
      p95: number;
      p99: number;
    };
    escalations: {
      dfa_resolved: number;
      pda_escalations: number;
      cfg_escalations: number;
    };
  };
}
