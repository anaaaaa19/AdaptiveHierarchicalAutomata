import React from 'react';
import {
  LayoutDashboard,
  Activity,
  Layers,
  ShieldAlert,
  Cpu,
  GitMerge,
  BarChart3,
  Search,
  Settings,
  TrendingUp,
} from 'lucide-react';

export type PageId =
  | 'dashboard'
  | 'monitor'
  | 'sessions'
  | 'alerts'
  | 'automata'
  | 'adaptation'
  | 'drift'
  | 'investigations'
  | 'experiments'
  | 'settings';

interface SidebarProps {
  activePage: PageId;
  onSelectPage: (page: PageId) => void;
  alertCount?: number;
  unresolvedInvestigations?: number;
}

interface NavItem {
  id: PageId;
  label: string;
  icon: React.ElementType;
  badge?: number;
  badgeColor?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activePage,
  onSelectPage,
  alertCount = 0,
  unresolvedInvestigations = 0,
}) => {
  const navItems: NavItem[] = [
    { id: 'dashboard', label: 'Overview', icon: LayoutDashboard },
    { id: 'monitor', label: 'Live Monitor', icon: Activity },
    { id: 'sessions', label: 'Sessions', icon: Layers },
    { id: 'alerts', label: 'Security Alerts', icon: ShieldAlert, badge: alertCount, badgeColor: 'bg-rose-500/20 text-rose-300 border border-rose-500/30' },
    { id: 'automata', label: 'Automata Explorer', icon: Cpu },
    { id: 'adaptation', label: 'Adaptation', icon: GitMerge },
    { id: 'drift', label: 'Drift Analytics', icon: TrendingUp },
    { id: 'investigations', label: 'Investigations', icon: Search, badge: unresolvedInvestigations, badgeColor: 'bg-purple-500/20 text-purple-300 border border-purple-500/30' },
    { id: 'experiments', label: 'Analytics & Benchmarks', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-60 bg-slate-950 border-r border-slate-800/80 flex flex-col shrink-0 min-h-[calc(100vh-57px)] font-sans">
      <div className="px-4 py-3 text-[10px] font-bold uppercase tracking-wider text-slate-500 border-b border-slate-900">
        Navigation
      </div>

      <nav className="flex-1 px-2.5 py-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectPage(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-md text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-slate-900 text-indigo-300 border border-slate-800 border-l-2 border-l-indigo-500 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border border-transparent'
              }`}
            >
              <div className="flex items-center space-x-2.5">
                <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-500'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span className={`px-1.5 py-0.2 text-[10px] font-mono font-bold rounded ${item.badgeColor || 'bg-slate-800 text-slate-300'}`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer system status hint */}
      <div className="p-3.5 border-t border-slate-900 bg-slate-950 text-xs text-slate-400 space-y-1">
        <div className="flex justify-between items-center text-[10px] text-slate-500 font-mono">
          <span>ENGINE CORE</span>
          <span className="text-emerald-400 font-semibold flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>ONLINE</span>
          </span>
        </div>
        <div className="text-[10px] text-slate-600 truncate font-mono">
          FastAPI + Hierarchical Automata
        </div>
      </div>
    </aside>
  );
};
