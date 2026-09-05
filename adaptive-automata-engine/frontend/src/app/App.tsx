import React, { useState } from 'react';
import { useApiData } from '../hooks/useApiData';
import { useWebSocket } from '../hooks/useWebSocket';
import { Navbar } from '../components/Navbar';
import { Sidebar, PageId } from '../components/Sidebar';

import { DashboardPage } from '../pages/DashboardPage';
import { LiveMonitorPage } from '../pages/LiveMonitorPage';
import { SessionsPage } from '../pages/SessionsPage';
import { AlertsPage } from '../pages/AlertsPage';
import { AutomataExplorerPage } from '../pages/AutomataExplorerPage';
import { AdaptationPage } from '../pages/AdaptationPage';
import { DriftPage } from '../pages/DriftPage';
import { AIInvestigationsPage } from '../pages/AIInvestigationsPage';
import { ExperimentsPage } from '../pages/ExperimentsPage';
import { SettingsPage } from '../pages/SettingsPage';

import { AlertOctagon, WifiOff } from 'lucide-react';

export const App: React.FC = () => {
  const [activePage, setActivePage] = useState<PageId>('dashboard');

  const {
    status,
    recentEvents,
    alerts,
    loading,
    error: apiError,
    refreshAll,
    appendEvent,
  } = useApiData();

  const { isConnected: wsConnected } = useWebSocket({
    onEvent: (evt) => {
      appendEvent(evt);
    },
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans flex flex-col selection:bg-indigo-500 selection:text-white">
      {/* Top SOC Navbar */}
      <Navbar status={status} wsConnected={wsConnected} onRefresh={refreshAll} />

      {/* Main Layout: Sidebar + Page Container */}
      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          activePage={activePage}
          onSelectPage={setActivePage}
          alertCount={alerts.length}
          unresolvedInvestigations={0}
        />

        <main className="flex-1 p-6 overflow-y-auto min-w-0 bg-slate-950">
          {/* Backend Connection Error Banner */}
          {apiError && (
            <div className="mb-6 p-4 bg-rose-950/60 border border-rose-500/50 rounded-xl flex items-center justify-between shadow-lg">
              <div className="flex items-center space-x-3 text-rose-300 text-xs">
                <AlertOctagon className="w-5 h-5 text-rose-400 shrink-0" />
                <div>
                  <span className="font-bold uppercase tracking-wider block">Backend Connection Degradation</span>
                  <span>{apiError} — Retrying background synchronization.</span>
                </div>
              </div>
              <button
                onClick={refreshAll}
                className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs rounded-lg transition-colors"
              >
                Retry
              </button>
            </div>
          )}

          {/* Page Routing Switch */}
          {activePage === 'dashboard' && (
            <DashboardPage
              status={status}
              alerts={alerts}
              recentEvents={recentEvents}
              onNavigateToAlerts={() => setActivePage('alerts')}
              onNavigateToMonitor={() => setActivePage('monitor')}
            />
          )}

          {activePage === 'monitor' && (
            <LiveMonitorPage
              events={recentEvents}
              wsConnected={wsConnected}
              onRefresh={refreshAll}
            />
          )}

          {activePage === 'sessions' && <SessionsPage />}

          {activePage === 'alerts' && (
            <AlertsPage
              alerts={alerts}
              onRefresh={refreshAll}
              onNavigateToInvestigations={() => setActivePage('investigations')}
            />
          )}

          {activePage === 'automata' && <AutomataExplorerPage />}

          {activePage === 'adaptation' && <AdaptationPage />}

          {activePage === 'drift' && <DriftPage />}

          {activePage === 'investigations' && <AIInvestigationsPage />}

          {activePage === 'experiments' && <ExperimentsPage />}

          {activePage === 'settings' && (
            <SettingsPage status={status} onRefresh={refreshAll} />
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
