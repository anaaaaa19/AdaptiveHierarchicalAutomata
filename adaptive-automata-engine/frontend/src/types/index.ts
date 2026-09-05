export type float = number;
export type str = string;

export interface MetricsSummaryDTO {
  throughput_events_per_sec?: number;
  dfa_fast_path_pct?: number;
  dfa_resolution_percentage?: number;
  pda_escalation_pct?: number;
  pda_escalation_percentage?: number;
  cfg_escalation_pct?: number;
  cfg_escalation_percentage?: number;
  total_events_processed?: number;
  deviation_count?: number;
  alerts_generated?: number;
  latency_ms?: {
    mean?: number;
    avg?: number;
    p50?: number;
    p95?: number;
    p99?: number;
    max?: number;
  };
  [key: string]: any;
}

export interface SystemStatusDTO {
  status?: string;
  active_model_version?: string;
  queue_depth?: number;
  is_capture_active?: boolean;
  active_sessions_count?: number;
  adaptation_state?: string;
  drift_state?: string;
  metrics?: MetricsSummaryDTO;
}

export interface SecurityAssessmentDTO {
  risk_level?: string;
  threat_score?: number;
  classification?: string;
  severity?: string;
  reason_codes?: string[];
}

export interface ProtocolAnalysisDTO {
  level_used: string;
  status: string;
  reason?: string;
}

export interface ProtocolEventDTO {
  event_id: string;
  session_id: string;
  timestamp: number;
  model_version: string;
  protocol: string;
  input_symbol?: string;
  symbol: string;
  output_symbol?: string;
  state_from?: string;
  state_to?: string;
  formal_state: string;
  analysis_level?: string;
  status: string;
  analysis: ProtocolAnalysisDTO;
  security_assessment?: SecurityAssessmentDTO;
  security: {
    classification: string;
    severity: string;
  };
  processing_latency_ms: number;
}

export interface SecurityAlertDTO {
  alert_id: string;
  session_id: string;
  timestamp?: number;
  created_at: number;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | string;
  status?: string;
  state: "NEW" | "ACKNOWLEDGED" | "INVESTIGATING" | "RESOLVED" | "FALSE_POSITIVE" | string;
  classification: string;
  representative_symbol: string;
  count: number;
  reason_codes?: string[];
  triggering_symbol?: string;
  current_state?: string;
  model_version?: string;
  evidence?: Record<string, any>;
}

export interface ModelVersionDTO {
  version_id: string;
  model_id?: string;
  version?: string;
  source?: string;
  state_count: number;
  transition_count: number;
  status: string;
  is_active: boolean;
  validation_result: string;
  created_at: number;
}

export type VersionedModelDTO = ModelVersionDTO;

export interface AutomataGraphDTO {
  model_version: string;
  states: string[];
  initial_state: string;
  accepting_states: string[];
  transitions: Array<{
    source: string;
    symbol: string;
    target: string;
    output?: string;
  }>;
}

export interface SessionDTO {
  session_id: string;
  protocol: string;
  status: 'ACTIVE' | 'CLOSED' | string;
  state?: string;
  current_state: string;
  event_count: number;
  max_level_escalation: 'DFA' | 'PDA' | 'CFG' | string;
  created_at?: number;
  last_activity: number;
  message_count?: number;
  risk_score?: number;
}

export type ProtocolSessionDTO = SessionDTO;

export interface AdaptationStateDTO {
  active_model_version: string;
  candidate_model_version?: string;
  evidence_count?: number;
  novelty_threshold?: number;
  drift_metric?: number;
  validation_status?: string;
  policy_status?: string;
}

export type AdaptationStatusDTO = AdaptationStateDTO;

export interface DriftDataDTO {
  drift_state: string;
  drift_score: number;
  window_size?: number;
  model_version?: string;
  time_series?: Array<{
    timestamp: number;
    drift_score: number;
  }>;
}

export type DriftStatusDTO = DriftDataDTO;

export interface AIInvestigationDTO {
  investigation_id: string;
  alert_id: string;
  status: 'RUNNING' | 'COMPLETED' | 'FAILED' | string;
  classification?: string;
  confidence_score?: number;
  findings?: string;
  recommendations?: string[];
  tool_activity?: Array<{
    tool_name: string;
    result_summary: string;
  }>;
  created_at: number;
}

export type InvestigationResultDTO = AIInvestigationDTO;

export interface ExperimentResultsDTO {
  experiments: Record<string, any>;
  baseline_comparison?: any;
  unseen_behavior?: any;
  legitimate_evolution?: any;
  poisoning_resistance?: any;
  hierarchy_efficiency?: any;
  performance_metrics?: any;
  ablation_study?: any;
}

export type ExperimentSummaryDTO = ExperimentResultsDTO;
