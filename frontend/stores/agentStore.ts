
import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { apiClient } from '@/services/api'

interface Agent {
  id: string
  name: string
  type: string
  status: 'active' | 'inactive' | 'busy' | 'error'
  description: string
  capabilities: string[]
  tasks_completed?: number
  created_at: string
  updated_at: string
}

interface AgentStore {
  agents: Agent[]
  selectedAgent: Agent | null
  loading: boolean
  error: string | null
  
  // Actions
  fetchAgents: () => Promise<void>
  createAgent: (agentData: Partial<Agent>) => Promise<void>
  updateAgent: (id: string, updates: Partial<Agent>) => Promise<void>
  deleteAgent: (id: string) => Promise<void>
  selectAgent: (agent: Agent | null) => void
  executeAgentTask: (agentId: string, task: any) => Promise<any>
  setError: (error: string | null) => void
}

export const useAgentStore = create<AgentStore>()(
  devtools(
    (set, get) => ({
      agents: [],
      selectedAgent: null,
      loading: false,
      error: null,

      fetchAgents: async () => {
        set({ loading: true, error: null })
        try {
          const response = await apiClient.get('/api/v1/agents')
          set({ agents: response.data.agents || [] })
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to fetch agents' })
        } finally {
          set({ loading: false })
        }
      },

      createAgent: async (agentData) => {
        set({ loading: true, error: null })
        try {
          const response = await apiClient.post('/api/v1/agents', agentData)
          const newAgent = response.data
          set(state => ({ 
            agents: [...state.agents, newAgent],
            selectedAgent: newAgent
          }))
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to create agent' })
          throw error
        } finally {
          set({ loading: false })
        }
      },

      updateAgent: async (id, updates) => {
        set({ loading: true, error: null })
        try {
          const response = await apiClient.put(`/api/v1/agents/${id}`, updates)
          const updatedAgent = response.data
          set(state => ({
            agents: state.agents.map(agent => 
              agent.id === id ? updatedAgent : agent
            ),
            selectedAgent: state.selectedAgent?.id === id ? updatedAgent : state.selectedAgent
          }))
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to update agent' })
          throw error
        } finally {
          set({ loading: false })
        }
      },

      deleteAgent: async (id) => {
        set({ loading: true, error: null })
        try {
          await apiClient.delete(`/api/v1/agents/${id}`)
          set(state => ({
            agents: state.agents.filter(agent => agent.id !== id),
            selectedAgent: state.selectedAgent?.id === id ? null : state.selectedAgent
          }))
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to delete agent' })
          throw error
        } finally {
          set({ loading: false })
        }
      },

      selectAgent: (agent) => set({ selectedAgent: agent }),

      executeAgentTask: async (agentId, task) => {
        try {
          const response = await apiClient.post(`/api/v1/agents/${agentId}/execute`, task)
          return response.data
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Failed to execute task' })
          throw error
        }
      },

      setError: (error) => set({ error }),
    }),
    {
      name: 'agent-store',
    }
  )
)
