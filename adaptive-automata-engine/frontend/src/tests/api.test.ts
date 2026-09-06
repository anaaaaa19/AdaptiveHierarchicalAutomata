import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  fetchStatus,
  fetchEvents,
  fetchAlerts,
  fetchModels,
  fetchAdaptationState,
  updateAlertStatus,
  triggerInvestigation,
} from '../api/client';

describe('Frontend API Client Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('fetchStatus requests /status and returns system status DTO', async () => {
    const mockStatus = {
      is_capture_active: true,
      active_model_version: 'v1.0.0',
      active_sessions_count: 5,
      adaptation_state: 'STABLE',
      drift_state: 'NO_DRIFT',
      metrics: {
        throughput_events_per_sec: 150,
        latency_ms: { avg: 0.5, p95: 1.2, max: 3.4 },
        total_events_processed: 1200,
        alerts_generated: 2,
        dfa_resolution_percentage: 95.0,
        pda_escalation_percentage: 4.0,
        cfg_escalation_percentage: 1.0,
      },
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockStatus,
    });

    const status = await fetchStatus();
    expect(globalThis.fetch).toHaveBeenCalledWith('/status', expect.any(Object));
    expect(status.active_model_version).toBe('v1.0.0');
    expect(status.metrics?.throughput_events_per_sec).toBe(150);
  });

  it('fetchEvents requests /events with parameters', async () => {
    const mockEvents = [
      {
        event_id: 'EVT-001',
        session_id: 'SESS-10',
        protocol: 'HTTP',
        symbol: 'GET',
        formal_state: 'REQUEST',
        analysis: { level_used: 'DFA', status: 'ACCEPTED' },
        security: { classification: 'BENIGN', severity: 'LOW' },
        model_version: 'v1.0.0',
        timestamp: 1600000000,
        processing_latency_ms: 0.4,
      },
    ];

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ events: mockEvents }),
    });

    const events = await fetchEvents(50, 'SESS-10');
    expect(globalThis.fetch).toHaveBeenCalledWith('/events?limit=50&session_id=SESS-10', expect.any(Object));
    expect(events).toHaveLength(1);
    expect(events[0].event_id).toBe('EVT-001');
  });

  it('updateAlertStatus posts status change to /alerts/{id}/status', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ success: true, alert_id: 'ALT-100', state: 'ACKNOWLEDGED' }),
    });

    const result = await updateAlertStatus('ALT-100', 'ACKNOWLEDGED');
    expect(globalThis.fetch).toHaveBeenCalledWith(
      '/alerts/ALT-100/status',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ status: 'ACKNOWLEDGED', state: 'ACKNOWLEDGED' }),
      })
    );
    expect(result.state).toBe('ACKNOWLEDGED');
  });

  it('triggerInvestigation posts alert ID to /investigations/trigger', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ investigation_id: 'INV-55', alert_id: 'ALT-100', status: 'RUNNING' }),
    });

    const res = await triggerInvestigation('ALT-100');
    expect(globalThis.fetch).toHaveBeenCalledWith(
      '/investigations/trigger',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ alert_id: 'ALT-100' }),
      })
    );
    expect(res.investigation_id).toBe('INV-55');
  });
});
