const getApiBase = () => {
  let raw = (import.meta.env.VITE_API_URL || '').trim().replace(/\/$/, '');
  if (!raw) return '/api';
  if (!raw.startsWith('http://') && !raw.startsWith('https://')) {
    raw = `https://${raw}`;
  }
  return `${raw}/api`;
};

const API_BASE = getApiBase();

const safeJson = async (res) => {
  const text = await res.text();
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch {
    throw new Error(`Server returned unexpected response (${res.status}). If the backend is waking up, please retry in 15 seconds.`);
  }
};

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
      const err = await safeJson(res);
      throw new Error(err?.detail || `Login failed (Status: ${res.status})`);
    }
    const data = await safeJson(res);
    auth.setUser({ ...data, email });
    return data;
  },

  // Incidents
  async getIncidents(status) {
    const url = status ? `${API_BASE}/incidents?status=${status}` : `${API_BASE}/incidents`;
    const res = await fetch(url, { headers: getHeaders() });
    if (!res.ok) {
      const err = await safeJson(res);
      throw new Error(err?.detail || `Failed to fetch incidents (Status: ${res.status})`);
    }
    return safeJson(res);
  },

  async getIncident(id) {
    const res = await fetch(`${API_BASE}/incidents/${id}`, { headers: getHeaders() });
    if (!res.ok) {
      const err = await safeJson(res);
      throw new Error(err?.detail || `Failed to fetch incident (Status: ${res.status})`);
    }
    return safeJson(res);
  },

  async createIncident(data) {
    const res = await fetch(`${API_BASE}/incidents`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await safeJson(res);
      throw new Error(err?.detail || `Failed to create incident (Status: ${res.status})`);
    }
    return safeJson(res);
  },

  async triggerAgent(id) {
    const res = await fetch(`${API_BASE}/incidents/${id}/trigger-agent`, {
      method: 'POST',
      headers: getHeaders(),
    });
    if (!res.ok) {
      const err = await safeJson(res);
      throw new Error(err?.detail || `Failed to trigger agent (Status: ${res.status})`);
    }
    return safeJson(res);
  },

  async approveAction(id, approved, feedback = '') {
    const res = await fetch(`${API_BASE}/incidents/${id}/approve`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ approved, feedback }),
    });
    if (!res.ok) {
      const err = await safeJson(res);
      throw new Error(err?.detail || `Failed to process approval (Status: ${res.status})`);
    }
    return safeJson(res);
  },

  async getIncidentSteps(id) {
    const res = await fetch(`${API_BASE}/incidents/${id}/steps`, { headers: getHeaders() });
    if (!res.ok) return [];
    return safeJson(res);
  },

  // Knowledge Base & RAG
  async getKnowledgeDocs() {
    const res = await fetch(`${API_BASE}/knowledge`, { headers: getHeaders() });
    if (!res.ok) return [];
    return safeJson(res);
  },

  async uploadKnowledgeDoc(formData) {
    const token = auth.getToken();
    const res = await fetch(`${API_BASE}/knowledge/upload`, {
      method: 'POST',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      body: formData,
    });
    if (!res.ok) {
      const err = await safeJson(res);
      throw new Error(err?.detail || `Failed to upload document (Status: ${res.status})`);
    }
    return safeJson(res);
  },

  async searchKnowledge(query) {
    const res = await fetch(`${API_BASE}/knowledge/search`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ query, limit: 3 }),
    });
    if (!res.ok) {
      const err = await safeJson(res);
      throw new Error(err?.detail || `Failed to search knowledge (Status: ${res.status})`);
    }
    return safeJson(res);
  },

  // Infrastructure Simulator
  async getServices() {
    const res = await fetch(`${API_BASE}/infra/services`, { headers: getHeaders() });
    if (!res.ok) return [];
    return safeJson(res);
  },

  async getInfraLogs(service = null, level = null) {
    let url = `${API_BASE}/infra/logs?limit=40`;
    if (service) url += `&service=${service}`;
    if (level) url += `&level=${level}`;
    const res = await fetch(url, { headers: getHeaders() });
    if (!res.ok) return [];
    return safeJson(res);
  },

  async simulateFailure(scenario) {
    const res = await fetch(`${API_BASE}/infra/simulate-failure`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ scenario }),
    });
    if (!res.ok) {
      const err = await safeJson(res);
      throw new Error(err?.detail || `Failed to simulate failure (Status: ${res.status})`);
    }
    return safeJson(res);
  },

  async resetInfra() {
    const res = await fetch(`${API_BASE}/infra/reset`, {
      method: 'POST',
      headers: getHeaders(),
    });
    if (!res.ok) {
      const err = await safeJson(res);
      throw new Error(err?.detail || `Failed to reset infrastructure (Status: ${res.status})`);
    }
    return safeJson(res);
  },

  // Analytics & Benchmark
  async getAnalytics() {
    const res = await fetch(`${API_BASE}/analytics/summary`, { headers: getHeaders() });
    if (!res.ok) return {};
    return safeJson(res);
  },

  async runAccuracyBenchmark() {
    const res = await fetch(`${API_BASE}/analytics/benchmark/run`, {
      method: 'POST',
      headers: getHeaders(),
    });
    if (!res.ok) {
      const err = await safeJson(res);
      throw new Error(err?.detail || `Failed to run benchmark (Status: ${res.status})`);
    }
    return safeJson(res);
  },
};

