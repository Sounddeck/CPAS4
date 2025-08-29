
import {
  Box,
  Button,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material'
import {
  Add as AddIcon,
  PlayArrow as ExecuteIcon,
  Schedule as ScheduleIcon,
  Email as EmailIcon,
} from '@mui/icons-material'
import { useState } from 'react'
import { useSnackbar } from 'notistack'

import { useAgentStore } from '@/stores/agentStore'

export default function QuickActions() {
  const [createAgentOpen, setCreateAgentOpen] = useState(false)
  const [newAgent, setNewAgent] = useState({
    name: '',
    type: 'general',
    description: '',
  })
  const { createAgent } = useAgentStore()
  const { enqueueSnackbar } = useSnackbar()

  const handleCreateAgent = async () => {
    try {
      await createAgent(newAgent)
      setCreateAgentOpen(false)
      setNewAgent({ name: '', type: 'general', description: '' })
      enqueueSnackbar('Agent created successfully', { variant: 'success' })
    } catch (error) {
      enqueueSnackbar('Failed to create agent', { variant: 'error' })
    }
  }

  const quickActions = [
    {
      label: 'Create Agent',
      icon: <AddIcon />,
      action: () => setCreateAgentOpen(true),
      color: 'primary' as const,
    },
    {
      label: 'Quick Task',
      icon: <ExecuteIcon />,
      action: () => console.log('Quick task'),
      color: 'secondary' as const,
    },
    {
      label: 'Schedule Meeting',
      icon: <ScheduleIcon />,
      action: () => console.log('Schedule meeting'),
      color: 'success' as const,
    },
    {
      label: 'Send Email',
      icon: <EmailIcon />,
      action: () => console.log('Send email'),
      color: 'info' as const,
    },
  ]

  return (
    <Box>
      <Grid container spacing={2}>
        {quickActions.map((action, index) => (
          <Grid item xs={12} key={index}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={action.icon}
              onClick={action.action}
              color={action.color}
              sx={{ justifyContent: 'flex-start', py: 1.5 }}
            >
              {action.label}
            </Button>
          </Grid>
        ))}
      </Grid>

      {/* Create Agent Dialog */}
      <Dialog open={createAgentOpen} onClose={() => setCreateAgentOpen(false)} maxWidth="sm" fullWidth>
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
          <Button onClick={() => setCreateAgentOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateAgent} variant="contained">
            Create Agent
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
