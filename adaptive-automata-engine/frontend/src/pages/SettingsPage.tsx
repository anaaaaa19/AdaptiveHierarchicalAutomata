import React, { useState } from 'react';
import { SystemStatusDTO } from '../types';
import { startCapture, stopCapture } from '../api/client';
import { Modal } from '../components/Modal';
import { Settings, Activity, RefreshCw, Brain, HardDrive, ShieldAlert, AlertTriangle, Check } from 'lucide-react';

interface SettingsPageProps {
  status: SystemStatusDTO | null;
  onRefresh: () => void;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({ status, onRefresh }) => {
  const [isCaptureActive, setIsCaptureActive] = useState<boolean>(status?.is_capture_active ?? false);
  const [adaptationMode, setAdaptationMode] = useState<'AUTO' | 'MANUAL'>('MANUAL');
  const [aiMode, setAiMode] = useState<boolean>(true);
  const [queueLimit, setQueueLimit] = useState<number>(10000);
  const [maxSessions, setMaxSessions] = useState<number>(500);

  const [confirmModal, setConfirmModal] = useState<{
    isOpen: boolean;
    action: string;
    title: string;
    description: string;
    onConfirm: () => Promise<void>;
  }>({
    isOpen: false,
    action: '',
    title: '',
    description: '',
    onConfirm: async () => {},
  });

  const [loading, setLoading] = useState<boolean>(false);

  const handleToggleCapture = () => {
    const targetState = !isCaptureActive;
    setConfirmModal({
      isOpen: true,
      action: targetState ? 'START_CAPTURE' : 'STOP_CAPTURE',
      title: targetState ? 'Start Live Network Packet Capture' : 'Stop Live Packet Capture',
      description: targetState
        ? 'Activating live network traffic capture will bind to local network sockets and stream live protocol traffic to the Level 1-3 formal engine.'
        : 'Stopping capture will halt incoming live packet evaluation and revert to offline replay state.',
      onConfirm: async () => {
        setLoading(true);
        try {
          if (targetState) {
            await startCapture();
          } else {
            await stopCapture();
          }
          setIsCaptureActive(targetState);
          onRefresh();
        } catch (err) {
          console.error(err);
        } finally {
          setLoading(false);
          setConfirmModal((prev) => ({ ...prev, isOpen: false }));
        }
      },
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Settings className="w-5 h-5 text-indigo-400" />
            <span>Engine Configuration & Operational Settings</span>
          </h2>
          <p className="text-xs text-slate-400">
            Control capture interfaces, adaptation policy modes, AI agent orchestration, and system resource bounds
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Capture Mode Setting */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-slate-200">Packet Capture Interface</h3>
            </div>
            <span className={`px-2.5 py-1 text-[10px] font-bold rounded-full border ${
              isCaptureActive
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
            }`}>
              {isCaptureActive ? 'LIVE CAPTURE ACTIVE' : 'REPLAY / DEMO MODE'}
            </span>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            Toggle between live socket packet capture and offline replay dataset mode. Mutating capture mode requires confirmation.
          </p>

          <button
            onClick={handleToggleCapture}
            className={`w-full py-2.5 rounded-lg text-xs font-bold transition-all shadow-md flex items-center justify-center space-x-2 ${
              isCaptureActive
                ? 'bg-rose-600 hover:bg-rose-500 text-white'
                : 'bg-cyan-600 hover:bg-cyan-500 text-white'
            }`}
          >
            <span>{isCaptureActive ? 'Deactivate Live Capture (Revert to Demo)' : 'Activate Live Network Capture'}</span>
          </button>
        </div>

        {/* Adaptation Mode Setting */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <RefreshCw className="w-4 h-4 text-indigo-400" />
              <h3 className="text-sm font-bold text-slate-200">Adaptation Promotion Mode</h3>
            </div>
            <span className="px-2.5 py-1 text-[10px] font-bold rounded-full bg-slate-800 text-slate-300 border border-slate-700">
              {adaptationMode}
            </span>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            In MANUAL mode, candidate model promotion requires explicit SOC operator confirmation. In AUTO mode, valid candidates auto-promote.
          </p>

          <div className="flex gap-3">
            <button
              onClick={() => setAdaptationMode('MANUAL')}
              className={`flex-1 py-2 rounded-lg text-xs font-semibold border transition-colors ${
                adaptationMode === 'MANUAL'
                  ? 'bg-indigo-600 border-indigo-500 text-white font-bold'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              Manual SOC Review (Recommended)
            </button>
            <button
              onClick={() => setAdaptationMode('AUTO')}
              className={`flex-1 py-2 rounded-lg text-xs font-semibold border transition-colors ${
                adaptationMode === 'AUTO'
                  ? 'bg-amber-600 border-amber-500 text-white font-bold'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              Autonomous Auto-Promote
            </button>
          </div>
        </div>

        {/* AI Agent Orchestration Mode */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <Brain className="w-4 h-4 text-purple-400" />
              <h3 className="text-sm font-bold text-slate-200">Phase 7 Agentic AI Mode</h3>
            </div>
            <button
              onClick={() => setAiMode(!aiMode)}
              className={`px-3 py-1 text-xs font-bold rounded-full transition-colors ${
                aiMode ? 'bg-purple-600 text-white' : 'bg-slate-800 text-slate-400'
              }`}
            >
              {aiMode ? 'ENABLED' : 'DISABLED'}
            </button>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            Controls out-of-band agent spawning upon security anomaly generation. Formal detection engine operates independently regardless of AI state.
          </p>
        </div>

        {/* Resource Limits Setting */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center space-x-2">
            <HardDrive className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-bold text-slate-200">Engine Resource Ceilings</h3>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <label className="text-slate-400 block mb-1 font-medium">Event Queue Capacity</label>
              <input
                type="number"
                value={queueLimit}
                onChange={(e) => setQueueLimit(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 font-mono focus:outline-none focus:border-emerald-500"
              />
            </div>
            <div>
              <label className="text-slate-400 block mb-1 font-medium">Max Active Sessions Limit</label>
              <input
                type="number"
                value={maxSessions}
                onChange={(e) => setMaxSessions(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 font-mono focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Confirmation Modal */}
      {confirmModal.isOpen && (
        <Modal
          isOpen={confirmModal.isOpen}
          onClose={() => setConfirmModal((prev) => ({ ...prev, isOpen: false }))}
          title={confirmModal.title}
          maxWidth="md"
        >
          <div className="space-y-4 font-sans">
            <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-lg flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
              <p className="text-xs text-amber-200">{confirmModal.description}</p>
            </div>

            <div className="flex justify-end space-x-3 pt-2">
              <button
                onClick={() => setConfirmModal((prev) => ({ ...prev, isOpen: false }))}
                className="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg text-xs font-semibold hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={confirmModal.onConfirm}
                disabled={loading}
                className="px-4 py-2 bg-cyan-600 text-white font-bold rounded-lg text-xs hover:bg-cyan-500"
              >
                {loading ? 'Executing...' : 'Confirm Action'}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
