import React, { useState, useEffect } from 'react';
import { 
  Server, 
  Database, 
  ShieldCheck, 
  CreditCard, 
  Cpu, 
  Flame, 
  RotateCcw, 
  Terminal, 
  AlertTriangle, 
  CheckCircle2, 
  Activity,
  Layers
} from 'lucide-react';
import { api } from '../api/client';

export default function InfraSimulator() {
  const [services, setServices] = useState([]);
  const [logs, setLogs] = useState([]);
  const [selectedService, setSelectedService] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState('');

  const loadData = async () => {
    try {
      const svcs = await api.getServices();
      setServices(svcs);
      const lgs = await api.getInfraLogs(selectedService);
      setLogs(lgs);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 4000);
    return () => clearInterval(interval);
  }, [selectedService]);

  const handleSimulate = async (scenario, label) => {
    setIsLoading(true);
    try {
      await api.simulateFailure(scenario);
      setActionMessage(`Injected Chaos: ${label}`);
      await loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = async () => {
    setIsLoading(true);
    try {
      await api.resetInfra();
      setActionMessage('All services restored to baseline HEALTHY.');
      await loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const getServiceIcon = (name) => {
    if (name.includes('db')) return <Database className="w-5 h-5 text-indigo-400" />;
    if (name.includes('auth')) return <ShieldCheck className="w-5 h-5 text-emerald-400" />;
    if (name.includes('payment')) return <CreditCard className="w-5 h-5 text-amber-400" />;
    if (name.includes('cache')) return <Cpu className="w-5 h-5 text-pink-400" />;
    return <Server className="w-5 h-5 text-blue-400" />;
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'HEALTHY':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">HEALTHY</span>;
      case 'CRITICAL':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 animate-pulse">CRITICAL</span>;
      case 'DEGRADED':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">DEGRADED</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400">UNKNOWN</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Chaos Controls */}
      <div className="bg-slate-900/80 rounded-xl border border-slate-800 p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Server className="w-5 h-5 text-blue-400" />
              <h2 className="text-base font-bold text-white">Live Infrastructure & Chaos Simulator</h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Simulated enterprise microservice cluster. Trigger realistic operational failures to test autonomous agent detection & resolution.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleReset}
              disabled={isLoading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white border border-slate-700 transition-all"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Cluster</span>
            </button>
          </div>
        </div>

        {/* Chaos Injection Buttons */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-4 pt-4 border-t border-slate-800">
          <button
            onClick={() => handleSimulate('http_500_gateway', 'HTTP 500 API Gateway Deadlock')}
            disabled={isLoading}
            className="flex items-center justify-between p-3 rounded-lg border border-rose-500/30 bg-rose-950/20 hover:bg-rose-950/40 text-left transition-all group"
          >
            <div>
              <div className="text-xs font-bold text-rose-300 flex items-center gap-1.5">
                <Flame className="w-4 h-4 text-rose-400 group-hover:scale-110 transition-transform" />
                <span>Simulate HTTP 500 Outage</span>
              </div>
              <span className="text-[11px] text-rose-300/70 block mt-0.5">Saturates api-gateway worker pool</span>
            </div>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300">P1</span>
          </button>

          <button
            onClick={() => handleSimulate('db_pool_exhaustion', 'Database Connection Pool Exhaustion')}
            disabled={isLoading}
            className="flex items-center justify-between p-3 rounded-lg border border-amber-500/30 bg-amber-950/20 hover:bg-amber-950/40 text-left transition-all group"
          >
            <div>
              <div className="text-xs font-bold text-amber-300 flex items-center gap-1.5">
                <Database className="w-4 h-4 text-amber-400 group-hover:scale-110 transition-transform" />
                <span>Simulate DB Pool Exhaustion</span>
              </div>
              <span className="text-[11px] text-amber-300/70 block mt-0.5">Exhausts 100/100 connection slots</span>
            </div>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300">P2</span>
          </button>

          <button
            onClick={() => handleSimulate('auth_token_failure', 'Auth Token Verification Failure')}
            disabled={isLoading}
            className="flex items-center justify-between p-3 rounded-lg border border-purple-500/30 bg-purple-950/20 hover:bg-purple-950/40 text-left transition-all group"
          >
            <div>
              <div className="text-xs font-bold text-purple-300 flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-purple-400 group-hover:scale-110 transition-transform" />
                <span>Simulate Auth Token Failure</span>
              </div>
              <span className="text-[11px] text-purple-300/70 block mt-0.5">Simulates JWKS key rotation cache desync</span>
            </div>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300">P2</span>
          </button>
        </div>

        {actionMessage && (
          <div className="mt-3 p-2 rounded bg-blue-500/10 border border-blue-500/20 text-xs text-blue-300 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-blue-400" />
            <span>{actionMessage}</span>
          </div>
        )}
      </div>

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {services.map(svc => {
          const isCritical = svc.status === 'CRITICAL';
          const isDegraded = svc.status === 'DEGRADED';

          return (
            <div
              key={svc.service_name}
              onClick={() => setSelectedService(svc.service_name)}
              className={`p-4 rounded-xl border transition-all cursor-pointer ${
                isCritical
                  ? 'bg-rose-950/30 border-rose-500/50 shadow-lg shadow-rose-950/20'
                  : isDegraded
                  ? 'bg-amber-950/20 border-amber-500/40'
                  : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-3">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                    {getServiceIcon(svc.service_name)}
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white font-mono">{svc.service_name}</h3>
                    <span className="text-[10px] text-slate-500 font-mono">cluster: production-us-east</span>
                  </div>
                </div>
                {getStatusBadge(svc.status)}
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono pt-3 border-t border-slate-800/80">
                <div className="bg-slate-950/60 p-2 rounded border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Latency</span>
                  <span className={`font-semibold ${svc.latency_ms > 1000 ? 'text-rose-400' : 'text-slate-200'}`}>
                    {svc.latency_ms.toFixed(1)} ms
                  </span>
                </div>
                <div className="bg-slate-950/60 p-2 rounded border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Error Rate</span>
                  <span className={`font-semibold ${svc.error_rate_percent > 5 ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {svc.error_rate_percent.toFixed(2)}%
                  </span>
                </div>
                <div className="bg-slate-950/60 p-2 rounded border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">CPU Load</span>
                  <span className="text-slate-200 font-semibold">{svc.cpu_percent.toFixed(1)}%</span>
                </div>
                <div className="bg-slate-950/60 p-2 rounded border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Connections</span>
                  <span className="text-slate-200 font-semibold">{svc.active_connections}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Live Application Log Stream */}
      <div className="bg-slate-950 rounded-xl border border-slate-800 p-4">
        <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2.5">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-emerald-400" />
            <h3 className="text-xs font-bold font-mono text-slate-200 uppercase tracking-wider">
              Live Application Log Stream {selectedService ? `(${selectedService})` : '(All Services)'}
            </h3>
          </div>
          {selectedService && (
            <button
              onClick={() => setSelectedService(null)}
              className="text-[10px] text-blue-400 hover:underline"
            >
              Clear filter
            </button>
          )}
        </div>

        <div className="h-64 overflow-y-auto space-y-1.5 font-mono text-[11px] pr-2">
          {logs.length === 0 ? (
            <div className="text-slate-600 text-center py-8">No recent log entries.</div>
          ) : (
            logs.map((log, idx) => {
              const isErr = log.level === 'ERROR' || log.level === 'CRITICAL';
              return (
                <div
                  key={idx}
                  className={`p-2 rounded border transition-colors ${
                    isErr 
                      ? 'bg-rose-950/30 border-rose-900/50 text-rose-300' 
                      : 'bg-slate-900/40 border-slate-800 text-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 text-[10px] text-slate-500 mb-0.5">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-400">[{log.service}]</span>
                      <span className={`font-bold ${isErr ? 'text-rose-400' : 'text-blue-400'}`}>
                        {log.level}
                      </span>
                    </div>
                    <span>{new Date(log.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <p className="leading-relaxed">{log.message}</p>
                  {log.stack_trace && (
                    <pre className="mt-1 text-[10px] text-rose-400/80 bg-slate-950/90 p-2 rounded border border-rose-900/40 whitespace-pre-wrap">
                      {log.stack_trace}
                    </pre>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
