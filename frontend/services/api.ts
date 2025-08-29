
import axios from 'axios'

// Create axios instance with base configuration
export const apiClient = axios.create({
  baseURL: process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API service functions
export const systemApi = {
  getStatus: () => apiClient.get('/v1/system/status'),
  getInfo: () => apiClient.get('/v1/system/info'),
  getMetrics: () => apiClient.get('/v1/system/metrics'),
}

export const agentApi = {
  list: () => apiClient.get('/v1/agents'),
  get: (id: string) => apiClient.get(`/v1/agents/${id}`),
  create: (data: any) => apiClient.post('/v1/agents', data),
  update: (id: string, data: any) => apiClient.put(`/v1/agents/${id}`, data),
  delete: (id: string) => apiClient.delete(`/v1/agents/${id}`),
  execute: (id: string, task: any) => apiClient.post(`/v1/agents/${id}/execute`, task),
}

export const workflowApi = {
  list: () => apiClient.get('/v1/workflows'),
  get: (id: string) => apiClient.get(`/v1/workflows/${id}`),
  create: (data: any) => apiClient.post('/v1/workflows', data),
  update: (id: string, data: any) => apiClient.put(`/v1/workflows/${id}`, data),
  delete: (id: string) => apiClient.delete(`/v1/workflows/${id}`),
  execute: (id: string, data: any) => apiClient.post(`/v1/workflows/${id}/execute`, data),
}

export const integrationApi = {
  list: () => apiClient.get('/v1/integrations'),
  get: (id: string) => apiClient.get(`/v1/integrations/${id}`),
  create: (data: any) => apiClient.post('/v1/integrations', data),
  update: (id: string, data: any) => apiClient.put(`/v1/integrations/${id}`, data),
  delete: (id: string) => apiClient.delete(`/v1/integrations/${id}`),
  sync: (id: string) => apiClient.post(`/v1/integrations/${id}/sync`),
}

export const proactiveApi = {
  getSuggestions: () => apiClient.get('/v1/proactive/suggestions'),
  getNotifications: () => apiClient.get('/v1/proactive/notifications'),
  getPatterns: () => apiClient.get('/v1/proactive/patterns'),
  getInsights: () => apiClient.get('/v1/proactive/insights'),
  acceptSuggestion: (id: string) => apiClient.post(`/v1/proactive/suggestions/${id}/accept`),
  dismissSuggestion: (id: string, reason?: string) => 
    apiClient.post(`/v1/proactive/suggestions/${id}/dismiss`, { reason }),
  markNotificationRead: (id: string) => 
    apiClient.post(`/v1/proactive/notifications/${id}/read`),
}

export const memoryApi = {
  list: () => apiClient.get('/v1/memory'),
  get: (id: string) => apiClient.get(`/v1/memory/${id}`),
  create: (data: any) => apiClient.post('/v1/memory', data),
  search: (query: string) => apiClient.post('/v1/memory/search', { query }),
  delete: (id: string) => apiClient.delete(`/v1/memory/${id}`),
}

export const llmApi = {
  generate: (data: any) => apiClient.post('/v1/llm/generate', data),
  chat: (data: any) => apiClient.post('/v1/llm/chat', data),
  getModels: () => apiClient.get('/v1/llm/models'),
}
