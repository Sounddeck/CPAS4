
import { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Tabs,
  Tab,
  LinearProgress,
} from '@mui/material'
import {
  CheckCircle as AcceptIcon,
  Close as DismissIcon,
  Psychology as BrainIcon,
  TrendingUp as TrendingIcon,
  Notifications as NotificationIcon,
  Insights as InsightsIcon,
} from '@mui/icons-material'
import { useSnackbar } from 'notistack'

import { useProactiveStore } from '@/stores/proactiveStore'

export default function ProactivePage() {
  const {
    suggestions,
    notifications,
    patterns,
    insights,
    fetchSuggestions,
    fetchNotifications,
    fetchPatterns,
    fetchInsights,
    acceptSuggestion,
    dismissSuggestion,
    markNotificationRead,
  } = useProactiveStore()
  
  const { enqueueSnackbar } = useSnackbar()
  const [tabValue, setTabValue] = useState(0)

  useEffect(() => {
    fetchSuggestions()
    fetchNotifications()
    fetchPatterns()
    fetchInsights()
  }, [fetchSuggestions, fetchNotifications, fetchPatterns, fetchInsights])

  const handleAccept = async (id: string) => {
    try {
      await acceptSuggestion(id)
      enqueueSnackbar('Suggestion accepted and executed', { variant: 'success' })
    } catch (error) {
      enqueueSnackbar('Failed to accept suggestion', { variant: 'error' })
    }
  }

  const handleDismiss = async (id: string) => {
    try {
      await dismissSuggestion(id)
      enqueueSnackbar('Suggestion dismissed', { variant: 'info' })
    } catch (error) {
      enqueueSnackbar('Failed to dismiss suggestion', { variant: 'error' })
    }
  }

  const handleMarkRead = async (id: string) => {
    try {
      await markNotificationRead(id)
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
    }
  }

  const getPriorityColor = (priority: number) => {
    if (priority >= 0.8) return 'error'
    if (priority >= 0.6) return 'warning'
    return 'info'
  }

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      'time_management': 'primary',
      'productivity': 'success',
      'communication': 'info',
      'learning': 'secondary',
    }
    return colors[type] || 'default'
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Proactive AI Assistant
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Your AI continuously monitors your patterns and provides intelligent suggestions to improve productivity.
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="Suggestions" icon={<BrainIcon />} />
          <Tab label="Notifications" icon={<NotificationIcon />} />
          <Tab label="Insights" icon={<InsightsIcon />} />
          <Tab label="Patterns" icon={<TrendingIcon />} />
        </Tabs>
      </Box>

      {/* Suggestions Tab */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Active Suggestions ({suggestions.filter(s => s.status === 'pending').length})
                </Typography>
                
                <List>
                  {suggestions.filter(s => s.status === 'pending').map((suggestion) => (
                    <ListItem
                      key={suggestion.id}
                      sx={{
                        border: 1,
                        borderColor: 'divider',
                        borderRadius: 2,
                        mb: 1,
                      }}
                    >
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <Typography variant="subtitle1">
                              {suggestion.title}
                            </Typography>
                            <Chip
                              label={suggestion.type.replace('_', ' ')}
                              size="small"
                              color={getTypeColor(suggestion.type) as any}
                              variant="outlined"
                            />
                            <Chip
                              label={`${Math.round(suggestion.priority * 100)}% priority`}
                              size="small"
                              color={getPriorityColor(suggestion.priority) as any}
                            />
                          </Box>
                        }
                        secondary={suggestion.message}
                      />
                      <ListItemSecondaryAction>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <IconButton
                            onClick={() => handleAccept(suggestion.id)}
                            color="success"
                            size="small"
                          >
                            <AcceptIcon />
                          </IconButton>
                          <IconButton
                            onClick={() => handleDismiss(suggestion.id)}
                            color="error"
                            size="small"
                          >
                            <DismissIcon />
                          </IconButton>
                        </Box>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>

                {suggestions.filter(s => s.status === 'pending').length === 0 && (
                  <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                    No active suggestions. Your AI is monitoring for opportunities to help.
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Notifications Tab */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Notifications ({notifications.filter(n => !n.read).length} unread)
                </Typography>
                
                <List>
                  {notifications.map((notification) => (
                    <ListItem
                      key={notification.id}
                      sx={{
                        border: 1,
                        borderColor: notification.read ? 'divider' : 'primary.main',
                        borderRadius: 2,
                        mb: 1,
                        bgcolor: notification.read ? 'transparent' : 'primary.50',
                      }}
                      onClick={() => !notification.read && handleMarkRead(notification.id)}
                    >
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="subtitle1">
                              {notification.title}
                            </Typography>
                            {!notification.read && (
                              <Box
                                sx={{
                                  width: 8,
                                  height: 8,
                                  borderRadius: '50%',
                                  bgcolor: 'primary.main',
                                }}
                              />
                            )}
                          </Box>
                        }
                        secondary={notification.message}
                      />
                    </ListItem>
                  ))}
                </List>

                {notifications.length === 0 && (
                  <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                    No notifications yet.
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Insights Tab */}
      {tabValue === 2 && (
        <Grid container spacing={3}>
          {insights && (
            <>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Productivity Score
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h3" color="primary.main" sx={{ mr: 2 }}>
                        {Math.round((insights.productivity_score || 0) * 100)}%
                      </Typography>
                      <Chip
                        label={insights.efficiency_trends || 'stable'}
                        color="success"
                        variant="outlined"
                      />
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={(insights.productivity_score || 0) * 100}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Key Metrics
                    </Typography>
                    <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                      <Box>
                        <Typography variant="h4" color="primary.main">
                          {insights.metrics?.tasks_completed || 0}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Tasks Completed
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="h4" color="secondary.main">
                          {insights.metrics?.focus_time_hours || 0}h
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Focus Time
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="h4" color="success.main">
                          {insights.metrics?.suggestions_accepted || 0}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Suggestions Accepted
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="h4" color="info.main">
                          {insights.metrics?.automation_saves_minutes || 0}m
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Time Saved
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Key Insights
                    </Typography>
                    <List>
                      {(insights.key_insights || []).map((insight: string, index: number) => (
                        <ListItem key={index}>
                          <ListItemText primary={insight} />
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            </>
          )}
        </Grid>
      )}

      {/* Patterns Tab */}
      {tabValue === 3 && (
        <Grid container spacing={3}>
          {patterns && (
            <>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Work Habits
                    </Typography>
                    {patterns.work_habits && (
                      <Box>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Peak Hours: {patterns.work_habits.peak_productivity_hours?.join(', ')}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Avg Focus: {patterns.work_habits.avg_continuous_work_hours}h
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Deep Work: {patterns.work_habits.deep_work_preference}
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Communication
                    </Typography>
                    {patterns.communication && (
                      <Box>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Response Time: {patterns.communication.avg_email_response_time}h
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Meetings/Week: {patterns.communication.meeting_frequency}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Peak Hours: {patterns.communication.communication_peak_hours?.join(', ')}
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Productivity
                    </Typography>
                    {patterns.productivity && (
                      <Box>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Completion Rate: {Math.round((patterns.productivity.task_completion_rate || 0) * 100)}%
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Context Switches: {patterns.productivity.context_switching_frequency}/day
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Focus Sessions: {patterns.productivity.focus_session_duration}min
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </>
          )}
        </Grid>
      )}
    </Box>
  )
}
