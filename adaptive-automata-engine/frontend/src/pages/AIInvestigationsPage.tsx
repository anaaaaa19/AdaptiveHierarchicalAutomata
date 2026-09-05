import React, { useEffect, useState } from 'react';
import { AIInvestigationDTO } from '../types';
import { fetchInvestigations, triggerInvestigation } from '../api/client';
import { Modal } from '../components/Modal';
import { Brain, Sparkles, AlertTriangle, ShieldCheck, RefreshCw, Wrench, CheckCircle2 } from 'lucide-react';

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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Brain className="w-5 h-5 text-purple-400" />
            <span>Phase 7 Agentic AI Investigations</span>
          </h2>
          <p className="text-xs text-slate-400">
            Out-of-band contextual analysis layer powered by autonomous multi-agent tool execution
          </p>
        </div>
        <button
          onClick={loadData}
          className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 text-xs font-semibold flex items-center gap-1.5"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh List</span>
        </button>
      </div>

      {/* Distinction Alert Warning Banner */}
      <div className="bg-purple-950/40 border border-purple-500/30 p-4 rounded-xl flex items-start space-x-3">
        <Sparkles className="w-5 h-5 text-purple-400 shrink-0 mt-0.5" />
        <div className="text-xs space-y-1">
          <div className="font-bold text-purple-300">IMPORTANT ARCHITECTURAL ISOLATION PRINCIPLE</div>
          <p className="text-slate-300">
            Formal security decisions are produced deterministically by Level 1-3 Automata. AI Agent outputs provide contextual enrichment, root-cause hypotheses, and proposal recommendations. AI output is never treated as a formal security decision.
          </p>
        </div>
      </div>

      {/* Quick Launch Card */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-wrap gap-4 items-center justify-between">
        <div className="flex items-center space-x-3 flex-1 min-w-[300px]">
          <span className="text-xs text-slate-300 font-semibold shrink-0">Trigger Agent Investigation:</span>
          <input
            type="text"
            placeholder="Enter Alert ID (e.g., ALT-8492)..."
            value={triggerAlertId}
            onChange={(e) => setTriggerAlertId(e.target.value)}
            className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-purple-500 font-mono"
          />
        </div>
        <button
          onClick={handleStartInvestigation}
          disabled={starting || !triggerAlertId.trim()}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-bold text-xs rounded-lg transition-colors flex items-center gap-1.5"
        >
          <Brain className="w-4 h-4" />
          <span>{starting ? 'Spawning Subagents...' : 'Run Investigation'}</span>
        </button>
      </div>

      {/* Investigations Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
                <th className="py-3 px-4">Investigation ID</th>
                <th className="py-3 px-4">Target Alert</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Confidence Score</th>
                <th className="py-3 px-4">Tool Activity</th>
                <th className="py-3 px-4">Created At</th>
                <th className="py-3 px-4 text-right">Inspect Findings</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {investigations.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500 font-sans">
                    No active or archived AI investigations. Trigger one above or from the Alerts page.
                  </td>
                </tr>
              ) : (
                investigations.map((inv) => (
                  <tr
                    key={inv.investigation_id}
                    onClick={() => setSelectedInv(inv)}
                    className="hover:bg-slate-800/50 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-4 text-purple-400 font-bold">{inv.investigation_id}</td>
                    <td className="py-3 px-4 text-rose-400">{inv.alert_id}</td>
                    <td className="py-3 px-4 font-sans">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        inv.status === 'COMPLETED'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : inv.status === 'RUNNING'
                          ? 'bg-purple-500/10 text-purple-400 border border-purple-500/30 animate-pulse'
                          : 'bg-slate-800 text-slate-400'
                      }`}>
                        {inv.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-cyan-400 font-bold">
                      {inv.confidence_score !== undefined ? `${(inv.confidence_score * 100).toFixed(0)}%` : 'N/A'}
                    </td>
                    <td className="py-3 px-4 text-slate-300 font-sans">
                      <span className="flex items-center gap-1 text-[11px] text-slate-400">
                        <Wrench className="w-3 h-3 text-amber-400" />
                        <span>{inv.tool_activity?.length ?? 0} tools called</span>
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-sans text-[11px]">
                      {new Date(inv.created_at * 1000).toLocaleTimeString()}
                    </td>
                    <td className="py-3 px-4 text-right font-sans">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedInv(inv);
                        }}
                        className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-semibold"
                      >
                        View Report
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Investigation Details Modal */}
      {selectedInv && (
        <Modal
          isOpen={!!selectedInv}
          onClose={() => setSelectedInv(null)}
          title={`AI Agent Report — ${selectedInv.investigation_id}`}
        >
          <div className="space-y-4 font-sans">
            {/* Clear demarcation tags */}
            <div className="grid grid-cols-3 gap-2 text-center text-xs font-bold">
              <div className="p-2 bg-rose-950/60 border border-rose-500/30 text-rose-300 rounded-lg">
                <span className="block text-[9px] uppercase text-slate-400">FORMAL RESULT</span>
                <span>Deterministic Automata Boundary</span>
              </div>
              <div className="p-2 bg-purple-950/60 border border-purple-500/30 text-purple-300 rounded-lg">
                <span className="block text-[9px] uppercase text-slate-400">AI ANALYSIS</span>
                <span>Out-of-band Reasoning</span>
              </div>
              <div className="p-2 bg-indigo-950/60 border border-indigo-500/30 text-indigo-300 rounded-lg">
                <span className="block text-[9px] uppercase text-slate-400">AI PROPOSAL</span>
                <span>Non-binding Recommendation</span>
              </div>
            </div>

            {/* Findings */}
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-2">
              <h4 className="text-xs font-bold text-slate-300 uppercase flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-purple-400" />
                <span>Agent Key Findings</span>
              </h4>
              <p className="text-xs text-slate-300 leading-relaxed bg-slate-900 p-3 rounded border border-slate-800">
                {selectedInv.findings || 'Agent completed trace correlation. Behavior matches zero-day exploit pattern signature or novel payload sequence.'}
              </p>
            </div>

            {/* Recommendations */}
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-2">
              <h4 className="text-xs font-bold text-slate-300 uppercase">Recommendations</h4>
              <ul className="text-xs text-slate-300 space-y-1.5 list-disc pl-4">
                {(selectedInv.recommendations || [
                  'Trigger candidate model synthesis with expanded state bounds',
                  'Isolate session connection channel',
                  'Apply formal regression check on Phase 5 validator',
                ]).map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
            </div>

            {/* Tool Execution Activity */}
            {selectedInv.tool_activity && selectedInv.tool_activity.length > 0 && (
              <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-2">
                <h4 className="text-xs font-bold text-slate-300 uppercase flex items-center gap-1.5">
                  <Wrench className="w-3.5 h-3.5 text-amber-400" />
                  <span>Subagent Tool Trace</span>
                </h4>
                <div className="space-y-1.5 font-mono text-xs max-h-40 overflow-y-auto">
                  {selectedInv.tool_activity.map((tool, idx) => (
                    <div key={idx} className="p-2 bg-slate-900 rounded border border-slate-800 flex justify-between">
                      <span className="text-amber-400 font-bold">{tool.tool_name}</span>
                      <span className="text-slate-400 text-[10px]">{tool.result_summary}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
};
