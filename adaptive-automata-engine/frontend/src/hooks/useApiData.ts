import { useEffect, useState } from 'react';
import { api } from '../api/client';
import {
  AdaptationStatusDTO,
  DriftStatusDTO,
  ProtocolSessionDTO,
  SecurityAlertDTO,
  SystemStatusDTO,
  VersionedModelDTO,
} from '../types';

export function useSystemStatus(pollIntervalMs: number = 2000) {
  const [status, setStatus] = useState<SystemStatusDTO | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const fetchStatus = async () => {
      try {
        const data = await api.getStatus();
        if (isMounted) {
          setStatus(data);
          setError(null);
          setLoading(false);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Failed to fetch status');
          setLoading(false);
        }
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, pollIntervalMs);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [pollIntervalMs]);

  return { status, loading, error };
}

export function useAlerts(pollIntervalMs: number = 3000) {
  const [alerts, setAlerts] = useState<SecurityAlertDTO[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const reload = async () => {
    try {
      const data = await api.getAlerts();
      setAlerts(data.alerts || []);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch alerts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    reload();
    const interval = setInterval(reload, pollIntervalMs);
    return () => clearInterval(interval);
  }, [pollIntervalMs]);

  return { alerts, loading, error, reload };
}

export function useActiveModel() {
  const [activeModel, setActiveModel] = useState<VersionedModelDTO | null>(null);
  const [modelsList, setModelsList] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const reload = async () => {
    try {
      const modelData = await api.getActiveModel();
      const listData = await api.getModels();
      setActiveModel(modelData);
      setModelsList(listData.versions || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    reload();
  }, []);

  return { activeModel, modelsList, loading, reload };
}

export function useSessions(pollIntervalMs: number = 4000) {
  const [sessions, setSessions] = useState<ProtocolSessionDTO[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchSess = async () => {
      try {
        const data = await api.getSessions();
        setSessions(data.sessions || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchSess();
    const interval = setInterval(fetchSess, pollIntervalMs);
    return () => clearInterval(interval);
  }, [pollIntervalMs]);

  return { sessions, loading };
}

export function useDriftAndAdaptation() {
  const [drift, setDrift] = useState<DriftStatusDTO | null>(null);
  const [adaptation, setAdaptation] = useState<AdaptationStatusDTO | null>(null);

  const reload = async () => {
    try {
      const [dData, aData] = await Promise.all([api.getDrift(), api.getAdaptation()]);
      setDrift(dData);
      setAdaptation(aData);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    reload();
    const interval = setInterval(reload, 3000);
    return () => clearInterval(interval);
  }, []);

  return { drift, adaptation, reload };
}
