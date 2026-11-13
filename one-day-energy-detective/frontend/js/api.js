/**
 * One-Day Energy Detective - API Client
 * Manages HTTP communication with the backend REST API, auth headers, and errors.
 */

const API = {
  TOKEN_KEY: "energy_detective_token",

  getToken() {
    return localStorage.getItem(this.TOKEN_KEY);
  },

  setToken(token) {
    if (token) {
      localStorage.setItem(this.TOKEN_KEY, token);
    } else {
      localStorage.removeItem(this.TOKEN_KEY);
    }
  },

  clearToken() {
    localStorage.removeItem(this.TOKEN_KEY);
  },

  async request(endpoint, options = {}) {
    const url = endpoint.startsWith("http") ? endpoint : endpoint;
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {})
    };

    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const config = {
      ...options,
      headers
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        // If unauthorized, clear session and broadcast auth expiration
        if (response.status === 401) {
          this.clearToken();
          window.dispatchEvent(new CustomEvent("auth:expired"));
        }
        const error = new Error(data.error || `HTTP error ${response.status}`);
        error.status = response.status;
        error.details = data.details || null;
        throw error;
      }

      return data;
    } catch (err) {
      console.error(`API Error [${options.method || "GET"} ${endpoint}]:`, err);
      throw err;
    }
  },

  // Auth endpoints
  async register(payload) {
    return this.request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },

  async login(email, password) {
    return this.request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
  },

  async getMe() {
    return this.request("/api/auth/me");
  },

  async logout() {
    try {
      await this.request("/api/auth/logout", { method: "POST" });
    } finally {
      this.clearToken();
    }
  },

  // Household endpoints
  async getHousehold() {
    return this.request("/api/household");
  },

  async updateHousehold(payload) {
    return this.request("/api/household", {
      method: "PUT",
      body: JSON.stringify(payload)
    });
  },

  // Appliance endpoints
  async getPresets() {
    return this.request("/api/appliances/presets");
  },

  async getAppliances() {
    return this.request("/api/appliances");
  },

  async createAppliance(payload) {
    return this.request("/api/appliances", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },

  async updateAppliance(id, payload) {
    return this.request(`/api/appliances/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload)
    });
  },

  async deleteAppliance(id) {
    return this.request(`/api/appliances/${id}`, {
      method: "DELETE"
    });
  },

  // Audit and Detective endpoints
  async getAuditSummary() {
    return this.request("/api/audit/summary");
  },

  async getDetectiveCase() {
    return this.request("/api/audit/detective-case");
  },

  async simulateScenario(modifications) {
    return this.request("/api/audit/simulate", {
      method: "POST",
      body: JSON.stringify({ modifications })
    });
  }
};
