export const getApiBase = () => {
  // 1. Check for user-defined runtime override in localStorage
  const override = typeof window !== 'undefined' ? localStorage.getItem('AEGISOPS_API_URL') : null;
  let raw = (override || import.meta.env.VITE_API_URL || '').trim().replace(/\/$/, '');

  // 2. Reject internal container / private network hostnames (e.g. 'aegisops-backend' or 'aegisops-backend:10000')
  // Browsers cannot resolve these over the public internet.
  if (raw && !raw.includes('.') && !raw.includes('localhost') && !raw.includes('127.0.0.1')) {
    raw = '';
  }

  // 3. Fallback for Render deployments:
  // If frontend is running at https://aegisops-frontend.onrender.com, target https://aegisops-backend.onrender.com
  if (!raw && typeof window !== 'undefined' && window.location.hostname.endsWith('.onrender.com')) {
    const parts = window.location.hostname.split('.');
    const backendSubdomain = parts[0].replace('frontend', 'backend');
    raw = `https://${backendSubdomain}.onrender.com`;
  }

  if (!raw) return '/api';
  if (!raw.startsWith('http://') && !raw.startsWith('https://')) {
    raw = `https://${raw}`;
  }
  return `${raw}/api`;
};

export const API_BASE = getApiBase();

if (typeof window !== 'undefined') {
  console.log('[AegisOps] Connected to API Base:', API_BASE);
}

const safeFetch = async (url, options = {}) => {
  try {
    return await fetch(url, options);
  } catch (err) {
    if (err.name === 'TypeError' || (err.message && err.message.toLowerCase().includes('fetch'))) {
      throw new Error(
        `Unable to connect to backend at ${url}. ` +
        `If using Render free tier, the backend server spins down when idle and takes ~40 seconds to wake up. ` +
        `Please check if the backend service is running or wait a moment and try again.`
      );
    }
    throw err;
  }
};

const safeJson = async (res) => {
  const text = await res.text();
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch {
    throw new Error(`Server returned unexpected response (Status: ${res.status}). If the backend is waking up, please retry in 15 seconds.`);
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
    const res = await safeFetch(`${API_BASE}/auth/login`, {
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
    const res = await safeFetch(url, { headers: getHeaders() });
    if (!res.ok) {
      const err = await safeJson(res);
      throw new Error(err?.detail || `Failed to fetch incidents (Status: ${res.status})`);
    }
    return safeJson(res);
  },

  async getIncident(id) {
    const res = await safeFetch(`${API_BASE}/incidents/${id}`, { headers: getHeaders() });
    if (!res.ok) {
      const err = await safeJson(res);
      throw new Error(err?.detail || `Failed to fetch incident (Status: ${res.status})`);
    }
    return safeJson(res);
  },

  async createIncident(data) {
    const res = await safeFetch(`${API_BASE}/incidents`, {
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
    const res = await safeFetch(`${API_BASE}/incidents/${id}/trigger-agent`, {
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
    const res = await safeFetch(`${API_BASE}/incidents/${id}/approve`, {
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
    const res = await safeFetch(`${API_BASE}/incidents/${id}/steps`, { headers: getHeaders() });
    if (!res.ok) return [];
    return safeJson(res);
  },

  // Knowledge Base & RAG
  async getKnowledgeDocs() {
    const res = await safeFetch(`${API_BASE}/knowledge`, { headers: getHeaders() });
    if (!res.ok) return [];
    return safeJson(res);
  },

  async uploadKnowledgeDoc(formData) {
    const token = auth.getToken();
    const res = await safeFetch(`${API_BASE}/knowledge/upload`, {
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
    const res = await safeFetch(`${API_BASE}/knowledge/search`, {
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
    const res = await safeFetch(`${API_BASE}/infra/services`, { headers: getHeaders() });
    if (!res.ok) return [];
    return safeJson(res);
  },

  async getInfraLogs(service = null, level = null) {
    let url = `${API_BASE}/infra/logs?limit=40`;
    if (service) url += `&service=${service}`;
    if (level) url += `&level=${level}`;
    const res = await safeFetch(url, { headers: getHeaders() });
    if (!res.ok) return [];
    return safeJson(res);
  },

  async simulateFailure(scenario) {
    const res = await safeFetch(`${API_BASE}/infra/simulate-failure`, {
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
    const res = await safeFetch(`${API_BASE}/infra/reset`, {
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
    const res = await safeFetch(`${API_BASE}/analytics/summary`, { headers: getHeaders() });
    if (!res.ok) return {};
    return safeJson(res);
  },

  async runAccuracyBenchmark() {
    const res = await safeFetch(`${API_BASE}/analytics/benchmark/run`, {
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
