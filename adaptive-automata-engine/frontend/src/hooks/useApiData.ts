import { useEffect, useState, useCallback } from 'react';
import {
  SystemStatusDTO,
  ProtocolEventDTO,
  SecurityAlertDTO,
  ModelVersionDTO,
  SessionDTO,
} from '../types';
import {
  fetchStatus,
  fetchEvents,
  fetchAlerts,
  fetchModels,
  fetchSessions,
  fetchDriftMetrics,
  fetchAdaptationState,
} from '../api/client';

export interface UseApiDataReturn {
  status: SystemStatusDTO | null;
  recentEvents: ProtocolEventDTO[];
  alerts: SecurityAlertDTO[];
  models: ModelVersionDTO[];
  sessions: SessionDTO[];
  loading: boolean;
  error: string | null;
  refreshAll: () => Promise<void>;
  appendEvent: (event: ProtocolEventDTO) => void;
}

export function useApiData(): UseApiDataReturn {
  const [status, setStatus] = useState<SystemStatusDTO | null>(null);
  const [recentEvents, setRecentEvents] = useState<ProtocolEventDTO[]>([]);
  const [alerts, setAlerts] = useState<SecurityAlertDTO[]>([]);
  const [models, setModels] = useState<ModelVersionDTO[]>([]);
  const [sessions, setSessions] = useState<SessionDTO[]>([]);

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const refreshAll = useCallback(async () => {
    try {
      setError(null);
      const [sysStatus, evts, alrts, mdls, sess] = await Promise.allSettled([
        fetchStatus(),
        fetchEvents(100),
        fetchAlerts(),
        fetchModels(),
        fetchSessions(),
      ]);

      if (sysStatus.status === 'fulfilled') setStatus(sysStatus.value);
      if (evts.status === 'fulfilled') setRecentEvents(evts.value);
      if (alrts.status === 'fulfilled') setAlerts(alrts.value);
      if (mdls.status === 'fulfilled') setModels(mdls.value);
      if (sess.status === 'fulfilled') setSessions(sess.value);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch backend system data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshAll();
    const interval = setInterval(refreshAll, 3000);
    return () => clearInterval(interval);
  }, [refreshAll]);

  const appendEvent = useCallback((event: ProtocolEventDTO) => {
    setRecentEvents((prev) => [event, ...prev.slice(0, 99)]);
  }, []);

  return {
    status,
    recentEvents,
    alerts,
    models,
    sessions,
    loading,
    error,
    refreshAll,
    appendEvent,
  };
}
