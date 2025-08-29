
"""
Task Manager Agent - Specialized agent for task management and productivity
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from models.agent import Agent, AgentCapability, AgentPersonality
from services.agent_core import AgentCore

class TaskManagerAgent(AgentCore):
    """Specialized agent for task management, scheduling, and productivity optimization"""
    
    def __init__(self, agent_id: str, db):
        super().__init__(agent_id, db)
        self.agent_type = "task_manager"
        self.capabilities = [
            AgentCapability(
                name="task_creation",
                description="Create and organize tasks from various inputs",
                confidence=0.95
            ),
            AgentCapability(
                name="priority_management",
                description="Analyze and set task priorities based on context",
                confidence=0.90
            ),
            AgentCapability(
                name="schedule_optimization",
                description="Optimize schedules and suggest time blocks",
                confidence=0.85
            ),
            AgentCapability(
                name="deadline_tracking",
                description="Monitor deadlines and send proactive reminders",
                confidence=0.92
            ),
            AgentCapability(
                name="productivity_analysis",
                description="Analyze productivity patterns and suggest improvements",
                confidence=0.88
            )
        ]
        
        self.personality = AgentPersonality(
            traits={
                "organized": 0.95,
                "proactive": 0.90,
                "detail_oriented": 0.88,
                "efficient": 0.92,
                "supportive": 0.85
            },
            communication_style="professional_helpful",
            decision_making="analytical_systematic"
        )
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process task management requests"""
        task_type = task_data.get("type", "general")
        
        if task_type == "create_task":
            return await self._create_task(task_data)
        elif task_type == "prioritize_tasks":
            return await self._prioritize_tasks(task_data)
        elif task_type == "schedule_optimization":
            return await self._optimize_schedule(task_data)
        elif task_type == "deadline_analysis":
            return await self._analyze_deadlines(task_data)
        elif task_type == "productivity_report":
            return await self._generate_productivity_report(task_data)
        elif task_type == "task_breakdown":
            return await self._break_down_complex_task(task_data)
        else:
            return await self._general_task_assistance(task_data)
    
    async def _create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create tasks from various inputs (emails, meetings, conversations)"""
        source = task_data.get("source", "manual")
        content = task_data.get("content", "")
        context = task_data.get("context", {})
        
        # Analyze content to extract task information
        task_analysis = await self._analyze_task_content(content, context)
        
        # Create structured task
        task = {
            "title": task_analysis.get("title", "New Task"),
            "description": task_analysis.get("description", ""),
            "priority": task_analysis.get("priority", "medium"),
            "estimated_duration": task_analysis.get("duration", 60),  # minutes
            "deadline": task_analysis.get("deadline"),
            "category": task_analysis.get("category", "general"),
            "subtasks": task_analysis.get("subtasks", []),
            "dependencies": task_analysis.get("dependencies", []),
            "source": source,
            "created_at": datetime.utcnow(),
            "status": "pending"
        }
        
        # Store task in memory
        await self.store_memory({
            "type": "task_created",
            "task": task,
            "source": source,
            "analysis": task_analysis
        })
        
        logger.info(f"Task Manager created task: {task['title']}")
        
        return {
            "success": True,
            "task": task,
            "analysis": task_analysis,
            "recommendations": await self._get_task_recommendations(task)
        }
    
    async def _prioritize_tasks(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and prioritize a list of tasks"""
        tasks = task_data.get("tasks", [])
        criteria = task_data.get("criteria", {})
        
        prioritized_tasks = []
        
        for task in tasks:
            priority_score = await self._calculate_priority_score(task, criteria)
            task["priority_score"] = priority_score
            task["priority_reasoning"] = await self._explain_priority(task, priority_score)
            prioritized_tasks.append(task)
        
        # Sort by priority score
        prioritized_tasks.sort(key=lambda x: x["priority_score"], reverse=True)
        
        # Generate priority recommendations
        recommendations = await self._generate_priority_recommendations(prioritized_tasks)
        
        return {
            "success": True,
            "prioritized_tasks": prioritized_tasks,
            "recommendations": recommendations,
            "priority_matrix": await self._create_priority_matrix(prioritized_tasks)
        }
    
    async def _optimize_schedule(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize schedule and suggest time blocks"""
        tasks = task_data.get("tasks", [])
        calendar_events = task_data.get("calendar_events", [])
        preferences = task_data.get("preferences", {})
        
        # Analyze available time slots
        available_slots = await self._find_available_time_slots(calendar_events, preferences)
        
        # Match tasks to optimal time slots
        schedule_optimization = await self._match_tasks_to_slots(tasks, available_slots, preferences)
        
        # Generate schedule recommendations
        recommendations = {
            "optimal_schedule": schedule_optimization["schedule"],
            "time_blocks": schedule_optimization["time_blocks"],
            "productivity_tips": await self._get_productivity_tips(tasks, preferences),
            "schedule_conflicts": schedule_optimization["conflicts"],
            "buffer_time_suggestions": schedule_optimization["buffers"]
        }
        
        return {
            "success": True,
            "schedule_optimization": recommendations,
            "efficiency_score": schedule_optimization["efficiency_score"]
        }
    
    async def _analyze_deadlines(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze deadlines and provide proactive recommendations"""
        tasks = task_data.get("tasks", [])
        current_time = datetime.utcnow()
        
        deadline_analysis = {
            "overdue": [],
            "due_today": [],
            "due_this_week": [],
            "upcoming": [],
            "at_risk": []
        }
        
        for task in tasks:
            if not task.get("deadline"):
                continue
                
            deadline = datetime.fromisoformat(task["deadline"])
            time_until_deadline = deadline - current_time
            
            if time_until_deadline.total_seconds() < 0:
                deadline_analysis["overdue"].append(task)
            elif time_until_deadline.days == 0:
                deadline_analysis["due_today"].append(task)
            elif time_until_deadline.days <= 7:
                deadline_analysis["due_this_week"].append(task)
            else:
                deadline_analysis["upcoming"].append(task)
            
            # Check if task is at risk based on estimated duration
            estimated_hours = task.get("estimated_duration", 60) / 60
            if time_until_deadline.total_seconds() / 3600 < estimated_hours * 1.5:
                deadline_analysis["at_risk"].append(task)
        
        # Generate proactive recommendations
        recommendations = await self._generate_deadline_recommendations(deadline_analysis)
        
        return {
            "success": True,
            "deadline_analysis": deadline_analysis,
            "recommendations": recommendations,
            "urgency_matrix": await self._create_urgency_matrix(tasks)
        }
    
    async def _generate_productivity_report(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive productivity analysis report"""
        time_period = task_data.get("time_period", "week")  # day, week, month
        tasks = task_data.get("completed_tasks", [])
        
        # Analyze productivity metrics
        metrics = await self._calculate_productivity_metrics(tasks, time_period)
        
        # Identify patterns
        patterns = await self._identify_productivity_patterns(tasks, time_period)
        
        # Generate insights and recommendations
        insights = await self._generate_productivity_insights(metrics, patterns)
        
        report = {
            "period": time_period,
            "metrics": metrics,
            "patterns": patterns,
            "insights": insights,
            "recommendations": await self._get_productivity_recommendations(metrics, patterns),
            "goals": await self._suggest_productivity_goals(metrics),
            "generated_at": datetime.utcnow()
        }
        
        return {
            "success": True,
            "productivity_report": report
        }
    
    async def _break_down_complex_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Break down complex tasks into manageable subtasks"""
        task = task_data.get("task", {})
        complexity_level = task_data.get("complexity_level", "medium")
        
        # Analyze task complexity
        complexity_analysis = await self._analyze_task_complexity(task)
        
        # Generate subtask breakdown
        subtasks = await self._generate_subtasks(task, complexity_analysis)
        
        # Create task dependencies
        dependencies = await self._identify_task_dependencies(subtasks)
        
        # Estimate timeline
        timeline = await self._estimate_task_timeline(subtasks, dependencies)
        
        breakdown = {
            "original_task": task,
            "complexity_analysis": complexity_analysis,
            "subtasks": subtasks,
            "dependencies": dependencies,
            "timeline": timeline,
            "milestones": await self._identify_milestones(subtasks, timeline),
            "risk_assessment": await self._assess_task_risks(task, subtasks)
        }
        
        return {
            "success": True,
            "task_breakdown": breakdown
        }
    
    async def _analyze_task_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content to extract task information using LLM"""
        prompt = f"""
        Analyze the following content and extract task information:
        
        Content: {content}
        Context: {context}
        
        Extract:
        1. Task title (concise, actionable)
        2. Description (detailed explanation)
        3. Priority (high, medium, low) based on urgency and importance
        4. Estimated duration in minutes
        5. Potential deadline (if mentioned or can be inferred)
        6. Category (work, personal, learning, etc.)
        7. Possible subtasks
        8. Dependencies on other tasks
        
        Respond in JSON format.
        """
        
        response = await self.llm_service.generate(
            prompt=prompt,
            model="llama3.2:3b",
            max_tokens=500
        )
        
        try:
            import json
            return json.loads(response.get("response", "{}"))
        except:
            return {
                "title": "Extracted Task",
                "description": content[:200],
                "priority": "medium",
                "duration": 60,
                "category": "general"
            }
    
    async def _calculate_priority_score(self, task: Dict[str, Any], criteria: Dict[str, Any]) -> float:
        """Calculate priority score based on multiple criteria"""
        score = 0.0
        
        # Deadline urgency (0-40 points)
        if task.get("deadline"):
            deadline = datetime.fromisoformat(task["deadline"])
            days_until = (deadline - datetime.utcnow()).days
            if days_until <= 0:
                score += 40
            elif days_until <= 1:
                score += 35
            elif days_until <= 3:
                score += 25
            elif days_until <= 7:
                score += 15
            else:
                score += 5
        
        # Importance level (0-30 points)
        importance_map = {"high": 30, "medium": 20, "low": 10}
        score += importance_map.get(task.get("importance", "medium"), 20)
        
        # Impact assessment (0-20 points)
        impact_map = {"high": 20, "medium": 15, "low": 10}
        score += impact_map.get(task.get("impact", "medium"), 15)
        
        # Dependencies (0-10 points)
        if task.get("dependencies"):
            score += len(task["dependencies"]) * 2
        
        return min(score, 100.0)  # Cap at 100
    
    async def _find_available_time_slots(self, calendar_events: List[Dict], preferences: Dict[str, Any]) -> List[Dict]:
        """Find available time slots in calendar"""
        # Implementation for finding free time slots
        # This would integrate with calendar service
        
        work_hours_start = preferences.get("work_hours_start", 9)  # 9 AM
        work_hours_end = preferences.get("work_hours_end", 17)    # 5 PM
        
        # Generate available slots (simplified implementation)
        available_slots = []
        current_time = datetime.utcnow().replace(hour=work_hours_start, minute=0, second=0, microsecond=0)
        end_time = current_time.replace(hour=work_hours_end)
        
        while current_time < end_time:
            slot_end = current_time + timedelta(hours=1)
            
            # Check if slot conflicts with calendar events
            conflicts = False
            for event in calendar_events:
                event_start = datetime.fromisoformat(event["start_time"])
                event_end = datetime.fromisoformat(event["end_time"])
                
                if (current_time < event_end and slot_end > event_start):
                    conflicts = True
                    break
            
            if not conflicts:
                available_slots.append({
                    "start": current_time,
                    "end": slot_end,
                    "duration": 60  # minutes
                })
            
            current_time = slot_end
        
        return available_slots
    
    async def _get_task_recommendations(self, task: Dict[str, Any]) -> List[str]:
        """Generate recommendations for a task"""
        recommendations = []
        
        if task.get("priority") == "high":
            recommendations.append("Consider breaking this high-priority task into smaller chunks")
        
        if task.get("estimated_duration", 0) > 120:  # > 2 hours
            recommendations.append("This task might benefit from being split into subtasks")
        
        if not task.get("deadline"):
            recommendations.append("Consider setting a deadline to maintain momentum")
        
        return recommendations
    
    async def _general_task_assistance(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general task management queries"""
        query = task_data.get("query", "")
        context = task_data.get("context", {})
        
        # Use LLM for general task management advice
        prompt = f"""
        As a task management expert, provide helpful advice for this query:
        
        Query: {query}
        Context: {context}
        
        Provide practical, actionable advice focused on productivity and organization.
        """
        
        response = await self.llm_service.generate(
            prompt=prompt,
            model="llama3.2:3b",
            max_tokens=300
        )
        
        return {
            "success": True,
            "advice": response.get("response", ""),
            "suggestions": [
                "Break large tasks into smaller, manageable pieces",
                "Use time-blocking to focus on important work",
                "Review and adjust priorities regularly",
                "Set realistic deadlines and buffer time"
            ]
        }
    
    # Additional helper methods would be implemented here...
    async def _explain_priority(self, task: Dict[str, Any], score: float) -> str:
        """Explain why a task received its priority score"""
        return f"Priority score {score:.1f} based on deadline urgency, importance level, and dependencies"
    
    async def _generate_priority_recommendations(self, tasks: List[Dict]) -> List[str]:
        """Generate recommendations based on prioritized tasks"""
        return [
            "Focus on high-priority tasks first",
            "Consider delegating lower-priority items",
            "Block time for important but not urgent tasks"
        ]
    
    async def _create_priority_matrix(self, tasks: List[Dict]) -> Dict[str, List]:
        """Create Eisenhower matrix categorization"""
        matrix = {
            "urgent_important": [],
            "not_urgent_important": [],
            "urgent_not_important": [],
            "not_urgent_not_important": []
        }
        
        for task in tasks:
            urgency = "urgent" if task.get("priority_score", 0) > 70 else "not_urgent"
            importance = "important" if task.get("importance") == "high" else "not_important"
            key = f"{urgency}_{importance}"
            matrix[key].append(task)
        
        return matrix
