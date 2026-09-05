import React, { useState } from 'react';
import { ProtocolEventDTO } from '../types';
import { Modal } from '../components/Modal';
import { Activity, Search, Filter, Eye, RefreshCw } from 'lucide-react';

interface LiveMonitorPageProps {
  events: ProtocolEventDTO[];
  wsConnected: boolean;
  onRefresh?: () => void;
}

export const LiveMonitorPage: React.FC<LiveMonitorPageProps> = ({
  events,
  wsConnected,
  onRefresh,
}) => {
  const [selectedEvent, setSelectedEvent] = useState<ProtocolEventDTO | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  const filteredEvents = events.filter((e) => {
    const matchesSearch =
      e.event_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.session_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.protocol.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus =
      statusFilter === 'ALL' ||
      (statusFilter === 'ACCEPTED' && e.analysis.status === 'ACCEPTED') ||
      (statusFilter === 'DEVIATION' && e.analysis.status !== 'ACCEPTED');

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            <span>Live Protocol Event Monitor</span>
          </h2>
          <p className="text-xs text-slate-400">
            Real-time packet/message token stream evaluated across DFA, PDA, and CFG layers
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <div className={`px-3 py-1 rounded-full text-xs font-semibold flex items-center space-x-1.5 ${
            wsConnected ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
          }`}>
            <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-emerald-400 animate-ping' : 'bg-amber-400'}`}></span>
            <span>{wsConnected ? 'WebSocket Streaming' : 'Polling Active'}</span>
          </div>
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 text-xs font-semibold flex items-center gap-1.5"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Refresh</span>
            </button>
          )}
        </div>
      </div>

      {/* Filter Controls */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap gap-4 items-center justify-between">
        <div className="flex-1 min-w-[240px] relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Filter by Event ID, Session ID, Symbol, Protocol..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg pl-9 pr-4 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center space-x-2">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-xs text-slate-400 font-medium">Status Filter:</span>
          {(['ALL', 'ACCEPTED', 'DEVIATION'] as const).map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors ${
                statusFilter === st
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Event Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Event ID</th>
                <th className="py-3 px-4">Session</th>
                <th className="py-3 px-4">Protocol</th>
                <th className="py-3 px-4">Symbol</th>
                <th className="py-3 px-4">State</th>
                <th className="py-3 px-4">Analysis Result</th>
                <th className="py-3 px-4">Security Result</th>
                <th className="py-3 px-4">Model Ver</th>
                <th className="py-3 px-4 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {filteredEvents.length === 0 ? (
                <tr>
                  <td colSpan={10} className="py-8 text-center text-slate-500 font-sans">
                    No protocol events match current filter criteria.
                  </td>
                </tr>
              ) : (
                filteredEvents.map((evt) => (
                  <tr
                    key={evt.event_id}
                    onClick={() => setSelectedEvent(evt)}
                    className="hover:bg-slate-800/50 cursor-pointer transition-colors"
                  >
                    <td className="py-2.5 px-4 text-slate-400 text-[11px] font-sans">
                      {new Date(evt.timestamp * 1000).toLocaleTimeString()}
                    </td>
                    <td className="py-2.5 px-4 text-cyan-400 font-semibold">{evt.event_id}</td>
                    <td className="py-2.5 px-4 text-slate-300">{evt.session_id}</td>
                    <td className="py-2.5 px-4 text-slate-400 font-sans font-medium">{evt.protocol}</td>
                    <td className="py-2.5 px-4 text-slate-100 font-bold">{evt.symbol}</td>
                    <td className="py-2.5 px-4 text-purple-300">{evt.formal_state}</td>
                    <td className="py-2.5 px-4 font-sans">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        evt.analysis.status === 'ACCEPTED'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      }`}>
                        {evt.analysis.status} ({evt.analysis.level_used})
                      </span>
                    </td>
                    <td className="py-2.5 px-4 font-sans">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        evt.security.severity === 'HIGH' || evt.security.severity === 'CRITICAL'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                          : evt.security.severity === 'MEDIUM'
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                          : 'bg-slate-800 text-slate-400'
                      }`}>
                        {evt.security.classification} [{evt.security.severity}]
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-slate-400">{evt.model_version}</td>
                    <td className="py-2.5 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedEvent(evt);
                        }}
                        className="p-1 text-slate-400 hover:text-indigo-300 hover:bg-slate-800 rounded"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Event Detail Modal */}
      {selectedEvent && (
        <Modal
          isOpen={!!selectedEvent}
          onClose={() => setSelectedEvent(null)}
          title={`Event Inspection — ${selectedEvent.event_id}`}
        >
          <div className="space-y-4 font-sans">
            <div className="grid grid-cols-2 gap-4 text-xs bg-slate-950 p-4 rounded-lg border border-slate-800">
              <div>
                <span className="text-slate-500 block uppercase font-bold">Session ID</span>
                <span className="font-mono text-cyan-300 font-semibold">{selectedEvent.session_id}</span>
              </div>
              <div>
                <span className="text-slate-500 block uppercase font-bold">Protocol</span>
                <span className="font-semibold text-slate-200">{selectedEvent.protocol}</span>
              </div>
              <div>
                <span className="text-slate-500 block uppercase font-bold">Symbol Token</span>
                <span className="font-mono font-bold text-sky-400">{selectedEvent.symbol}</span>
              </div>
              <div>
                <span className="text-slate-500 block uppercase font-bold">Formal State</span>
                <span className="font-mono font-semibold text-purple-400">{selectedEvent.formal_state}</span>
              </div>
            </div>

            {/* Analysis Breakdown */}
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-2">
              <h4 className="text-xs font-bold text-slate-300 uppercase">Hierarchical Analysis Engine</h4>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div>
                  <span className="text-slate-500 block text-[10px]">Evaluation Level</span>
                  <span className="font-mono text-amber-400 font-bold">{selectedEvent.analysis.level_used}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">Decision Status</span>
                  <span className="font-bold text-emerald-400">{selectedEvent.analysis.status}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">Latency</span>
                  <span className="font-mono text-slate-300">{selectedEvent.processing_latency_ms} ms</span>
                </div>
              </div>
              {selectedEvent.analysis.reason && (
                <div className="text-xs text-slate-400 bg-slate-900 p-2.5 rounded border border-slate-800 mt-2">
                  <span className="font-semibold text-slate-300">Reason:</span> {selectedEvent.analysis.reason}
                </div>
              )}
            </div>

            {/* Security Decision */}
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-2">
              <h4 className="text-xs font-bold text-slate-300 uppercase">Backend Formal Security Decision</h4>
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-400">Classification:</span>
                <span className="font-semibold text-rose-400">{selectedEvent.security.classification}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-slate-400">Severity:</span>
                <span className="font-bold text-rose-500">{selectedEvent.security.severity}</span>
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
