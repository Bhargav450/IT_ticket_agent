import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import IncidentList from './components/IncidentList';
import IncidentDetail from './components/IncidentDetail';
import InfraSimulator from './components/InfraSimulator';
import KnowledgeBase from './components/KnowledgeBase';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import CreateIncidentModal from './components/CreateIncidentModal';
import EmployeePortal from './components/EmployeePortal';
import Login from './components/Login';
import { api, auth } from './api/client';

export default function App() {
  const [currentUser, setCurrentUser] = useState(() => auth.getUser());
  const [activeTab, setActiveTab] = useState('incidents');
  const [incidents, setIncidents] = useState([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState(null);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [incidentSteps, setIncidentSteps] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  // Load Incidents
  const fetchIncidents = async () => {
    try {
      const data = await api.getIncidents();
      setIncidents(data);
      // Only set initial selection if no incident has been selected yet
      setSelectedIncidentId(prev => {
        if (prev) return prev;
        return data.length > 0 ? data[0].id : null;
      });
    } catch (err) {
      console.error(err);
    }
  };

  // Load Incident Details & Steps
  const fetchDetail = async (id) => {
    if (!id) return;
    try {
      const inc = await api.getIncident(id);
      setSelectedIncident(inc);
      const st = await api.getIncidentSteps(id);
      setIncidentSteps(st);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (currentUser) {
      fetchIncidents();
      const interval = setInterval(fetchIncidents, 3000);
      return () => clearInterval(interval);
    }
  }, [currentUser]);

  useEffect(() => {
    if (!currentUser || !selectedIncidentId) return;
    fetchDetail(selectedIncidentId);
    // Stop polling once the incident reaches a terminal state
    const isTerminal = selectedIncident && ['RESOLVED', 'ESCALATED', 'CLOSED'].includes(selectedIncident.status);
    if (isTerminal) return;
    const interval = setInterval(() => fetchDetail(selectedIncidentId), 2500);
    return () => clearInterval(interval);
  }, [selectedIncidentId, selectedIncident?.status, currentUser]);

  const handleLogout = () => {
    auth.logout();
    setCurrentUser(null);
    setSelectedIncidentId(null);
    setSelectedIncident(null);
  };

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    if (user.role === 'employee') {
      setActiveTab('my-tickets');
    } else {
      setActiveTab('incidents');
    }
  };

  // If not logged in, show modern Login screen
  if (!currentUser) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  const isAdmin = currentUser.role === 'admin' || currentUser.role === 'support_engineer';

  // Trigger Autonomous Agent on Incident (Admin only)
  const handleTriggerAgent = async (id) => {
    setIsProcessing(true);
    try {
      await api.triggerAgent(id);
      await fetchDetail(id);
      await fetchIncidents();
    } catch (err) {
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  // Handle Human-in-the-Loop Approval (Admin only)
  const handleApproveAction = async (id, approved, feedback) => {
    setIsProcessing(true);
    try {
      await api.approveAction(id, approved, feedback);
      await fetchDetail(id);
      await fetchIncidents();
    } catch (err) {
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  // Create Incident
  const handleCreateIncident = async (data) => {
    const newInc = await api.createIncident({
      ...data,
      reporter_email: data.reporter_email || currentUser.email || 'employee@enterprise.io'
    });
    await fetchIncidents();
    setSelectedIncidentId(newInc.id);
    setActiveTab('incidents');
  };

  // Quick Demo Simulator
  const handleSimulateDemo = async () => {
    try {
      await api.simulateFailure('http_500_gateway');
      const newInc = await api.createIncident({
        title: 'Application returning HTTP 500 errors. Cannot access checkout.',
        description: 'My application is returning HTTP 500 errors. I cannot access the application.',
        severity: 'P1_CRITICAL',
        reporter_email: currentUser.email || 'employee@enterprise.io',
      });
      await fetchIncidents();
      setSelectedIncidentId(newInc.id);
      setActiveTab('incidents');
    } catch (err) {
      console.error(err);
    }
  };

  const pendingApprovalsCount = incidents.filter(i => i.status === 'AWAITING_APPROVAL').length;

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenCreate={() => setIsCreateOpen(true)}
        onSimulateDemo={handleSimulateDemo}
        pendingApprovalsCount={pendingApprovalsCount}
        currentUser={currentUser}
        onLogout={handleLogout}
      />

      {/* 👤 EMPLOYEE VIEW */}
      {!isAdmin ? (
        <main className="flex-1">
          <EmployeePortal
            user={currentUser}
            incidents={incidents}
            onRefresh={fetchIncidents}
          />
        </main>
      ) : (
        /* 🛡️ ADMIN / SRE VIEW */
        <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
          {activeTab === 'incidents' && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-full">
              {/* Left Column: Incidents List */}
              <div className="lg:col-span-5 h-[calc(100vh-140px)]">
                <IncidentList
                  incidents={incidents}
                  selectedId={selectedIncidentId}
                  onSelectIncident={(id) => setSelectedIncidentId(id)}
                />
              </div>

              {/* Right Column: Incident Studio & Agent Execution */}
              <div className="lg:col-span-7 h-[calc(100vh-140px)] overflow-y-auto pr-1">
                <IncidentDetail
                  incident={selectedIncident}
                  steps={incidentSteps}
                  onTriggerAgent={handleTriggerAgent}
                  onApproveAction={handleApproveAction}
                  isProcessing={isProcessing}
                />
              </div>
            </div>
          )}

          {activeTab === 'infra' && <InfraSimulator />}
          {activeTab === 'knowledge' && <KnowledgeBase />}
          {activeTab === 'analytics' && <AnalyticsDashboard />}
        </main>
      )}

      {isAdmin && (
        <CreateIncidentModal
          isOpen={isCreateOpen}
          onClose={() => setIsCreateOpen(false)}
          onCreate={handleCreateIncident}
        />
      )}
    </div>
  );
}

