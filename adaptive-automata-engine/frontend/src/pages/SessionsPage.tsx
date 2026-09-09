import React, { useEffect, useState } from 'react';
import { SessionDTO, ProtocolEventDTO } from '../types';
import { fetchSessions, fetchEvents } from '../api/client';
import { DetailInspector } from '../components/DetailInspector';
import { Layers, RefreshCw, Eye, PlayCircle, CheckCircle2 } from 'lucide-react';

export const SessionsPage: React.FC = () => {
  const [sessions, setSessions] = useState<SessionDTO[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedSession, setSelectedSession] = useState<SessionDTO | null>(null);

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

  return (
    <div className="space-y-4 font-sans">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-base font-bold text-slate-100 tracking-tight flex items-center gap-2">
            <Layers className="w-4 h-4 text-purple-400" />
            <span>Protocol Sessions Inspector</span>
          </h2>
          <p className="text-xs text-slate-400">
            Active and archived stateful communication sessions monitored by formal automata
          </p>
        </div>
        <button
          onClick={loadSessions}
          className="px-2.5 py-1 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded border border-slate-800 text-xs font-semibold flex items-center gap-1.5"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Sessions</span>
        </button>
      </div>

      {/* Sessions Table */}
      <div className="bg-slate-900/90 border border-slate-800/80 rounded-lg overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold font-sans">
                <th className="py-2.5 px-4">Session ID</th>
                <th className="py-2.5 px-4">Protocol</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">Current State</th>
                <th className="py-2.5 px-4">Events Evaluated</th>
                <th className="py-2.5 px-4">Max Escalation Tier</th>
                <th className="py-2.5 px-4">Last Activity</th>
                <th className="py-2.5 px-4 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 font-mono">
              {sessions.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500 font-sans text-xs">
                    No protocol sessions recorded yet. Run replay stream or start capture.
                  </td>
                </tr>
              ) : (
                sessions.map((sess) => (
                  <tr
                    key={sess.session_id}
                    onClick={() => setSelectedSession(sess)}
                    className="hover:bg-slate-800/50 cursor-pointer transition-colors"
                  >
                    <td className="py-2.5 px-4 text-purple-400 font-bold truncate max-w-[180px]">{sess.session_id}</td>
                    <td className="py-2.5 px-4 text-slate-300 font-sans">{sess.protocol || 'TCP'}</td>
                    <td className="py-2.5 px-4 font-sans">
                      <span className={`px-2 py-0.2 rounded text-[10px] font-semibold flex items-center w-fit gap-1 ${
                        sess.status === 'ACTIVE'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : 'bg-slate-800 text-slate-400 border border-slate-700'
                      }`}>
                        {sess.status === 'ACTIVE' ? <PlayCircle className="w-3 h-3" /> : <CheckCircle2 className="w-3 h-3" />}
                        <span>{sess.status || 'ACTIVE'}</span>
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-sky-300 font-bold">{sess.current_state || sess.state || 'q0'}</td>
                    <td className="py-2.5 px-4 text-slate-200 font-bold">{sess.event_count || sess.message_count || 0}</td>
                    <td className="py-2.5 px-4">
                      <span className={`px-2 py-0.2 rounded text-[10px] font-bold ${
                        sess.max_level_escalation === 'CFG'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : sess.max_level_escalation === 'PDA'
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          : 'bg-sky-500/20 text-sky-400 border border-sky-500/30'
                      }`}>
                        {sess.max_level_escalation || 'DFA'}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-slate-400 font-sans text-[11px]">
                      {sess.last_activity ? new Date(sess.last_activity > 1e11 ? sess.last_activity : sess.last_activity * 1000).toLocaleTimeString() : 'Just now'}
                    </td>
                    <td className="py-2.5 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedSession(sess);
                        }}
                        className="px-2 py-0.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded font-sans text-[11px] flex items-center gap-1 ml-auto"
                      >
                        <Eye className="w-3 h-3" />
                        <span>Inspect</span>
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
        isOpen={!!selectedSession}
        onClose={() => setSelectedSession(null)}
        title="Session Inspector"
        subtitle={selectedSession?.session_id}
        type="session"
        data={selectedSession}
      />
    </div>
  );
};
