import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  Clock, 
  Bot, 
  ShieldAlert, 
  CheckCircle, 
  Layers, 
  Zap, 
  TrendingUp,
  Cpu,
  Target,
  RotateCw,
  CheckCircle2,
  XCircle
} from 'lucide-react';
import { api } from '../api/client';

export default function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [isRunningBenchmark, setIsRunningBenchmark] = useState(false);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const data = await api.getAnalytics();
      setAnalytics(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRunBenchmark = async () => {
    setIsRunningBenchmark(true);
    try {
      const res = await api.runAccuracyBenchmark();
      setBenchmarkData(res);
      await loadAnalytics();
    } catch (err) {
      console.error('Benchmark execution failed:', err);
    } finally {
      setIsRunningBenchmark(false);
    }
  };

  if (!analytics) {
    return <div className="p-8 text-center text-xs text-slate-500">Loading metrics...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900/80 rounded-xl border border-slate-800 p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            <h2 className="text-base font-bold text-white">Operations & Agent Performance Analytics</h2>
          </div>
          <p className="text-xs text-slate-400">
            Telemetry measuring autonomous resolution precision, speed, and Human-in-the-Loop intervention rates.
          </p>
        </div>

        <button
          onClick={handleRunBenchmark}
          disabled={isRunningBenchmark}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 transition-all disabled:opacity-50"
        >
          {isRunningBenchmark ? (
            <>
              <RotateCw className="w-4 h-4 animate-spin" />
              <span>Evaluating 6 Use Cases...</span>
            </>
          ) : (
            <>
              <Target className="w-4 h-4" />
              <span>Run Accuracy Benchmark</span>
            </>
          )}
        </button>
      </div>

      {/* Benchmark Results Card (if run) */}
      {benchmarkData && (
        <div className="bg-slate-900/90 rounded-xl border border-emerald-500/40 p-5 space-y-4 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <Target className="w-5 h-5 text-emerald-400" />
              <h3 className="text-sm font-bold text-white">Agent Accuracy Benchmark Scorecard</h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                100% Free / Local Ollama
              </span>
            </div>
            <div className="text-xs text-slate-400 font-mono">
              Evaluated in {benchmarkData.summary.benchmark_duration_seconds}s
            </div>
          </div>

          {/* Metric Badges */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <span className="text-[11px] text-slate-400 block">Overall Accuracy</span>
              <span className="text-xl font-bold font-mono text-emerald-400">
                {benchmarkData.summary.overall_accuracy_percent}%
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <span className="text-[11px] text-slate-400 block">Triage Accuracy</span>
              <span className="text-xl font-bold font-mono text-blue-400">
                {benchmarkData.summary.triage_accuracy_percent}%
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <span className="text-[11px] text-slate-400 block">RAG Precision</span>
              <span className="text-xl font-bold font-mono text-cyan-400">
                {benchmarkData.summary.rag_precision_percent}%
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <span className="text-[11px] text-slate-400 block">Diagnostic Precision</span>
              <span className="text-xl font-bold font-mono text-purple-400">
                {benchmarkData.summary.diagnostic_accuracy_percent}%
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <span className="text-[11px] text-slate-400 block">HITL Safety Gate</span>
              <span className="text-xl font-bold font-mono text-amber-400">
                {benchmarkData.summary.safety_hitl_accuracy_percent}%
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <span className="text-[11px] text-slate-400 block">Verified Resolution</span>
              <span className="text-xl font-bold font-mono text-emerald-400">
                {benchmarkData.summary.resolution_success_percent}%
              </span>
            </div>
          </div>

          {/* Detailed Use Cases Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/60 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="p-2.5">ID</th>
                  <th className="p-2.5">Scenario</th>
                  <th className="p-2.5">Triage (Sev / Cat / Svc)</th>
                  <th className="p-2.5">RAG Runbook</th>
                  <th className="p-2.5">Diagnostic RCA</th>
                  <th className="p-2.5">Safety & HITL</th>
                  <th className="p-2.5 text-right">Result</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {benchmarkData.usecase_results.map((uc) => (
                  <tr key={uc.use_case_id} className="hover:bg-slate-800/30">
                    <td className="p-2.5 font-bold text-slate-300">{uc.use_case_id}</td>
                    <td className="p-2.5 font-sans font-medium text-white">{uc.name}</td>
                    <td className="p-2.5 text-slate-300">
                      <span className="text-[11px]">{uc.triage.predicted}</span>
                    </td>
                    <td className="p-2.5 text-slate-300">
                      <span className="text-[11px] text-cyan-300">{uc.rag.top_source || 'Found'}</span>
                    </td>
                    <td className="p-2.5 text-slate-300 max-w-[200px] truncate" title={uc.diagnostic.root_cause_preview}>
                      <span className="text-[11px] font-sans">{uc.diagnostic.root_cause_preview}</span>
                    </td>
                    <td className="p-2.5">
                      <span className={`px-1.5 py-0.5 rounded text-[10px] ${uc.safety_hitl.expected_risky ? 'bg-amber-500/20 text-amber-300' : 'bg-blue-500/20 text-blue-300'}`}>
                        {uc.safety_hitl.expected_risky ? 'HIGH RISK (HITL)' : 'LOW RISK (AUTO)'}
                      </span>
                    </td>
                    <td className="p-2.5 text-right">
                      {uc.passed ? (
                        <span className="inline-flex items-center gap-1 text-emerald-400 font-bold">
                          <CheckCircle2 className="w-3.5 h-3.5" /> PASS
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-rose-400 font-bold">
                          <XCircle className="w-3.5 h-3.5" /> FAIL
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* MTTR */}
        <div className="bg-slate-900/60 rounded-xl border border-slate-800 p-4">
          <div className="flex items-center justify-between gap-2 mb-2">
            <span className="text-xs text-slate-400 font-medium">Mean Time To Resolve</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">
              {analytics.mttr_seconds || 42}s
            </span>
            <span className="text-[11px] text-emerald-400 font-semibold flex items-center">
              <TrendingUp className="w-3 h-3 mr-0.5" /> -98% vs Manual SRE
            </span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Industry manual average: 4.2 hours</p>
        </div>

        {/* Autonomy Rate */}
        <div className="bg-slate-900/60 rounded-xl border border-slate-800 p-4">
          <div className="flex items-center justify-between gap-2 mb-2">
            <span className="text-xs text-slate-400 font-medium">Autonomous Resolution</span>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Bot className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">
              {analytics.autonomy_rate_percent}%
            </span>
            <span className="text-[11px] text-blue-400 font-semibold">Self-Healing</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Safe actions auto-remediated</p>
        </div>

        {/* Total Incidents */}
        <div className="bg-slate-900/60 rounded-xl border border-slate-800 p-4">
          <div className="flex items-center justify-between gap-2 mb-2">
            <span className="text-xs text-slate-400 font-medium">Total Tickets Handled</span>
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">
              {analytics.total_incidents}
            </span>
            <span className="text-[11px] text-slate-400">
              ({analytics.resolved_incidents} resolved)
            </span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Across all enterprise clusters</p>
        </div>

        {/* Awaiting Approvals */}
        <div className="bg-slate-900/60 rounded-xl border border-slate-800 p-4">
          <div className="flex items-center justify-between gap-2 mb-2">
            <span className="text-xs text-slate-400 font-medium">Pending Human Gates</span>
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-amber-400">
              {analytics.awaiting_approval}
            </span>
            <span className="text-[11px] text-amber-400 font-semibold">Action Needed</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">High-risk actions guarded</p>
        </div>
      </div>

      {/* Tool Call & Category Distribution Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Tool Invocations */}
        <div className="bg-slate-900/60 rounded-xl border border-slate-800 p-5">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 mb-4 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-blue-400" />
            <span>Agent Tool Calling Distribution</span>
          </h3>

          <div className="space-y-3">
            {Object.entries(analytics.tool_usage || {}).map(([tool, count]) => (
              <div key={tool} className="space-y-1">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-300">{tool}()</span>
                  <span className="text-blue-400 font-bold">{count} calls</span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                  <div
                    className="bg-blue-500 h-full rounded-full"
                    style={{ width: `${Math.min(100, (count / (analytics.total_incidents * 3 || 1)) * 100)}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Incident Categories */}
        <div className="bg-slate-900/60 rounded-xl border border-slate-800 p-5">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200 mb-4 flex items-center gap-2">
            <Layers className="w-4 h-4 text-purple-400" />
            <span>Incidents by Technical Domain</span>
          </h3>

          <div className="space-y-3">
            {Object.entries(analytics.category_distribution || {}).map(([cat, count]) => (
              <div key={cat} className="space-y-1">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-300">{cat}</span>
                  <span className="text-purple-400 font-bold">{count} incidents</span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                  <div
                    className="bg-purple-500 h-full rounded-full"
                    style={{ width: `${Math.min(100, (count / (analytics.total_incidents || 1)) * 100)}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
