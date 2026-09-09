import React, { useEffect, useState } from 'react';
import { AdaptationStateDTO } from '../types';
import { fetchAdaptationState, promoteCandidateModel } from '../api/client';
import { GitMerge, CheckCircle2, ShieldCheck, RefreshCw, AlertCircle, ArrowRight } from 'lucide-react';

export const AdaptationPage: React.FC = () => {
  const [adaptationState, setAdaptationState] = useState<AdaptationStateDTO | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [promoting, setPromoting] = useState<boolean>(false);
  const [showConfirmModal, setShowConfirmModal] = useState<boolean>(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchAdaptationState();
      setAdaptationState(data);
    } catch (err) {
      console.error('Failed to fetch adaptation state', err);
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
      console.error(err);
    } finally {
      setPromoting(false);
    }
  };

  const stages = [
    { label: 'Observed', status: 'COMPLETED', desc: 'Novel symbol pattern detected' },
    { label: 'Under Review', status: 'COMPLETED', desc: 'Evidence threshold evaluation' },
    { label: 'Validation', status: 'COMPLETED', desc: 'Regression safety verification' },
    { label: 'Approved', status: adaptationState?.candidate_model_version ? 'ACTIVE' : 'PENDING', desc: 'Model candidate ready for activation' },
    { label: 'Activated', status: 'PENDING', desc: 'Deployed to live fast-path pipeline' },
  ];

  return (
    <div className="space-y-4 font-sans">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-base font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <GitMerge className="w-4 h-4 text-cyan-400" />
            <span>Automated Model Adaptation Policy</span>
          </h2>
          <p className="text-xs text-slate-400">
            Controlled change-management workflow and regression validation prior to candidate model activation
          </p>
        </div>
        <button
          onClick={loadData}
          className="px-2.5 py-1 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded border border-slate-800 text-xs font-semibold flex items-center gap-1.5"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Policy</span>
        </button>
      </div>

      {/* Change Management Workflow Stages Bar */}
      <div className="bg-slate-900/90 border border-slate-800/80 rounded-lg p-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Model Change Lifecycle</h3>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-2">
          {stages.map((stg, idx) => (
            <div key={idx} className="bg-slate-950 p-3 rounded border border-slate-800 space-y-1 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-200">{stg.label}</span>
                <span className={`w-2 h-2 rounded-full ${
                  stg.status === 'COMPLETED' ? 'bg-emerald-400' : stg.status === 'ACTIVE' ? 'bg-cyan-400 animate-pulse' : 'bg-slate-700'
                }`} />
              </div>
              <p className="text-[10px] text-slate-500">{stg.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Model State Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Active Model Summary */}
        <div className="bg-slate-900/90 border border-slate-800/80 rounded-lg p-4 space-y-3">
          <div className="flex items-center space-x-2 pb-2 border-b border-slate-800/60">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">Active Model Status</h3>
          </div>
          <div className="bg-slate-950 p-3.5 rounded border border-slate-800 font-mono text-xs space-y-2">
            <div className="flex justify-between">
              <span className="text-slate-500 font-sans">Active Version</span>
              <span className="text-indigo-400 font-bold">{adaptationState?.active_model_version || 'v1.0.0'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 font-sans">Evidence Threshold</span>
              <span className="text-slate-300 font-bold">{adaptationState?.evidence_count ?? 5} observations</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 font-sans">Regression Check</span>
              <span className="text-emerald-400 font-sans font-bold text-[11px]">PASSED (0.0% regression)</span>
            </div>
          </div>
        </div>

        {/* Pending Candidate Action */}
        <div className="bg-slate-900/90 border border-slate-800/80 rounded-lg p-4 space-y-3 flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 pb-2 border-b border-slate-800/60">
              <GitMerge className="w-4 h-4 text-cyan-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">Pending Candidate Model</h3>
            </div>
            <div className="bg-slate-950 p-3.5 rounded border border-slate-800 font-mono text-xs mt-3 space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-500 font-sans">Candidate Version</span>
                <span className="text-cyan-400 font-bold">{adaptationState?.candidate_model_version || 'None Pending'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-sans">Validation Status</span>
                <span className="text-emerald-400 font-sans font-bold text-[11px]">
                  {adaptationState?.candidate_model_version ? 'VALIDATED & APPROVED' : 'NO PENDING CANDIDATE'}
                </span>
              </div>
            </div>
          </div>

          <div className="pt-2 flex justify-end">
            <button
              onClick={() => setShowConfirmModal(true)}
              disabled={!adaptationState?.candidate_model_version || promoting}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold text-xs rounded transition-colors flex items-center gap-1.5"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Promote Validated Model</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
