import React from 'react';

export const TableSkeleton: React.FC<{ rows?: number; cols?: number }> = ({ rows = 5, cols = 6 }) => {
  return (
    <div className="w-full space-y-3 animate-pulse">
      {Array.from({ length: rows }).map((_, rIdx) => (
        <div key={rIdx} className="flex items-center space-x-4 py-3 px-4 bg-slate-900/60 rounded-lg border border-slate-800/40">
          {Array.from({ length: cols }).map((_, cIdx) => (
            <div
              key={cIdx}
              className="h-4 bg-slate-800/80 rounded"
              style={{ width: `${100 / cols}%` }}
            />
          ))}
        </div>
      ))}
    </div>
  );
};

export const CardSkeleton: React.FC = () => {
  return (
    <div className="bg-slate-900/60 border border-slate-800/60 rounded-xl p-5 space-y-3 animate-pulse">
      <div className="h-4 w-1/3 bg-slate-800/80 rounded" />
      <div className="h-8 w-1/2 bg-slate-800/80 rounded" />
      <div className="h-3 w-2/3 bg-slate-800/40 rounded" />
    </div>
  );
};
