import React, { useEffect, useState } from 'react';
import { SessionDTO, ProtocolEventDTO } from '../types';
import { fetchSessions, fetchEvents } from '../api/client';
import { Modal } from '../components/Modal';
import { Layers, RefreshCw, CheckCircle2, AlertCircle, PlayCircle, Eye } from 'lucide-react';

export const SessionsPage: React.FC = () => {
  const [sessions, setSessions] = useState<SessionDTO[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedSession, setSelectedSession] = useState<SessionDTO | null>(null);
  const [sessionEvents, setSessionEvents] = useState<ProtocolEventDTO[]>([]);

  const loadSessions = async () => {
    setLoading(true);
    try {
      const data = await fetchSessions();
      setSessions(data);
    } catch (err) {
      console.error('Failed to fetch sessions', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  const handleInspectSession = async (sess: SessionDTO) => {
    setSelectedSession(sess);
    try {
      const evts = await fetchEvents(100, sess.session_id);
      setSessionEvents(evts);
    } catch (err) {
      console.error(err);
      setSessionEvents([]);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Layers className="w-5 h-5 text-purple-400" />
            <span>Protocol Sessions Inspector</span>
          </h2>
          <p className="text-xs text-slate-400">
            Active and archived stateful communication sessions monitored by hierarchical automata
          </p>
        </div>
        <button
          onClick={loadSessions}
          className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 text-xs font-semibold flex items-center gap-1.5"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Sessions</span>
        </button>
      </div>

      {/* Sessions Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
                <th className="py-3 px-4">Session ID</th>
                <th className="py-3 px-4">Protocol</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Current Automata State</th>
                <th className="py-3 px-4">Events Evaluated</th>
                <th className="py-3 px-4">Max Level Escalation</th>
                <th className="py-3 px-4">Last Activity</th>
                <th className="py-3 px-4 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {sessions.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-500 font-sans">
                    No protocol sessions recorded yet. Start packet capture or run demo traffic.
                  </td>
                </tr>
              ) : (
                sessions.map((sess) => (
                  <tr key={sess.session_id} className="hover:bg-slate-800/50 transition-colors">
                    <td className="py-3 px-4 text-purple-400 font-bold">{sess.session_id}</td>
                    <td className="py-3 px-4 text-slate-300 font-sans">{sess.protocol}</td>
                    <td className="py-3 px-4 font-sans">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold flex items-center w-fit gap-1 ${
                        sess.status === 'ACTIVE'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : 'bg-slate-800 text-slate-400 border border-slate-700'
                      }`}>
                        {sess.status === 'ACTIVE' ? <PlayCircle className="w-3 h-3" /> : <CheckCircle2 className="w-3 h-3" />}
                        <span>{sess.status}</span>
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sky-300">{sess.current_state}</td>
                    <td className="py-3 px-4 text-slate-200 font-bold">{sess.event_count}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        sess.max_level_escalation === 'CFG'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : sess.max_level_escalation === 'PDA'
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          : 'bg-sky-500/20 text-sky-400 border border-sky-500/30'
                      }`}>
                        {sess.max_level_escalation || 'DFA'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-sans text-[11px]">
                      {new Date(sess.last_activity * 1000).toLocaleTimeString()}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleInspectSession(sess)}
                        className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded font-sans text-xs flex items-center gap-1 ml-auto"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Trace</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Session Inspector Modal */}
      {selectedSession && (
        <Modal
          isOpen={!!selectedSession}
          onClose={() => setSelectedSession(null)}
          title={`Session Execution Path — ${selectedSession.session_id}`}
        >
          <div className="space-y-4 font-sans">
            <div className="grid grid-cols-3 gap-4 text-xs bg-slate-950 p-4 rounded-lg border border-slate-800">
              <div>
                <span className="text-slate-500 block uppercase font-bold">Protocol</span>
                <span className="font-semibold text-slate-200">{selectedSession.protocol}</span>
              </div>
              <div>
                <span className="text-slate-500 block uppercase font-bold">Current State</span>
                <span className="font-mono text-purple-400 font-bold">{selectedSession.current_state}</span>
              </div>
              <div>
                <span className="text-slate-500 block uppercase font-bold">Total Events</span>
                <span className="font-mono text-cyan-400 font-bold">{selectedSession.event_count}</span>
              </div>
            </div>

            {/* Trace Timeline */}
            <div>
              <h4 className="text-xs font-bold text-slate-300 uppercase mb-3">Event Execution Sequence</h4>
              {sessionEvents.length === 0 ? (
                <p className="text-xs text-slate-500 py-4 text-center">No trace events available for this session.</p>
              ) : (
                <div className="space-y-2 max-h-60 overflow-y-auto pr-2">
                  {sessionEvents.map((evt, idx) => (
                    <div
                      key={evt.event_id}
                      className="p-2.5 bg-slate-950 border border-slate-800 rounded flex justify-between items-center text-xs font-mono"
                    >
                      <div className="flex items-center space-x-3">
                        <span className="text-slate-500 font-bold text-[10px]">#{idx + 1}</span>
                        <span className="text-sky-400 font-bold">{evt.symbol}</span>
                        <span className="text-slate-400">→ {evt.formal_state}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-amber-400 text-[10px] font-sans">{evt.analysis.level_used}</span>
                        <span className={`px-1.5 py-0.5 text-[9px] rounded font-sans ${
                          evt.analysis.status === 'ACCEPTED' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                        }`}>
                          {evt.analysis.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
