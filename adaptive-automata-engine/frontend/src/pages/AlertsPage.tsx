import React, { useState } from 'react';
import { SecurityAlertDTO } from '../types';
import { updateAlertStatus, triggerInvestigation } from '../api/client';
import { Modal } from '../components/Modal';
import { AlertTriangle, Filter, CheckSquare, Brain, ShieldAlert, Check, RefreshCw } from 'lucide-react';

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
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
            <span>Formal Security Alerts & Anomaly Center</span>
          </h2>
          <p className="text-xs text-slate-400">
            Real-time protocol security alerts classified by Level 1-3 formal automata verification engine
          </p>
        </div>
        <button
          onClick={onRefresh}
          className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 text-xs font-semibold flex items-center gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Alerts</span>
        </button>
      </div>

      {/* Filtering Toolbar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
        {/* Severity filter */}
        <div className="flex items-center space-x-2">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-xs text-slate-400 font-medium">Severity:</span>
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`px-2.5 py-1 rounded text-xs font-semibold ${
                severityFilter === sev
                  ? 'bg-rose-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>

        {/* Status filter */}
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400 font-medium">Status:</span>
          {['ALL', ...statuses].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-2 py-1 rounded text-[11px] font-semibold ${
                statusFilter === st
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Alerts Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Alert ID</th>
                <th className="py-3 px-4">Session</th>
                <th className="py-3 px-4">Classification</th>
                <th className="py-3 px-4">Formal State</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {filteredAlerts.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-500 font-sans">
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
                    <td className="py-3 px-4 font-sans">
                      <span className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                        alt.severity === 'CRITICAL' || alt.severity === 'HIGH'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                          : alt.severity === 'MEDIUM'
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                          : 'bg-sky-500/20 text-sky-400 border border-sky-500/40'
                      }`}>
                        {alt.severity}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-rose-400 font-bold">{alt.alert_id}</td>
                    <td className="py-3 px-4 text-slate-300">{alt.session_id}</td>
                    <td className="py-3 px-4 font-sans text-slate-200 font-medium">{alt.classification}</td>
                    <td className="py-3 px-4 text-purple-300">{alt.state}</td>
                    <td className="py-3 px-4 font-sans">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        alt.state === 'NEW'
                          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                          : alt.state === 'RESOLVED'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/30'
                      }`}>
                        {alt.state}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-400 text-[11px] font-sans">
                      {new Date(alt.created_at * 1000).toLocaleTimeString()}
                    </td>
                    <td className="py-3 px-4 text-right font-sans" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => handleRunAIInvestigation(alt.alert_id)}
                        disabled={invitingAI}
                        className="px-2.5 py-1 bg-purple-600 hover:bg-purple-500 text-white font-semibold rounded text-[11px] flex items-center gap-1 ml-auto transition-colors"
                      >
                        <Brain className="w-3.5 h-3.5" />
                        <span>AI Analysis</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Alert Details & Status Transition Modal */}
      {selectedAlert && (
        <Modal
          isOpen={!!selectedAlert}
          onClose={() => setSelectedAlert(null)}
          title={`Security Alert Inspection — ${selectedAlert.alert_id}`}
        >
          <div className="space-y-5 font-sans">
            {/* Formal Security Banner */}
            <div className="bg-rose-950/40 border border-rose-500/40 p-4 rounded-lg flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold text-rose-300">FORMAL SECURITY DECISION</h4>
                <p className="text-xs text-rose-200/80 mt-1">
                  Classification: <strong>{selectedAlert.classification}</strong> | Severity: <strong>{selectedAlert.severity}</strong>
                </p>
                <p className="text-xs text-slate-400 mt-1 font-mono">
                  State: {selectedAlert.state} | Symbol: {selectedAlert.representative_symbol} | Count: {selectedAlert.count}
                </p>
              </div>
            </div>

            {/* Reason Codes */}
            {selectedAlert.reason_codes && selectedAlert.reason_codes.length > 0 && (
              <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-2">
                <h5 className="text-xs font-bold text-slate-300 uppercase">Reason Codes</h5>
                <div className="flex flex-wrap gap-2">
                  {selectedAlert.reason_codes.map((rc, idx) => (
                    <span key={idx} className="px-2 py-1 bg-slate-900 border border-slate-700 text-amber-300 font-mono text-xs rounded">
                      {rc}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Change Status Controls */}
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-3">
              <h5 className="text-xs font-bold text-slate-300 uppercase">Update Alert SOC Status</h5>
              <div className="flex flex-wrap gap-2">
                {statuses.map((st) => (
                  <button
                    key={st}
                    disabled={updating || selectedAlert.state === st}
                    onClick={() => handleStatusChange(selectedAlert.alert_id, st)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1 ${
                      selectedAlert.state === st
                        ? 'bg-emerald-600 text-white font-bold cursor-default'
                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    {selectedAlert.state === st && <Check className="w-3.5 h-3.5" />}
                    <span>{st}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Trigger AI Action */}
            <div className="pt-2 flex justify-between items-center">
              <span className="text-xs text-slate-500">
                AI investigation runs out-of-band to inspect context without altering formal decisions.
              </span>
              <button
                onClick={() => handleRunAIInvestigation(selectedAlert.alert_id)}
                disabled={invitingAI}
                className="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold text-xs rounded-lg shadow-md flex items-center gap-2"
              >
                <Brain className="w-4 h-4" />
                <span>{invitingAI ? 'Spawning Agent...' : 'Trigger AI Investigation'}</span>
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
