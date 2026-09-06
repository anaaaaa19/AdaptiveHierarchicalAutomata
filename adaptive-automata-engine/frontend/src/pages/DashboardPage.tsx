import React from 'react';
import { SystemStatusDTO, SecurityAlertDTO, ProtocolEventDTO } from '../types';
import { StatCard } from '../components/StatCard';
import { CascadePieChart } from '../components/CascadePieChart';
import { Activity, ShieldAlert, Cpu, Layers, Clock, TrendingUp, AlertTriangle } from 'lucide-react';

interface DashboardPageProps {
  status: SystemStatusDTO | null;
  alerts: SecurityAlertDTO[];
  recentEvents: ProtocolEventDTO[];
  onNavigateToAlerts: () => void;
  onNavigateToMonitor: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  status,
  alerts,
  recentEvents,
  onNavigateToAlerts,
  onNavigateToMonitor,
}) => {
  const dfaPct = status?.metrics?.dfa_resolution_percentage ?? 0.0;
  const pdaPct = status?.metrics?.pda_escalation_percentage ?? 0.0;
  const cfgPct = status?.metrics?.cfg_escalation_percentage ?? 0.0;

  const unackAlerts = alerts.filter(a => a.state === 'NEW').length;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100">SOC Operational Dashboard</h2>
          <p className="text-xs text-slate-400">
            Real-time formal metrics, hierarchical automata breakdown, and security alert status
          </p>
        </div>
        <div className="flex gap-3 text-xs">
          <div className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 flex items-center gap-2">
            <span className="text-slate-400">Adaptation State:</span>
            <span className="font-semibold text-cyan-400 uppercase">{status?.adaptation_state || 'STABLE'}</span>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 flex items-center gap-2">
            <span className="text-slate-400">Drift State:</span>
            <span className="font-semibold text-emerald-400 uppercase">{status?.drift_state || 'NO_DRIFT'}</span>
          </div>
        </div>
      </div>

      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Throughput"
          value={status?.metrics?.throughput_events_per_sec ?? 0}
          unit="evt/s"
          subtitle={`Total evaluated events: ${status?.metrics?.total_events_processed ?? 0}`}
          icon={Activity}
          color="cyan"
        />
        <StatCard
          title="P95 Latency"
          value={status?.metrics?.latency_ms?.p95 ?? 0.0}
          unit="ms"
          subtitle={`Avg: ${status?.metrics?.latency_ms?.avg ?? 0.0} ms | Max: ${status?.metrics?.latency_ms?.max ?? 0.0} ms`}
          icon={Clock}
          color="emerald"
        />
        <StatCard
          title="Active Sessions"
          value={status?.active_sessions_count ?? 0}
          unit="sessions"
          subtitle="Monitored protocol state channels"
          icon={Layers}
          color="purple"
        />
        <StatCard
          title="Security Alerts"
          value={status?.metrics?.alerts_generated ?? alerts.length}
          unit={`(${unackAlerts} New)`}
          subtitle="Formal security anomalies detected"
          icon={ShieldAlert}
          color={alerts.length > 0 ? 'rose' : 'emerald'}
        />
      </div>

      {/* Main Grid: Hierarchical Breakdown + Alerts/Events Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Hierarchical Cascading Breakdown */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-sky-400" />
                <span>Hierarchical Automata Cascade</span>
              </h3>
              <span className="text-[11px] text-slate-500 font-mono">Level 1 → Level 3</span>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              95%+ traffic resolved at O(1) Level 1 (DFA/Mealy). Deviations escalate to Level 2 (PDA) and structural anomalies to Level 3 (CFG).
            </p>
            <CascadePieChart dfaPct={dfaPct} pdaPct={pdaPct} cfgPct={cfgPct} />
          </div>

          <div className="mt-4 pt-4 border-t border-slate-800 grid grid-cols-3 gap-2 text-center text-xs">
            <div className="bg-slate-950 p-2 rounded-lg border border-slate-800">
              <div className="text-[10px] text-slate-500 font-bold uppercase">L1: DFA</div>
              <div className="text-sm font-bold text-sky-400">{dfaPct}%</div>
            </div>
            <div className="bg-slate-950 p-2 rounded-lg border border-slate-800">
              <div className="text-[10px] text-slate-500 font-bold uppercase">L2: PDA</div>
              <div className="text-sm font-bold text-amber-400">{pdaPct}%</div>
            </div>
            <div className="bg-slate-950 p-2 rounded-lg border border-slate-800">
              <div className="text-[10px] text-slate-500 font-bold uppercase">L3: CFG</div>
              <div className="text-sm font-bold text-rose-400">{cfgPct}%</div>
            </div>
          </div>
        </div>

        {/* Live Alerts & System Overview */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Security Alerts */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5">
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                <h3 className="text-sm font-bold text-slate-200">Recent Security Alerts</h3>
              </div>
              <button
                onClick={onNavigateToAlerts}
                className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold"
              >
                View All Alerts ({alerts.length}) →
              </button>
            </div>

            {alerts.length === 0 ? (
              <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-6 text-center text-slate-500 text-xs">
                No active security alerts recorded. Formal protocol boundaries are clean.
              </div>
            ) : (
              <div className="space-y-2.5">
                {alerts.slice(0, 3).map((alt) => (
                  <div
                    key={alt.alert_id}
                    className="p-3 bg-slate-950/80 border border-rose-500/30 rounded-lg flex items-center justify-between hover:border-rose-500/50 transition-colors"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-rose-500/20 text-rose-400 border border-rose-500/40">
                          {alt.severity}
                        </span>
                        <span className="font-mono text-xs font-semibold text-slate-200">{alt.alert_id}</span>
                        <span className="text-[11px] text-slate-400">Session: {alt.session_id}</span>
                      </div>
                      <p className="text-xs text-slate-400">
                        {alt.classification} — State <code className="text-purple-300">{alt.state}</code>, symbol <code className="text-sky-300">{alt.representative_symbol}</code>
                      </p>
                    </div>
                    <span className="px-2 py-1 text-[11px] font-mono rounded bg-slate-800 text-slate-300">
                      {alt.state}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Live Recent Events Preview */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                <Activity className="w-4 h-4 text-cyan-400" />
                <span>Recent Evaluated Events</span>
              </h3>
              <button
                onClick={onNavigateToMonitor}
                className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold"
              >
                Open Live Monitor →
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                    <th className="py-2">Event ID</th>
                    <th className="py-2">Session</th>
                    <th className="py-2">Symbol</th>
                    <th className="py-2">Level</th>
                    <th className="py-2">Status</th>
                    <th className="py-2">Latency</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {recentEvents.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-4 text-center text-slate-500 font-sans">
                        No events logged yet. Waiting for live packet capture or replay stream.
                      </td>
                    </tr>
                  ) : (
                    recentEvents.slice(0, 5).map((evt) => (
                      <tr key={evt.event_id} className="hover:bg-slate-800/40">
                        <td className="py-2 text-cyan-400">{evt.event_id}</td>
                        <td className="py-2 text-slate-300">{evt.session_id}</td>
                        <td className="py-2 font-bold text-slate-200">{evt.symbol}</td>
                        <td className="py-2 text-amber-400">{evt.analysis.level_used}</td>
                        <td className="py-2">
                          <span className={`px-1.5 py-0.5 rounded text-[10px] ${
                            evt.analysis.status === 'ACCEPTED'
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                              : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                          }`}>
                            {evt.analysis.status}
                          </span>
                        </td>
                        <td className="py-2 text-slate-400">{evt.processing_latency_ms} ms</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
