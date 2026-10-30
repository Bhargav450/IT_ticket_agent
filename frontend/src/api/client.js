const API_BASE = '/api';

export const api = {
  // Incidents
  async getIncidents(status) {
    const url = status ? `${API_BASE}/incidents?status=${status}` : `${API_BASE}/incidents`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch incidents');
    return res.json();
  },

  async getIncident(id) {
    const res = await fetch(`${API_BASE}/incidents/${id}`);
    if (!res.ok) throw new Error('Failed to fetch incident');
    return res.json();
  },

  async createIncident(data) {
    const res = await fetch(`${API_BASE}/incidents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create incident');
    return res.json();
  },

  async triggerAgent(id) {
    const res = await fetch(`${API_BASE}/incidents/${id}/trigger-agent`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to trigger agent');
    return res.json();
  },

  async approveAction(id, approved, feedback = '') {
    const res = await fetch(`${API_BASE}/incidents/${id}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved, feedback }),
    });
    if (!res.ok) throw new Error('Failed to process approval');
    return res.json();
  },

  async getIncidentSteps(id) {
    const res = await fetch(`${API_BASE}/incidents/${id}/steps`);
    if (!res.ok) throw new Error('Failed to fetch steps');
    return res.json();
  },

  // Knowledge Base & RAG
  async getKnowledgeDocs() {
    const res = await fetch(`${API_BASE}/knowledge`);
    if (!res.ok) throw new Error('Failed to fetch documents');
    return res.json();
  },

  async uploadKnowledgeDoc(formData) {
    const res = await fetch(`${API_BASE}/knowledge/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to upload document');
    return res.json();
  },

  async searchKnowledge(query) {
    const res = await fetch(`${API_BASE}/knowledge/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, limit: 3 }),
    });
    if (!res.ok) throw new Error('Failed to search knowledge');
    return res.json();
  },

  // Infrastructure Simulator
  async getServices() {
    const res = await fetch(`${API_BASE}/infra/services`);
    if (!res.ok) throw new Error('Failed to fetch services');
    return res.json();
  },

  async getInfraLogs(service = null, level = null) {
    let url = `${API_BASE}/infra/logs?limit=40`;
    if (service) url += `&service=${service}`;
    if (level) url += `&level=${level}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch logs');
    return res.json();
  },

  async simulateFailure(scenario) {
    const res = await fetch(`${API_BASE}/infra/simulate-failure`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario }),
    });
    if (!res.ok) throw new Error('Failed to simulate failure');
    return res.json();
  },

  async resetInfra() {
    const res = await fetch(`${API_BASE}/infra/reset`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to reset infrastructure');
    return res.json();
  },

  // Analytics
  async getAnalytics() {
    const res = await fetch(`${API_BASE}/analytics/summary`);
    if (!res.ok) throw new Error('Failed to fetch analytics');
    return res.json();
  },
};
