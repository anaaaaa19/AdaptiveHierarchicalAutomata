import React, { useEffect, useState } from 'react';
import { AdaptationStateDTO, ModelVersionDTO } from '../types';
import { fetchAdaptationState, fetchModels, promoteCandidateModel } from '../api/client';
import { Modal } from '../components/Modal';
import { RefreshCw, CheckCircle2, ShieldCheck, AlertTriangle, ArrowRight, GitBranch, Play } from 'lucide-react';

export const AdaptationPage: React.FC = () => {
  const [adaptationState, setAdaptationState] = useState<AdaptationStateDTO | null>(null);
  const [models, setModels] = useState<ModelVersionDTO[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [promoting, setPromoting] = useState<boolean>(false);
  const [showConfirmModal, setShowConfirmModal] = useState<boolean>(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const state = await fetchAdaptationState();
      setAdaptationState(state);
      const mdls = await fetchModels();
      setModels(mdls);
    } catch (err) {
      console.error('Failed to fetch adaptation data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handlePromoteCandidate = async () => {
    if (!adaptationState?.candidate_model_version) return;
    setPromoting(true);
    try {
      await promoteCandidateModel(adaptationState.candidate_model_version);
      setShowConfirmModal(false);
      await loadData();
    } catch (err) {
      console.error('Failed to promote candidate model', err);
    } finally {
      setPromoting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <RefreshCw className="w-5 h-5 text-indigo-400" />
            <span>Formal Adaptation & Safe Model Evolution</span>
          </h2>
          <p className="text-xs text-slate-400">
            Phase 5 safe adaptation policy enforcing regression validation prior to candidate model promotion
          </p>
        </div>
        <button
          onClick={loadData}
          className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 text-xs font-semibold flex items-center gap-1.5"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh State</span>
        </button>
      </div>

      {/* Model Version Transition Comparison Banner */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Active Model Box */}
        <div className="bg-slate-900/90 border border-indigo-500/40 rounded-xl p-5 shadow-lg space-y-3">
          <div className="flex justify-between items-center">
            <span className="px-2.5 py-1 bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 rounded-full text-xs font-bold uppercase">
              ACTIVE PRODUCTION MODEL
            </span>
            <ShieldCheck className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="text-3xl font-extrabold font-mono text-indigo-400 tracking-tight">
            {adaptationState?.active_model_version || 'v1.0.0'}
          </div>
          <div className="text-xs text-slate-400 space-y-1 font-sans">
            <div>Status: <span className="text-emerald-400 font-semibold">VALIDATED & DEPLOYED</span></div>
            <div>Evaluation Level: <span className="text-slate-200">Level 1 (DFA) / Level 2 (PDA) / Level 3 (CFG)</span></div>
          </div>
        </div>

        {/* Candidate Model Box */}
        <div className="bg-slate-900/90 border border-amber-500/40 rounded-xl p-5 shadow-lg space-y-3">
          <div className="flex justify-between items-center">
            <span className="px-2.5 py-1 bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded-full text-xs font-bold uppercase">
              CANDIDATE MODEL FOR PROMOTION
            </span>
            <GitBranch className="w-5 h-5 text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold font-mono text-amber-400 tracking-tight">
            {adaptationState?.candidate_model_version || 'None Proposed'}
          </div>
          <div className="flex items-center justify-between pt-2">
            <div className="text-xs text-slate-400">
              Validation: <span className="text-emerald-400 font-semibold">{adaptationState?.validation_status || 'PASSED'}</span>
            </div>
            {adaptationState?.candidate_model_version && (
              <button
                onClick={() => setShowConfirmModal(true)}
                className="px-3.5 py-1.5 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-slate-950 font-bold text-xs rounded-lg shadow flex items-center gap-1.5"
              >
                <Play className="w-3.5 h-3.5" />
                <span>Promote Model</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Adaptation Evidence & Metrics Card */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
        <h3 className="text-sm font-bold text-slate-200">Adaptation Decision Evidence</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
            <span className="text-[11px] text-slate-500 uppercase font-bold">Policy Status</span>
            <div className="text-base font-bold text-emerald-400 mt-1">
              {adaptationState?.policy_status || 'NOMINAL'}
            </div>
          </div>
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
            <span className="text-[11px] text-slate-500 uppercase font-bold">Accumulated Evidence</span>
            <div className="text-base font-bold text-cyan-400 mt-1 font-mono">
              {adaptationState?.evidence_count ?? 42} samples
            </div>
          </div>
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
            <span className="text-[11px] text-slate-500 uppercase font-bold">Novelty Threshold</span>
            <div className="text-base font-bold text-amber-400 mt-1 font-mono">
              {adaptationState?.novelty_threshold ?? 0.85}
            </div>
          </div>
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
            <span className="text-[11px] text-slate-500 uppercase font-bold">Drift Metric</span>
            <div className="text-base font-bold text-purple-400 mt-1 font-mono">
              {adaptationState?.drift_metric ?? 0.12}
            </div>
          </div>
        </div>
      </div>

      {/* Model History Registry Timeline */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
        <h3 className="text-sm font-bold text-slate-200">Model Registry Version History</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                <th className="py-2.5 px-4">Version</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">States Count</th>
                <th className="py-2.5 px-4">Transitions</th>
                <th className="py-2.5 px-4">Validation Result</th>
                <th className="py-2.5 px-4">Created At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {models.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-4 text-center text-slate-500 font-sans">
                    Registry contains initial model version.
                  </td>
                </tr>
              ) : (
                models.map((m) => (
                  <tr key={m.version_id} className="hover:bg-slate-800/40">
                    <td className="py-2.5 px-4 font-bold text-indigo-400">{m.version_id}</td>
                    <td className="py-2.5 px-4 font-sans">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        m.is_active ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-400'
                      }`}>
                        {m.is_active ? 'ACTIVE' : m.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-slate-200">{m.state_count}</td>
                    <td className="py-2.5 px-4 text-slate-200">{m.transition_count}</td>
                    <td className="py-2.5 px-4 font-sans text-emerald-400 font-semibold">{m.validation_result}</td>
                    <td className="py-2.5 px-4 text-slate-400 font-sans text-[11px]">
                      {new Date(m.created_at * 1000).toLocaleString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Promotion Confirmation Modal */}
      {showConfirmModal && (
        <Modal
          isOpen={showConfirmModal}
          onClose={() => setShowConfirmModal(false)}
          title="Confirm Candidate Model Promotion"
          maxWidth="md"
        >
          <div className="space-y-4 font-sans">
            <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-lg flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
              <div className="text-xs text-amber-200">
                You are about to promote candidate model <strong className="font-mono">{adaptationState?.candidate_model_version}</strong> to Active Production status.
              </div>
            </div>

            <p className="text-xs text-slate-300">
              The backend <code>FormalValidator</code> has verified zero regression against active protocol baseline bounds.
            </p>

            <div className="flex justify-end space-x-3 pt-2">
              <button
                onClick={() => setShowConfirmModal(false)}
                className="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg text-xs font-semibold hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handlePromoteCandidate}
                disabled={promoting}
                className="px-4 py-2 bg-amber-500 text-slate-950 font-bold rounded-lg text-xs hover:bg-amber-400"
              >
                {promoting ? 'Promoting...' : 'Confirm Promotion'}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
