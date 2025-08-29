
"""
Task Manager Agent - Specialized for project planning, scheduling, and deadline tracking
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from loguru import logger

from .base_specialized_agent import BaseSpecializedAgent

class TaskManagerAgent(BaseSpecializedAgent):
    """Specialized agent for task and project management"""
    
    def _initialize_specialized_capabilities(self):
        """Initialize task management specific capabilities"""
        
        # Task management tools
        self.add_specialized_tool(
            "create_project",
            self._create_project,
            "Create a new project with tasks and timeline"
        )
        
        self.add_specialized_tool(
            "schedule_task",
            self._schedule_task,
            "Schedule a task with deadline and dependencies"
        )
        
        self.add_specialized_tool(
            "track_progress",
            self._track_progress,
            "Track progress on tasks and projects"
        )
        
        self.add_specialized_tool(
            "estimate_time",
            self._estimate_time,
            "Estimate time required for tasks"
        )
        
        # Initialize project storage
        self.store_specialized_memory("projects", {})
        self.store_specialized_memory("tasks", {})
        self.store_specialized_memory("schedules", {})
    
    def get_supported_task_types(self) -> List[str]:
        """Get supported task management task types"""
        return [
            "project_planning",
            "task_scheduling", 
            "deadline_tracking",
            "progress_monitoring",
            "time_estimation",
            "resource_allocation"
        ]
    
    def get_task_type_keywords(self, task_type: str) -> List[str]:
        """Get keywords for each task type"""
        keywords_map = {
            "project_planning": ["project", "plan", "planning", "organize", "structure"],
            "task_scheduling": ["schedule", "timeline", "deadline", "due date", "calendar"],
            "deadline_tracking": ["deadline", "due", "overdue", "track", "monitor"],
            "progress_monitoring": ["progress", "status", "update", "completion", "done"],
            "time_estimation": ["estimate", "time", "duration", "how long", "effort"],
            "resource_allocation": ["resource", "assign", "allocate", "team", "capacity"]
        }
        return keywords_map.get(task_type, [])
    
    def get_specialized_prompt_additions(self) -> str:
        """Get task management specific prompt additions"""
        return """
SPECIALIZED TASK MANAGEMENT CAPABILITIES:

You are an expert project manager and task organizer with the following specialized skills:

1. PROJECT PLANNING:
   - Break down complex projects into manageable tasks
   - Create realistic timelines and milestones
   - Identify dependencies and critical paths
   - Suggest optimal task sequencing

2. TASK SCHEDULING:
   - Create detailed schedules with deadlines
   - Account for resource availability and constraints
   - Suggest buffer time for unexpected delays
   - Optimize for efficiency and productivity

3. PROGRESS TRACKING:
   - Monitor task completion status
   - Identify bottlenecks and delays
   - Suggest corrective actions
   - Provide progress reports and updates

4. TIME ESTIMATION:
   - Estimate task duration based on complexity
   - Account for skill level and experience
   - Consider potential obstacles and risks
   - Provide confidence intervals for estimates

5. RESOURCE MANAGEMENT:
   - Allocate team members to appropriate tasks
   - Balance workload across resources
   - Identify skill gaps and training needs
   - Optimize resource utilization

Always provide structured, actionable plans with clear timelines, dependencies, and success criteria.
"""
    
    async def process_specialized_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process task management specific tasks"""
        task_type = task['type']
        message = task['message']
        context = task.get('context', {})
        
        try:
            if task_type == "project_planning":
                return await self._handle_project_planning(message, context)
            elif task_type == "task_scheduling":
                return await self._handle_task_scheduling(message, context)
            elif task_type == "deadline_tracking":
                return await self._handle_deadline_tracking(message, context)
            elif task_type == "progress_monitoring":
                return await self._handle_progress_monitoring(message, context)
            elif task_type == "time_estimation":
                return await self._handle_time_estimation(message, context)
            elif task_type == "resource_allocation":
                return await self._handle_resource_allocation(message, context)
            else:
                return await self._handle_general_task_management(message, context)
                
        except Exception as e:
            logger.error(f"Task management processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'task_type': task_type
            }
    
    async def _handle_project_planning(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle project planning requests"""
        
        # Use LLM to analyze project requirements
        planning_prompt = f"""
As a project management expert, analyze this project request and create a comprehensive project plan:

Request: {message}
Context: {json.dumps(context, indent=2)}

Please provide:
1. Project overview and objectives
2. Key deliverables and milestones
3. Task breakdown structure
4. Estimated timeline
5. Resource requirements
6. Risk assessment
7. Success criteria

Format your response as a structured project plan.
"""
        
        response = await self.llm_service.generate_response(
            prompt=planning_prompt,
            system_prompt=self.get_specialized_prompt_additions(),
            model="llama3.2:3b"
        )
        
        # Create project record
        project_id = f"proj_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        project_data = {
            'id': project_id,
            'name': message[:100],
            'description': message,
            'plan': response['content'],
            'created_at': datetime.utcnow().isoformat(),
            'status': 'planning'
        }
        
        # Store project
        projects = self.get_specialized_memory("projects") or {}
        projects[project_id] = project_data
        self.store_specialized_memory("projects", projects)
        
        return {
            'success': True,
            'response': response['content'],
            'project_id': project_id,
            'task_type': 'project_planning',
            'metadata': {
                'project_created': True,
                'planning_time': response.get('processing_time', 0)
            }
        }
    
    async def _handle_task_scheduling(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle task scheduling requests"""
        
        scheduling_prompt = f"""
As a scheduling expert, create a detailed schedule for this request:

Request: {message}
Context: {json.dumps(context, indent=2)}

Please provide:
1. Task list with priorities
2. Detailed timeline with dates
3. Dependencies between tasks
4. Resource assignments
5. Buffer time for risks
6. Critical path analysis
7. Schedule optimization suggestions

Format as a practical, actionable schedule.
"""
        
        response = await self.llm_service.generate_response(
            prompt=scheduling_prompt,
            system_prompt=self.get_specialized_prompt_additions(),
            model="llama3.2:3b"
        )
        
        # Create schedule record
        schedule_id = f"sched_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        schedule_data = {
            'id': schedule_id,
            'description': message,
            'schedule': response['content'],
            'created_at': datetime.utcnow().isoformat(),
            'status': 'active'
        }
        
        # Store schedule
        schedules = self.get_specialized_memory("schedules") or {}
        schedules[schedule_id] = schedule_data
        self.store_specialized_memory("schedules", schedules)
        
        return {
            'success': True,
            'response': response['content'],
            'schedule_id': schedule_id,
            'task_type': 'task_scheduling'
        }
    
    async def _handle_deadline_tracking(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle deadline tracking requests"""
        
        # Get current projects and schedules
        projects = self.get_specialized_memory("projects") or {}
        schedules = self.get_specialized_memory("schedules") or {}
        
        tracking_prompt = f"""
As a deadline tracking expert, analyze the current status and provide tracking insights:

Request: {message}
Current Projects: {json.dumps(list(projects.keys()), indent=2)}
Current Schedules: {json.dumps(list(schedules.keys()), indent=2)}
Context: {json.dumps(context, indent=2)}

Please provide:
1. Upcoming deadlines (next 7 days)
2. Overdue items
3. At-risk tasks
4. Progress status
5. Recommended actions
6. Priority adjustments needed

Focus on actionable deadline management insights.
"""
        
        response = await self.llm_service.generate_response(
            prompt=tracking_prompt,
            system_prompt=self.get_specialized_prompt_additions(),
            model="llama3.2:3b"
        )
        
        return {
            'success': True,
            'response': response['content'],
            'task_type': 'deadline_tracking',
            'metadata': {
                'projects_tracked': len(projects),
                'schedules_tracked': len(schedules)
            }
        }
    
    async def _handle_progress_monitoring(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle progress monitoring requests"""
        
        projects = self.get_specialized_memory("projects") or {}
        
        monitoring_prompt = f"""
As a progress monitoring expert, provide comprehensive progress analysis:

Request: {message}
Active Projects: {json.dumps({k: v.get('name', k) for k, v in projects.items()}, indent=2)}
Context: {json.dumps(context, indent=2)}

Please provide:
1. Overall progress summary
2. Completed milestones
3. Current bottlenecks
4. Team performance insights
5. Schedule adherence
6. Quality metrics
7. Recommendations for improvement

Provide actionable progress insights and next steps.
"""
        
        response = await self.llm_service.generate_response(
            prompt=monitoring_prompt,
            system_prompt=self.get_specialized_prompt_additions(),
            model="llama3.2:3b"
        )
        
        return {
            'success': True,
            'response': response['content'],
            'task_type': 'progress_monitoring'
        }
    
    async def _handle_time_estimation(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle time estimation requests"""
        
        estimation_prompt = f"""
As a time estimation expert, provide detailed time estimates:

Request: {message}
Context: {json.dumps(context, indent=2)}

Please provide:
1. Task breakdown for estimation
2. Base time estimates
3. Complexity factors
4. Risk adjustments
5. Confidence levels
6. Best/worst case scenarios
7. Estimation methodology used

Provide realistic, well-justified time estimates.
"""
        
        response = await self.llm_service.generate_response(
            prompt=estimation_prompt,
            system_prompt=self.get_specialized_prompt_additions(),
            model="llama3.2:3b"
        )
        
        return {
            'success': True,
            'response': response['content'],
            'task_type': 'time_estimation'
        }
    
    async def _handle_resource_allocation(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle resource allocation requests"""
        
        allocation_prompt = f"""
As a resource allocation expert, provide optimal resource assignment:

Request: {message}
Context: {json.dumps(context, indent=2)}

Please provide:
1. Resource requirements analysis
2. Skill matching recommendations
3. Workload balancing strategy
4. Capacity planning
5. Training needs identification
6. Alternative resource options
7. Optimization suggestions

Focus on practical resource allocation solutions.
"""
        
        response = await self.llm_service.generate_response(
            prompt=allocation_prompt,
            system_prompt=self.get_specialized_prompt_additions(),
            model="llama3.2:3b"
        )
        
        return {
            'success': True,
            'response': response['content'],
            'task_type': 'resource_allocation'
        }
    
    async def _handle_general_task_management(self, message: str, context: Dict) -> Dict[str, Any]:
        """Handle general task management requests"""
        
        response = await self.llm_service.generate_response(
            prompt=message,
            system_prompt=self.get_specialized_prompt_additions(),
            context=json.dumps(context, indent=2),
            model="llama3.2:3b"
        )
        
        return {
            'success': True,
            'response': response['content'],
            'task_type': 'general_task_management'
        }
    
    # Specialized tool implementations
    async def _create_project(self, project_name: str, description: str, **kwargs) -> Dict[str, Any]:
        """Create a new project"""
        project_id = f"proj_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        project_data = {
            'id': project_id,
            'name': project_name,
            'description': description,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'active',
            'tasks': [],
            'milestones': [],
            **kwargs
        }
        
        projects = self.get_specialized_memory("projects") or {}
        projects[project_id] = project_data
        self.store_specialized_memory("projects", projects)
        
        return {'project_id': project_id, 'status': 'created'}
    
    async def _schedule_task(self, task_name: str, deadline: str, **kwargs) -> Dict[str, Any]:
        """Schedule a new task"""
        task_id = f"task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        task_data = {
            'id': task_id,
            'name': task_name,
            'deadline': deadline,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'scheduled',
            **kwargs
        }
        
        tasks = self.get_specialized_memory("tasks") or {}
        tasks[task_id] = task_data
        self.store_specialized_memory("tasks", tasks)
        
        return {'task_id': task_id, 'status': 'scheduled'}
    
    async def _track_progress(self, project_id: str) -> Dict[str, Any]:
        """Track progress on a project"""
        projects = self.get_specialized_memory("projects") or {}
        
        if project_id not in projects:
            return {'error': 'Project not found'}
        
        project = projects[project_id]
        
        # Calculate progress metrics
        total_tasks = len(project.get('tasks', []))
        completed_tasks = len([t for t in project.get('tasks', []) if t.get('status') == 'completed'])
        
        progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            'project_id': project_id,
            'progress_percentage': progress_percentage,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'status': project.get('status')
        }
    
    async def _estimate_time(self, task_description: str, complexity: str = "medium") -> Dict[str, Any]:
        """Estimate time for a task"""
        
        # Simple estimation logic (could be enhanced with ML)
        base_hours = {
            'simple': 2,
            'medium': 8,
            'complex': 24,
            'very_complex': 80
        }
        
        estimated_hours = base_hours.get(complexity.lower(), 8)
        
        # Add buffer based on complexity
        buffer_multiplier = {
            'simple': 1.2,
            'medium': 1.5,
            'complex': 2.0,
            'very_complex': 2.5
        }
        
        buffered_hours = estimated_hours * buffer_multiplier.get(complexity.lower(), 1.5)
        
        return {
            'task_description': task_description,
            'complexity': complexity,
            'base_estimate_hours': estimated_hours,
            'buffered_estimate_hours': buffered_hours,
            'confidence': 'medium'
        }
