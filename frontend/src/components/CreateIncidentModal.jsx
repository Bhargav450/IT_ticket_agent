import React, { useState } from 'react';
import { X, PlusCircle, Sparkles, Bot, AlertTriangle } from 'lucide-react';

export default function CreateIncidentModal({ isOpen, onClose, onCreate }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [severity, setSeverity] = useState('P2_HIGH');
  const [reporterEmail, setReporterEmail] = useState('employee@enterprise.io');
  const [autoTrigger, setAutoTrigger] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const presets = [
    {
      label: 'HTTP 500 Gateway Outage',
      title: 'Application returning HTTP 500 errors - users unable to access app',
      description: 'My application is returning HTTP 500 errors. I cannot access the application.',
      severity: 'P1_CRITICAL',
    },
    {
      label: 'DB Pool Saturated',
      title: 'Database connection pool exhausted during checkout surge',
      description: 'Order database queries failing with OperationalError: remaining connection slots are reserved for non-replication superuser connections. QueuePool limit of size 50 reached.',
      severity: 'P2_HIGH',
    },
    {
      label: 'Auth 401 Token Spike',
      title: 'Users logged out randomly with 401 Unauthorized',
      description: 'Multiple employees reported getting kicked out of internal dashboards with JWT signature verification errors.',
      severity: 'P2_HIGH',
    },
  ];

  const applyPreset = (p) => {
    setTitle(p.title);
    setDescription(p.description);
    setSeverity(p.severity);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title || !description) return;

    setIsSubmitting(true);
    try {
      await onCreate({
        title,
        description,
        severity,
        reporter_email: reporterEmail,
      }, autoTrigger);
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <PlusCircle className="w-5 h-5 text-blue-400" />
            <h3 className="text-sm font-bold text-white">Report New IT Incident</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Quick Fill Presets */}
        <div className="p-4 bg-slate-950/50 border-b border-slate-800">
          <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-2">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Quick-fill realistic incident scenarios:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {presets.map((p, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => applyPreset(p)}
                className="px-2.5 py-1 rounded bg-slate-800/80 hover:bg-blue-600/20 hover:border-blue-500/30 border border-slate-700 text-[11px] text-slate-300 font-medium transition-all"
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Incident Summary / Title
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. My application is returning HTTP 500 errors"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Problem Description & Symptoms
            </label>
            <textarea
              required
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe error codes, impacted URLs, symptoms..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Severity Level
              </label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
              >
                <option value="P1_CRITICAL">P1 - Critical Outage</option>
                <option value="P2_HIGH">P2 - High Priority</option>
                <option value="P3_MEDIUM">P3 - Medium Priority</option>
                <option value="P4_LOW">P4 - Low / General</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Reporter Email
              </label>
              <input
                type="email"
                value={reporterEmail}
                onChange={(e) => setReporterEmail(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div className="flex items-center gap-2 p-2.5 rounded bg-blue-500/10 border border-blue-500/20 text-xs text-blue-300">
            <input
              type="checkbox"
              id="autoTrigger"
              checked={autoTrigger}
              onChange={(e) => setAutoTrigger(e.target.checked)}
              className="rounded bg-slate-950 border-slate-700 text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="autoTrigger" className="cursor-pointer font-medium">
              Immediately dispatch Autonomous LangGraph Agent upon ticket creation
            </label>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-600/20 transition-all disabled:opacity-50"
            >
              <Bot className="w-4 h-4" />
              <span>{isSubmitting ? 'Dispatching...' : 'Submit & Launch Agent'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
