import React, { useState } from 'react';
import { 
  ShieldAlert, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Terminal, 
  Info,
  Send
} from 'lucide-react';

export default function HumanApprovalModal({ incident, onApprove, isProcessing }) {
  const [feedback, setFeedback] = useState('Approved by Lead Site Reliability Engineer.');

  if (!incident || incident.status !== 'AWAITING_APPROVAL') {
    return null;
  }

  return (
    <div className="bg-gradient-to-b from-purple-950/40 to-slate-900/90 rounded-xl border-2 border-purple-500/60 p-5 shadow-2xl shadow-purple-950/40 relative overflow-hidden">
      {/* Top Banner */}
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2.5 rounded-xl bg-purple-500/20 border border-purple-500/30 text-purple-300">
          <ShieldAlert className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-white">Human-in-the-Loop Authorization Required</h3>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500 text-slate-950">
              HIGH RISK
            </span>
          </div>
          <p className="text-xs text-purple-300/80">
            The autonomous agent has formulated a remediation plan that exceeds autonomous risk thresholds.
          </p>
        </div>
      </div>

      {/* Action Details Card */}
      <div className="bg-slate-950/80 rounded-lg border border-purple-500/30 p-4 mb-4 space-y-3 font-mono text-xs">
        <div>
          <span className="text-slate-400 block text-[10px] uppercase tracking-wider mb-1">Proposed Execution Action</span>
          <div className="flex items-center gap-2 p-2 rounded bg-purple-900/20 border border-purple-500/40 text-purple-200">
            <Terminal className="w-4 h-4 text-purple-400 shrink-0" />
            <span className="font-bold">{incident.proposed_action || "restart_service()"}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-slate-800 text-[11px]">
          <div>
            <span className="text-slate-400 block text-[10px] uppercase">Target Component</span>
            <span className="text-slate-200 font-semibold">{incident.affected_service || "api-gateway"}</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px] uppercase">Blast Radius Rating</span>
            <span className="text-amber-400 font-semibold">5-10s Service Recreation</span>
          </div>
        </div>

        <div className="pt-2 border-t border-slate-800 text-[11px] font-sans">
          <span className="text-slate-400 block text-[10px] font-mono uppercase mb-0.5">Safety & RCA Justification</span>
          <p className="text-slate-300 leading-relaxed">
            {incident.root_cause_analysis || "Deadlock detected in service worker pool. Restart clears corrupted memory and active socket state."}
          </p>
        </div>
      </div>

      {/* Operator Feedback / Instructions */}
      <div className="mb-4">
        <label className="block text-xs font-medium text-slate-300 mb-1.5">
          Operator Approval Note / Instructions (Optional):
        </label>
        <input
          type="text"
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          placeholder="e.g. Approved by Sarah Chen. Monitor latency post-restart."
          className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500"
        />
      </div>

      {/* Decision Buttons */}
      <div className="flex items-center justify-end gap-3 pt-2">
        <button
          onClick={() => onApprove(incident.id, false, feedback)}
          disabled={isProcessing}
          className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold border border-rose-500/40 text-rose-300 hover:bg-rose-500/10 transition-all disabled:opacity-50"
        >
          <XCircle className="w-4 h-4 text-rose-400" />
          <span>Reject Action</span>
        </button>

        <button
          onClick={() => onApprove(incident.id, true, feedback)}
          disabled={isProcessing}
          className="flex items-center gap-1.5 px-5 py-2 rounded-lg text-xs font-bold bg-gradient-to-r from-emerald-600 to-teal-500 text-white hover:from-emerald-500 hover:to-teal-400 shadow-lg shadow-emerald-600/30 transition-all disabled:opacity-50"
        >
          <CheckCircle className="w-4 h-4" />
          <span>{isProcessing ? 'Executing Action...' : 'Authorize & Execute Remediation'}</span>
        </button>
      </div>
    </div>
  );
}

