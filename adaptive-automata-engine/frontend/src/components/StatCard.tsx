import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  unit?: string;
  subtitle?: string;
  icon?: React.ElementType;
  trend?: {
    value: string;
    isPositive?: boolean;
  };
  color?: 'cyan' | 'emerald' | 'purple' | 'rose' | 'amber' | 'indigo';
}

const colorMap = {
  cyan: { text: 'text-cyan-400', bg: 'bg-cyan-500/10', border: 'border-cyan-500/20' },
  emerald: { text: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' },
  purple: { text: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/20' },
  rose: { text: 'text-rose-400', bg: 'bg-rose-500/10', border: 'border-rose-500/20' },
  amber: { text: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' },
  indigo: { text: 'text-indigo-400', bg: 'bg-indigo-500/10', border: 'border-indigo-500/20' },
};

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  unit,
  subtitle,
  icon: Icon,
  trend,
  color = 'cyan',
}) => {
  const styles = colorMap[color] || colorMap.cyan;

  return (
    <div className={`bg-slate-900/80 border ${styles.border} rounded-xl p-4 shadow-sm backdrop-blur-sm flex flex-col justify-between`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          {title}
        </span>
        {Icon && (
          <div className={`p-2 rounded-lg ${styles.bg} ${styles.text}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="mt-2 flex items-baseline justify-between">
        <div className="flex items-baseline space-x-1.5">
          <span className={`text-2xl font-bold font-mono tracking-tight ${styles.text}`}>
            {value}
          </span>
          {unit && <span className="text-xs text-slate-400 font-medium">{unit}</span>}
        </div>
        {trend && (
          <span className={`text-xs font-semibold ${trend.isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
            {trend.value}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="mt-1 text-[11px] text-slate-500 truncate">
          {subtitle}
        </p>
      )}
    </div>
  );
};
