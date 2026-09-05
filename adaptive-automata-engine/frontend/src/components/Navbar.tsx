import React from 'react';
import { Activity, ShieldAlert, Cpu, Radio, RefreshCw } from 'lucide-react';
import { SystemStatusDTO } from '../types';

interface NavbarProps {
  status: SystemStatusDTO | null;
  wsConnected: boolean;
  onRefresh?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ status, wsConnected, onRefresh }) => {
  return (
    <header className="bg-slate-900 border-b border-slate-800 px-6 py-3.5 flex items-center justify-between sticky top-0 z-40 shadow-lg">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-indigo-500/10 rounded-lg border border-indigo-500/20">
          <Cpu className="w-6 h-6 text-indigo-400" />
        </div>
        <div>
          <h1 className="text-lg font-bold bg-gradient-to-r from-cyan-400 via-sky-400 to-indigo-400 bg-clip-text text-transparent tracking-tight">
            Adaptive Hierarchical Automata Engine
          </h1>
          <p className="text-xs text-slate-400 flex items-center gap-2">
            <span>SOC Protocol Security & Anomaly Platform</span>
            <span className="text-slate-600">•</span>
            <span className="font-mono text-cyan-400">Formal Verification Enabled</span>
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-3 text-xs font-semibold">
        {/* Connection status */}
        <div className={`px-3 py-1.5 rounded-full border flex items-center space-x-1.5 ${
          wsConnected
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
            : 'bg-amber-500/10 border-amber-500/30 text-amber-400'
        }`}>
          <Radio className={`w-3.5 h-3.5 ${wsConnected ? 'animate-pulse' : ''}`} />
          <span>{wsConnected ? 'LIVE WS CONNECTED' : 'POLLING FALLBACK'}</span>
        </div>

        {/* Capture status */}
        <div className={`px-3 py-1.5 rounded-full border flex items-center space-x-1.5 ${
          status?.is_capture_active
            ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400'
            : 'bg-purple-500/10 border-purple-500/30 text-purple-400'
        }`}>
          <Activity className="w-3.5 h-3.5" />
          <span>{status?.is_capture_active ? 'LIVE TRAFFIC CAPTURE' : 'DEMO / REPLAY MODE'}</span>
        </div>

        {/* Active Model Version */}
        <div className="px-3 py-1.5 bg-slate-800 border border-slate-700 rounded-full text-slate-300 flex items-center space-x-1.5">
          <span className="text-slate-400">Model:</span>
          <span className="font-mono font-bold text-indigo-400">{status?.active_model_version || 'v1.0.0'}</span>
        </div>

        {/* Refresh button */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="p-1.5 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg transition-colors"
            title="Refresh state"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        )}
      </div>
    </header>
  );
};
