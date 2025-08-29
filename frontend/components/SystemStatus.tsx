
import { useEffect } from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Grid,
  LinearProgress,
} from '@mui/material'
import {
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'

import { useSystemStore } from '@/stores/systemStore'

export default function SystemStatus() {
  const { systemStatus, metrics, loading, fetchSystemStatus, fetchMetrics } = useSystemStore()

  useEffect(() => {
    fetchSystemStatus()
    fetchMetrics()
    
    // Refresh every 30 seconds
    const interval = setInterval(() => {
      fetchSystemStatus()
      fetchMetrics()
    }, 30000)

    return () => clearInterval(interval)
  }, [fetchSystemStatus, fetchMetrics])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckIcon color="success" />
      case 'warning':
        return <WarningIcon color="warning" />
      case 'error':
        return <ErrorIcon color="error" />
      default:
        return <ErrorIcon color="disabled" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'success'
      case 'warning':
        return 'warning'
      case 'error':
        return 'error'
      default:
        return 'default'
    }
  }

  if (loading && !systemStatus) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            System Status
          </Typography>
          <LinearProgress />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ mr: 2 }}>
            System Status
          </Typography>
          {systemStatus && (
            <Chip
              icon={getStatusIcon(systemStatus.status)}
              label={systemStatus.status.toUpperCase()}
              color={getStatusColor(systemStatus.status) as any}
              variant="outlined"
            />
          )}
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                Database
              </Typography>
              <Chip
                icon={systemStatus?.database ? <CheckIcon /> : <ErrorIcon />}
                label={systemStatus?.database ? 'Connected' : 'Disconnected'}
                color={systemStatus?.database ? 'success' : 'error'}
                size="small"
                sx={{ mt: 1 }}
              />
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                LLM Service
              </Typography>
              <Chip
                icon={systemStatus?.ollama ? <CheckIcon /> : <ErrorIcon />}
                label={systemStatus?.ollama ? 'Online' : 'Offline'}
                color={systemStatus?.ollama ? 'success' : 'error'}
                size="small"
                sx={{ mt: 1 }}
              />
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                Active Integrations
              </Typography>
              <Typography variant="h6" sx={{ mt: 1 }}>
                {systemStatus?.integrations || 0}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                Active Agents
              </Typography>
              <Typography variant="h6" sx={{ mt: 1 }}>
                {systemStatus?.agents || 0}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  )
}
