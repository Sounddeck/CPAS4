
import { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  IconButton,
  Fab,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  SmartToy as AgentIcon,
  Notifications as NotificationIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  Email as EmailIcon,
  Task as TaskIcon,
  Mic as MicIcon,
  Add as AddIcon,
} from '@mui/icons-material'
import { motion } from 'framer-motion'

import { useSystemStore } from '@/stores/systemStore'
import { useAgentStore } from '@/stores/agentStore'
import { useProactiveStore } from '@/stores/proactiveStore'
import QuickActions from '@/components/QuickActions'
import SystemStatus from '@/components/SystemStatus'
import VoiceInterface from '@/components/VoiceInterface'
import ProactiveSuggestions from '@/components/ProactiveSuggestions'

export default function Dashboard() {
  const { systemStatus, metrics } = useSystemStore()
  const { agents } = useAgentStore()
  const { suggestions, notifications } = useProactiveStore()
  const [voiceOpen, setVoiceOpen] = useState(false)

  const activeAgents = agents.filter(agent => agent.status === 'active')
  const recentNotifications = notifications.slice(0, 5)
  const topSuggestions = suggestions.filter(s => s.priority > 0.7).slice(0, 3)

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Welcome to Enhanced CPAS
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Your comprehensive personal AI system is ready to assist you.
        </Typography>
      </Box>

      {/* System Status */}
      <SystemStatus />

      {/* Main Dashboard Grid */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <QuickActions />
            </CardContent>
          </Card>
        </Grid>

        {/* Active Agents */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AgentIcon sx={{ mr: 1 }} />
                <Typography variant="h6">
                  Active Agents ({activeAgents.length})
                </Typography>
              </Box>
              <List dense>
                {activeAgents.slice(0, 4).map((agent) => (
                  <ListItem key={agent.id} sx={{ px: 0 }}>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                        {agent.name.charAt(0)}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={agent.name}
                      secondary={`${agent.type} • ${agent.tasks_completed || 0} tasks`}
                    />
                    <Chip
                      label={agent.status}
                      size="small"
                      color="success"
                      variant="outlined"
                    />
                  </ListItem>
                ))}
              </List>
              {activeAgents.length > 4 && (
                <Button size="small" sx={{ mt: 1 }}>
                  View All Agents
                </Button>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Notifications */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <NotificationIcon sx={{ mr: 1 }} />
                <Typography variant="h6">
                  Recent Notifications
                </Typography>
              </Box>
              <List dense>
                {recentNotifications.map((notification) => (
                  <ListItem key={notification.id} sx={{ px: 0 }}>
                    <ListItemText
                      primary={notification.title}
                      secondary={notification.message}
                      primaryTypographyProps={{ variant: 'body2' }}
                      secondaryTypographyProps={{ variant: 'caption' }}
                    />
                    {!notification.read && (
                      <Box
                        sx={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          bgcolor: 'primary.main',
                          ml: 1,
                        }}
                      />
                    )}
                  </ListItem>
                ))}
              </List>
              <Button size="small" sx={{ mt: 1 }}>
                View All Notifications
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Proactive Suggestions */}
        <Grid item xs={12} md={8}>
          <ProactiveSuggestions suggestions={topSuggestions} />
        </Grid>

        {/* System Metrics */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Performance
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">CPU Usage</Typography>
                  <Typography variant="body2">{metrics?.cpu_usage || 0}%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={metrics?.cpu_usage || 0}
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Memory Usage</Typography>
                  <Typography variant="body2">{metrics?.memory_usage || 0}%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={metrics?.memory_usage || 0}
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Active Connections</Typography>
                  <Typography variant="body2">{metrics?.active_connections || 0}</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <TaskIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                    <Typography variant="h4" component="div">
                      {metrics?.tasks_completed || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Tasks Completed
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <EmailIcon sx={{ fontSize: 40, color: 'secondary.main', mb: 1 }} />
                    <Typography variant="h4" component="div">
                      {metrics?.emails_processed || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Emails Processed
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <ScheduleIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                    <Typography variant="h4" component="div">
                      {metrics?.meetings_scheduled || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Meetings Scheduled
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <TrendingUpIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
                    <Typography variant="h4" component="div">
                      {metrics?.productivity_score || 0}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Productivity Score
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Voice Interface FAB */}
      <Fab
        color="primary"
        aria-label="voice"
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
        }}
        onClick={() => setVoiceOpen(true)}
      >
        <MicIcon />
      </Fab>

      {/* Voice Interface Dialog */}
      <VoiceInterface
        open={voiceOpen}
        onClose={() => setVoiceOpen(false)}
      />
    </Box>
  )
}
