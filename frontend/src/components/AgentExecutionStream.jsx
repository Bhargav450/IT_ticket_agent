import React, { useState } from 'react';
import { 
  Bot, 
  Search, 
  Terminal, 
  CheckCircle2, 
  Clock, 
  AlertTriangle, 
  Layers, 
  ShieldCheck, 
  ChevronDown, 
  ChevronRight,
  ArrowRight,
  Cpu
} from 'lucide-react';

export default function AgentExecutionStream({ steps, currentStatus }) {
  const [expandedSteps, setExpandedSteps] = useState({});

  const toggleStep = (id) => {
    setExpandedSteps(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const getNodeIcon = (nodeName) => {
    switch (nodeName) {
      case 'supervisor':
        return <Cpu className="w-4 h-4 text-purple-400" />;
      case 'triage':
        return <Layers className="w-4 h-4 text-blue-400" />;
      case 'knowledge_rag':
        return <Search className="w-4 h-4 text-amber-400" />;
      case 'diagnostic':
        return <Terminal className="w-4 h-4 text-cyan-400" />;
      case 'resolution_human_gate':
        return <AlertTriangle className="w-4 h-4 text-amber-400 animate-pulse" />;
      case 'resolution':
        return <Bot className="w-4 h-4 text-indigo-400" />;
      case 'verification':
        return <ShieldCheck className="w-4 h-4 text-emerald-400" />;
      default:
        return <Bot className="w-4 h-4 text-blue-400" />;
    }
  };

  const getNodeColor = (nodeName, status) => {
    if (status === 'AWAITING_APPROVAL') return 'border-amber-500/50 bg-amber-500/10 text-amber-300';
    if (status === 'VERIFICATION_FAILED') return 'border-rose-500/50 bg-rose-500/10 text-rose-300';
    return 'border-slate-800 bg-slate-900/60 text-slate-200';
  };

  return (
    <div className="bg-slate-900/40 rounded-xl border border-slate-800 p-4">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-blue-400" />
          <h3 className="text-sm font-bold text-slate-100">LangGraph Agent Execution Trajectory</h3>
        </div>
        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
          StateGraph v2.0
        </span>
      </div>

      {steps.length === 0 ? (
        <div className="text-center py-8 text-slate-500 text-xs">
          Agent has not executed for this incident yet. Click "Investigate & Resolve" to launch.
        </div>
      ) : (
        <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
          {steps.map((step, idx) => {
            const isExpanded = !!expandedSteps[step.id];
            const hasPayload = step.tool_input || step.tool_output;

            return (
              <div key={step.id || idx} className="relative group">
                {/* Node Milestone Circle */}
                <div className="absolute -left-6 top-1.5 w-5 h-5 rounded-full bg-slate-950 border border-slate-700 flex items-center justify-center shadow">
                  {getNodeIcon(step.node_name)}
                </div>

                {/* Step Card */}
                <div className={`p-3 rounded-lg border transition-all ${getNodeColor(step.node_name, step.status)}`}>
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
                        {step.node_name.replace('_', ' ')}
                      </span>
                      {step.tool_name && (
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                          {step.tool_name}()
                        </span>
                      )}
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {new Date(step.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </span>
                  </div>

                  {/* Thought / Reasoning Summary */}
                  {step.thought_summary && (
                    <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                      {step.thought_summary}
                    </p>
                  )}

                  {/* Expandable Tool Input / Output Payload */}
                  {hasPayload && (
                    <div className="mt-2.5">
                      <button
                        onClick={() => toggleStep(step.id)}
                        className="flex items-center gap-1 text-[11px] text-blue-400 hover:text-blue-300 font-mono"
                      >
                        {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                        <span>{isExpanded ? 'Hide Payload & Tool Logs' : 'View Tool Logs & Evidence'}</span>
                      </button>

                      {isExpanded && (
                        <div className="mt-2 p-2.5 rounded bg-slate-950 border border-slate-800 text-[11px] font-mono text-slate-300 space-y-2 overflow-x-auto">
                          {step.tool_input && (
                            <div>
                              <span className="text-slate-500 uppercase tracking-wider text-[10px]">Tool Input:</span>
                              <pre className="text-sky-300 mt-0.5 whitespace-pre-wrap">{JSON.stringify(step.tool_input, null, 2)}</pre>
                            </div>
                          )}
                          {step.tool_output && (
                            <div className="pt-2 border-t border-slate-800/80">
                              <span className="text-slate-500 uppercase tracking-wider text-[10px]">Tool Output:</span>
                              <pre className="text-emerald-300 mt-0.5 whitespace-pre-wrap">{JSON.stringify(step.tool_output, null, 2)}</pre>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

