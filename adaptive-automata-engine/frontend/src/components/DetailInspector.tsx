import React from 'react';
import { X, ShieldAlert, Cpu, Activity, Layers, Brain, CheckCircle2, Clock, Terminal, ArrowRight, FileText } from 'lucide-react';
import { ProtocolEventDTO, SessionDTO, SecurityAlertDTO, ModelVersionDTO, AIInvestigationDTO } from '../types';

interface DetailInspectorProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  type: 'event' | 'session' | 'alert' | 'model' | 'investigation';
  data: any;
  onUpdateAlertStatus?: (alertId: string, status: string) => void;
  onTriggerAI?: (alertId: string) => void;
}

export const DetailInspector: React.FC<DetailInspectorProps> = ({
  isOpen,
  onClose,
  title,
  subtitle,
  type,
  data,
  onUpdateAlertStatus,
  onTriggerAI,
}) => {
  if (!isOpen || !data) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden flex justify-end font-sans">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Slide-over Drawer Panel */}
      <div className="relative w-full max-w-lg bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col h-full z-10 animate-in slide-in-from-right duration-200">
        {/* Drawer Header */}
        <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
          <div className="flex items-center space-x-3">
            <div className="p-1.5 bg-indigo-500/10 rounded-lg border border-indigo-500/20 text-indigo-400">
              {type === 'event' && <Activity className="w-4 h-4" />}
              {type === 'session' && <Layers className="w-4 h-4" />}
              {type === 'alert' && <ShieldAlert className="w-4 h-4 text-rose-400" />}
              {type === 'model' && <Cpu className="w-4 h-4" />}
              {type === 'investigation' && <Brain className="w-4 h-4 text-purple-400" />}
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-100 truncate max-w-[320px]">{title}</h3>
              {subtitle && <p className="text-[11px] text-slate-400">{subtitle}</p>}
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-md transition-colors"
            title="Close Inspector"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Drawer Body Content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5 text-xs text-slate-300">
          {/* EVENT INSPECTION VIEW */}
          {type === 'event' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3 bg-slate-950 p-3.5 rounded-lg border border-slate-800 font-mono">
                <div>
                  <span className="text-[10px] uppercase text-slate-500 block font-sans font-bold">Event ID</span>
                  <span className="text-indigo-400 font-bold truncate block">{data.event_id}</span>
                </div>
                <div>
                  <span className="text-[10px] uppercase text-slate-500 block font-sans font-bold">Session ID</span>
                  <span className="text-purple-400 truncate block">{data.session_id}</span>
                </div>
                <div>
                  <span className="text-[10px] uppercase text-slate-500 block font-sans font-bold">Input Symbol</span>
                  <span className="text-sky-300 font-bold">{data.symbol || data.input_symbol}</span>
                </div>
                <div>
                  <span className="text-[10px] uppercase text-slate-500 block font-sans font-bold">Formal State</span>
                  <span className="text-purple-300 font-bold">{data.formal_state}</span>
                </div>
              </div>

              {/* Analysis Status Card */}
              <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-2 font-sans">
                <div className="flex justify-between items-center">
                  <span className="text-[10px] uppercase text-slate-400 font-bold">Formal Analysis Level</span>
                  <span className="px-2 py-0.5 bg-slate-800 text-cyan-400 rounded text-[10px] font-mono font-bold">
                    {data.analysis?.level_used || data.analysis_level || 'DFA_MEALY'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-[10px] uppercase text-slate-400 font-bold">Execution Status</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    data.analysis?.status === 'ACCEPTED' || data.status === 'ACCEPTED'
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                      : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                  }`}>
                    {data.analysis?.status || data.status}
                  </span>
                </div>
                {data.analysis?.reason && (
                  <p className="text-[11px] text-amber-300/90 bg-amber-950/20 p-2.5 rounded border border-amber-500/20 mt-2 font-mono">
                    {data.analysis.reason}
                  </p>
                )}
              </div>

              {/* Security Assessment Card */}
              <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-2 font-sans">
                <span className="text-[10px] uppercase text-slate-400 font-bold block">Security Assessment</span>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-slate-500 text-[10px] block">Classification</span>
                    <span className="font-semibold text-slate-200">
                      {data.security?.classification || data.security_assessment?.classification || 'BENIGN'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] block">Severity</span>
                    <span className={`font-bold ${
                      (data.security?.severity || data.security_assessment?.severity) === 'HIGH' ||
                      (data.security?.severity || data.security_assessment?.severity) === 'CRITICAL'
                        ? 'text-rose-400'
                        : 'text-emerald-400'
                    }`}>
                      {data.security?.severity || data.security_assessment?.severity || 'LOW'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Payload Snippet */}
              {data.raw_payload_snippet && (
                <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800 space-y-1 font-mono text-[11px]">
                  <span className="text-[10px] uppercase text-slate-500 block font-sans font-bold">Raw Payload Snippet</span>
                  <div className="text-slate-300 bg-slate-900 p-2.5 rounded border border-slate-800 overflow-x-auto whitespace-pre-wrap">
                    {data.raw_payload_snippet}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* SESSION INSPECTION VIEW */}
          {type === 'session' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3 bg-slate-950 p-3.5 rounded-lg border border-slate-800 font-mono">
                <div>
                  <span className="text-[10px] uppercase text-slate-500 block font-sans font-bold">Session ID</span>
                  <span className="text-purple-400 font-bold truncate block">{data.session_id}</span>
                </div>
                <div>
                  <span className="text-[10px] uppercase text-slate-500 block font-sans font-bold">Protocol</span>
                  <span className="text-slate-200 font-sans">{data.protocol}</span>
                </div>
                <div>
                  <span className="text-[10px] uppercase text-slate-500 block font-sans font-bold">Status</span>
                  <span className={`font-sans font-bold text-[10px] ${data.status === 'ACTIVE' ? 'text-emerald-400' : 'text-slate-400'}`}>
                    {data.status}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] uppercase text-slate-500 block font-sans font-bold">Current State</span>
                  <span className="text-sky-300 font-bold">{data.current_state || data.state}</span>
                </div>
              </div>

              <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-2 font-sans">
                <span className="text-[10px] uppercase text-slate-400 font-bold block">Telemetry Metrics</span>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-slate-500 text-[10px] block">Events Evaluated</span>
                    <span className="font-bold text-slate-200 font-mono">{data.event_count || data.packet_count || 0}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] block">Max Hierarchy Tier</span>
                    <span className="font-bold text-cyan-400 font-mono">{data.max_level_escalation || 'DFA'}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ALERT INSPECTION VIEW */}
          {type === 'alert' && (
            <div className="space-y-4">
              <div className="bg-rose-950/30 border border-rose-500/30 p-4 rounded-lg space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-[10px] uppercase text-rose-400 font-bold font-sans">Formal Assessment</span>
                  <span className="px-2 py-0.5 bg-rose-500/20 text-rose-300 border border-rose-500/40 rounded text-[10px] font-bold">
                    {data.severity} SEVERITY
                  </span>
                </div>
                <div className="text-sm font-bold text-slate-100">{data.classification}</div>
                <p className="text-[11px] text-slate-400 font-mono">
                  Alert ID: <span className="text-rose-400">{data.alert_id}</span> | Session: {data.session_id}
                </p>
              </div>

              {/* Status Update Buttons */}
              {onUpdateAlertStatus && (
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-2 font-sans">
                  <span className="text-[10px] uppercase text-slate-400 font-bold block">Update SOC Status</span>
                  <div className="flex flex-wrap gap-2">
                    {['NEW', 'ACKNOWLEDGED', 'INVESTIGATING', 'RESOLVED', 'FALSE_POSITIVE'].map((st) => (
                      <button
                        key={st}
                        onClick={() => onUpdateAlertStatus(data.alert_id, st)}
                        className={`px-2.5 py-1 rounded text-xs font-semibold transition-colors ${
                          data.state === st
                            ? 'bg-indigo-600 text-white font-bold'
                            : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                        }`}
                      >
                        {st}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Reason Codes */}
              {data.reason_codes && data.reason_codes.length > 0 && (
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-2">
                  <span className="text-[10px] uppercase text-slate-400 font-bold block font-sans">Reason Triggers</span>
                  <div className="flex flex-wrap gap-1.5 font-mono text-[11px]">
                    {data.reason_codes.map((rc: string, idx: number) => (
                      <span key={idx} className="px-2 py-0.5 bg-slate-900 border border-slate-700 text-amber-300 rounded">
                        {rc}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* AI Trigger */}
              {onTriggerAI && (
                <div className="pt-2 flex justify-end">
                  <button
                    onClick={() => onTriggerAI(data.alert_id)}
                    className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs rounded-lg transition-colors flex items-center gap-2"
                  >
                    <Brain className="w-4 h-4" />
                    <span>Run Security Investigation</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
