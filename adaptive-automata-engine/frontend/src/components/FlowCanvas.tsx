import React, { useMemo } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  Node,
  Edge,
  MarkerType,
  BackgroundVariant,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { AutomataGraphDTO } from '../types';

interface FlowCanvasProps {
  graphData: AutomataGraphDTO | null;
  currentState?: string;
  executionPath?: string[];
  onSelectNode?: (nodeId: string) => void;
  onSelectEdge?: (edgeId: string) => void;
}

export const FlowCanvas: React.FC<FlowCanvasProps> = ({
  graphData,
  currentState,
  executionPath = [],
  onSelectNode,
  onSelectEdge,
}) => {
  const nodes: Node[] = useMemo(() => {
    if (!graphData || !graphData.states || graphData.states.length === 0) {
      // Default placeholder nodes if no backend graph available
      return [
        {
          id: 'START',
          data: { label: 'START (q0)' },
          position: { x: 100, y: 150 },
          style: {
            background: '#0284c7',
            color: '#fff',
            border: '2px solid #38bdf8',
            borderRadius: '9999px',
            padding: '12px 20px',
            fontWeight: 'bold',
          },
        },
        {
          id: 'AUTH_REQ',
          data: { label: 'AUTH_REQ (q1)' },
          position: { x: 350, y: 150 },
          style: {
            background: '#1e293b',
            color: '#e2e8f0',
            border: '2px solid #475569',
            borderRadius: '8px',
            padding: '12px 20px',
          },
        },
        {
          id: 'ACCEPTED',
          data: { label: 'ACCEPTED (q_acc)' },
          position: { x: 600, y: 150 },
          style: {
            background: '#065f46',
            color: '#34d399',
            border: '2px solid #10b981',
            borderRadius: '8px',
            padding: '12px 20px',
            fontWeight: 'bold',
          },
        },
      ];
    }

    // Grid layout calculations
    const cols = Math.ceil(Math.sqrt(graphData.states.length));
    const pathSet = new Set(executionPath);

    return graphData.states.map((st, idx) => {
      const isStart = st === graphData.initial_state;
      const isAccepting = graphData.accepting_states?.includes(st);
      const isCurrent = st === currentState;
      const isInPath = pathSet.has(st);

      const col = idx % cols;
      const row = Math.floor(idx / cols);

      let bgColor = '#1e293b';
      let borderColor = '#475569';
      let textColor = '#cbd5e1';

      if (isStart) {
        bgColor = '#0369a1';
        borderColor = '#38bdf8';
        textColor = '#f0f9ff';
      }
      if (isAccepting) {
        bgColor = '#065f46';
        borderColor = '#34d399';
        textColor = '#ecfdf5';
      }
      if (isInPath) {
        borderColor = '#f59e0b';
      }
      if (isCurrent) {
        bgColor = '#4c1d95';
        borderColor = '#a855f7';
        textColor = '#faf5ff';
      }

      return {
        id: st,
        data: {
          label: (
            <div className="flex flex-col items-center">
              <span className="font-mono text-xs font-bold">{st}</span>
              <div className="flex gap-1 mt-1 text-[9px]">
                {isStart && <span className="bg-sky-400/20 text-sky-300 px-1 rounded">START</span>}
                {isAccepting && <span className="bg-emerald-400/20 text-emerald-300 px-1 rounded">ACCEPT</span>}
                {isCurrent && <span className="bg-purple-400/20 text-purple-300 px-1 rounded animate-pulse">ACTIVE</span>}
              </div>
            </div>
          ),
        },
        position: { x: col * 220 + 80, y: row * 160 + 80 },
        style: {
          background: bgColor,
          borderColor: borderColor,
          borderWidth: isCurrent || isInPath ? '3px' : '2px',
          color: textColor,
          borderRadius: isAccepting ? '9999px' : '10px',
          padding: '10px 16px',
          boxShadow: isCurrent ? '0 0 15px rgba(168, 85, 247, 0.5)' : 'none',
        },
      };
    });
  }, [graphData, currentState, executionPath]);

  const edges: Edge[] = useMemo(() => {
    if (!graphData || !graphData.transitions || graphData.transitions.length === 0) {
      return [
        {
          id: 'e1',
          source: 'START',
          target: 'AUTH_REQ',
          label: 'ClientHello',
          animated: true,
          style: { stroke: '#38bdf8' },
          markerEnd: { type: MarkerType.ArrowClosed, color: '#38bdf8' },
        },
        {
          id: 'e2',
          source: 'AUTH_REQ',
          target: 'ACCEPTED',
          label: 'AuthToken',
          animated: true,
          style: { stroke: '#34d399' },
          markerEnd: { type: MarkerType.ArrowClosed, color: '#34d399' },
        },
      ];
    }

    return graphData.transitions.map((tr, idx) => {
      const edgeId = `e-${tr.source}-${tr.symbol}-${tr.target}-${idx}`;
      const isPathEdge =
        executionPath.length > 1 &&
        executionPath.some((node, i) => i < executionPath.length - 1 && node === tr.source && executionPath[i + 1] === tr.target);

      return {
        id: edgeId,
        source: tr.source,
        target: tr.target,
        label: `${tr.symbol}${tr.output ? ` / ${tr.output}` : ''}`,
        animated: isPathEdge,
        style: {
          stroke: isPathEdge ? '#f59e0b' : '#64748b',
          strokeWidth: isPathEdge ? 3 : 1.5,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: isPathEdge ? '#f59e0b' : '#64748b',
        },
        labelStyle: { fill: '#94a3b8', fontSize: 10, fontWeight: 600 },
        labelBgStyle: { fill: '#0f172a', fillOpacity: 0.8 },
      };
    });
  }, [graphData, executionPath]);

  return (
    <div className="w-full h-full min-h-[500px] bg-slate-950 rounded-xl overflow-hidden border border-slate-800 relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodeClick={(_, node) => onSelectNode && onSelectNode(node.id)}
        onEdgeClick={(_, edge) => onSelectEdge && onSelectEdge(edge.id)}
        fitView
      >
        <Background color="#334155" variant={BackgroundVariant.Dots} gap={20} size={1} />
        <Controls className="bg-slate-900 border-slate-800 text-slate-200 fill-slate-200" />
      </ReactFlow>
    </div>
  );
};
