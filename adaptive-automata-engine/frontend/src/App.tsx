import React, { useEffect, useState } from 'react';
import { ProtocolEventDTO, SecurityAlertDTO, SystemStatusDTO } from './types';

export const App: React.FC = () => {
  const [status, setStatus] = useState<SystemStatusDTO | null>(null);
  const [events, setEvents] = useState<ProtocolEventDTO[]>([]);
  const [alerts, setAlerts] = useState<SecurityAlertDTO[]>([]);
  const [activeTab, setActiveTab] = useState<'events' | 'alerts' | 'models' | 'agents'>('events');

  useEffect(() => {
    // Poll system status
    const fetchStatus = async () => {
      try {
        const res = await fetch('/status');
        if (res.ok) {
          const data = await res.json();
          setStatus(data);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Poll alerts
    const fetchAlerts = async () => {
      try {
        const res = await fetch('/alerts');
        if (res.ok) {
          const data = await res.json();
          setAlerts(data.alerts || []);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchAlerts();
  }, [activeTab]);

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', borderBottom: '1px solid #334155', paddingBottom: '16px' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 700, background: 'linear-gradient(90deg, #38bdf8, #818cf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Adaptive Automata Engine — Phase 8
          </h1>
          <p style={{ margin: '4px 0 0', color: '#94a3b8', fontSize: '14px' }}>
            Real-Time Protocol Monitoring & Formal Security Detection Platform
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <span style={{ padding: '6px 12px', borderRadius: '9999px', fontSize: '12px', fontWeight: 600, backgroundColor: status?.is_capture_active ? '#064e3b' : '#334155', color: status?.is_capture_active ? '#34d399' : '#94a3b8' }}>
            ● Capture: {status?.is_capture_active ? 'Active' : 'Offline Replay'}
          </span>
          <span style={{ padding: '6px 12px', borderRadius: '9999px', fontSize: '12px', fontWeight: 600, backgroundColor: '#1e1b4b', color: '#a78bfa' }}>
            Model: {status?.active_model_version || 'v1.0.0'}
          </span>
        </div>
      </header>

      {/* Metrics Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
        <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
          <div style={{ color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Throughput</div>
          <div style={{ fontSize: '28px', fontWeight: 700, color: '#38bdf8', marginTop: '4px' }}>
            {status?.metrics?.throughput_events_per_sec || 0} <span style={{ fontSize: '14px', color: '#64748b' }}>evt/s</span>
          </div>
        </div>
        <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
          <div style={{ color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>P95 Latency</div>
          <div style={{ fontSize: '28px', fontWeight: 700, color: '#34d399', marginTop: '4px' }}>
            {status?.metrics?.latency_ms?.p95 || 0.0} <span style={{ fontSize: '14px', color: '#64748b' }}>ms</span>
          </div>
        </div>
        <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
          <div style={{ color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Active Sessions</div>
          <div style={{ fontSize: '28px', fontWeight: 700, color: '#a78bfa', marginTop: '4px' }}>
            {status?.active_sessions_count || 0}
          </div>
        </div>
        <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '16px' }}>
          <div style={{ color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Security Alerts</div>
          <div style={{ fontSize: '28px', fontWeight: 700, color: '#f87171', marginTop: '4px' }}>
            {status?.metrics?.alerts_generated || 0}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid #334155', marginBottom: '16px' }}>
        {(['events', 'alerts', 'models', 'agents'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '10px 20px',
              backgroundColor: activeTab === tab ? '#334155' : 'transparent',
              color: activeTab === tab ? '#f8fafc' : '#94a3b8',
              border: 'none',
              borderBottom: activeTab === tab ? '2px solid #38bdf8' : '2px solid transparent',
              fontWeight: 600,
              cursor: 'pointer',
              textTransform: 'capitalize',
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Main Panel Content */}
      <div style={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '12px', padding: '20px' }}>
        {activeTab === 'events' && (
          <div>
            <h3 style={{ margin: '0 0 16px', color: '#f8fafc' }}>Live Event Stream</h3>
            <p style={{ color: '#94a3b8', fontSize: '14px' }}>
              Real-time protocol events evaluated by Level 1 DFA, Level 2 PDA, and Level 3 CFG formal engine.
            </p>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8' }}>
                    <th style={{ padding: '8px' }}>Event ID</th>
                    <th style={{ padding: '8px' }}>Session</th>
                    <th style={{ padding: '8px' }}>Symbol</th>
                    <th style={{ padding: '8px' }}>State</th>
                    <th style={{ padding: '8px' }}>Analysis Level</th>
                    <th style={{ padding: '8px' }}>Status</th>
                    <th style={{ padding: '8px' }}>Severity</th>
                    <th style={{ padding: '8px' }}>Latency</th>
                  </tr>
                </thead>
                <tbody>
                  {events.length === 0 ? (
                    <tr>
                      <td colSpan={8} style={{ padding: '24px', textAlign: 'center', color: '#64748b' }}>
                        No events logged yet. Start replay or live capture.
                      </td>
                    </tr>
                  ) : (
                    events.map(e => (
                      <tr key={e.event_id} style={{ borderBottom: '1px solid #0f172a' }}>
                        <td style={{ padding: '8px', fontFamily: 'monospace', color: '#38bdf8' }}>{e.event_id}</td>
                        <td style={{ padding: '8px' }}>{e.session_id}</td>
                        <td style={{ padding: '8px', fontWeight: 600 }}>{e.symbol}</td>
                        <td style={{ padding: '8px', color: '#a78bfa' }}>{e.formal_state}</td>
                        <td style={{ padding: '8px' }}>{e.analysis.level_used}</td>
                        <td style={{ padding: '8px' }}>{e.analysis.status}</td>
                        <td style={{ padding: '8px', color: e.security.severity === 'HIGH' ? '#f87171' : '#34d399' }}>{e.security.severity}</td>
                        <td style={{ padding: '8px' }}>{e.processing_latency_ms} ms</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'alerts' && (
          <div>
            <h3 style={{ margin: '0 0 16px', color: '#f8fafc' }}>Security Alerts</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {alerts.length === 0 ? (
                <p style={{ color: '#64748b' }}>No security alerts recorded.</p>
              ) : (
                alerts.map(alt => (
                  <div key={alt.alert_id} style={{ padding: '16px', backgroundColor: '#0f172a', border: '1px solid #f87171', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <span style={{ fontWeight: 700, color: '#f87171' }}>[{alt.severity}]</span>
                        <span style={{ fontWeight: 600 }}>{alt.alert_id}</span>
                        <span style={{ color: '#94a3b8', fontSize: '12px' }}>Session: {alt.session_id}</span>
                      </div>
                      <p style={{ margin: '4px 0 0', color: '#cbd5e1', fontSize: '13px' }}>
                        Classification: {alt.classification} | State: {alt.state} | Symbol: {alt.representative_symbol} | Count: {alt.count}
                      </p>
                    </div>
                    <button style={{ padding: '8px 16px', backgroundColor: '#3b82f6', border: 'none', borderRadius: '6px', color: '#fff', fontWeight: 600, cursor: 'pointer' }}>
                      Run AI Investigation
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {activeTab === 'models' && (
          <div>
            <h3 style={{ margin: '0 0 16px', color: '#f8fafc' }}>Model Version Registry & Adaptation</h3>
            <p style={{ color: '#94a3b8' }}>
              Active Model: <strong>{status?.active_model_version || 'v1.0.0'}</strong>
            </p>
            <p style={{ color: '#94a3b8', fontSize: '14px' }}>
              All candidate models must pass Phase 5 <code>FormalValidator</code> regression checks prior to activation.
            </p>
          </div>
        )}

        {activeTab === 'agents' && (
          <div>
            <h3 style={{ margin: '0 0 16px', color: '#f8fafc' }}>Phase 7 Agentic AI Orchestration</h3>
            <p style={{ color: '#94a3b8', fontSize: '14px' }}>
              Asynchronous agent investigations run out-of-band via <code>AgentRouter</code>.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
