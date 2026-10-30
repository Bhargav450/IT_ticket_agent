import React, { useState } from 'react';
import { 
  ShieldAlert, 
  CheckCircle2, 
  Clock, 
  Terminal, 
  BookOpen, 
  Play, 
  RefreshCw, 
  CheckCircle, 
  ExternalLink,
  ChevronDown,
  ChevronRight,
  User,
  AlertCircle
} from 'lucide-react';
import AgentExecutionStream from './AgentExecutionStream';
import HumanApprovalModal from './HumanApprovalModal';

export default function IncidentDetail({ 
  incident, 
  steps, 
  onTriggerAgent, 
  onApproveAction, 
  isProcessing 
}) {
  const [expandedCitation, setExpandedCitation] = useState(null);

  if (!incident) {
    return (
      <div className="bg-slate-900/60 rounded-xl border border-slate-800 p-12 text-center text-slate-500 text-xs flex flex-col items-center justify-center h-full">
        <ShieldAlert className="w-10 h-10 text-slate-700 mb-3" />
        <p>Select an incident from the list to view autonomous diagnostic trajectory.</p>
      </div>
    );
  }

  const toggleCitation = (idx) => {
    setExpandedCitation(expandedCitation === idx ? null : idx);
  };

  const isResolved = incident.status === 'RESOLVED';
  const isAwaiting = incident.status === 'AWAITING_APPROVAL';

  return (
    <div className="space-y-4">
      {/* Top Banner & Header */}
      <div className="bg-slate-900/80 rounded-xl border border-slate-800 p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <span className="font-mono text-sm font-bold text-blue-400 bg-blue-500/10 px-2.5 py-1 rounded-md border border-blue-500/20">
              {incident.ticket_number}
            </span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
              {incident.category}
            </span>
            {incident.affected_service && (
              <span className="text-xs font-mono font-medium px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-cyan-500/30">
                svc:{incident.affected_service}
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {(!isResolved && !isAwaiting) && (
              <button
                onClick={() => onTriggerAgent(incident.id)}
                disabled={isProcessing}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 text-white hover:bg-blue-500 shadow-md shadow-blue-600/20 transition-all disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5" />
                <span>{isProcessing ? 'Agent Running...' : 'Investigate Ticket'}</span>
              </button>
            )}
            
            {isResolved && (
              <div className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <CheckCircle2 className="w-4 h-4" />
                <span>Resolved & Verified</span>
              </div>
            )}
          </div>
        </div>

        <div className="mt-4">
          <h2 className="text-lg font-bold text-white mb-2 leading-snug">
            {incident.title}
          </h2>
          <p className="text-xs text-slate-400 leading-relaxed bg-slate-950/60 p-3 rounded-lg border border-slate-800">
            {incident.description}
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-4 pt-3 border-t border-slate-800/80 text-[11px]">
          <div>
            <span className="text-slate-500 block">Reporter</span>
            <span className="text-slate-300 font-medium">{incident.reporter_email}</span>
          </div>
          <div>
            <span className="text-slate-500 block">Status</span>
            <span className="text-slate-200 font-semibold">{incident.status}</span>
          </div>
          <div>
            <span className="text-slate-500 block">Severity</span>
            <span className="text-amber-400 font-semibold">{incident.severity}</span>
          </div>
          <div>
            <span className="text-slate-500 block">MTTR (Resolution Time)</span>
            <span className="text-emerald-400 font-mono font-semibold">
              {incident.resolution_time_seconds ? `${incident.resolution_time_seconds}s` : 'In Progress'}
            </span>
          </div>
        </div>
      </div>

      {/* Human In The Loop Gate Card (Appears when awaiting human authorization) */}
      {isAwaiting && (
        <HumanApprovalModal 
          incident={incident} 
          onApprove={onApproveAction} 
          isProcessing={isProcessing} 
        />
      )}

      {/* Root Cause Analysis & Findings Card */}
      {incident.root_cause_analysis && (
        <div className="bg-slate-900/60 rounded-xl border border-slate-800 p-4">
          <div className="flex items-center gap-2 mb-3">
            <Terminal className="w-4 h-4 text-cyan-400" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Autonomous Root Cause Analysis (RCA)
            </h3>
          </div>
          <div className="p-3 bg-cyan-950/20 border border-cyan-500/20 rounded-lg text-xs text-cyan-200 leading-relaxed font-mono">
            {incident.root_cause_analysis}
          </div>
        </div>
      )}

      {/* RAG Knowledge Runbook Citations */}
      {incident.rag_sources && incident.rag_sources.length > 0 && (
        <div className="bg-slate-900/60 rounded-xl border border-slate-800 p-4">
          <div className="flex items-center gap-2 mb-3">
            <BookOpen className="w-4 h-4 text-amber-400" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Internal Knowledge Citations (RAG)
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.2 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
              {incident.rag_sources.length} Runbooks Matched
            </span>
          </div>

          <div className="space-y-2">
            {incident.rag_sources.map((cit, idx) => (
              <div 
                key={idx}
                className="bg-slate-950/80 rounded-lg border border-slate-800 p-3 text-xs"
              >
                <div 
                  onClick={() => toggleCitation(idx)}
                  className="flex items-center justify-between cursor-pointer"
                >
                  <div className="flex items-center gap-2">
                    {expandedCitation === idx ? (
                      <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                    ) : (
                      <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
                    )}
                    <span className="font-semibold text-slate-200">{cit.document_title}</span>
                    <span className="text-[10px] font-mono text-slate-400">({cit.filename})</span>
                  </div>
                  <span className="text-[10px] font-mono text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                    Similarity: {cit.similarity_score}
                  </span>
                </div>

                {expandedCitation === idx && (
                  <div className="mt-2.5 pt-2.5 border-t border-slate-800/80 text-[11px] text-slate-400 font-mono leading-relaxed bg-slate-900/50 p-2.5 rounded">
                    <pre className="whitespace-pre-wrap">{cit.excerpt}</pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Verification & Resolution Summary */}
      {isResolved && incident.resolution_notes && (
        <div className="bg-emerald-950/20 rounded-xl border border-emerald-500/30 p-4">
          <div className="flex items-center gap-2 mb-2 text-emerald-400">
            <CheckCircle className="w-4 h-4" />
            <h3 className="text-xs font-bold uppercase tracking-wider">
              Verification & Final Resolution Summary
            </h3>
          </div>
          <p className="text-xs text-emerald-200/90 leading-relaxed font-sans mb-3">
            {incident.resolution_notes}
          </p>
          {incident.verification_details && (
            <div className="p-2.5 rounded bg-slate-950/80 border border-emerald-500/20 text-[11px] font-mono text-emerald-300">
              {incident.verification_details}
            </div>
          )}
        </div>
      )}

      {/* Execution Trajectory */}
      <AgentExecutionStream steps={steps} currentStatus={incident.status} />
    </div>
  );
}
