import React, { useState } from 'react';
import { Activity, Cpu, Radio, RefreshCw, Play } from 'lucide-react';
import { SystemStatusDTO } from '../types';
import { triggerReplay } from '../api/client';

interface NavbarProps {
  status: SystemStatusDTO | null;
  wsConnected: boolean;
  onRefresh?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ status, wsConnected, onRefresh }) => {
  const [isReplaying, setIsReplaying] = useState(false);

  const handleRunReplay = async () => {
    setIsReplaying(true);
    try {
      await triggerReplay();
      if (onRefresh) onRefresh();
    } catch (e) {
      console.error('Replay trigger error:', e);
    } finally {
      setIsReplaying(false);
    }
  };

  return (
    <header className="bg-slate-950 border-b border-slate-800/80 px-5 py-2.5 flex items-center justify-between sticky top-0 z-40 shadow-sm font-sans">
      <div className="flex items-center space-x-3">
        <div className="p-1.5 bg-slate-900 rounded-md border border-slate-800 text-indigo-400">
          <Cpu className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-sm font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <span>Adaptive Hierarchical Automata Engine</span>
            <span className="px-1.5 py-0.2 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[10px] font-mono font-semibold rounded">
              v8.0.0
            </span>
          </h1>
          <p className="text-[11px] text-slate-400 flex items-center gap-2">
            <span>Protocol Security & Network Intelligence</span>
            <span className="text-slate-700">•</span>
            <span className="font-mono text-slate-400">Formal Verification Active</span>
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-2.5 text-xs font-medium">
        {/* Connection status */}
        <div className={`px-2.5 py-1 rounded border flex items-center space-x-1.5 text-[11px] ${
          wsConnected
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 font-mono'
            : 'bg-amber-500/10 border-amber-500/30 text-amber-400 font-mono'
        }`}>
          <Radio className={`w-3 h-3 ${wsConnected ? 'animate-pulse' : ''}`} />
          <span>{wsConnected ? 'LIVE WS CONNECTED' : 'POLLING FALLBACK'}</span>
        </div>

        {/* Capture status */}
        <div className={`px-2.5 py-1 rounded border flex items-center space-x-1.5 text-[11px] ${
          status?.is_capture_active
            ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400 font-mono'
            : 'bg-purple-500/10 border-purple-500/30 text-purple-300 font-mono'
        }`}>
          <Activity className="w-3 h-3" />
          <span>{status?.is_capture_active ? 'LIVE CAPTURE' : 'REPLAY MODE'}</span>
        </div>

        {/* Active Model Version */}
        <div className="px-2.5 py-1 bg-slate-900 border border-slate-800 rounded text-slate-300 flex items-center space-x-1.5 text-[11px] font-mono">
          <span className="text-slate-500 font-sans">Model:</span>
          <span className="font-bold text-indigo-400">{status?.active_model_version || 'v1.0.0'}</span>
        </div>

        {/* Replay Stream Trigger Button */}
        <button
          onClick={handleRunReplay}
          disabled={isReplaying}
          className="px-2.5 py-1 text-cyan-300 hover:text-white bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded transition-colors flex items-center gap-1.5 text-xs font-semibold"
          title="Run deterministic replay trace"
        >
          <Play className={`w-3 h-3 text-cyan-400 ${isReplaying ? 'animate-spin' : ''}`} />
          <span>{isReplaying ? 'Replaying...' : 'Run Replay'}</span>
        </button>

        {/* Refresh button */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="p-1 text-slate-400 hover:text-slate-200 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded transition-colors"
            title="Refresh engine state"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
    </header>
  );
};
