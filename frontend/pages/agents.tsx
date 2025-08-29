
import { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Avatar,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as ExecuteIcon,
  SmartToy as AgentIcon,
} from '@mui/icons-material'
import { useSnackbar } from 'notistack'

import { useAgentStore } from '@/stores/agentStore'

export default function AgentsPage() {
  const { agents, loading, fetchAgents, createAgent, deleteAgent, executeAgentTask } = useAgentStore()
  const { enqueueSnackbar } = useSnackbar()
  
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [executeDialogOpen, setExecuteDialogOpen] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<any>(null)
  const [newAgent, setNewAgent] = useState({
    name: '',
    type: 'general',
    description: '',
  })
  const [taskInput, setTaskInput] = useState('')

  useEffect(() => {
    fetchAgents()
  }, [fetchAgents])

  const handleCreateAgent = async () => {
    try {
      await createAgent(newAgent)
      setCreateDialogOpen(false)
      setNewAgent({ name: '', type: 'general', description: '' })
      enqueueSnackbar('Agent created successfully', { variant: 'success' })
    } catch (error) {
      enqueueSnackbar('Failed to create agent', { variant: 'error' })
    }
  }

  const handleDeleteAgent = async (id: string) => {
    try {
      await deleteAgent(id)
      enqueueSnackbar('Agent deleted successfully', { variant: 'success' })
    } catch (error) {
      enqueueSnackbar('Failed to delete agent', { variant: 'error' })
    }
  }

  const handleExecuteTask = async () => {
    if (!selectedAgent || !taskInput) return
    
    try {
      const result = await executeAgentTask(selectedAgent.id, {
        type: 'general',
        instruction: taskInput,
      })
      setExecuteDialogOpen(false)
      setTaskInput('')
      setSelectedAgent(null)
      enqueueSnackbar('Task executed successfully', { variant: 'success' })
    } catch (error) {
      enqueueSnackbar('Failed to execute task', { variant: 'error' })
    }
  }

  const getAgentTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      'task_manager': 'primary',
      'research_agent': 'secondary',
      'creative_agent': 'success',
      'technical_agent': 'info',
      'personal_assistant': 'warning',
      'general': 'default',
    }
    return colors[type] || 'default'
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'active': 'success',
      'inactive': 'default',
      'busy': 'warning',
      'error': 'error',
    }
    return colors[status] || 'default'
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          AI Agents
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Create Agent
        </Button>
      </Box>

      <Grid container spacing={3}>
        {agents.map((agent) => (
          <Grid item xs={12} sm={6} md={4} key={agent.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                    <AgentIcon />
                  </Avatar>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" component="div">
                      {agent.name}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                      <Chip
                        label={agent.type.replace('_', ' ')}
                        size="small"
                        color={getAgentTypeColor(agent.type) as any}
                        variant="outlined"
                      />
                      <Chip
                        label={agent.status}
                        size="small"
                        color={getStatusColor(agent.status) as any}
                      />
                    </Box>
                  </Box>
                </Box>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {agent.description}
                </Typography>

                <Typography variant="caption" color="text.secondary">
                  Tasks completed: {agent.tasks_completed || 0}
                </Typography>
              </CardContent>
              
              <CardActions>
                <Button
                  size="small"
                  startIcon={<ExecuteIcon />}
                  onClick={() => {
                    setSelectedAgent(agent)
                    setExecuteDialogOpen(true)
                  }}
                >
                  Execute Task
                </Button>
                <IconButton
                  size="small"
                  onClick={() => handleDeleteAgent(agent.id)}
                  color="error"
                >
                  <DeleteIcon />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {agents.length === 0 && !loading && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <AgentIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No agents created yet
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Create your first AI agent to get started
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create Your First Agent
          </Button>
        </Box>
      )}

      {/* Create Agent Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Agent</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Agent Name"
            fullWidth
            variant="outlined"
            value={newAgent.name}
            onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
            sx={{ mb: 2 }}
          />
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Agent Type</InputLabel>
            <Select
              value={newAgent.type}
              label="Agent Type"
              onChange={(e) => setNewAgent({ ...newAgent, type: e.target.value })}
            >
              <MenuItem value="general">General Assistant</MenuItem>
              <MenuItem value="task_manager">Task Manager</MenuItem>
              <MenuItem value="research_agent">Research Agent</MenuItem>
              <MenuItem value="creative_agent">Creative Agent</MenuItem>
              <MenuItem value="technical_agent">Technical Agent</MenuItem>
              <MenuItem value="personal_assistant">Personal Assistant</MenuItem>
            </Select>
          </FormControl>

          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={newAgent.description}
            onChange={(e) => setNewAgent({ ...newAgent, description: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateAgent} variant="contained">
            Create Agent
          </Button>
        </DialogActions>
      </Dialog>

      {/* Execute Task Dialog */}
      <Dialog open={executeDialogOpen} onClose={() => setExecuteDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Execute Task - {selectedAgent?.name}</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Task Description"
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            value={taskInput}
            onChange={(e) => setTaskInput(e.target.value)}
            placeholder="Describe what you want the agent to do..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExecuteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleExecuteTask} variant="contained">
            Execute Task
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
