import React from 'react';
import {
  LayoutDashboard,
  Activity,
  Layers,
  AlertTriangle,
  GitGraph,
  RefreshCw,
  TrendingUp,
  Brain,
  FlaskConical,
  Settings,
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
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'monitor', label: 'Live Monitor', icon: Activity },
    { id: 'sessions', label: 'Sessions', icon: Layers },
    { id: 'alerts', label: 'Alerts', icon: AlertTriangle, badge: alertCount, badgeColor: 'bg-rose-500 text-white' },
    { id: 'automata', label: 'Automata Explorer', icon: GitGraph },
    { id: 'adaptation', label: 'Adaptation', icon: RefreshCw },
    { id: 'drift', label: 'Drift Analytics', icon: TrendingUp },
    { id: 'investigations', label: 'AI Investigations', icon: Brain, badge: unresolvedInvestigations, badgeColor: 'bg-purple-500 text-white' },
    { id: 'experiments', label: 'Experiments (Phase 9)', icon: FlaskConical },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-slate-900/90 border-r border-slate-800 flex flex-col shrink-0 min-h-[calc(100vh-61px)]">
      <div className="p-4 uppercase tracking-wider text-[10px] font-bold text-slate-500 border-b border-slate-800/60">
        Engine Navigation
      </div>
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectPage(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-gradient-to-r from-indigo-600/30 to-indigo-500/10 text-indigo-300 border border-indigo-500/30 shadow-md'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span className={`px-2 py-0.5 text-[11px] font-bold rounded-full ${item.badgeColor || 'bg-slate-700 text-slate-300'}`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer system status hint */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40 text-xs text-slate-400 space-y-1">
        <div className="flex justify-between items-center text-[11px] text-slate-500">
          <span>Engine Core</span>
          <span className="text-emerald-400 font-mono font-semibold">ONLINE</span>
        </div>
        <div className="text-[10px] text-slate-600 truncate font-mono">
          FastAPI + Formal Engine L1-L3
        </div>
      </div>
    </aside>
  );
};
