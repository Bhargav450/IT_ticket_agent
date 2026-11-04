import React, { useState } from 'react';
import { 
  PlusCircle, 
  Clock, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles, 
  HelpCircle, 
  FileText, 
  Laptop, 
  ExternalLink,
  ShieldAlert
} from 'lucide-react';
import { api } from '../api/client';

export default function EmployeePortal({ user, incidents, onRefresh }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    severity: 'P3_MEDIUM'
  });

  // Filter incidents reported by this employee or show enterprise demo tickets
  const myIncidents = incidents.filter(
    (inc) => inc.reporter_email?.toLowerCase() === user.email?.toLowerCase() || !user.email
  );

  const activeTicket = selectedIncident || (myIncidents.length > 0 ? myIncidents[0] : null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title || !formData.description) return;
    setSubmitting(true);
    try {
      const created = await api.createIncident({
        ...formData,
        reporter_email: user.email || 'employee@enterprise.io'
      });
      setFormData({ title: '', description: '', severity: 'P3_MEDIUM' });
      setIsModalOpen(false);
      setSelectedIncident(created);
      onRefresh();
    } catch (err) {
      alert(`Error submitting ticket: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'RESOLVED':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Resolved
          </span>
        );
      case 'INVESTIGATING':
      case 'OPEN':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 animate-pulse">
            <Clock className="w-3.5 h-3.5" />
            AI Investigating...
          </span>
        );
      case 'AWAITING_APPROVAL':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <AlertCircle className="w-3.5 h-3.5" />
            Pending Engineer Sign-off
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-300">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Welcome Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-blue-900/40 via-indigo-900/30 to-slate-900 border border-blue-800/30 shadow-xl flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              Welcome, {user.user_name || 'Employee'}
            </h1>
            <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              Employee Portal
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400 max-w-xl">
            Need IT help, VPN access, or software troubleshooting? Submit a request and our autonomous agent will investigate and resolve it immediately.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm shadow-lg shadow-blue-600/30 transition-all hover:scale-[1.02] active:scale-[0.98] shrink-0"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Raise New IT Ticket</span>
        </button>
      </div>

      {/* Main Split: Ticket List (Left) & Ticket Details (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: My Tickets */}
        <div className="lg:col-span-5 bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-lg flex flex-col h-[600px]">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-400" />
              My Tickets ({myIncidents.length})
            </h2>
            <button
              onClick={onRefresh}
              className="text-xs text-slate-400 hover:text-white transition-colors"
            >
              Refresh
            </button>
          </div>

          <div className="flex-1 overflow-y-auto mt-3 space-y-2.5 pr-1">
            {myIncidents.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-500">
                <Laptop className="w-10 h-10 mb-2 stroke-[1.5]" />
                <p className="text-sm font-medium text-slate-400">No tickets submitted yet</p>
                <p className="text-xs mt-1">Click "Raise New IT Ticket" above to get started.</p>
              </div>
            ) : (
              myIncidents.map((inc) => (
                <div
                  key={inc.id}
                  onClick={() => setSelectedIncident(inc)}
                  className={`p-3.5 rounded-xl border text-left cursor-pointer transition-all ${
                    activeTicket?.id === inc.id
                      ? 'bg-blue-600/10 border-blue-500/40 shadow-sm'
                      : 'bg-slate-800/40 border-slate-700/50 hover:bg-slate-800/80 hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-[11px] font-mono font-semibold text-blue-400">
                      Ticket #{inc.ticket_number}
                    </span>
                    {getStatusBadge(inc.status)}
                  </div>
                  <h3 className="text-xs font-semibold text-white line-clamp-1">
                    {inc.title}
                  </h3>
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-1">
                    {inc.description}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Column: Ticket Status & AI Resolution View */}
        <div className="lg:col-span-7 bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-lg flex flex-col h-[600px] overflow-y-auto">
          {activeTicket ? (
            <div className="space-y-5">
              {/* Ticket Header */}
              <div className="pb-4 border-b border-slate-800 flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono font-bold text-blue-400">
                      #{activeTicket.ticket_number}
                    </span>
                    <span className="text-xs text-slate-500">•</span>
                    <span className="text-xs text-slate-400">
                      Submitted by {activeTicket.reporter_email}
                    </span>
                  </div>
                  <h2 className="text-base sm:text-lg font-bold text-white">
                    {activeTicket.title}
                  </h2>
                </div>
                <div>{getStatusBadge(activeTicket.status)}</div>
              </div>

              {/* Description */}
              <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-800">
                <h4 className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                  Your Problem Description
                </h4>
                <p className="text-xs sm:text-sm text-slate-200 whitespace-pre-wrap leading-relaxed">
                  {activeTicket.description}
                </p>
              </div>

              {/* AI Autonomous Resolution Box */}
              {activeTicket.status === 'RESOLVED' ? (
                <div className="p-5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 space-y-3">
                  <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
                    <Sparkles className="w-4 h-4" />
                    <span>Autonomous AI Resolution Provided</span>
                  </div>

                  {activeTicket.root_cause_analysis && (
                    <div>
                      <h4 className="text-[11px] font-semibold text-emerald-300 uppercase tracking-wider mb-1">
                        Root Cause
                      </h4>
                      <p className="text-xs text-slate-200 bg-slate-900/60 p-3 rounded-lg border border-emerald-500/20">
                        {activeTicket.root_cause_analysis}
                      </p>
                    </div>
                  )}

                  {activeTicket.resolution_notes && (
                    <div>
                      <h4 className="text-[11px] font-semibold text-emerald-300 uppercase tracking-wider mb-1">
                        Action & Next Steps
                      </h4>
                      <div className="text-xs text-slate-200 bg-slate-900/60 p-3 rounded-lg border border-emerald-500/20 whitespace-pre-wrap leading-relaxed">
                        {activeTicket.resolution_notes}
                      </div>
                    </div>
                  )}

                  <div className="flex items-center gap-2 pt-2 text-[11px] text-emerald-400/80">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Synchronized & closed in enterprise helpdesk (Zammad).</span>
                  </div>
                </div>
              ) : (
                <div className="p-6 rounded-xl bg-blue-500/5 border border-blue-500/20 text-center space-y-2">
                  <div className="inline-flex p-3 rounded-xl bg-blue-500/10 text-blue-400">
                    <Clock className="w-6 h-6 animate-spin" />
                  </div>
                  <h3 className="text-sm font-semibold text-white">Investigation in Progress</h3>
                  <p className="text-xs text-slate-400 max-w-md mx-auto">
                    The autonomous agent is searching corporate runbooks, inspecting service health, and preparing a fix. Your ticket will update automatically.
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center text-slate-500 p-8">
              <HelpCircle className="w-12 h-12 mb-3 stroke-[1.5]" />
              <h3 className="text-sm font-semibold text-slate-300">No ticket selected</h3>
              <p className="text-xs mt-1">Select a ticket from the left or create a new one.</p>
            </div>
          )}
        </div>
      </div>

      {/* New Ticket Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl relative">
            <h3 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
              <PlusCircle className="w-5 h-5 text-blue-400" />
              Raise an IT Incident
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Describe what's broken and the autonomous agent will immediately begin diagnosis.
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Issue Summary (Title) *
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="e.g. Cannot connect to GlobalProtect VPN on Mac"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Detailed Description *
                </label>
                <textarea
                  rows={4}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Provide error messages, error codes, what steps you were taking..."
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Severity / Urgency
                </label>
                <select
                  value={formData.severity}
                  onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40"
                >
                  <option value="P4_LOW">P4 - Low (General inquiry / How-to)</option>
                  <option value="P3_MEDIUM">P3 - Medium (Minor inconvenience)</option>
                  <option value="P2_HIGH">P2 - High (Cannot perform work / outage)</option>
                  <option value="P1_CRITICAL">P1 - Critical (Entire service / app down)</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-all shadow-md shadow-blue-600/30 disabled:opacity-50"
                >
                  {submitting ? 'Submitting...' : 'Submit Ticket'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

