
import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { apiClient } from '@/services/api'

interface Suggestion {
  id: string
  type: string
  title: string
  message: string
  priority: number
  action?: string
  status: 'pending' | 'accepted' | 'dismissed'
  created_at: string
}

interface Notification {
  id: string
  type: string
  title: string
  message: string
  priority: number
  read: boolean
  created_at: string
}

interface ProactiveStore {
  suggestions: Suggestion[]
  notifications: Notification[]
  patterns: any
  insights: any
  loading: boolean
  error: string | null
  
  // Actions
  fetchSuggestions: () => Promise<void>
  fetchNotifications: () => Promise<void>
  fetchPatterns: () => Promise<void>
  fetchInsights: () => Promise<void>
  acceptSuggestion: (id: string) => Promise<void>
  dismissSuggestion: (id: string, reason?: string) => Promise<void>
  markNotificationRead: (id: string) => Promise<void>
  setError: (error: string | null) => void
}

export const useProactiveStore = create<ProactiveStore>()(
  devtools(
    (set, get) => ({
      suggestions: [],
      notifications: [],
      patterns: null,
      insights: null,
      loading: false,
      error: null,

      fetchSuggestions: async () => {
        try {
          const response = await apiClient.get('/api/v1/proactive/suggestions')
          set({ suggestions: response.data.suggestions || [] })
        } catch (error) {
          console.error('Failed to fetch suggestions:', error)
        }
      },

      fetchNotifications: async () => {
        try {
          const response = await apiClient.get('/api/v1/proactive/notifications')
          set({ notifications: response.data.notifications || [] })
        } catch (error) {
          console.error('Failed to fetch notifications:', error)
        }
      },

      fetchPatterns: async () => {
        try {
          const response = await apiClient.get('/api/v1/proactive/patterns')
          set({ patterns: response.data.patterns })
        } catch (error) {
          console.error('Failed to fetch patterns:', error)
        }
      },

      fetchInsights: async () => {
        try {
          const response = await apiClient.get('/api/v1/proactive/insights')
          set({ insights: response.data })
        } catch (error) {
          console.error('Failed to fetch insights:', error)
        }
      },

      acceptSuggestion: async (id) => {
        try {
          await apiClient.post(`/api/v1/proactive/suggestions/${id}/accept`)
          set(state => ({
            suggestions: state.suggestions.map(s => 
              s.id === id ? { ...s, status: 'accepted' } : s
            )
          }))
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to accept suggestion' })
        }
      },

      dismissSuggestion: async (id, reason) => {
        try {
          await apiClient.post(`/api/v1/proactive/suggestions/${id}/dismiss`, { reason })
          set(state => ({
            suggestions: state.suggestions.map(s => 
              s.id === id ? { ...s, status: 'dismissed' } : s
            )
          }))
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to dismiss suggestion' })
        }
      },

      markNotificationRead: async (id) => {
        try {
          await apiClient.post(`/api/v1/proactive/notifications/${id}/read`)
          set(state => ({
            notifications: state.notifications.map(n => 
              n.id === id ? { ...n, read: true } : n
            )
          }))
        } catch (error) {
          console.error('Failed to mark notification as read:', error)
        }
      },

      setError: (error) => set({ error }),
    }),
    {
      name: 'proactive-store',
    }
  )
)
