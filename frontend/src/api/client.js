const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '') + '/api';

export const auth = {
  getUser() {
    try {
      const u = localStorage.getItem('aegis_user');
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  },
  setUser(user) {
    if (user) {
      localStorage.setItem('aegis_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('aegis_user');
    }
  },
  getToken() {
    const u = this.getUser();
    return u?.access_token || null;
  },
  logout() {
    localStorage.removeItem('aegis_user');
  }
};

const getHeaders = (extra = {}) => {
  const token = auth.getToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...extra
  };
};

export const api = {
  // Auth
  async login(email, password) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Login failed. Invalid email or password.');
    }
    const data = await res.json();
    auth.setUser({ ...data, email });
    return data;
  },

  // Incidents
  async getIncidents(status) {
    const url = status ? `${API_BASE}/incidents?status=${status}` : `${API_BASE}/incidents`;
    const res = await fetch(url, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch incidents');
    return res.json();
  },

  async getIncident(id) {
    const res = await fetch(`${API_BASE}/incidents/${id}`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch incident');
    return res.json();
  },

  async createIncident(data) {
    const res = await fetch(`${API_BASE}/incidents`, {
      method: 'POST',
      headers: getHeaders(),
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

  // Analytics & Benchmark
  async getAnalytics() {
    const res = await fetch(`${API_BASE}/analytics/summary`);
    if (!res.ok) throw new Error('Failed to fetch analytics');
    return res.json();
  },

  async runAccuracyBenchmark() {
    const res = await fetch(`${API_BASE}/analytics/benchmark/run`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to run benchmark');
    return res.json();
  },
};

