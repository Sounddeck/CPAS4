
"""
Proactive AI Service for Enhanced CPAS
Handles proactive suggestions, notifications, and intelligent automation
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase

from services.integration_service import IntegrationService
from services.agent_service import AgentService
from services.memory_service import MemoryService

class ProactiveService:
    """Service for proactive AI capabilities and intelligent automation"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.proactive_tasks = db.proactive_tasks
        self.notifications = db.notifications
        self.user_patterns = db.user_patterns
        self.suggestions = db.suggestions
        
        self.integration_service = IntegrationService(db)
        self.agent_service = AgentService(db)
        self.memory_service = MemoryService(db)
        
        # Proactive monitoring tasks
        self.monitoring_tasks = {}
        
    async def start_proactive_monitoring(self):
        """Start proactive monitoring and suggestion system"""
        logger.info("Starting proactive AI monitoring...")
        
        # Start various monitoring tasks
        self.monitoring_tasks["calendar"] = asyncio.create_task(self._monitor_calendar())
        self.monitoring_tasks["email"] = asyncio.create_task(self._monitor_email())
        self.monitoring_tasks["patterns"] = asyncio.create_task(self._analyze_user_patterns())
        self.monitoring_tasks["suggestions"] = asyncio.create_task(self._generate_proactive_suggestions())
        self.monitoring_tasks["reminders"] = asyncio.create_task(self._manage_smart_reminders())
        
        logger.info("Proactive monitoring started successfully")
    
    async def stop_proactive_monitoring(self):
        """Stop proactive monitoring"""
        logger.info("Stopping proactive AI monitoring...")
        
        for task_name, task in self.monitoring_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.monitoring_tasks.clear()
        logger.info("Proactive monitoring stopped")
    
    async def _monitor_calendar(self):
        """Monitor calendar for proactive suggestions"""
        while True:
            try:
                # Get upcoming calendar events
                upcoming_events = await self._get_upcoming_calendar_events()
                
                for event in upcoming_events:
                    await self._analyze_calendar_event(event)
                
                # Check for scheduling conflicts
                conflicts = await self._detect_scheduling_conflicts(upcoming_events)
                for conflict in conflicts:
                    await self._handle_scheduling_conflict(conflict)
                
                # Suggest optimal meeting times
                await self._suggest_optimal_meeting_times()
                
                # Check for travel time requirements
                await self._check_travel_time_requirements(upcoming_events)
                
            except Exception as e:
                logger.error(f"Calendar monitoring error: {e}")
            
            # Wait 15 minutes before next check
            await asyncio.sleep(900)
    
    async def _monitor_email(self):
        """Monitor email for proactive actions"""
        while True:
            try:
                # Get recent emails
                recent_emails = await self._get_recent_emails()
                
                for email in recent_emails:
                    await self._analyze_email_for_actions(email)
                
                # Check for emails requiring responses
                pending_responses = await self._identify_pending_email_responses()
                for email in pending_responses:
                    await self._suggest_email_response(email)
                
                # Identify action items from emails
                action_items = await self._extract_email_action_items(recent_emails)
                for item in action_items:
                    await self._create_task_from_email(item)
                
                # Suggest email organization
                await self._suggest_email_organization(recent_emails)
                
            except Exception as e:
                logger.error(f"Email monitoring error: {e}")
            
            # Wait 10 minutes before next check
            await asyncio.sleep(600)
    
    async def _analyze_user_patterns(self):
        """Analyze user behavior patterns for insights"""
        while True:
            try:
                # Analyze work patterns
                work_patterns = await self._analyze_work_patterns()
                await self._store_user_pattern("work_habits", work_patterns)
                
                # Analyze communication patterns
                comm_patterns = await self._analyze_communication_patterns()
                await self._store_user_pattern("communication", comm_patterns)
                
                # Analyze productivity patterns
                productivity_patterns = await self._analyze_productivity_patterns()
                await self._store_user_pattern("productivity", productivity_patterns)
                
                # Generate insights from patterns
                insights = await self._generate_pattern_insights(
                    work_patterns, comm_patterns, productivity_patterns
                )
                
                for insight in insights:
                    await self._create_proactive_suggestion(insight)
                
            except Exception as e:
                logger.error(f"Pattern analysis error: {e}")
            
            # Wait 1 hour before next analysis
            await asyncio.sleep(3600)
    
    async def _generate_proactive_suggestions(self):
        """Generate proactive suggestions based on context"""
        while True:
            try:
                current_context = await self._get_current_context()
                
                # Generate different types of suggestions
                suggestions = []
                
                # Time management suggestions
                time_suggestions = await self._generate_time_management_suggestions(current_context)
                suggestions.extend(time_suggestions)
                
                # Productivity suggestions
                productivity_suggestions = await self._generate_productivity_suggestions(current_context)
                suggestions.extend(productivity_suggestions)
                
                # Communication suggestions
                comm_suggestions = await self._generate_communication_suggestions(current_context)
                suggestions.extend(comm_suggestions)
                
                # Learning suggestions
                learning_suggestions = await self._generate_learning_suggestions(current_context)
                suggestions.extend(learning_suggestions)
                
                # Store and prioritize suggestions
                for suggestion in suggestions:
                    await self._store_suggestion(suggestion)
                
                # Send high-priority suggestions as notifications
                high_priority = [s for s in suggestions if s.get("priority", 0) > 0.8]
                for suggestion in high_priority:
                    await self._send_proactive_notification(suggestion)
                
            except Exception as e:
                logger.error(f"Suggestion generation error: {e}")
            
            # Wait 30 minutes before next suggestion cycle
            await asyncio.sleep(1800)
    
    async def _manage_smart_reminders(self):
        """Manage intelligent reminders and notifications"""
        while True:
            try:
                # Check for due reminders
                due_reminders = await self._get_due_reminders()
                
                for reminder in due_reminders:
                    await self._send_smart_reminder(reminder)
                
                # Create contextual reminders
                contextual_reminders = await self._generate_contextual_reminders()
                
                for reminder in contextual_reminders:
                    await self._schedule_reminder(reminder)
                
                # Optimize reminder timing
                await self._optimize_reminder_timing()
                
            except Exception as e:
                logger.error(f"Reminder management error: {e}")
            
            # Wait 5 minutes before next check
            await asyncio.sleep(300)
    
    async def _analyze_calendar_event(self, event: Dict[str, Any]):
        """Analyze calendar event for proactive actions"""
        event_time = datetime.fromisoformat(event["start_time"])
        time_until_event = event_time - datetime.utcnow()
        
        # Suggest preparation time
        if timedelta(hours=1) <= time_until_event <= timedelta(hours=2):
            await self._suggest_meeting_preparation(event)
        
        # Check for required materials
        if "materials" in event.get("description", "").lower():
            await self._suggest_material_preparation(event)
        
        # Suggest agenda if missing
        if not event.get("agenda") and "meeting" in event.get("title", "").lower():
            await self._suggest_agenda_creation(event)
        
        # Check for location and travel time
        if event.get("location") and event.get("location") != "Online":
            await self._suggest_travel_planning(event)
    
    async def _analyze_email_for_actions(self, email: Dict[str, Any]):
        """Analyze email for potential actions"""
        content = email.get("content", "").lower()
        subject = email.get("subject", "").lower()
        
        # Check for action keywords
        action_keywords = ["deadline", "due", "meeting", "schedule", "urgent", "asap", "follow up"]
        
        for keyword in action_keywords:
            if keyword in content or keyword in subject:
                action_type = await self._classify_email_action(email, keyword)
                await self._suggest_email_action(email, action_type)
        
        # Check for questions requiring responses
        if "?" in content:
            await self._suggest_response_needed(email)
        
        # Check for attachments requiring review
        if email.get("attachments"):
            await self._suggest_attachment_review(email)
    
    async def _generate_time_management_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate time management suggestions"""
        suggestions = []
        
        # Analyze current schedule
        schedule_density = context.get("schedule_density", 0.5)
        
        if schedule_density > 0.8:
            suggestions.append({
                "type": "time_management",
                "title": "Schedule Optimization",
                "message": "Your schedule looks packed. Consider blocking time for focused work.",
                "action": "schedule_focus_time",
                "priority": 0.8
            })
        
        # Check for long meetings
        long_meetings = context.get("long_meetings", [])
        if long_meetings:
            suggestions.append({
                "type": "time_management",
                "title": "Meeting Efficiency",
                "message": f"You have {len(long_meetings)} meetings over 1 hour. Consider agenda optimization.",
                "action": "optimize_meetings",
                "priority": 0.7
            })
        
        # Suggest break times
        continuous_work_hours = context.get("continuous_work_hours", 0)
        if continuous_work_hours > 3:
            suggestions.append({
                "type": "time_management",
                "title": "Break Reminder",
                "message": "You've been working for over 3 hours. Consider taking a break.",
                "action": "schedule_break",
                "priority": 0.6
            })
        
        return suggestions
    
    async def _generate_productivity_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate productivity improvement suggestions"""
        suggestions = []
        
        # Analyze task completion patterns
        completion_rate = context.get("task_completion_rate", 0.7)
        
        if completion_rate < 0.6:
            suggestions.append({
                "type": "productivity",
                "title": "Task Management",
                "message": "Your task completion rate is below average. Consider breaking tasks into smaller chunks.",
                "action": "optimize_task_breakdown",
                "priority": 0.8
            })
        
        # Check for context switching
        context_switches = context.get("context_switches", 0)
        if context_switches > 10:
            suggestions.append({
                "type": "productivity",
                "title": "Focus Improvement",
                "message": "High context switching detected. Consider time-blocking similar tasks.",
                "action": "reduce_context_switching",
                "priority": 0.7
            })
        
        # Suggest automation opportunities
        repetitive_tasks = context.get("repetitive_tasks", [])
        if repetitive_tasks:
            suggestions.append({
                "type": "productivity",
                "title": "Automation Opportunity",
                "message": f"Found {len(repetitive_tasks)} repetitive tasks that could be automated.",
                "action": "create_automation",
                "priority": 0.6
            })
        
        return suggestions
    
    async def _generate_communication_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate communication improvement suggestions"""
        suggestions = []
        
        # Check email response time
        avg_response_time = context.get("avg_email_response_time", 24)  # hours
        
        if avg_response_time > 48:
            suggestions.append({
                "type": "communication",
                "title": "Email Response Time",
                "message": "Your average email response time is over 48 hours. Consider setting up auto-responses.",
                "action": "improve_email_response",
                "priority": 0.7
            })
        
        # Check for pending follow-ups
        pending_followups = context.get("pending_followups", [])
        if pending_followups:
            suggestions.append({
                "type": "communication",
                "title": "Follow-up Reminders",
                "message": f"You have {len(pending_followups)} pending follow-ups.",
                "action": "schedule_followups",
                "priority": 0.8
            })
        
        # Suggest communication optimization
        meeting_frequency = context.get("meeting_frequency", 0)
        if meeting_frequency > 20:  # per week
            suggestions.append({
                "type": "communication",
                "title": "Meeting Optimization",
                "message": "High meeting frequency detected. Consider consolidating or async alternatives.",
                "action": "optimize_communication",
                "priority": 0.6
            })
        
        return suggestions
    
    async def _get_current_context(self) -> Dict[str, Any]:
        """Get current user context for suggestions"""
        now = datetime.utcnow()
        
        # Get calendar context
        calendar_events = await self._get_upcoming_calendar_events(hours=24)
        schedule_density = len(calendar_events) / 8  # Assuming 8-hour workday
        
        # Get email context
        recent_emails = await self._get_recent_emails(hours=24)
        unread_count = len([e for e in recent_emails if not e.get("read", False)])
        
        # Get task context
        pending_tasks = await self._get_pending_tasks()
        completion_rate = await self._calculate_task_completion_rate()
        
        # Get pattern context
        work_patterns = await self._get_user_pattern("work_habits")
        
        context = {
            "timestamp": now,
            "schedule_density": min(schedule_density, 1.0),
            "unread_emails": unread_count,
            "pending_tasks": len(pending_tasks),
            "task_completion_rate": completion_rate,
            "work_patterns": work_patterns,
            "long_meetings": [e for e in calendar_events if self._get_event_duration(e) > 60],
            "continuous_work_hours": work_patterns.get("avg_continuous_work_hours", 0) if work_patterns else 0
        }
        
        return context
    
    async def _store_suggestion(self, suggestion: Dict[str, Any]):
        """Store proactive suggestion"""
        suggestion["created_at"] = datetime.utcnow()
        suggestion["status"] = "pending"
        
        await self.suggestions.insert_one(suggestion)
    
    async def _send_proactive_notification(self, suggestion: Dict[str, Any]):
        """Send proactive notification to user"""
        notification = {
            "type": "proactive_suggestion",
            "title": suggestion["title"],
            "message": suggestion["message"],
            "action": suggestion.get("action"),
            "priority": suggestion.get("priority", 0.5),
            "created_at": datetime.utcnow(),
            "read": False
        }
        
        await self.notifications.insert_one(notification)
        logger.info(f"Sent proactive notification: {suggestion['title']}")
    
    async def _store_user_pattern(self, pattern_type: str, pattern_data: Dict[str, Any]):
        """Store user behavior pattern"""
        pattern = {
            "type": pattern_type,
            "data": pattern_data,
            "analyzed_at": datetime.utcnow()
        }
        
        await self.user_patterns.update_one(
            {"type": pattern_type},
            {"$set": pattern},
            upsert=True
        )
    
    async def _get_user_pattern(self, pattern_type: str) -> Optional[Dict[str, Any]]:
        """Get user behavior pattern"""
        doc = await self.user_patterns.find_one({"type": pattern_type})
        return doc.get("data") if doc else None
    
    # Helper methods for data retrieval
    async def _get_upcoming_calendar_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get upcoming calendar events"""
        # Mock implementation - would integrate with calendar service
        return []
    
    async def _get_recent_emails(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent emails"""
        # Mock implementation - would integrate with email service
        return []
    
    async def _get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get pending tasks"""
        # Mock implementation - would integrate with task service
        return []
    
    async def _calculate_task_completion_rate(self) -> float:
        """Calculate task completion rate"""
        # Mock implementation
        return 0.75
    
    async def _get_event_duration(self, event: Dict[str, Any]) -> int:
        """Get event duration in minutes"""
        start = datetime.fromisoformat(event["start_time"])
        end = datetime.fromisoformat(event["end_time"])
        return int((end - start).total_seconds() / 60)
    
    # Placeholder methods for various proactive actions
    async def _suggest_meeting_preparation(self, event: Dict[str, Any]):
        """Suggest meeting preparation"""
        pass
    
    async def _suggest_material_preparation(self, event: Dict[str, Any]):
        """Suggest material preparation"""
        pass
    
    async def _suggest_agenda_creation(self, event: Dict[str, Any]):
        """Suggest agenda creation"""
        pass
    
    async def _suggest_travel_planning(self, event: Dict[str, Any]):
        """Suggest travel planning"""
        pass
    
    async def _classify_email_action(self, email: Dict[str, Any], keyword: str) -> str:
        """Classify email action type"""
        return "general_action"
    
    async def _suggest_email_action(self, email: Dict[str, Any], action_type: str):
        """Suggest email action"""
        pass
    
    async def _suggest_response_needed(self, email: Dict[str, Any]):
        """Suggest response needed"""
        pass
    
    async def _suggest_attachment_review(self, email: Dict[str, Any]):
        """Suggest attachment review"""
        pass
