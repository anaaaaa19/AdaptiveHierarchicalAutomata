import React, { useEffect, useState } from 'react';
import { DriftDataDTO } from '../types';
import { fetchDriftMetrics } from '../api/client';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp, RefreshCw, Activity, AlertTriangle } from 'lucide-react';

export const DriftPage: React.FC = () => {
  const [driftData, setDriftData] = useState<DriftDataDTO | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchDriftMetrics();
      setDriftData(data);
    } catch (err) {
      console.error('Failed to fetch drift data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const timeSeries = driftData?.time_series ?? [
    { timestamp: 10, drift_score: 0.02 },
    { timestamp: 20, drift_score: 0.05 },
    { timestamp: 30, drift_score: 0.08 },
    { timestamp: 40, drift_score: 0.12 },
    { timestamp: 50, drift_score: 0.11 },
    { timestamp: 60, drift_score: 0.15 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
            <span>Concept & Protocol Drift Analytics</span>
          </h2>
          <p className="text-xs text-slate-400">
            Real-time statistical boundary monitoring tracking distribution shift across windowed protocol traces
          </p>
        </div>
        <button
          onClick={loadData}
          className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 text-xs font-semibold flex items-center gap-1.5"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Drift</span>
        </button>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <span className="text-xs font-semibold uppercase text-slate-400">Current Drift State</span>
          <div className={`text-xl font-bold font-mono mt-1 ${
            driftData?.drift_state === 'DRIFT_DETECTED'
              ? 'text-rose-400'
              : driftData?.drift_state === 'WARNING'
              ? 'text-amber-400'
              : 'text-emerald-400'
          }`}>
            {driftData?.drift_state || 'NO_DRIFT'}
          </div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <span className="text-xs font-semibold uppercase text-slate-400">Drift Score Metric</span>
          <div className="text-xl font-bold font-mono text-cyan-400 mt-1">
            {driftData?.drift_score?.toFixed(3) ?? '0.045'}
          </div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <span className="text-xs font-semibold uppercase text-slate-400">Window Size</span>
          <div className="text-xl font-bold font-mono text-purple-400 mt-1">
            {driftData?.window_size ?? 500} events
          </div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <span className="text-xs font-semibold uppercase text-slate-400">Active Model</span>
          <div className="text-xl font-bold font-mono text-indigo-400 mt-1">
            {driftData?.model_version || 'v1.0.0'}
          </div>
        </div>
      </div>

      {/* Time Series Chart Card */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            <span>Drift Score Trajectory Over Time</span>
          </h3>
          <span className="text-xs text-slate-500 font-mono">Detection Threshold: 0.35</span>
        </div>

        <div className="w-full h-72 pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={timeSeries}>
              <defs>
                <linearGradient id="driftGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="timestamp" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} domain={[0, 0.5]} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f8fafc' }}
              />
              <Area type="monotone" dataKey="drift_score" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#driftGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
