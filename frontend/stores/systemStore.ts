
import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { apiClient } from '@/services/api'

interface SystemMetrics {
  cpu_usage: number
  memory_usage: number
  active_connections: number
  tasks_completed: number
  emails_processed: number
  meetings_scheduled: number
  productivity_score: number
}

interface SystemStatus {
  status: 'healthy' | 'warning' | 'error'
  database: boolean
  ollama: boolean
  integrations: number
  agents: number
}

interface SystemStore {
  systemStatus: SystemStatus | null
  metrics: SystemMetrics | null
  loading: boolean
  error: string | null
  
  // Actions
  initializeSystem: () => Promise<void>
  fetchSystemStatus: () => Promise<void>
  fetchMetrics: () => Promise<void>
  setError: (error: string | null) => void
}

export const useSystemStore = create<SystemStore>()(
  devtools(
    (set, get) => ({
      systemStatus: null,
      metrics: null,
      loading: false,
      error: null,

      initializeSystem: async () => {
        set({ loading: true, error: null })
        try {
          await Promise.all([
            get().fetchSystemStatus(),
            get().fetchMetrics(),
          ])
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'System initialization failed' })
        } finally {
          set({ loading: false })
        }
      },

      fetchSystemStatus: async () => {
        try {
          const response = await apiClient.get('/api/v1/system/status')
          set({ systemStatus: response.data })
        } catch (error) {
          console.error('Failed to fetch system status:', error)
          set({ 
            systemStatus: {
              status: 'error',
              database: false,
              ollama: false,
              integrations: 0,
              agents: 0
            }
          })
        }
      },

      fetchMetrics: async () => {
        try {
          const response = await apiClient.get('/api/v1/system/metrics')
          set({ metrics: response.data })
        } catch (error) {
          console.error('Failed to fetch metrics:', error)
          set({
            metrics: {
              cpu_usage: 0,
              memory_usage: 0,
              active_connections: 0,
              tasks_completed: 0,
              emails_processed: 0,
              meetings_scheduled: 0,
              productivity_score: 0
            }
          })
        }
      },

      setError: (error) => set({ error }),
    }),
    {
      name: 'system-store',
    }
  )
)
