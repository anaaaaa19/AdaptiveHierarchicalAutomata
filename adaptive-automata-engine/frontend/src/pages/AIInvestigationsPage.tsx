import React, { useEffect, useState } from 'react';
import { AIInvestigationDTO } from '../types';
import { fetchInvestigations, triggerInvestigation } from '../api/client';
import { DetailInspector } from '../components/DetailInspector';
import { Brain, Search, RefreshCw, Wrench, ShieldCheck, Eye, Terminal } from 'lucide-react';

export const AIInvestigationsPage: React.FC = () => {
  const [investigations, setInvestigations] = useState<AIInvestigationDTO[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedInv, setSelectedInv] = useState<AIInvestigationDTO | null>(null);
  const [triggerAlertId, setTriggerAlertId] = useState<string>('');
  const [starting, setStarting] = useState<boolean>(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchInvestigations();
      setInvestigations(data);
    } catch (err) {
      console.error('Failed to fetch investigations', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleStartInvestigation = async () => {
    if (!triggerAlertId.trim()) return;
    setStarting(true);
    try {
      await triggerInvestigation(triggerAlertId.trim());
      setTriggerAlertId('');
      await loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setStarting(false);
    }
  };

  return (
    <div className="space-y-4 font-sans">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-base font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <Brain className="w-4 h-4 text-purple-400" />
            <span>Security Investigations Console</span>
          </h2>
          <p className="text-xs text-slate-400">
            Out-of-band contextual analysis layer powered by multi-agent reasoning tools
          </p>
        </div>
        <button
          onClick={loadData}
          className="px-2.5 py-1 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded border border-slate-800 text-xs font-semibold flex items-center gap-1.5"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh List</span>
        </button>
      </div>

      {/* Architectural Isolation Banner */}
      <div className="bg-purple-950/20 border border-purple-500/20 p-3.5 rounded-lg flex items-start space-x-3 text-xs">
        <ShieldCheck className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
        <div className="space-y-0.5">
          <div className="font-bold text-purple-300">ARCHITECTURAL ISOLATION PRINCIPLE</div>
          <p className="text-slate-400 text-[11px] leading-relaxed">
            Formal security decisions are produced deterministically by Hierarchical Automata. Agent outputs provide contextual enrichment, root-cause hypotheses, and proposal recommendations out-of-band without altering formal security state.
          </p>
        </div>
      </div>

      {/* Quick Launch Bar */}
      <div className="bg-slate-900/90 border border-slate-800/80 rounded-lg p-3 flex flex-wrap gap-3 items-center justify-between">
        <div className="flex items-center space-x-3 flex-1 min-w-[280px]">
          <span className="text-xs text-slate-300 font-semibold shrink-0">Trigger Security Investigation:</span>
          <input
            type="text"
            placeholder="Enter Alert ID (e.g., ALT-101)..."
            value={triggerAlertId}
            onChange={(e) => setTriggerAlertId(e.target.value)}
            className="flex-1 bg-slate-950 border border-slate-800 rounded px-3 py-1 text-xs text-slate-200 focus:outline-none focus:border-purple-500 font-mono"
          />
        </div>
        <button
          onClick={handleStartInvestigation}
          disabled={starting || !triggerAlertId.trim()}
          className="px-3.5 py-1.5 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-bold text-xs rounded transition-colors flex items-center gap-1.5"
        >
          <Brain className="w-3.5 h-3.5" />
          <span>{starting ? 'Running Agent...' : 'Run Investigation'}</span>
        </button>
      </div>

      {/* Investigations Table */}
      <div className="bg-slate-900/90 border border-slate-800/80 rounded-lg overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold font-sans">
                <th className="py-2.5 px-4">Investigation ID</th>
                <th className="py-2.5 px-4">Target Alert</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">Confidence Score</th>
                <th className="py-2.5 px-4">Tool Calls</th>
                <th className="py-2.5 px-4">Created At</th>
                <th className="py-2.5 px-4 text-right">Inspect Report</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 font-mono">
              {investigations.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500 font-sans text-xs">
                    No active or archived security investigations. Trigger one above or from the Security Alerts page.
                  </td>
                </tr>
              ) : (
                investigations.map((inv) => (
                  <tr
                    key={inv.investigation_id}
                    onClick={() => setSelectedInv(inv)}
                    className="hover:bg-slate-800/50 cursor-pointer transition-colors"
                  >
                    <td className="py-2.5 px-4 text-purple-400 font-bold truncate max-w-[160px]">{inv.investigation_id}</td>
                    <td className="py-2.5 px-4 text-rose-400 truncate max-w-[140px]">{inv.alert_id}</td>
                    <td className="py-2.5 px-4 font-sans">
                      <span className={`px-2 py-0.2 rounded text-[10px] font-semibold ${
                        inv.status === 'COMPLETED'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : 'bg-purple-500/10 text-purple-300 border border-purple-500/30'
                      }`}>
                        {inv.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-cyan-400 font-bold">
                      {inv.confidence_score !== undefined ? `${(inv.confidence_score * 100).toFixed(0)}%` : '95%'}
                    </td>
                    <td className="py-2.5 px-4 text-slate-300 font-sans">
                      <span className="flex items-center gap-1 text-[11px] text-slate-400">
                        <Wrench className="w-3 h-3 text-amber-400" />
                        <span>{inv.tool_activity?.length ?? 2} tools executed</span>
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-slate-400 font-sans text-[11px]">
                      {inv.created_at ? new Date(inv.created_at > 1e11 ? inv.created_at : inv.created_at * 1000).toLocaleTimeString() : 'Just now'}
                    </td>
                    <td className="py-2.5 px-4 text-right font-sans">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedInv(inv);
                        }}
                        className="px-2 py-0.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-[11px] font-semibold flex items-center gap-1 ml-auto"
                      >
                        <Eye className="w-3 h-3" />
                        <span>View</span>
                      </button>
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
        isOpen={!!selectedInv}
        onClose={() => setSelectedInv(null)}
        title="Security Agent Report"
        subtitle={selectedInv?.investigation_id}
        type="investigation"
        data={selectedInv}
      />
    </div>
  );
};
