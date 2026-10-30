import React, { useState } from 'react';
import { 
  AlertCircle, 
  Clock, 
  CheckCircle, 
  Bot, 
  Search, 
  Filter, 
  ExternalLink, 
  Layers, 
  Activity,
  User
} from 'lucide-react';

export default function IncidentList({ incidents, selectedId, onSelectIncident }) {
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  const filtered = incidents.filter(inc => {
    const matchesFilter = 
      filterStatus === 'ALL' ? true :
      filterStatus === 'AWAITING' ? inc.status === 'AWAITING_APPROVAL' :
      filterStatus === 'ACTIVE' ? ['OPEN', 'INVESTIGATING', 'VERIFYING'].includes(inc.status) :
      filterStatus === 'RESOLVED' ? inc.status === 'RESOLVED' : true;

    const matchesSearch = 
      inc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inc.ticket_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (inc.affected_service && inc.affected_service.toLowerCase().includes(searchTerm.toLowerCase()));

    return matchesFilter && matchesSearch;
  });

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case 'P1_CRITICAL':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">P1 CRITICAL</span>;
      case 'P2_HIGH':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">P2 HIGH</span>;
      case 'P3_MEDIUM':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">P3 MEDIUM</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-500/20 text-slate-300 border border-slate-500/30">P4 LOW</span>;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'AWAITING_APPROVAL':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40 animate-pulse">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-400"></span>
            Approval Required
          </span>
        );
      case 'RESOLVED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle className="w-3 h-3 text-emerald-400" />
            Resolved
          </span>
        );
      case 'INVESTIGATING':
      case 'VERIFYING':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-sky-500/10 text-sky-400 border border-sky-500/20">
            <Activity className="w-3 h-3 text-sky-400 animate-spin" />
            Investigating
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-slate-800 text-slate-300 border border-slate-700">
            Open
          </span>
        );
    }
  };

  return (
    <div className="bg-slate-900/60 rounded-xl border border-slate-800 p-4 flex flex-col h-full">
      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 mb-4">
        {/* Filter Buttons */}
        <div className="flex items-center gap-1 bg-slate-950/60 p-1 rounded-lg border border-slate-800 w-full sm:w-auto">
          {[
            { id: 'ALL', label: 'All' },
            { id: 'ACTIVE', label: 'Active' },
            { id: 'AWAITING', label: 'Awaiting Gate' },
            { id: 'RESOLVED', label: 'Resolved' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setFilterStatus(tab.id)}
              className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${
                filterStatus === tab.id
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search tickets, service..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>
      </div>

      {/* Incidents List */}
      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
        {filtered.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-xs">
            No incidents matching current filter.
          </div>
        ) : (
          filtered.map(inc => {
            const isSelected = selectedId === inc.id;
            return (
              <div
                key={inc.id}
                onClick={() => onSelectIncident(inc.id)}
                className={`p-3.5 rounded-lg border transition-all cursor-pointer flex flex-col gap-2 ${
                  isSelected
                    ? 'bg-blue-950/40 border-blue-500/60 shadow-md shadow-blue-900/20'
                    : 'bg-slate-950/40 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/40'
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-slate-300">
                      {inc.ticket_number}
                    </span>
                    {getSeverityBadge(inc.severity)}
                    {inc.affected_service && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300 border border-slate-700">
                        {inc.affected_service}
                      </span>
                    )}
                  </div>
                  {getStatusBadge(inc.status)}
                </div>

                <h4 className="text-sm font-semibold text-slate-100 line-clamp-1">
                  {inc.title}
                </h4>

                <p className="text-xs text-slate-400 line-clamp-2">
                  {inc.description}
                </p>

                <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-800/60 mt-1">
                  <div className="flex items-center gap-1.5">
                    <Bot className="w-3.5 h-3.5 text-blue-400" />
                    <span className="text-slate-400">{inc.assigned_agent}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    {inc.resolution_time_seconds > 0 && (
                      <span className="text-emerald-400 font-mono">
                        MTTR: {inc.resolution_time_seconds}s
                      </span>
                    )}
                    <span className="text-slate-500">
                      {new Date(inc.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

