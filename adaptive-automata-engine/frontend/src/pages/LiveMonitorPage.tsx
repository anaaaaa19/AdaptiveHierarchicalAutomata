import React, { useState } from 'react';
import { ProtocolEventDTO } from '../types';
import { Activity, Radio, Filter, Search, Eye, ShieldAlert, Cpu, Terminal, RefreshCw } from 'lucide-react';

interface LiveMonitorPageProps {
  events: ProtocolEventDTO[];
  wsConnected: boolean;
  onRefresh: () => void;
}

export const LiveMonitorPage: React.FC<LiveMonitorPageProps> = ({
  events,
  wsConnected,
  onRefresh,
}) => {
  const [selectedEvent, setSelectedEvent] = useState<ProtocolEventDTO | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const filteredEvents = events.filter((evt) => {
    const matchesStatus =
      statusFilter === 'ALL' ||
      evt.status === statusFilter ||
      evt.analysis?.status === statusFilter;
    const matchesQuery =
      !searchQuery.trim() ||
      evt.event_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      evt.session_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      evt.symbol.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesQuery;
  });

  const activeEvent = selectedEvent || (filteredEvents.length > 0 ? filteredEvents[0] : null);

  return (
    <div className="space-y-4 font-sans h-[calc(100vh-105px)] flex flex-col">
      {/* Console Top Action Bar */}
      <div className="flex justify-between items-center shrink-0">
        <div className="flex items-center space-x-3">
          <div className="p-1.5 bg-slate-900 border border-slate-800 rounded text-cyan-400">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-100 tracking-tight flex items-center gap-2">
              <span>Live Monitor Console</span>
              <span className={`px-2 py-0.2 rounded text-[10px] font-mono font-bold ${
                wsConnected ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/10 text-amber-400'
              }`}>
                {wsConnected ? 'LIVE WS CONNECTED' : 'POLLING'}
              </span>
            </h2>
            <p className="text-[11px] text-slate-400">Real-time protocol event stream and state transduction inspector</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* Search Input */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2" />
            <input
              type="text"
              placeholder="Search session / symbol..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded pl-8 pr-3 py-1 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono w-52"
            />
          </div>

          <button
            onClick={onRefresh}
            className="px-2.5 py-1 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded border border-slate-800 text-xs font-semibold flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh Stream</span>
          </button>
        </div>
      </div>

      {/* Main Split Console Grid */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-4 min-h-0 overflow-hidden">
        {/* Left Pane (2/3 width): Live Real-Time Event Stream */}
        <div className="lg:col-span-2 bg-slate-900/90 border border-slate-800/80 rounded-lg flex flex-col min-h-0 overflow-hidden">
          {/* Filter Toolbar */}
          <div className="px-4 py-2.5 bg-slate-950/80 border-b border-slate-800/80 flex items-center justify-between shrink-0">
            <div className="flex items-center space-x-2">
              <Filter className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-[11px] font-semibold text-slate-400">Filter Status:</span>
              {['ALL', 'ACCEPTED', 'UNKNOWN', 'REJECTED'].map((st) => (
                <button
                  key={st}
                  onClick={() => setStatusFilter(st)}
                  className={`px-2 py-0.5 rounded text-[10px] font-semibold font-mono ${
                    statusFilter === st
                      ? 'bg-indigo-600 text-white'
                      : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>
            <span className="text-[11px] font-mono text-slate-500">
              Showing {filteredEvents.length} events
            </span>
          </div>

          {/* Event Stream List Table */}
          <div className="flex-1 overflow-y-auto font-mono text-xs">
            <table className="w-full text-left">
              <thead className="sticky top-0 bg-slate-950 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold font-sans">
                <tr>
                  <th className="py-2.5 px-3">Time</th>
                  <th className="py-2.5 px-3">Session</th>
                  <th className="py-2.5 px-3">Symbol</th>
                  <th className="py-2.5 px-3">State</th>
                  <th className="py-2.5 px-3">Level</th>
                  <th className="py-2.5 px-3">Result</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {filteredEvents.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-16 text-center text-slate-500 font-sans text-xs">
                      No matching protocol events in stream.
                    </td>
                  </tr>
                ) : (
                  filteredEvents.map((evt) => {
                    const isSelected = activeEvent?.event_id === evt.event_id;
                    return (
                      <tr
                        key={evt.event_id}
                        onClick={() => setSelectedEvent(evt)}
                        className={`cursor-pointer transition-colors ${
                          isSelected
                            ? 'bg-indigo-950/40 border-l-2 border-l-indigo-500'
                            : 'hover:bg-slate-800/50'
                        }`}
                      >
                        <td className="py-2 px-3 text-slate-400 text-[11px] font-sans">
                          {new Date(evt.timestamp > 1e11 ? evt.timestamp : evt.timestamp * 1000).toLocaleTimeString()}
                        </td>
                        <td className="py-2 px-3 text-indigo-300 font-bold truncate max-w-[120px]">{evt.session_id}</td>
                        <td className="py-2 px-3 text-sky-300 font-bold">{evt.symbol || evt.input_symbol}</td>
                        <td className="py-2 px-3 text-purple-300">{evt.formal_state}</td>
                        <td className="py-2 px-3 text-slate-400 text-[10px] font-sans">
                          {evt.analysis?.level_used || evt.analysis_level || 'DFA'}
                        </td>
                        <td className="py-2 px-3 font-sans">
                          <span className={`px-1.5 py-0.2 rounded text-[10px] font-semibold ${
                            evt.analysis?.status === 'ACCEPTED' || evt.status === 'ACCEPTED'
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                              : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                          }`}>
                            {evt.analysis?.status || evt.status}
                          </span>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Pane (1/3 width): Instant Context & Transduction Panel */}
        <div className="bg-slate-900/90 border border-slate-800/80 rounded-lg p-4 flex flex-col justify-between overflow-y-auto">
          {activeEvent ? (
            <div className="space-y-4">
              <div className="pb-3 border-b border-slate-800/80">
                <span className="text-[10px] uppercase font-bold text-slate-500 block">Selected Context</span>
                <h3 className="text-xs font-bold text-indigo-400 font-mono truncate">{activeEvent.event_id}</h3>
              </div>

              {/* Session & Symbol Info */}
              <div className="bg-slate-950 p-3 rounded border border-slate-800 font-mono text-xs space-y-2">
                <div>
                  <span className="text-[10px] text-slate-500 block font-sans">Target Session</span>
                  <span className="text-purple-300 font-bold truncate block">{activeEvent.session_id}</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <span className="text-[10px] text-slate-500 block font-sans">Input Symbol</span>
                    <span className="text-sky-300 font-bold">{activeEvent.symbol || activeEvent.input_symbol}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 block font-sans">Formal State</span>
                    <span className="text-purple-300 font-bold">{activeEvent.formal_state}</span>
                  </div>
                </div>
              </div>

              {/* Analysis Transduction Step */}
              <div className="bg-slate-950 p-3 rounded border border-slate-800 space-y-2 font-sans">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Formal Transduction</span>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">Analysis Tier:</span>
                  <span className="font-mono text-cyan-400 font-bold">{activeEvent.analysis?.level_used || 'DFA_MEALY'}</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">Result:</span>
                  <span className={`font-mono font-bold ${
                    (activeEvent.analysis?.status || activeEvent.status) === 'ACCEPTED' ? 'text-emerald-400' : 'text-rose-400'
                  }`}>
                    {activeEvent.analysis?.status || activeEvent.status}
                  </span>
                </div>
              </div>

              {/* Security Assessment Context */}
              <div className="bg-slate-950 p-3 rounded border border-slate-800 space-y-2 font-sans">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Security Classification</span>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">Classification:</span>
                  <span className="font-bold text-slate-200">{activeEvent.security?.classification || 'BENIGN'}</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400">Severity:</span>
                  <span className={`font-bold ${
                    (activeEvent.security?.severity || 'LOW') === 'HIGH' ? 'text-rose-400' : 'text-emerald-400'
                  }`}>
                    {activeEvent.security?.severity || 'LOW'}
                  </span>
                </div>
              </div>

              {/* Raw Payload Snippet */}
              {activeEvent.raw_payload_snippet && (
                <div className="bg-slate-950 p-3 rounded border border-slate-800 space-y-1 font-mono text-[11px]">
                  <span className="text-[10px] text-slate-500 font-sans font-bold uppercase block">Raw Payload</span>
                  <div className="bg-slate-900 p-2 rounded text-slate-300 overflow-x-auto whitespace-pre-wrap">
                    {activeEvent.raw_payload_snippet}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="py-12 text-center text-xs text-slate-500">
              Select an event from the stream to view state transduction context.
            </div>
          )}

          <div className="pt-3 border-t border-slate-800/80 text-[11px] text-slate-500 flex justify-between font-mono">
            <span>Latency: {activeEvent?.processing_latency_ms?.toFixed(2) || '0.00'} ms</span>
            <span>Events: {filteredEvents.length}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
