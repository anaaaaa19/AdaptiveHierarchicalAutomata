import React, { useEffect, useState } from 'react';
import { AutomataGraphDTO, ModelVersionDTO } from '../types';
import { fetchModelGraph, fetchModels } from '../api/client';
import { FlowCanvas } from '../components/FlowCanvas';
import { GitGraph, ArrowDown, Cpu, Layers, RefreshCw } from 'lucide-react';

export const AutomataExplorerPage: React.FC = () => {
  const [graphData, setGraphData] = useState<AutomataGraphDTO | null>(null);
  const [models, setModels] = useState<ModelVersionDTO[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<string>('v1.0.0');
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const loadModelsAndGraph = async () => {
      setLoading(true);
      try {
        const mdls = await fetchModels();
        setModels(mdls);
        if (mdls.length > 0 && !selectedVersion) {
          setSelectedVersion(mdls[0].version_id);
        }
        const graph = await fetchModelGraph(selectedVersion || 'v1.0.0');
        setGraphData(graph);
      } catch (err) {
        console.error('Failed to fetch graph data', err);
      } finally {
        setLoading(false);
      }
    };
    loadModelsAndGraph();
  }, [selectedVersion]);

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <GitGraph className="w-5 h-5 text-sky-400" />
            <span>Formal Automata Explorer</span>
          </h2>
          <p className="text-xs text-slate-400">
            Interactive state machine graph loaded directly from backend model registry
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {/* Model Version Dropdown */}
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5">
            <span className="text-xs text-slate-400 font-semibold">Model Version:</span>
            <select
              value={selectedVersion}
              onChange={(e) => setSelectedVersion(e.target.value)}
              className="bg-slate-950 text-sky-400 font-mono font-bold text-xs rounded border border-slate-700 px-2 py-1 focus:outline-none focus:border-sky-500"
            >
              {models.length === 0 ? (
                <option value="v1.0.0">v1.0.0 (Default)</option>
              ) : (
                models.map((m) => (
                  <option key={m.version_id} value={m.version_id}>
                    {m.version_id} ({m.is_active ? 'ACTIVE' : m.status})
                  </option>
                ))
              )}
            </select>
          </div>

          <button
            onClick={() => setSelectedVersion((v) => v)}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 text-xs font-semibold"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Main Canvas + Hierarchy Side Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* React Flow Graph Visualizer */}
        <div className="lg:col-span-3 h-[600px] flex flex-col">
          <FlowCanvas
            graphData={graphData}
            onSelectNode={(nodeId) => {
              setSelectedNode(nodeId);
              setSelectedEdge(null);
            }}
            onSelectEdge={(edgeId) => {
              setSelectedEdge(edgeId);
              setSelectedNode(null);
            }}
          />
        </div>

        {/* Right Details & Hierarchy View Panel */}
        <div className="space-y-6">
          {/* Hierarchy Cascade Flow */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3">
            <h3 className="text-xs font-bold text-slate-200 uppercase flex items-center gap-2">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <span>Hierarchical Escalation Flow</span>
            </h3>

            <div className="space-y-2 text-xs font-mono">
              <div className="bg-slate-950 p-2.5 rounded border border-slate-800 text-center">
                <span className="text-slate-400 font-bold">Input Protocol Packet</span>
              </div>

              <div className="flex justify-center">
                <ArrowDown className="w-4 h-4 text-slate-500" />
              </div>

              <div className="bg-sky-950/60 p-2.5 rounded border border-sky-500/30 text-sky-300">
                <div className="font-bold flex justify-between">
                  <span>Level 1: DFA / Mealy</span>
                  <span className="text-emerald-400">95.2%</span>
                </div>
                <div className="text-[10px] text-slate-400 font-sans mt-0.5">O(1) State transition lookup</div>
              </div>

              <div className="flex justify-center">
                <ArrowDown className="w-4 h-4 text-amber-500/80" />
              </div>

              <div className="bg-amber-950/60 p-2.5 rounded border border-amber-500/30 text-amber-300">
                <div className="font-bold flex justify-between">
                  <span>Level 2: PDA</span>
                  <span className="text-amber-400">3.8%</span>
                </div>
                <div className="text-[10px] text-slate-400 font-sans mt-0.5">Stack-based context check</div>
              </div>

              <div className="flex justify-center">
                <ArrowDown className="w-4 h-4 text-rose-500/80" />
              </div>

              <div className="bg-rose-950/60 p-2.5 rounded border border-rose-500/30 text-rose-300">
                <div className="font-bold flex justify-between">
                  <span>Level 3: CFG</span>
                  <span className="text-rose-400">1.0%</span>
                </div>
                <div className="text-[10px] text-slate-400 font-sans mt-0.5">Grammar bounds parsing</div>
              </div>
            </div>
          </div>

          {/* Node/Edge Inspector Card */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3">
            <h3 className="text-xs font-bold text-slate-200 uppercase flex items-center gap-2">
              <Layers className="w-4 h-4 text-purple-400" />
              <span>Inspector Panel</span>
            </h3>

            {selectedNode ? (
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-2 text-xs">
                <div className="text-slate-400 font-bold">State Selected:</div>
                <div className="font-mono text-cyan-400 text-sm font-bold">{selectedNode}</div>
                {graphData?.initial_state === selectedNode && (
                  <div className="px-2 py-0.5 bg-sky-500/20 text-sky-400 rounded text-[10px] font-bold w-fit">
                    INITIAL STATE (q0)
                  </div>
                )}
                {graphData?.accepting_states?.includes(selectedNode) && (
                  <div className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-[10px] font-bold w-fit">
                    ACCEPTING STATE (q_acc)
                  </div>
                )}
              </div>
            ) : selectedEdge ? (
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 space-y-2 text-xs">
                <div className="text-slate-400 font-bold">Transition Selected:</div>
                <div className="font-mono text-amber-400 text-xs font-bold">{selectedEdge}</div>
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">
                Click any state or transition in the graph to inspect formal state details.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
