import {
  AdaptationStatusDTO,
  DriftStatusDTO,
  ExperimentSummaryDTO,
  InvestigationResultDTO,
  ProtocolEventDTO,
  ProtocolSessionDTO,
  SecurityAlertDTO,
  SystemStatusDTO,
  VersionedModelDTO,
} from '../types';

const API_BASE = '';

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });
  if (!res.ok) {
    const errorText = await res.text().catch(() => res.statusText);
    throw new Error(`API Error [${res.status}] ${endpoint}: ${errorText}`);
  }
  return res.json();
}

export const api = {
  getHealth: () => fetchJson<{ service: string; pipeline: string }>('/health'),
  getStatus: () => fetchJson<SystemStatusDTO>('/status'),
  getMetrics: () => fetchJson<Record<string, any>>('/metrics'),
  getDrift: () => fetchJson<DriftStatusDTO>('/drift'),
  getAdaptation: () => fetchJson<AdaptationStatusDTO>('/adaptation'),

  getModels: () => fetchJson<{ model_id: string; active_version: string; versions: string[] }>('/models'),
  getActiveModel: () => fetchJson<VersionedModelDTO>('/models/active'),
  activateModel: (version: string, reason: string = 'User requested activation') =>
    fetchJson<{ status: string; active_version: string }>(`/models/${version}/activate`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    }),
  rollbackModel: () =>
    fetchJson<{ status: string; active_version: string }>('/models/rollback', {
      method: 'POST',
    }),

  getSessions: () => fetchJson<{ count: number; sessions: ProtocolSessionDTO[] }>('/sessions'),
  getSessionDetails: (id: string) => fetchJson<ProtocolSessionDTO & { events: ProtocolEventDTO[] }>(`/sessions/${id}`),

  getEvents: (limit: number = 50) => fetchJson<{ count: number; total_in_store: number; events: ProtocolEventDTO[] }>(`/events?limit=${limit}`),
  getEventDetails: (id: string) => fetchJson<ProtocolEventDTO>(`/events/${id}`),

  getAlerts: () => fetchJson<{ count: number; alerts: SecurityAlertDTO[] }>('/alerts'),
  updateAlertStatus: (alertId: string, status: string) =>
    fetchJson<SecurityAlertDTO>(`/alerts/${alertId}/status`, {
      method: 'POST',
      body: JSON.stringify({ status }),
    }),

  getInvestigations: () => fetchJson<{ investigations: any[] }>('/investigations'),
  triggerInvestigation: (alertId: string) =>
    fetchJson<InvestigationResultDTO>('/investigations/run', {
      method: 'POST',
      body: JSON.stringify({ alert_id: alertId }),
    }),

  getExperimentResults: () => fetchJson<{ experiments: Record<string, ExperimentSummaryDTO> }>('/experiments/results'),
};
