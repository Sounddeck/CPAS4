
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material'
import {
  CheckCircle as AcceptIcon,
  Close as DismissIcon,
  TrendingUp as TrendingIcon,
  Schedule as ScheduleIcon,
  Psychology as BrainIcon,
} from '@mui/icons-material'
import { useSnackbar } from 'notistack'

import { useProactiveStore } from '@/stores/proactiveStore'

interface ProactiveSuggestionsProps {
  suggestions: any[]
}

export default function ProactiveSuggestions({ suggestions }: ProactiveSuggestionsProps) {
  const { acceptSuggestion, dismissSuggestion } = useProactiveStore()
  const { enqueueSnackbar } = useSnackbar()

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

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'time_management':
        return <ScheduleIcon />
      case 'productivity':
        return <TrendingIcon />
      case 'communication':
        return <BrainIcon />
      default:
        return <BrainIcon />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'time_management':
        return 'primary'
      case 'productivity':
        return 'success'
      case 'communication':
        return 'info'
      default:
        return 'default'
    }
  }

  const getPriorityColor = (priority: number) => {
    if (priority >= 0.8) return 'error'
    if (priority >= 0.6) return 'warning'
    return 'info'
  }

  if (suggestions.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Proactive Suggestions
          </Typography>
          <Typography variant="body2" color="text.secondary">
            No suggestions at the moment. Your AI is monitoring for opportunities to help.
          </Typography>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <BrainIcon sx={{ mr: 1 }} />
          <Typography variant="h6">
            Proactive Suggestions ({suggestions.length})
          </Typography>
        </Box>

        <List>
          {suggestions.map((suggestion) => (
            <ListItem
              key={suggestion.id}
              sx={{
                border: 1,
                borderColor: 'divider',
                borderRadius: 2,
                mb: 1,
                '&:last-child': { mb: 0 },
              }}
            >
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Typography variant="subtitle1" component="span">
                      {suggestion.title}
                    </Typography>
                    <Chip
                      icon={getTypeIcon(suggestion.type)}
                      label={suggestion.type.replace('_', ' ')}
                      size="small"
                      color={getTypeColor(suggestion.type) as any}
                      variant="outlined"
                    />
                    <Chip
                      label={`Priority: ${Math.round(suggestion.priority * 100)}%`}
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
                    edge="end"
                    aria-label="accept"
                    onClick={() => handleAccept(suggestion.id)}
                    color="success"
                    size="small"
                  >
                    <AcceptIcon />
                  </IconButton>
                  <IconButton
                    edge="end"
                    aria-label="dismiss"
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

        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Button size="small" href="/proactive">
            View All Suggestions
          </Button>
        </Box>
      </CardContent>
    </Card>
  )
}
