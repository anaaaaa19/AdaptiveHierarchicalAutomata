import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

interface CascadePieChartProps {
  dfaPct: number;
  pdaPct: number;
  cfgPct: number;
}

export const CascadePieChart: React.FC<CascadePieChartProps> = ({ dfaPct, pdaPct, cfgPct }) => {
  const data = [
    { name: 'Level 1: DFA / Mealy (Normal)', value: dfaPct, color: '#38bdf8' },
    { name: 'Level 2: PDA (Context Shift)', value: pdaPct, color: '#fbbf24' },
    { name: 'Level 3: CFG (Structural Anomaly)', value: cfgPct, color: '#f87171' },
  ];

  return (
    <div className="w-full h-64 flex flex-col justify-center items-center">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={85}
            paddingAngle={4}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} stroke="#0f172a" strokeWidth={2} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#0f172a',
              borderColor: '#334155',
              borderRadius: '8px',
              color: '#f8fafc',
              fontSize: '12px',
            }}
            formatter={(value: any) => [`${value}%`, 'Resolution Share']}
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value: string) => <span className="text-xs text-slate-300 font-medium">{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
