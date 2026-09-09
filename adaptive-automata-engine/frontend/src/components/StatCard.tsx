import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  unit?: string;
  subtitle?: string;
  icon: React.ElementType;
  color?: 'cyan' | 'purple' | 'amber' | 'emerald' | 'rose' | 'indigo';
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  unit,
  subtitle,
  icon: Icon,
  color = 'indigo',
  change,
  changeType = 'neutral',
}) => {
  const colorMap = {
    indigo: 'text-indigo-400 border-indigo-500/20 bg-indigo-500/10',
    cyan: 'text-cyan-400 border-cyan-500/20 bg-cyan-500/10',
    purple: 'text-purple-400 border-purple-500/20 bg-purple-500/10',
    amber: 'text-amber-400 border-amber-500/20 bg-amber-500/10',
    emerald: 'text-emerald-400 border-emerald-500/20 bg-emerald-500/10',
    rose: 'text-rose-400 border-rose-500/20 bg-rose-500/10',
  };

  const accentColor = colorMap[color] || colorMap.indigo;

  return (
    <div className="bg-slate-900/90 border border-slate-800/80 rounded-lg p-4 font-sans flex flex-col justify-between hover:border-slate-700/80 transition-colors shadow-sm">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        <div className={`p-1.5 rounded border ${accentColor}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="mt-2.5 flex items-baseline space-x-1.5">
        <span className="text-2xl font-bold font-mono text-slate-100 tracking-tight">{value}</span>
        {unit && <span className="text-xs font-mono text-slate-400">{unit}</span>}
      </div>

      {subtitle && (
        <div className="mt-2 text-[11px] text-slate-400 font-mono flex items-center justify-between pt-2 border-t border-slate-800/60">
          <span className="truncate">{subtitle}</span>
          {change && (
            <span className={`text-[10px] font-bold font-sans ${
              changeType === 'positive' ? 'text-emerald-400' : changeType === 'negative' ? 'text-rose-400' : 'text-slate-400'
            }`}>
              {change}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
