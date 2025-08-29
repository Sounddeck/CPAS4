
"""
Agent Orchestration Service
Manages coordination between Master Agent and specialized agents
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from loguru import logger
from pydantic import BaseModel

from .master_agent import MasterAgent
from .memory_service import MemoryService
from ..models.agent import Agent


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    DELEGATED = "delegated"


class TaskPriority(Enum):
    """Task priority levels"""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class Task:
    """Task representation for orchestration"""
    id: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    assigned_agent: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    dependencies: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentOrchestrator:
    """
    Central orchestration service for managing all agents
    Coordinates between Master Agent and specialized agents
    """
    
    def __init__(self, master_agent: MasterAgent, memory_service: MemoryService):
        self.master_agent = master_agent
        self.memory_service = memory_service
        
        # Task management
        self.active_tasks: Dict[str, Task] = {}
        self.task_queue: List[Task] = []
        self.completed_tasks: List[Task] = []
        
        # Agent registry
        self.registered_agents: Dict[str, Agent] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}
        self.agent_load: Dict[str, int] = {}
        
        # Orchestration metrics
        self.metrics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_completion_time": 0.0,
            "agent_utilization": {}
        }
        
        # Background task for processing queue
        self._processing_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
    
    async def start(self):
        """Start the orchestration service"""
        logger.info("🎭 Starting Agent Orchestrator...")
        
        # Start background task processing
        self._processing_task = asyncio.create_task(self._process_task_queue())
        
        # Register default agents
        await self._register_default_agents()
        
        logger.info("✅ Agent Orchestrator started successfully")
    
    async def stop(self):
        """Stop the orchestration service"""
        logger.info("🛑 Stopping Agent Orchestrator...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Wait for processing task to complete
        if self._processing_task:
            await self._processing_task
        
        logger.info("✅ Agent Orchestrator stopped")
    
    async def submit_task(
        self, 
        description: str, 
        priority: TaskPriority = TaskPriority.NORMAL,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Submit a new task for processing"""
        
        # Generate unique task ID
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_tasks)}"
        
        # Create task
        task = Task(
            id=task_id,
            description=description,
            priority=priority,
            status=TaskStatus.PENDING,
            context=context or {}
        )
        
        # Add to active tasks and queue
        self.active_tasks[task_id] = task
        self.task_queue.append(task)
        
        # Sort queue by priority
        self.task_queue.sort(key=lambda t: self._priority_weight(t.priority), reverse=True)
        
        # Update metrics
        self.metrics["total_tasks"] += 1
        
        logger.info(f"📝 Task submitted: {task_id} - {description[:50]}...")
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        
        task = self.active_tasks.get(task_id)
        if not task:
            # Check completed tasks
            for completed_task in self.completed_tasks:
                if completed_task.id == task_id:
                    task = completed_task
                    break
        
        if not task:
            return None
        
        return {
            "id": task.id,
            "description": task.description,
            "status": task.status.value,
            "priority": task.priority.value,
            "assigned_agent": task.assigned_agent,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "result": task.result,
            "error": task.error
        }
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or in-progress task"""
        
        task = self.active_tasks.get(task_id)
        if not task:
            return False
        
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            return False
        
        # Remove from queue if pending
        if task.status == TaskStatus.PENDING:
            self.task_queue = [t for t in self.task_queue if t.id != task_id]
        
        # Mark as failed and move to completed
        task.status = TaskStatus.FAILED
        task.error = "Task cancelled by user"
        task.updated_at = datetime.now()
        
        self.completed_tasks.append(task)
        del self.active_tasks[task_id]
        
        logger.info(f"❌ Task cancelled: {task_id}")
        
        return True
    
    async def register_agent(
        self, 
        agent_id: str, 
        agent: Agent, 
        capabilities: List[str]
    ) -> bool:
        """Register a new agent with the orchestrator"""
        
        self.registered_agents[agent_id] = agent
        self.agent_capabilities[agent_id] = capabilities
        self.agent_load[agent_id] = 0
        
        logger.info(f"🤖 Agent registered: {agent_id} with capabilities: {capabilities}")
        
        return True
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the orchestrator"""
        
        if agent_id not in self.registered_agents:
            return False
        
        # Check if agent has active tasks
        active_agent_tasks = [
            task for task in self.active_tasks.values() 
            if task.assigned_agent == agent_id and task.status == TaskStatus.IN_PROGRESS
        ]
        
        if active_agent_tasks:
            logger.warning(f"⚠️ Cannot unregister agent {agent_id}: has {len(active_agent_tasks)} active tasks")
            return False
        
        # Remove agent
        del self.registered_agents[agent_id]
        del self.agent_capabilities[agent_id]
        del self.agent_load[agent_id]
        
        logger.info(f"🗑️ Agent unregistered: {agent_id}")
        
        return True
    
    async def get_orchestration_status(self) -> Dict[str, Any]:
        """Get overall orchestration status"""
        
        return {
            "active_tasks": len(self.active_tasks),
            "queued_tasks": len([t for t in self.active_tasks.values() if t.status == TaskStatus.PENDING]),
            "in_progress_tasks": len([t for t in self.active_tasks.values() if t.status == TaskStatus.IN_PROGRESS]),
            "completed_tasks": len(self.completed_tasks),
            "registered_agents": list(self.registered_agents.keys()),
            "agent_load": self.agent_load.copy(),
            "metrics": self.metrics.copy(),
            "master_agent_status": await self.master_agent.get_status()
        }
    
    async def _process_task_queue(self):
        """Background task to process the task queue"""
        
        while not self._shutdown_event.is_set():
            try:
                # Process pending tasks
                if self.task_queue:
                    task = self.task_queue.pop(0)
                    await self._process_task(task)
                
                # Wait before next iteration
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Error in task queue processing: {e}")
                await asyncio.sleep(5.0)
    
    async def _process_task(self, task: Task):
        """Process a single task"""
        
        try:
            logger.info(f"🔄 Processing task: {task.id}")
            
            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            task.updated_at = datetime.now()
            
            # Prepare request for Master Agent
            request = {
                "input": task.description,
                "context": task.context,
                "priority": task.priority.value,
                "task_id": task.id
            }
            
            # Process through Master Agent
            start_time = datetime.now()
            result = await self.master_agent.process_request(request)
            end_time = datetime.now()
            
            # Update task with result
            task.result = result
            task.status = TaskStatus.COMPLETED if result.get("success") else TaskStatus.FAILED
            task.updated_at = end_time
            
            if not result.get("success"):
                task.error = result.get("error", "Unknown error")
            
            # Update metrics
            processing_time = (end_time - start_time).total_seconds()
            await self._update_metrics(task, processing_time)
            
            # Move to completed tasks
            self.completed_tasks.append(task)
            del self.active_tasks[task.id]
            
            # Store task result in memory
            await self._store_task_memory(task)
            
            logger.info(f"✅ Task completed: {task.id} in {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error processing task {task.id}: {e}")
            
            # Mark task as failed
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.updated_at = datetime.now()
            
            # Move to completed tasks
            self.completed_tasks.append(task)
            del self.active_tasks[task.id]
            
            # Update metrics
            self.metrics["failed_tasks"] += 1
    
    async def _register_default_agents(self):
        """Register the default specialized agents"""
        
        default_agents = {
            "master_agent": {
                "capabilities": ["orchestration", "reasoning", "delegation", "osint"]
            },
            "task_manager": {
                "capabilities": ["task_management", "scheduling", "organization"]
            },
            "research_agent": {
                "capabilities": ["research", "analysis", "information_gathering"]
            },
            "creative_agent": {
                "capabilities": ["content_creation", "writing", "brainstorming"]
            },
            "technical_agent": {
                "capabilities": ["coding", "technical_analysis", "system_administration"]
            },
            "personal_assistant": {
                "capabilities": ["scheduling", "reminders", "personal_organization"]
            }
        }
        
        for agent_id, config in default_agents.items():
            # Create placeholder agent object
            agent = Agent(
                id=agent_id,
                name=agent_id.replace("_", " ").title(),
                description=f"Default {agent_id} for CPAS system",
                capabilities=config["capabilities"]
            )
            
            await self.register_agent(agent_id, agent, config["capabilities"])
    
    def _priority_weight(self, priority: TaskPriority) -> int:
        """Get numeric weight for task priority"""
        
        weights = {
            TaskPriority.URGENT: 4,
            TaskPriority.HIGH: 3,
            TaskPriority.NORMAL: 2,
            TaskPriority.LOW: 1
        }
        
        return weights.get(priority, 2)
    
    async def _update_metrics(self, task: Task, processing_time: float):
        """Update orchestration metrics"""
        
        if task.status == TaskStatus.COMPLETED:
            self.metrics["completed_tasks"] += 1
            
            # Update average completion time
            total_completed = self.metrics["completed_tasks"]
            current_avg = self.metrics["average_completion_time"]
            self.metrics["average_completion_time"] = (
                (current_avg * (total_completed - 1) + processing_time) / total_completed
            )
        
        elif task.status == TaskStatus.FAILED:
            self.metrics["failed_tasks"] += 1
        
        # Update agent utilization if task was assigned
        if task.assigned_agent:
            agent_id = task.assigned_agent
            if agent_id not in self.metrics["agent_utilization"]:
                self.metrics["agent_utilization"][agent_id] = 0
            self.metrics["agent_utilization"][agent_id] += 1
    
    async def _store_task_memory(self, task: Task):
        """Store task execution in memory for learning"""
        
        memory_content = {
            "task_id": task.id,
            "description": task.description,
            "status": task.status.value,
            "processing_time": (task.updated_at - task.created_at).total_seconds(),
            "assigned_agent": task.assigned_agent,
            "result_summary": str(task.result)[:500] if task.result else None,
            "error": task.error
        }
        
        await self.memory_service.store_memory(
            content=json.dumps(memory_content),
            memory_type="task_execution",
            importance=0.6 if task.status == TaskStatus.COMPLETED else 0.3
        )
