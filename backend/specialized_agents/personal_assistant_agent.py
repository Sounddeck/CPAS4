
"""
Personal Assistant Agent - Specialized for calendar management, reminders, and personal tasks
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from loguru import logger

from .base_specialized_agent import BaseSpecializedAgent

class PersonalAssistantAgent(BaseSpecializedAgent):
    """Specialized agent for personal assistance and task management"""
    
    def _initialize_specialized_capabilities(self):
        """Initialize personal assistant specific capabilities"""
        
        # Personal assistant tools
        self.add_specialized_tool(
            "manage_calendar",
            self._manage_calendar,
            "Manage calendar events and scheduling"
        )
        
        self.add_specialized_tool(
            "set_reminder",
            self._set_reminder,
            "Set reminders and notifications"
        )
        
        self.add_specialized_tool(
            "organize_tasks",
            self._organize_tasks,
            "Organize and prioritize personal tasks"
        )
        
        self.add_specialized_tool(
            "track_habits",
            self._track_habits,
            "Track habits and personal goals"
        )
        
        # Initialize personal storage
        self.store_specialized_memory("calendar_events", {})
        self.store_specialized_memory("reminders", {})
        self.store_specialized_memory("personal_tasks", {})
        self.store_specialized_memory("habits", {})
    
    def get_supported_task_types(self) -> List[str]:
        """Get supported personal assistant task types"""
        return [
            "calendar_management",
            "reminder_setting",
            "task_organization",
            "habit_tracking",
            "personal_planning",
            "goal_setting",
            "time_management",
            "personal_productivity"
        ]
    
    def get_task_type_keywords(self, task_type: str) -> List[str]:
        """Get keywords for each task type"""
        keywords_map = {
            "calendar_management": ["calendar", "schedule", "appointment", "meeting", "event"],
            "reminder_setting": ["remind", "reminder", "alert", "notification", "don't forget"],
            "task_organization": ["task", "todo", "organize", "prioritize", "list"],
            "habit_tracking": ["habit", "routine", "daily", "track", "goal"],
            "personal_planning": ["plan", "planning", "organize", "schedule", "prepare"],
            "goal_setting": ["goal", "objective", "target", "achievement", "milestone"],
            "time_management": ["time", "manage", "schedule", "productivity", "efficiency"],
            "personal_productivity": ["productivity", "efficient", "optimize", "improve", "better"]
        }
        return keywords_map.get(task_type, [])
    
    def get_specialized_prompt_additions(self) -> str:
        """Get personal assistant specific prompt additions"""
        return """
SPECIALIZED PERSONAL ASSISTANT CAPABILITIES:

You are a highly organized and proactive personal assistant with expertise in:

1. CALENDAR MANAGEMENT:
   - Scheduling appointments and meetings
   - Managing conflicts and priorities
   - Time blocking and optimization
   - Travel time considerations
   - Meeting preparation assistance

2. REMINDER & NOTIFICATION SYSTEM:
   - Setting timely reminders
   - Priority-based notifications
   - Recurring reminder management
   - Context-aware alerts
   - Follow-up tracking

3. TASK ORGANIZATION:
   - Task prioritization using various methods
   - Deadline management
   - Project breakdown
   - Progress tracking
   - Productivity optimization

4. PERSONAL PRODUCTIVITY:
   - Habit formation and tracking
   - Goal setting and monitoring
   - Time management strategies
   - Work-life balance optimization
   - Personal development planning

5. PROACTIVE ASSISTANCE:
   - Anticipating needs
   - Suggesting optimizations
   - Identifying patterns
   - Providing insights
   - Streamlining workflows

Your assistance style is:
- Proactive and anticipatory
- Highly organized and systematic
- Respectful of personal preferences
- Focused on efficiency and productivity
- Supportive and encouraging

Always maintain confidentiality and provide personalized, actionable assistance.
"""
    
    async def process_specialized_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process personal assistant specific tasks"""
        task_type = task['type']
        message = task['message']
        context = task.get('context', {})
        
        try:
            if task_type == "calendar_management":
                return await self._handle_calendar_management(message, context)
            elif task_type == "reminder_setting":
                return await self._handle_reminder_setting(message, context)
            elif task_type == "task_organization":
                return await self._handle_task_organization(message, context)
            elif task_type == "habit_tracking":
                return await self._handle_habit_tracking(message, context)
            elif task_type == "personal_planning":
                return await self._handle_personal_planning(message, context)
            elif task_type == "goal_setting":
                return await self._handle_goal_setting(message, context)
            elif task_type == "time_management":
                return await self._handle_time_management(message, context)
            elif task_type == "personal_productivity":
                return await self._handle_personal_productivity(message, context)
            else:
                return await self._handle_general_assistance(message, context)
                
        except Exception as e:
            logger.error(f"Personal assistant processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'task_type': task_type
            }
    
    async def _handle_calendar_management(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle calendar management requests"""
        
        calendar_prompt = f"""
As a calendar management expert, provide comprehensive scheduling assistance:

Calendar Request: {message}
Context: {json.dumps(context, indent=2)}

Please provide:
1. Event scheduling recommendations
2. Time conflict analysis
3. Optimal time slot suggestions
4. Meeting preparation checklist
5. Travel time considerations
6. Buffer time recommendations
7. Calendar optimization tips
8. Follow-up scheduling

Provide practical calendar management with attention to efficiency and balance.
"""
        
        response = await self.llm_service.generate_response(
            prompt=calendar_prompt,
            system_prompt=self.get_specialized_prompt_additions(),
            model="llama3.2:3b"
        )
        
        # Store calendar event
        event_id = f"event_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        event_data = {
            'id': event_id,
            'request': message,
            'recommendations': response['content'],
            'created_at': datetime.utcnow().isoformat(),
            'status': 'planned'
        }
        
        events = self.get_specialized_memory("calendar_events") or {}
        events[event_id] = event_data
        self.store_specialized_memory("calendar_events", events)
        
        return {
            'success': True,
            'response': response['content'],
            'event_id': event_id,
            'task_type': 'calendar_management'
        }
    
    async def _handle_reminder_setting(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle reminder setting requests"""
        
        reminder_prompt = f"""
As a reminder management expert, provide comprehensive reminder assistance:

Reminder Request: {message}
Context: {json.dumps(context, indent=2)}

Please provide:
1. Optimal reminder timing
2. Reminder frequency recommendations
3. Context-appropriate reminder content
4. Priority level assessment
5. Follow-up reminder strategy
6. Reminder delivery method suggestions
7. Escalation procedures
8. Completion tracking

Create effective reminder systems that ensure important tasks aren't forgotten.
"""
        
        response = await self.llm_service.generate_response(
            prompt=reminder_prompt,
            system_prompt=self.get_specialized_prompt_additions(),
            model="llama3.2:3b"
        )
        
        # Store reminder
        reminder_id = f"reminder_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        reminder_data = {
            'id': reminder_id,
            'request': message,
            'reminder_plan': response['content'],
            'created_at': datetime.utcnow().isoformat(),
            'status': 'active'
        }
        
        reminders = self.get_specialized_memory("reminders") or {}
        reminders[reminder_id] = reminder_data
        self.store_specialized_memory("reminders", reminders)
        
        return {
            'success': True,
            'response': response['content'],
            'reminder_id': reminder_id,
            'task_type': 'reminder_setting'
        }
    
    async def _handle_task_organization(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle task organization requests"""
        
        task_prompt = f"""
As a task organization expert, provide comprehensive task management:

Task Organization Request: {message}
Context: {json.dumps(context, indent=2)}

Please provide:
1. Task prioritization using appropriate methods
2. Task breakdown and categorization
3. Deadline and timeline management
4. Resource requirement assessment
5. Progress tracking recommendations
6. Productivity optimization strategies
7. Task delegation opportunities
8. Completion celebration planning

Create organized, actionable task management systems.
"""
        
        response = await self.llm_service.generate_response(
            prompt=task_prompt,
            system_prompt=self.get_specialized_prompt_additions(),
            model="llama3.2:3b"
        )
        
        # Store task organization
        task_id = f"task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        task_data = {
            'id': task_id,
            'request': message,
            'organization_plan': response['content'],
            'created_at': datetime.utcnow().isoformat(),
            'status': 'organized'
        }
        
        tasks = self.get_specialized_memory("personal_tasks") or {}
        tasks[task_id] = task_data
        self.store_specialized_memory("personal_tasks", tasks)
        
        return {
            'success': True,
            'response': response['content'],
            'task_id': task_id,
            'task_type': 'task_organization'
        }
    
    async def _handle_habit_tracking(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle habit tracking requests"""
        
        habit_prompt = f"""
As a habit tracking expert, provide comprehensive habit development assistance:

Habit Tracking Request: {message}
Context: {json.dumps(context, indent=2)}

Please provide:
1. Habit formation strategy
2. Tracking methodology and tools
3. Motivation and accountability systems
4. Progress measurement techniques
5. Obstacle identification and solutions
6. Habit stacking opportunities
7. Reward system design
8. Long-term sustainability planning

Create effective habit tracking systems that promote lasting change.
"""
        
        response = await self.llm_service.generate_response(
            prompt=habit_prompt,
            system_prompt=self.get_specialized_prompt_additions(),
            model="llama3.2:3b"
        )
        
        # Store habit tracking
        habit_id = f"habit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        habit_data = {
            'id': habit_id,
            'request': message,
            'tracking_plan': response['content'],
            'created_at': datetime.utcnow().isoformat(),
            'status': 'tracking'
        }
        
        habits = self.get_specialized_memory("habits") or {}
        habits[habit_id] = habit_data
        self.store_specialized_memory("habits", habits)
        
        return {
            'success': True,
            'response': response['content'],
            'habit_id': habit_id,
            'task_type': 'habit_tracking'
        }
    
    async def _handle_personal_planning(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle personal planning requests"""
        
        planning_prompt = f"""
As a personal planning expert, provide comprehensive life planning assistance:

Personal Planning Request: {message}
Context: {json.dumps(context, indent=2)}

Please provide:
1. Goal identification and clarification
2. Strategic planning approach
3. Timeline and milestone development
4. Resource allocation planning
5. Risk assessment and mitigation
6. Progress monitoring systems
7. Flexibility and adaptation strategies
8. Success celebration planning

Create comprehensive personal plans that are realistic and achievable.
"""
        
        response = await self.llm_service.generate_response(
            prompt=planning_prompt,
            system_prompt=self.get_specialized_prompt_additions(),
            model="llama3.2:3b"
        )
        
        return {
            'success': True,
            'response': response['content'],
            'task_type': 'personal_planning'
        }
    
    async def _handle_goal_setting(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle goal setting requests"""
        
        goal_prompt = f"""
As a goal setting expert, provide comprehensive goal achievement assistance:

Goal Setting Request: {message}
Context: {json.dumps(context, indent=2)}

Please provide:
1. SMART goal formulation
2. Goal hierarchy and prioritization
3. Action plan development
4. Milestone and checkpoint creation
5. Accountability system design
6. Progress tracking methods
7. Obstacle anticipation and solutions
8. Motivation maintenance strategies

Create clear, achievable goals with robust support systems.
"""
        
        response = await self.llm_service.generate_response(
            prompt=goal_prompt,
            system_prompt=self.get_specialized_prompt_additions(),
            model="llama3.2:3b"
        )
        
        return {
            'success': True,
            'response': response['content'],
            'task_type': 'goal_setting'
        }
    
    async def _handle_time_management(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle time management requests"""
        
        time_prompt = f"""
As a time management expert, provide comprehensive productivity assistance:

Time Management Request: {message}
Context: {json.dumps(context, indent=2)}

Please provide:
1. Time audit and analysis
2. Priority matrix application
3. Time blocking strategies
4. Productivity technique recommendations
5. Distraction management solutions
6. Energy management alignment
7. Work-life balance optimization
8. Continuous improvement methods

Create effective time management systems that maximize productivity and well-being.
"""
        
        response = await self.llm_service.generate_response(
            prompt=time_prompt,
            system_prompt=self.get_specialized_prompt_additions(),
            model="llama3.2:3b"
        )
        
        return {
            'success': True,
            'response': response['content'],
            'task_type': 'time_management'
        }
    
    async def _handle_personal_productivity(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle personal productivity requests"""
        
        productivity_prompt = f"""
As a personal productivity expert, provide comprehensive efficiency assistance:

Productivity Request: {message}
Context: {json.dumps(context, indent=2)}

Please provide:
1. Productivity assessment and analysis
2. Workflow optimization recommendations
3. Tool and system suggestions
4. Habit and routine improvements
5. Environment optimization
6. Energy and focus management
7. Stress reduction strategies
8. Continuous improvement planning

Create personalized productivity systems that enhance effectiveness and satisfaction.
"""
        
        response = await self.llm_service.generate_response(
            prompt=productivity_prompt,
            system_prompt=self.get_specialized_prompt_additions(),
            model="llama3.2:3b"
        )
        
        return {
            'success': True,
            'response': response['content'],
            'task_type': 'personal_productivity'
        }
    
    async def _handle_general_assistance(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle general personal assistance requests"""
        
        response = await self.llm_service.generate_response(
            prompt=message,
            system_prompt=self.get_specialized_prompt_additions(),
            context=json.dumps(context, indent=2),
            model="llama3.2:3b"
        )
        
        return {
            'success': True,
            'response': response['content'],
            'task_type': 'general_assistance'
        }
    
    # Specialized tool implementations
    async def _manage_calendar(self, event_title: str, date_time: str, duration: int = 60, **kwargs) -> Dict[str, Any]:
        """Manage calendar events"""
        event_id = f"event_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        event_data = {
            'id': event_id,
            'title': event_title,
            'date_time': date_time,
            'duration_minutes': duration,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'scheduled',
            **kwargs
        }
        
        events = self.get_specialized_memory("calendar_events") or {}
        events[event_id] = event_data
        self.store_specialized_memory("calendar_events", events)
        
        return {'event_id': event_id, 'status': 'scheduled'}
    
    async def _set_reminder(self, reminder_text: str, remind_at: str, **kwargs) -> Dict[str, Any]:
        """Set a reminder"""
        reminder_id = f"reminder_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        reminder_data = {
            'id': reminder_id,
            'text': reminder_text,
            'remind_at': remind_at,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'active',
            **kwargs
        }
        
        reminders = self.get_specialized_memory("reminders") or {}
        reminders[reminder_id] = reminder_data
        self.store_specialized_memory("reminders", reminders)
        
        return {'reminder_id': reminder_id, 'status': 'set'}
    
    async def _organize_tasks(self, task_list: List[str], priority_method: str = "eisenhower", **kwargs) -> Dict[str, Any]:
        """Organize and prioritize tasks"""
        organization_id = f"org_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Simple task organization (would be enhanced with actual prioritization algorithms)
        organized_tasks = {
            'high_priority': task_list[:len(task_list)//3] if task_list else [],
            'medium_priority': task_list[len(task_list)//3:2*len(task_list)//3] if task_list else [],
            'low_priority': task_list[2*len(task_list)//3:] if task_list else []
        }
        
        organization_data = {
            'id': organization_id,
            'original_tasks': task_list,
            'organized_tasks': organized_tasks,
            'priority_method': priority_method,
            'created_at': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        tasks = self.get_specialized_memory("personal_tasks") or {}
        tasks[organization_id] = organization_data
        self.store_specialized_memory("personal_tasks", tasks)
        
        return {'organization_id': organization_id, 'tasks_organized': len(task_list)}
    
    async def _track_habits(self, habit_name: str, frequency: str = "daily", **kwargs) -> Dict[str, Any]:
        """Track a habit"""
        habit_id = f"habit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        habit_data = {
            'id': habit_id,
            'name': habit_name,
            'frequency': frequency,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'tracking',
            'streak': 0,
            **kwargs
        }
        
        habits = self.get_specialized_memory("habits") or {}
        habits[habit_id] = habit_data
        self.store_specialized_memory("habits", habits)
        
        return {'habit_id': habit_id, 'status': 'tracking'}
