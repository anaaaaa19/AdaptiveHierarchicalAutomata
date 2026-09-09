import React, { useState } from 'react';
import { SystemStatusDTO, SecurityAlertDTO, ProtocolEventDTO } from '../types';
import { StatCard } from '../components/StatCard';
import { DetailInspector } from '../components/DetailInspector';
import { Activity, ShieldAlert, Cpu, Layers, Clock, TrendingUp, AlertTriangle, ArrowRight, Eye, RefreshCw } from 'lucide-react';

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
  const [selectedInspectItem, setSelectedInspectItem] = useState<{
    type: 'event' | 'alert';
    data: any;
  } | null>(null);

  const dfaPct = status?.metrics?.dfa_resolution_percentage ?? 0.0;
  const pdaPct = status?.metrics?.pda_escalation_percentage ?? 0.0;
  const cfgPct = status?.metrics?.cfg_escalation_percentage ?? 0.0;

  const activeAlerts = alerts.filter(a => a.state === 'NEW' || a.state === 'ACKNOWLEDGED' || a.state === 'INVESTIGATING');

  return (
    <div className="space-y-5 font-sans">
      {/* Top Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-lg font-bold text-slate-100 tracking-tight">Security Operational Dashboard</h2>
          <p className="text-xs text-slate-400">
            Real-time protocol security telemetry, formal automata execution, and threat detection
          </p>
        </div>
        <div className="flex gap-2 text-xs">
          <div className="bg-slate-900 border border-slate-800 rounded px-2.5 py-1 flex items-center gap-1.5 font-mono">
            <span className="text-slate-500 font-sans text-[11px]">Adaptation:</span>
            <span className="font-semibold text-cyan-400 uppercase text-[11px]">{status?.adaptation_state || 'STABLE'}</span>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded px-2.5 py-1 flex items-center gap-1.5 font-mono">
            <span className="text-slate-500 font-sans text-[11px]">Behavior:</span>
            <span className="font-semibold text-emerald-400 uppercase text-[11px]">{status?.drift_state || 'NO_DRIFT'}</span>
          </div>
        </div>
      </div>

      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3.5">
        <StatCard
          title="Throughput"
          value={status?.metrics?.throughput_events_per_sec ?? 0}
          unit="evt/s"
          subtitle={`Total evaluated: ${status?.metrics?.total_events_processed ?? 0}`}
          icon={Activity}
          color="cyan"
        />
        <StatCard
          title="Active Sessions"
          value={status?.active_sessions_count ?? 0}
          unit="sessions"
          subtitle="Real-time 5-tuple tracking"
          icon={Layers}
          color="purple"
        />
        <StatCard
          title="Security Alerts"
          value={activeAlerts.length}
          unit="active"
          subtitle={`Total generated: ${status?.metrics?.alerts_generated ?? 0}`}
          icon={ShieldAlert}
          color={activeAlerts.length > 0 ? "rose" : "emerald"}
        />
        <StatCard
          title="Fast-Path DFA Resolution"
          value={`${dfaPct.toFixed(1)}%`}
          subtitle="O(1) Mealy Machine fast-path"
          icon={Cpu}
          color="indigo"
        />
      </div>

      {/* Main Asymmetric Operational Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left Column (2/3 width): Live Event Activity Stream */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-slate-900/90 border border-slate-800/80 rounded-lg p-4 space-y-3">
            <div className="flex justify-between items-center pb-2 border-b border-slate-800/60">
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">Live Activity Stream</h3>
              </div>
              <button
                onClick={onNavigateToMonitor}
                className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1 transition-colors"
              >
                <span>Console View</span>
                <ArrowRight className="w-3 h-3" />
              </button>
            </div>

            {/* Recent Events List */}
            <div className="space-y-1.5 font-mono text-xs max-h-[340px] overflow-y-auto pr-1">
              {recentEvents.length === 0 ? (
                <div className="py-12 text-center text-slate-500 font-sans text-xs">
                  No live events recorded yet. Click "Run Replay" in top header or start capture.
                </div>
              ) : (
                recentEvents.slice(0, 8).map((evt) => (
                  <div
                    key={evt.event_id}
                    onClick={() => setSelectedInspectItem({ type: 'event', data: evt })}
                    className="p-2.5 bg-slate-950/80 hover:bg-slate-800/60 border border-slate-800/50 rounded flex items-center justify-between cursor-pointer transition-colors"
                  >
                    <div className="flex items-center space-x-3 truncate">
                      <span className="text-[10px] text-slate-500 font-sans">
                        {new Date(evt.timestamp > 1e11 ? evt.timestamp : evt.timestamp * 1000).toLocaleTimeString()}
                      </span>
                      <span className="text-indigo-400 font-bold truncate max-w-[120px]">{evt.session_id}</span>
                      <span className="text-sky-300 font-bold">{evt.symbol}</span>
                      <span className="text-slate-500">→</span>
                      <span className="text-purple-300">{evt.formal_state}</span>
                    </div>
                    <div className="flex items-center space-x-2 shrink-0">
                      <span className="text-[10px] text-slate-400 font-sans">{evt.analysis?.level_used || 'DFA'}</span>
                      <span className={`px-1.5 py-0.2 rounded text-[10px] font-sans font-semibold ${
                        evt.analysis?.status === 'ACCEPTED' || evt.status === 'ACCEPTED'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      }`}>
                        {evt.analysis?.status || evt.status}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* System Latency & Performance Breakdown */}
          <div className="bg-slate-900/90 border border-slate-800/80 rounded-lg p-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-indigo-400" />
              <span>Processing Latency & Hierarchy Tier Breakdown</span>
            </h3>
            <div className="grid grid-cols-3 gap-3 text-center">
              <div className="p-3 bg-slate-950 rounded border border-slate-800">
                <span className="text-[10px] text-slate-500 font-bold uppercase block">Fast-Path DFA</span>
                <span className="text-base font-mono font-bold text-cyan-400">{dfaPct.toFixed(1)}%</span>
              </div>
              <div className="p-3 bg-slate-950 rounded border border-slate-800">
                <span className="text-[10px] text-slate-500 font-bold uppercase block">PDA Escalation</span>
                <span className="text-base font-mono font-bold text-amber-400">{pdaPct.toFixed(1)}%</span>
              </div>
              <div className="p-3 bg-slate-950 rounded border border-slate-800">
                <span className="text-[10px] text-slate-500 font-bold uppercase block">CFG Escalation</span>
                <span className="text-base font-mono font-bold text-rose-400">{cfgPct.toFixed(1)}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column (1/3 width): Attention Required & Model Status */}
        <div className="space-y-4">
          {/* Attention Required Card */}
          <div className="bg-slate-900/90 border border-slate-800/80 rounded-lg p-4 space-y-3">
            <div className="flex justify-between items-center pb-2 border-b border-slate-800/60">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">Attention Required</h3>
              </div>
              <button
                onClick={onNavigateToAlerts}
                className="text-xs text-rose-400 hover:text-rose-300 font-semibold flex items-center gap-1 transition-colors"
              >
                <span>View All ({alerts.length})</span>
              </button>
            </div>

            <div className="space-y-2">
              {activeAlerts.length === 0 ? (
                <p className="py-6 text-center text-xs text-slate-500">No active security alerts pending review.</p>
              ) : (
                activeAlerts.slice(0, 4).map((alt) => (
                  <div
                    key={alt.alert_id}
                    onClick={() => setSelectedInspectItem({ type: 'alert', data: alt })}
                    className="p-3 bg-slate-950/80 border border-rose-500/20 hover:border-rose-500/40 rounded flex items-start justify-between cursor-pointer transition-colors"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className={`px-1.5 py-0.2 rounded text-[9px] font-bold ${
                          alt.severity === 'CRITICAL' || alt.severity === 'HIGH'
                            ? 'bg-rose-500/20 text-rose-400'
                            : 'bg-amber-500/20 text-amber-400'
                        }`}>
                          {alt.severity}
                        </span>
                        <span className="text-xs font-bold text-slate-200">{alt.classification}</span>
                      </div>
                      <p className="text-[11px] text-slate-400 font-mono">Session: {alt.session_id}</p>
                    </div>
                    <Eye className="w-3.5 h-3.5 text-slate-500 hover:text-slate-300 shrink-0" />
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Model Status Card */}
          <div className="bg-slate-900/90 border border-slate-800/80 rounded-lg p-4 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-indigo-400" />
              <span>Active Model Registry</span>
            </h3>

            <div className="bg-slate-950 p-3 rounded border border-slate-800 font-mono text-xs space-y-1.5">
              <div className="flex justify-between">
                <span className="text-slate-500 font-sans">Active Version</span>
                <span className="text-indigo-400 font-bold">{status?.active_model_version || 'v1.0.0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-sans">Model Status</span>
                <span className="text-emerald-400 font-bold font-sans text-[11px]">VALIDATED</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-sans">Formal Engine</span>
                <span className="text-slate-300 font-sans text-[11px]">O(1) Mealy Machine</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right-Side Reusable Detail Inspector Drawer */}
      <DetailInspector
        isOpen={!!selectedInspectItem}
        onClose={() => setSelectedInspectItem(null)}
        title={selectedInspectItem?.type === 'event' ? 'Event Inspection' : 'Security Alert Inspection'}
        subtitle={selectedInspectItem?.data?.event_id || selectedInspectItem?.data?.alert_id}
        type={selectedInspectItem?.type || 'event'}
        data={selectedInspectItem?.data}
        onUpdateAlertStatus={(alertId, st) => {
          setSelectedInspectItem(null);
          onNavigateToAlerts();
        }}
      />
    </div>
  );
};
