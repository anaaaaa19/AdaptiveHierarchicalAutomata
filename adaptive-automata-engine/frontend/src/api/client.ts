import {
  SystemStatusDTO,
  ProtocolEventDTO,
  SecurityAlertDTO,
  SessionDTO,
  ModelVersionDTO,
  AutomataGraphDTO,
  AdaptationStateDTO,
  DriftDataDTO,
  AIInvestigationDTO,
  ExperimentResultsDTO,
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

// Named API Helper Exports
export const fetchStatus = async (): Promise<SystemStatusDTO> => {
  return fetchJson<SystemStatusDTO>('/status');
};

export const fetchEvents = async (limit: number = 50, sessionId?: string): Promise<ProtocolEventDTO[]> => {
  const url = `/events?limit=${limit}${sessionId ? `&session_id=${sessionId}` : ''}`;
  const res = await fetchJson<{ events?: ProtocolEventDTO[] } | ProtocolEventDTO[]>(url);
  if (Array.isArray(res)) return res;
  return res.events || [];
};

export const fetchAlerts = async (): Promise<SecurityAlertDTO[]> => {
  const res = await fetchJson<{ alerts?: SecurityAlertDTO[] } | SecurityAlertDTO[]>('/alerts');
  if (Array.isArray(res)) return res;
  return res.alerts || [];
};

export const updateAlertStatus = async (alertId: string, state: SecurityAlertDTO['state']): Promise<any> => {
  return fetchJson(`/alerts/${alertId}/status`, {
    method: 'POST',
    body: JSON.stringify({ status: state, state }),
  });
};

export const fetchSessions = async (): Promise<SessionDTO[]> => {
  const res = await fetchJson<{ sessions?: SessionDTO[] } | SessionDTO[]>('/sessions');
  if (Array.isArray(res)) return res;
  return res.sessions || [];
};

export const fetchModels = async (): Promise<ModelVersionDTO[]> => {
  const res = await fetchJson<{ models?: ModelVersionDTO[] } | ModelVersionDTO[]>('/models');
  if (Array.isArray(res)) return res;
  return res.models || [];
};

export const fetchModelGraph = async (versionId: string): Promise<AutomataGraphDTO> => {
  return fetchJson<AutomataGraphDTO>(`/models/${versionId}/graph`);
};

export const fetchAdaptationState = async (): Promise<AdaptationStateDTO> => {
  return fetchJson<AdaptationStateDTO>('/adaptation');
};

export const promoteCandidateModel = async (candidateVersion: string): Promise<any> => {
  return fetchJson('/adaptation/promote', {
    method: 'POST',
    body: JSON.stringify({ candidate_version: candidateVersion }),
  });
};

export const fetchDriftMetrics = async (): Promise<DriftDataDTO> => {
  return fetchJson<DriftDataDTO>('/drift');
};

export const fetchInvestigations = async (): Promise<AIInvestigationDTO[]> => {
  const res = await fetchJson<{ investigations?: AIInvestigationDTO[] } | AIInvestigationDTO[]>('/investigations');
  if (Array.isArray(res)) return res;
  return res.investigations || [];
};

export const triggerInvestigation = async (alertId: string): Promise<AIInvestigationDTO> => {
  return fetchJson<AIInvestigationDTO>('/investigations/trigger', {
    method: 'POST',
    body: JSON.stringify({ alert_id: alertId }),
  });
};

export const fetchExperimentResults = async (): Promise<ExperimentResultsDTO> => {
  return fetchJson<ExperimentResultsDTO>('/experiments/results');
};

export const startCapture = async (): Promise<any> => {
  return fetchJson('/capture/start', { method: 'POST' });
};

export const stopCapture = async (): Promise<any> => {
  return fetchJson('/capture/stop', { method: 'POST' });
};

export const triggerReplay = async (): Promise<any> => {
  return fetchJson('/replay/trigger', { method: 'POST' });
};

export const api = {
  fetchStatus,
  fetchEvents,
  fetchAlerts,
  updateAlertStatus,
  fetchSessions,
  fetchModels,
  fetchModelGraph,
  fetchAdaptationState,
  promoteCandidateModel,
  fetchDriftMetrics,
  fetchInvestigations,
  triggerInvestigation,
  fetchExperimentResults,
  startCapture,
  stopCapture,
  triggerReplay,
};

