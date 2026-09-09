import React, { useState } from 'react';
import { SecurityAlertDTO } from '../types';
import { updateAlertStatus, triggerInvestigation } from '../api/client';
import { DetailInspector } from '../components/DetailInspector';
import { ShieldAlert, Filter, RefreshCw, Eye, Brain } from 'lucide-react';

interface AlertsPageProps {
  alerts: SecurityAlertDTO[];
  onRefresh: () => void;
  onNavigateToInvestigations?: () => void;
}

export const AlertsPage: React.FC<AlertsPageProps> = ({
  alerts,
  onRefresh,
  onNavigateToInvestigations,
}) => {
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [selectedAlert, setSelectedAlert] = useState<SecurityAlertDTO | null>(null);
  const [updating, setUpdating] = useState<boolean>(false);
  const [invitingAI, setInvitingAI] = useState<boolean>(false);

  const statuses: SecurityAlertDTO['state'][] = [
    'NEW',
    'ACKNOWLEDGED',
    'INVESTIGATING',
    'RESOLVED',
    'FALSE_POSITIVE',
  ];

  const filteredAlerts = alerts.filter((alt) => {
    const matchesSev = severityFilter === 'ALL' || alt.severity === severityFilter;
    const matchesStat = statusFilter === 'ALL' || alt.state === statusFilter;
    return matchesSev && matchesStat;
  });

  const handleStatusChange = async (alertId: string, newStatus: SecurityAlertDTO['state']) => {
    setUpdating(true);
    try {
      await updateAlertStatus(alertId, newStatus);
      onRefresh();
      if (selectedAlert?.alert_id === alertId) {
        setSelectedAlert((prev) => (prev ? { ...prev, state: newStatus } : null));
      }
    } catch (err) {
      console.error('Failed to update alert status', err);
    } finally {
      setUpdating(false);
    }
  };

  const handleRunAIInvestigation = async (alertId: string) => {
    setInvitingAI(true);
    try {
      await triggerInvestigation(alertId);
      if (onNavigateToInvestigations) {
        onNavigateToInvestigations();
      }
    } catch (err) {
      console.error('Failed to trigger AI investigation', err);
    } finally {
      setInvitingAI(false);
    }
  };

  return (
    <div className="space-y-4 font-sans">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-base font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-rose-400" />
            <span>Security Alerts & Threat Management</span>
          </h2>
          <p className="text-xs text-slate-400">
            Real-time security alerts classified by formal automata verification engine
          </p>
        </div>
        <button
          onClick={onRefresh}
          className="px-2.5 py-1 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded border border-slate-800 text-xs font-semibold flex items-center gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Alerts</span>
        </button>
      </div>

      {/* Filtering Toolbar */}
      <div className="bg-slate-900/90 border border-slate-800/80 rounded-lg p-3 flex flex-wrap items-center justify-between gap-3 text-xs">
        {/* Severity filter */}
        <div className="flex items-center space-x-2">
          <Filter className="w-3.5 h-3.5 text-slate-500" />
          <span className="text-[11px] font-semibold text-slate-400">Severity:</span>
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`px-2.5 py-0.5 rounded text-[11px] font-semibold transition-colors ${
                severityFilter === sev
                  ? 'bg-rose-600 text-white font-bold'
                  : 'bg-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>

        {/* Status filter */}
        <div className="flex items-center space-x-2">
          <span className="text-[11px] font-semibold text-slate-400">Status:</span>
          {['ALL', ...statuses].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-colors ${
                statusFilter === st
                  ? 'bg-indigo-600 text-white font-bold'
                  : 'bg-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Alerts Table */}
      <div className="bg-slate-900/90 border border-slate-800/80 rounded-lg overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold font-sans">
                <th className="py-2.5 px-4">Severity</th>
                <th className="py-2.5 px-4">Alert ID</th>
                <th className="py-2.5 px-4">Session</th>
                <th className="py-2.5 px-4">Classification</th>
                <th className="py-2.5 px-4">State</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">Timestamp</th>
                <th className="py-2.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 font-mono">
              {filteredAlerts.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500 font-sans text-xs">
                    No security alerts found matching selected filters.
                  </td>
                </tr>
              ) : (
                filteredAlerts.map((alt) => (
                  <tr
                    key={alt.alert_id}
                    onClick={() => setSelectedAlert(alt)}
                    className="hover:bg-slate-800/50 cursor-pointer transition-colors"
                  >
                    <td className="py-2.5 px-4 font-sans">
                      <span className={`px-2 py-0.2 text-[10px] font-bold rounded ${
                        alt.severity === 'CRITICAL' || alt.severity === 'HIGH'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : alt.severity === 'MEDIUM'
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          : 'bg-sky-500/20 text-sky-400 border border-sky-500/30'
                      }`}>
                        {alt.severity}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-rose-400 font-bold truncate max-w-[160px]">{alt.alert_id}</td>
                    <td className="py-2.5 px-4 text-purple-300 truncate max-w-[160px]">{alt.session_id}</td>
                    <td className="py-2.5 px-4 font-sans text-slate-200 font-medium">{alt.classification}</td>
                    <td className="py-2.5 px-4 text-purple-300">{alt.state}</td>
                    <td className="py-2.5 px-4 font-sans">
                      <span className={`px-2 py-0.2 rounded text-[10px] font-semibold ${
                        alt.state === 'NEW'
                          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                          : alt.state === 'RESOLVED'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/30'
                      }`}>
                        {alt.state}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-slate-400 text-[11px] font-sans">
                      {alt.timestamp ? (typeof alt.timestamp === 'string' ? alt.timestamp : new Date(alt.timestamp > 1e11 ? alt.timestamp : alt.timestamp * 1000).toLocaleTimeString()) : (alt.created_at ? new Date(alt.created_at > 1e11 ? alt.created_at : alt.created_at * 1000).toLocaleTimeString() : 'Just now')}
                    </td>
                    <td className="py-2.5 px-4 text-right font-sans" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center space-x-1.5 justify-end">
                        <button
                          onClick={() => handleRunAIInvestigation(alt.alert_id)}
                          disabled={invitingAI}
                          className="px-2 py-0.5 bg-purple-600 hover:bg-purple-500 text-white font-semibold rounded text-[10px] flex items-center gap-1 transition-colors"
                        >
                          <Brain className="w-3 h-3" />
                          <span>Investigate</span>
                        </button>
                        <button
                          onClick={() => setSelectedAlert(alt)}
                          className="px-2 py-0.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[10px] font-semibold flex items-center gap-1"
                        >
                          <Eye className="w-3 h-3" />
                          <span>Inspect</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detail Inspector Drawer */}
      <DetailInspector
        isOpen={!!selectedAlert}
        onClose={() => setSelectedAlert(null)}
        title="Security Alert Inspection"
        subtitle={selectedAlert?.alert_id}
        type="alert"
        data={selectedAlert}
        onUpdateAlertStatus={handleStatusChange}
        onTriggerAI={handleRunAIInvestigation}
      />
    </div>
  );
};
