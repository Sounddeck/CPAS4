
"""
Task Delegator for Multi-Agent Task Assignment and Management
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from loguru import logger
import uuid

from .message_bus import MessageBus, Message, MessageType, MessagePriority

class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class TaskAssignment:
    """Task assignment structure"""
    task_id: str
    requester_id: str
    assigned_agent_id: Optional[str]
    task_type: str
    description: str
    requirements: Dict[str, Any]
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for field in ['created_at', 'assigned_at', 'started_at', 'completed_at', 'deadline']:
            if data[field]:
                data[field] = data[field].isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskAssignment':
        """Create from dictionary"""
        # Convert ISO strings back to datetime
        for field in ['created_at', 'assigned_at', 'started_at', 'completed_at', 'deadline']:
            if data.get(field):
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)

class TaskDelegator:
    """Manages task delegation and assignment across multiple agents"""
    
    def __init__(self, message_bus: MessageBus, agent_registry, database):
        self.message_bus = message_bus
        self.agent_registry = agent_registry
        self.db = database
        self.collection_name = "task_assignments"
        
        # Task management
        self.active_tasks: Dict[str, TaskAssignment] = {}
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.agent_workloads: Dict[str, int] = {}
        
        # Task routing and assignment strategies
        self.assignment_strategies = {
            'round_robin': self._round_robin_assignment,
            'capability_based': self._capability_based_assignment,
            'workload_balanced': self._workload_balanced_assignment,
            'priority_based': self._priority_based_assignment
        }
        
        # Task monitoring
        self.task_timeouts: Dict[str, asyncio.Task] = {}
        self.assignment_history: List[Dict[str, Any]] = []
        
        # Background tasks
        self.task_processor = None
        self.timeout_monitor = None
        
        logger.info("Task Delegator initialized")
    
    async def start(self):
        """Start task delegation services"""
        # Start task processing
        self.task_processor = asyncio.create_task(self._process_task_queue())
        
        # Start timeout monitoring
        self.timeout_monitor = asyncio.create_task(self._monitor_task_timeouts())
        
        logger.info("Task Delegator services started")
    
    async def stop(self):
        """Stop task delegation services"""
        if self.task_processor:
            self.task_processor.cancel()
        
        if self.timeout_monitor:
            self.timeout_monitor.cancel()
        
        # Cancel all timeout tasks
        for timeout_task in self.task_timeouts.values():
            timeout_task.cancel()
        
        logger.info("Task Delegator services stopped")
    
    async def submit_task(self, 
                         requester_id: str,
                         task_type: str,
                         description: str,
                         requirements: Dict[str, Any],
                         priority: TaskPriority = TaskPriority.NORMAL,
                         deadline: Optional[datetime] = None,
                         dependencies: Optional[List[str]] = None) -> str:
        """Submit a new task for delegation"""
        
        task_id = str(uuid.uuid4())
        
        task_assignment = TaskAssignment(
            task_id=task_id,
            requester_id=requester_id,
            assigned_agent_id=None,
            task_type=task_type,
            description=description,
            requirements=requirements,
            priority=priority,
            status=TaskStatus.PENDING,
            created_at=datetime.utcnow(),
            deadline=deadline,
            dependencies=dependencies or []
        )
        
        # Store task
        self.active_tasks[task_id] = task_assignment
        await self._store_task_assignment(task_assignment)
        
        # Add to queue for processing
        priority_value = self._get_priority_value(priority)
        await self.task_queue.put((priority_value, datetime.utcnow(), task_assignment))
        
        logger.info(f"Task {task_id} submitted by {requester_id}")
        return task_id
    
    async def assign_task(self, task_id: str, agent_id: str, force: bool = False) -> bool:
        """Manually assign a task to a specific agent"""
        
        if task_id not in self.active_tasks:
            logger.error(f"Task {task_id} not found")
            return False
        
        task = self.active_tasks[task_id]
        
        # Check if task is already assigned
        if task.assigned_agent_id and not force:
            logger.warning(f"Task {task_id} already assigned to {task.assigned_agent_id}")
            return False
        
        # Check if agent is available
        if not force:
            available_agents = await self.agent_registry.get_available_agents()
            if agent_id not in available_agents:
                logger.warning(f"Agent {agent_id} not available for task assignment")
                return False
        
        # Assign task
        task.assigned_agent_id = agent_id
        task.assigned_at = datetime.utcnow()
        task.status = TaskStatus.ASSIGNED
        
        # Update agent workload
        self.agent_workloads[agent_id] = self.agent_workloads.get(agent_id, 0) + 1
        
        # Send task to agent
        success = await self._send_task_to_agent(task)
        
        if success:
            await self._update_task_assignment(task)
            logger.info(f"Task {task_id} assigned to agent {agent_id}")
        else:
            # Revert assignment on failure
            task.assigned_agent_id = None
            task.assigned_at = None
            task.status = TaskStatus.PENDING
            self.agent_workloads[agent_id] = max(0, self.agent_workloads.get(agent_id, 0) - 1)
        
        return success
    
    async def update_task_status(self, task_id: str, status: TaskStatus, 
                                result: Optional[Dict[str, Any]] = None,
                                error_message: Optional[str] = None) -> bool:
        """Update task status"""
        
        if task_id not in self.active_tasks:
            return False
        
        task = self.active_tasks[task_id]
        old_status = task.status
        
        task.status = status
        
        if status == TaskStatus.IN_PROGRESS and not task.started_at:
            task.started_at = datetime.utcnow()
        
        elif status == TaskStatus.COMPLETED:
            task.completed_at = datetime.utcnow()
            task.result = result
            
            # Update agent workload
            if task.assigned_agent_id:
                self.agent_workloads[task.assigned_agent_id] = \
                    max(0, self.agent_workloads.get(task.assigned_agent_id, 0) - 1)
        
        elif status == TaskStatus.FAILED:
            task.error_message = error_message
            task.retry_count += 1
            
            # Update agent workload
            if task.assigned_agent_id:
                self.agent_workloads[task.assigned_agent_id] = \
                    max(0, self.agent_workloads.get(task.assigned_agent_id, 0) - 1)
            
            # Retry if possible
            if task.retry_count <= task.max_retries:
                await self._retry_task(task)
        
        # Update database
        await self._update_task_assignment(task)
        
        # Notify requester of status change
        await self._notify_task_status_change(task, old_status)
        
        logger.info(f"Task {task_id} status updated: {old_status.value} -> {status.value}")
        return True
    
    async def cancel_task(self, task_id: str, reason: str = "Cancelled by user") -> bool:
        """Cancel a task"""
        
        if task_id not in self.active_tasks:
            return False
        
        task = self.active_tasks[task_id]
        
        # Cancel timeout if exists
        if task_id in self.task_timeouts:
            self.task_timeouts[task_id].cancel()
            del self.task_timeouts[task_id]
        
        # Update task status
        task.status = TaskStatus.CANCELLED
        task.error_message = reason
        
        # Update agent workload
        if task.assigned_agent_id:
            self.agent_workloads[task.assigned_agent_id] = \
                max(0, self.agent_workloads.get(task.assigned_agent_id, 0) - 1)
            
            # Notify agent of cancellation
            await self._notify_agent_task_cancelled(task)
        
        await self._update_task_assignment(task)
        
        logger.info(f"Task {task_id} cancelled: {reason}")
        return True
    
    async def get_task_status(self, task_id: str) -> Optional[TaskAssignment]:
        """Get task status and details"""
        return self.active_tasks.get(task_id)
    
    async def get_agent_tasks(self, agent_id: str) -> List[TaskAssignment]:
        """Get all tasks assigned to an agent"""
        return [task for task in self.active_tasks.values() 
                if task.assigned_agent_id == agent_id]
    
    async def get_pending_tasks(self) -> List[TaskAssignment]:
        """Get all pending tasks"""
        return [task for task in self.active_tasks.values() 
                if task.status == TaskStatus.PENDING]
    
    async def get_delegation_statistics(self) -> Dict[str, Any]:
        """Get task delegation statistics"""
        
        total_tasks = len(self.active_tasks)
        
        # Count by status
        status_counts = {}
        for task in self.active_tasks.values():
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count by priority
        priority_counts = {}
        for task in self.active_tasks.values():
            priority = task.priority.value
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Agent workload distribution
        workload_distribution = self.agent_workloads.copy()
        
        # Average completion time
        completed_tasks = [task for task in self.active_tasks.values() 
                          if task.status == TaskStatus.COMPLETED and task.completed_at and task.created_at]
        
        avg_completion_time = 0
        if completed_tasks:
            total_time = sum((task.completed_at - task.created_at).total_seconds() 
                           for task in completed_tasks)
            avg_completion_time = total_time / len(completed_tasks)
        
        return {
            'total_tasks': total_tasks,
            'status_distribution': status_counts,
            'priority_distribution': priority_counts,
            'agent_workloads': workload_distribution,
            'queue_size': self.task_queue.qsize(),
            'average_completion_time_seconds': avg_completion_time,
            'total_assignments': len(self.assignment_history)
        }
    
    def _get_priority_value(self, priority: TaskPriority) -> int:
        """Convert priority to numeric value for queue ordering"""
        priority_values = {
            TaskPriority.URGENT: 1,
            TaskPriority.HIGH: 2,
            TaskPriority.NORMAL: 3,
            TaskPriority.LOW: 4
        }
        return priority_values.get(priority, 3)
    
    async def _process_task_queue(self):
        """Background task to process the task queue"""
        while True:
            try:
                # Get next task from queue
                priority_value, timestamp, task = await self.task_queue.get()
                
                # Check if task is still pending
                if task.task_id not in self.active_tasks or \
                   self.active_tasks[task.task_id].status != TaskStatus.PENDING:
                    continue
                
                # Check dependencies
                if not await self._check_task_dependencies(task):
                    # Re-queue task for later
                    await asyncio.sleep(5)
                    await self.task_queue.put((priority_value, timestamp, task))
                    continue
                
                # Find suitable agent
                agent_id = await self._find_suitable_agent(task)
                
                if agent_id:
                    await self.assign_task(task.task_id, agent_id)
                else:
                    # No suitable agent found, re-queue
                    await asyncio.sleep(10)
                    await self.task_queue.put((priority_value, timestamp, task))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Task queue processing error: {e}")
                await asyncio.sleep(1)
    
    async def _find_suitable_agent(self, task: TaskAssignment) -> Optional[str]:
        """Find the most suitable agent for a task"""
        
        # Get available agents
        available_agents = await self.agent_registry.get_available_agents(
            capability=task.requirements.get('capability'),
            category=task.requirements.get('category')
        )
        
        if not available_agents:
            return None
        
        # Use assignment strategy
        strategy = task.requirements.get('assignment_strategy', 'capability_based')
        assignment_func = self.assignment_strategies.get(strategy, self._capability_based_assignment)
        
        return await assignment_func(task, available_agents)
    
    async def _capability_based_assignment(self, task: TaskAssignment, available_agents: List[str]) -> Optional[str]:
        """Assign based on agent capabilities"""
        
        # Score agents based on capability match
        agent_scores = {}
        
        for agent_id in available_agents:
            agent_info = await self.agent_registry.get_agent_info(agent_id)
            if not agent_info:
                continue
            
            score = 0
            
            # Check capability match
            required_capabilities = task.requirements.get('capabilities', [])
            agent_capabilities = agent_info.get('capabilities', [])
            
            for req_cap in required_capabilities:
                if req_cap in agent_capabilities:
                    score += 10
            
            # Check category match
            if task.requirements.get('category') == agent_info.get('category'):
                score += 5
            
            # Consider workload (lower is better)
            workload = self.agent_workloads.get(agent_id, 0)
            score -= workload
            
            agent_scores[agent_id] = score
        
        # Return agent with highest score
        if agent_scores:
            return max(agent_scores.items(), key=lambda x: x[1])[0]
        
        return available_agents[0] if available_agents else None
    
    async def _workload_balanced_assignment(self, task: TaskAssignment, available_agents: List[str]) -> Optional[str]:
        """Assign to agent with lowest workload"""
        
        if not available_agents:
            return None
        
        # Find agent with minimum workload
        min_workload = float('inf')
        best_agent = None
        
        for agent_id in available_agents:
            workload = self.agent_workloads.get(agent_id, 0)
            if workload < min_workload:
                min_workload = workload
                best_agent = agent_id
        
        return best_agent
    
    async def _round_robin_assignment(self, task: TaskAssignment, available_agents: List[str]) -> Optional[str]:
        """Round-robin assignment"""
        
        if not available_agents:
            return None
        
        # Simple round-robin based on assignment history
        assignment_count = len(self.assignment_history)
        return available_agents[assignment_count % len(available_agents)]
    
    async def _priority_based_assignment(self, task: TaskAssignment, available_agents: List[str]) -> Optional[str]:
        """Assign based on task priority and agent performance"""
        
        # For high priority tasks, prefer agents with better performance
        if task.priority in [TaskPriority.HIGH, TaskPriority.URGENT]:
            # Get agent performance metrics
            best_agent = None
            best_score = -1
            
            for agent_id in available_agents:
                # Get performance history
                performance_history = await self.agent_registry.get_agent_performance_history(agent_id)
                
                if performance_history:
                    # Calculate success rate
                    recent_metrics = performance_history[-10:]  # Last 10 entries
                    success_rate = sum(1 for m in recent_metrics if m.get('status') == 'completed') / len(recent_metrics)
                    
                    # Consider workload
                    workload_penalty = self.agent_workloads.get(agent_id, 0) * 0.1
                    score = success_rate - workload_penalty
                    
                    if score > best_score:
                        best_score = score
                        best_agent = agent_id
            
            return best_agent or available_agents[0]
        
        # For normal/low priority, use workload balancing
        return await self._workload_balanced_assignment(task, available_agents)
    
    async def _check_task_dependencies(self, task: TaskAssignment) -> bool:
        """Check if task dependencies are satisfied"""
        
        for dep_task_id in task.dependencies:
            if dep_task_id in self.active_tasks:
                dep_task = self.active_tasks[dep_task_id]
                if dep_task.status != TaskStatus.COMPLETED:
                    return False
        
        return True
    
    async def _send_task_to_agent(self, task: TaskAssignment) -> bool:
        """Send task assignment to agent"""
        
        try:
            message = Message(
                id=str(uuid.uuid4()),
                sender_id="task_delegator",
                recipient_id=task.assigned_agent_id,
                message_type=MessageType.TASK_REQUEST,
                priority=MessagePriority.NORMAL,
                content={
                    'task_id': task.task_id,
                    'task_type': task.task_type,
                    'description': task.description,
                    'requirements': task.requirements,
                    'priority': task.priority.value,
                    'deadline': task.deadline.isoformat() if task.deadline else None
                },
                timestamp=datetime.utcnow(),
                requires_response=True
            )
            
            success = await self.message_bus.send_message(message)
            
            if success:
                # Set up timeout monitoring
                if task.deadline:
                    timeout_task = asyncio.create_task(
                        self._handle_task_timeout(task.task_id, task.deadline)
                    )
                    self.task_timeouts[task.task_id] = timeout_task
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send task {task.task_id} to agent {task.assigned_agent_id}: {e}")
            return False
    
    async def _retry_task(self, task: TaskAssignment):
        """Retry a failed task"""
        
        logger.info(f"Retrying task {task.task_id} (attempt {task.retry_count}/{task.max_retries})")
        
        # Reset task state
        task.assigned_agent_id = None
        task.assigned_at = None
        task.started_at = None
        task.status = TaskStatus.PENDING
        task.error_message = None
        
        # Re-queue task
        priority_value = self._get_priority_value(task.priority)
        await self.task_queue.put((priority_value, datetime.utcnow(), task))
    
    async def _handle_task_timeout(self, task_id: str, deadline: datetime):
        """Handle task timeout"""
        
        # Wait until deadline
        now = datetime.utcnow()
        if deadline > now:
            await asyncio.sleep((deadline - now).total_seconds())
        
        # Check if task is still active
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            
            if task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
                logger.warning(f"Task {task_id} timed out")
                await self.update_task_status(
                    task_id, 
                    TaskStatus.FAILED, 
                    error_message="Task deadline exceeded"
                )
        
        # Clean up timeout task
        if task_id in self.task_timeouts:
            del self.task_timeouts[task_id]
    
    async def _monitor_task_timeouts(self):
        """Monitor and clean up timeout tasks"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Clean up completed timeout tasks
                completed_timeouts = []
                for task_id, timeout_task in self.task_timeouts.items():
                    if timeout_task.done():
                        completed_timeouts.append(task_id)
                
                for task_id in completed_timeouts:
                    del self.task_timeouts[task_id]
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Timeout monitor error: {e}")
    
    async def _notify_task_status_change(self, task: TaskAssignment, old_status: TaskStatus):
        """Notify requester of task status change"""
        
        try:
            message = Message(
                id=str(uuid.uuid4()),
                sender_id="task_delegator",
                recipient_id=task.requester_id,
                message_type=MessageType.STATUS_UPDATE,
                priority=MessagePriority.NORMAL,
                content={
                    'task_id': task.task_id,
                    'old_status': old_status.value,
                    'new_status': task.status.value,
                    'result': task.result,
                    'error_message': task.error_message
                },
                timestamp=datetime.utcnow()
            )
            
            await self.message_bus.send_message(message)
            
        except Exception as e:
            logger.error(f"Failed to notify status change for task {task.task_id}: {e}")
    
    async def _notify_agent_task_cancelled(self, task: TaskAssignment):
        """Notify agent that task was cancelled"""
        
        if not task.assigned_agent_id:
            return
        
        try:
            message = Message(
                id=str(uuid.uuid4()),
                sender_id="task_delegator",
                recipient_id=task.assigned_agent_id,
                message_type=MessageType.STATUS_UPDATE,
                priority=MessagePriority.NORMAL,
                content={
                    'task_id': task.task_id,
                    'status': 'cancelled',
                    'reason': task.error_message
                },
                timestamp=datetime.utcnow()
            )
            
            await self.message_bus.send_message(message)
            
        except Exception as e:
            logger.error(f"Failed to notify agent of task cancellation: {e}")
    
    async def _store_task_assignment(self, task: TaskAssignment):
        """Store task assignment in database"""
        try:
            await self.db.create_document(self.collection_name, task.to_dict())
        except Exception as e:
            logger.error(f"Failed to store task assignment {task.task_id}: {e}")
    
    async def _update_task_assignment(self, task: TaskAssignment):
        """Update task assignment in database"""
        try:
            await self.db.update_document(self.collection_name, task.task_id, task.to_dict())
        except Exception as e:
            logger.error(f"Failed to update task assignment {task.task_id}: {e}")
