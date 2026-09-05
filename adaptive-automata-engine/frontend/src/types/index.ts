export interface MetricsSummaryDTO {
  throughput_events_per_sec?: float;
  dfa_fast_path_pct?: float;
  pda_escalation_pct?: float;
  cfg_escalation_pct?: float;
  deviation_count?: number;
  alerts_generated?: number;
  latency_ms?: {
    mean?: number;
    p50?: number;
    p95?: number;
    p99?: number;
  };
  [key: string]: any;
}

export type float = number;

export interface SystemStatusDTO {
  status?: string;
  active_model_version?: string;
  queue_depth?: number;
  is_capture_active?: boolean;
  active_sessions_count?: number;
  metrics?: MetricsSummaryDTO;
}

export interface SecurityAssessmentDTO {
  risk_level?: string;
  threat_score?: number;
  classification?: string;
  reason_codes?: string[];
}

export interface ProtocolEventDTO {
  event_id: string;
  session_id: string;
  timestamp: string;
  model_version: string;
  protocol?: string;
  input_symbol: string;
  output_symbol?: str;
  state_from: string;
  state_to: string;
  analysis_level?: string;
  status: string;
  security_assessment?: SecurityAssessmentDTO;
}

export type str = string;

export interface SecurityAlertDTO {
  alert_id: string;
  session_id: string;
  timestamp: string;
  severity: "HIGH" | "MEDIUM" | "LOW" | string;
  status: "NEW" | "ACKNOWLEDGED" | "INVESTIGATING" | "RESOLVED" | "FALSE_POSITIVE" | string;
  reason_codes?: string[];
  triggering_symbol?: string;
  current_state?: string;
  model_version?: string;
  evidence?: Record<string, any>;
}

export interface VersionedModelDTO {
  model_id: string;
  version: str;
  source: string;
  num_states: number;
  num_transitions: number;
  created_at: string;
}

export interface ProtocolSessionDTO {
  session_id: string;
  state: string;
  created_at?: string;
  last_activity?: string;
  message_count?: number;
  risk_score?: number;
}

export interface InvestigationResultDTO {
  investigation_id: string;
  classification: string;
  action_recommendation: string;
  explanation: string;
  steps_executed: number;
  tools_used: string[];
}

export interface DriftStatusDTO {
  drift_status: string;
  js_divergence_threshold: number;
  observed_divergence: number;
  total_drift_evaluations: number;
}

export interface AdaptationStatusDTO {
  model_id: string;
  active_version: string;
  version_history: string[];
  adaptation_state: string;
  evidence_threshold: number;
  total_adaptations_promoted: number;
}

export interface ExperimentSummaryDTO {
  experiment: string;
  timestamp: string;
  seeds: number[];
  summary: Record<string, Record<string, { mean: number; std_dev: number }>>;
}
