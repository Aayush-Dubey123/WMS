/**
 * API Service - Connects frontend to Whitfield WMS backend
 * Base URL: http://127.0.0.1:8000
 *
 * Comprehensive API client covering all 16 router groups:
 * Auth, Users, API Keys, Warehouses, Inbox, Arrivals, Tickets,
 * Approvals, Storage, Orders, Reports, Audit, Query, Vision, Voice, Health
 */

const API_BASE = import.meta.env['VITE_API_BASE_URL'] || "http://127.0.0.1:8000";

// Token management
export const tokenManager = {
  getAccessToken: () => localStorage.getItem("access_token"),
  getRefreshToken: () => localStorage.getItem("refresh_token"),
  setTokens: (accessToken: string, refreshToken: string) => {
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
  },
  clearTokens: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },
};

// Headers with auth
const getHeaders = () => {
  const token = tokenManager.getAccessToken();
  return {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};

// API request handler with comprehensive error handling
async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      ...getHeaders(),
      ...options.headers,
    },
  });

  // Handle 401 - Unauthorized
  if (response.status === 401) {
    tokenManager.clearTokens();
    window.location.href = "/login";
    throw new Error("Unauthorized - please login again");
  }

  // Handle 403 - Forbidden
  if (response.status === 403) {
    throw new Error("Access denied - insufficient permissions");
  }

  // Handle other errors
  if (!response.ok) {
    try {
      const error = await response.json();
      throw new Error(error.detail || error.message || `HTTP ${response.status}`);
    } catch {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
  }

  return response.json();
}

// ============================================================================
// AUTHENTICATION
// ============================================================================

export const authAPI = {
  login: (email: string, password: string) =>
    apiCall("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  refresh: () =>
    apiCall("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: tokenManager.getRefreshToken() }),
    }),

  getProfile: () => apiCall("/auth/me", { method: "GET" }),
};

// ============================================================================
// USERS
// ============================================================================

export const usersAPI = {
  getAll: (skip = 0, limit = 50) =>
    apiCall(`/users?skip=${skip}&limit=${limit}`, { method: "GET" }),

  createManager: (data: {
    email: string;
    full_name: string;
    password: string;
    warehouse_id: string;
  }) =>
    apiCall("/users/managers", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  createStaff: (data: {
    email: string;
    full_name: string;
    password: string;
    experience_tier: string;
    function_roles: string[];
  }) =>
    apiCall("/users/staff", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateStaff: (id: string, data: Record<string, unknown>) =>
    apiCall(`/users/staff/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  remove: (id: string) => apiCall(`/users/${id}`, { method: "DELETE" }),
};

// ============================================================================
// WAREHOUSES
// ============================================================================

export const warehousesAPI = {
  getAll: (skip = 0, limit = 50) =>
    apiCall(`/warehouses?skip=${skip}&limit=${limit}`, { method: "GET" }),

  getById: (id: string) => apiCall(`/warehouses/${id}`, { method: "GET" }),

  create: (data: {
    code: string;
    name: string;
    address?: string;
  }) =>
    apiCall("/warehouses", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: string, data: Record<string, unknown>) =>
    apiCall(`/warehouses/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
};

// ============================================================================
// ORDERS
// ============================================================================

export const ordersAPI = {
  getAll: (skip = 0, limit = 50, status?: string) => {
    const query = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    if (status) query.append("status", status);
    return apiCall(`/orders?${query}`, { method: "GET" });
  },

  getById: (id: string) => apiCall(`/orders/${id}`, { method: "GET" }),

  getItems: (id: string) => apiCall(`/orders/${id}/items`, { method: "GET" }),

  create: (data: {
    order_id: string;
    customer_name: string;
    warehouse_id: string;
    items: Array<{ barcode: string; product_name: string; quantity: number }>;
  }) =>
    apiCall("/orders", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  reserve: (orderId: string) =>
    apiCall(`/orders/${orderId}/reserve`, { method: "POST" }),

  cancel: (orderId: string) =>
    apiCall(`/orders/${orderId}/cancel`, { method: "POST" }),

  pack: (
    orderId: string,
    data: {
      packed_weight: number;
      width: number;
      height: number;
      length: number;
    }
  ) =>
    apiCall(`/orders/${orderId}/pack`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  generateLabel: (orderId: string) =>
    apiCall(`/orders/${orderId}/label`, { method: "POST" }),

  ship: (orderId: string) =>
    apiCall(`/orders/${orderId}/ship`, { method: "POST" }),
};

// ============================================================================
// TICKETS & ARRIVALS
// ============================================================================

export const ticketsAPI = {
  getAll: (skip = 0, limit = 50, status?: string) => {
    const query = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    if (status) query.append("status", status);
    return apiCall(`/tickets?${query}`, { method: "GET" });
  },

  getById: (id: string) => apiCall(`/tickets/${id}`, { method: "GET" }),

  getItems: (ticketId: string) =>
    apiCall(`/tickets/${ticketId}/items`, { method: "GET" }),

  logItem: (
    ticketId: string,
    data: {
      barcode: string;
      product_name: string;
      width: number;
      height: number;
      weight: number;
      image_url?: string;
      damage?: { flag: boolean; note?: string };
    }
  ) =>
    apiCall(`/tickets/${ticketId}/items`, {
      method: "POST",
      headers: { "Idempotency-Key": crypto.randomUUID() },
      body: JSON.stringify(data),
    }),

  assignStorage: (ticketId: string, data: { storage_location: string }) =>
    apiCall(`/tickets/${ticketId}/store`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  submitInspection: (ticketId: string) =>
    apiCall(`/tickets/${ticketId}/submit-inspection`, { method: "PUT" }),

  approve: (ticketId: string) =>
    apiCall(`/tickets/${ticketId}/approve`, { method: "POST" }),
};

export const arrivalsAPI = {
  log: (data: {
    warehouse_id: string;
    tracking_number?: string;
    no_ticket_arrival: boolean;
  }) =>
    apiCall("/arrivals", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

// ============================================================================
// VOICE PIPELINE
// ============================================================================

export const voiceAPI = {
  transcribe: (audioFile: File) => {
    const formData = new FormData();
    formData.append("file", audioFile);
    return fetch(`${API_BASE}/voice/transcribe`, {
      method: "POST",
      headers: { Authorization: `Bearer ${tokenManager.getAccessToken()}` },
      body: formData,
    }).then(async (r) => {
      if (!r.ok) {
        const error = await r.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP ${r.status}`);
      }
      return r.json();
    });
  },

  parse: (ticketId: string, transcript: string) =>
    apiCall("/voice/parse", {
      method: "POST",
      body: JSON.stringify({ ticket_id: ticketId, transcript }),
    }),

  confirm: (draftId: string, data: { barcode: string; override_weight: number }) =>
    apiCall(`/voice/drafts/${draftId}/confirm`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

// ============================================================================
// REPORTS
// ============================================================================

export const reportsAPI = {
  getSummary: (date: string) =>
    apiCall(`/reports/summary?date=${date}`, { method: "GET" }),

  getArrivedToday: (skip = 0, limit = 100) =>
    apiCall(`/reports/arrived-today?skip=${skip}&limit=${limit}`, {
      method: "GET",
    }),

  getSoldToday: (skip = 0, limit = 100) =>
    apiCall(`/reports/sold-today?skip=${skip}&limit=${limit}`, {
      method: "GET",
    }),
};

// ============================================================================
// API KEYS (Scripting Integration)
// ============================================================================

export const apiKeysAPI = {
  create: (data: { name: string; description?: string; scopes?: string[] }) =>
    apiCall("/api-keys", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  list: () => apiCall("/api-keys", { method: "GET" }),

  revoke: (id: string) =>
    apiCall(`/api-keys/${id}`, { method: "DELETE" }),
};

// ============================================================================
// INBOX & ANNOUNCEMENTS
// ============================================================================

export const inboxAPI = {
  create: (data: {
    warehouse_id: string;
    tracking_number?: string;
    carrier?: string;
    announced_date?: string;
  }) =>
    apiCall("/inbox", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  list: (skip = 0, limit = 50, status?: string) => {
    const query = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    if (status) query.append("status", status);
    return apiCall(`/inbox?${query}`, { method: "GET" });
  },

  accept: (id: string) =>
    apiCall(`/inbox/${id}/accept`, { method: "POST" }),

  decline: (id: string) =>
    apiCall(`/inbox/${id}/decline`, { method: "POST" }),

  revert: (id: string, data: { comment?: string }) =>
    apiCall(`/inbox/${id}/revert`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

// ============================================================================
// STORAGE LOCATIONS
// ============================================================================

export const storageAPI = {
  create: (data: {
    warehouse_id: string;
    zone: string;
    rack: string;
    bin: string;
  }) =>
    apiCall("/storage-locations", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  list: (skip = 0, limit = 50, warehouseId?: string) => {
    const query = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    if (warehouseId) query.append("warehouse_id", warehouseId);
    return apiCall(`/storage-locations?${query}`, { method: "GET" });
  },
};

// ============================================================================
// APPROVAL QUEUE
// ============================================================================

export const approvalsAPI = {
  listPending: (skip = 0, limit = 50) =>
    apiCall(`/approvals?skip=${skip}&limit=${limit}`, { method: "GET" }),

  approve: (ticketId: string) =>
    apiCall(`/tickets/${ticketId}/approve`, { method: "POST" }),
};

// ============================================================================
// NATURAL LANGUAGE QUERY
// ============================================================================

export const queryAPI = {
  search: (data: { query: string; warehouse_id?: string }) =>
    apiCall("/query", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

// ============================================================================
// VISION MEASUREMENT
// ============================================================================

export const visionAPI = {
  measure: (imageFile: File) => {
    const formData = new FormData();
    formData.append("file", imageFile);
    return fetch(`${API_BASE}/vision/measure`, {
      method: "POST",
      headers: { Authorization: `Bearer ${tokenManager.getAccessToken()}` },
      body: formData,
    }).then((r) => r.json());
  },
};

// ============================================================================
// AUDIT LOG
// ============================================================================

export const auditAPI = {
  list: (skip = 0, limit = 50, filters?: {
    actor_id?: string;
    collection?: string;
    action?: string;
  }) => {
    const query = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    if (filters?.actor_id) query.append("actor_id", filters.actor_id);
    if (filters?.collection) query.append("collection", filters.collection);
    if (filters?.action) query.append("action", filters.action);
    return apiCall(`/audit?${query}`, { method: "GET" });
  },
};

// ============================================================================
// HEALTH CHECK
// ============================================================================

export const healthAPI = {
  check: () => apiCall("/health", { method: "GET" }),
};

// ============================================================================
// EXPORT
// ============================================================================

export default {
  authAPI,
  usersAPI,
  warehousesAPI,
  ordersAPI,
  ticketsAPI,
  arrivalsAPI,
  voiceAPI,
  reportsAPI,
  apiKeysAPI,
  inboxAPI,
  storageAPI,
  approvalsAPI,
  queryAPI,
  visionAPI,
  auditAPI,
  healthAPI,
};
