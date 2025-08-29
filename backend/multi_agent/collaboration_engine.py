
"""
Collaboration Engine for Multi-Agent Coordination
Facilitates collaboration between agents for complex tasks
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
from .task_delegator import TaskDelegator, TaskAssignment, TaskStatus

class CollaborationType(str, Enum):
    """Types of collaboration"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    PEER_TO_PEER = "peer_to_peer"
    PIPELINE = "pipeline"

class CollaborationStatus(str, Enum):
    """Collaboration status"""
    PLANNING = "planning"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class CollaborationSession:
    """Collaboration session between multiple agents"""
    session_id: str
    initiator_id: str
    participant_ids: List[str]
    collaboration_type: CollaborationType
    objective: str
    context: Dict[str, Any]
    status: CollaborationStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    tasks: List[str] = None  # Task IDs
    results: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tasks is None:
            self.tasks = []
        if self.results is None:
            self.results = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        if self.started_at:
            data['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CollaborationSession':
        """Create from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('started_at'):
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        if data.get('completed_at'):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        return cls(**data)

class CollaborationEngine:
    """Manages multi-agent collaboration sessions"""
    
    def __init__(self, message_bus: MessageBus, task_delegator: TaskDelegator, 
                 agent_registry, database):
        self.message_bus = message_bus
        self.task_delegator = task_delegator
        self.agent_registry = agent_registry
        self.db = database
        self.collection_name = "collaboration_sessions"
        
        # Active collaborations
        self.active_sessions: Dict[str, CollaborationSession] = {}
        self.session_monitors: Dict[str, asyncio.Task] = {}
        
        # Collaboration patterns and strategies
        self.collaboration_patterns = {
            CollaborationType.SEQUENTIAL: self._execute_sequential_collaboration,
            CollaborationType.PARALLEL: self._execute_parallel_collaboration,
            CollaborationType.HIERARCHICAL: self._execute_hierarchical_collaboration,
            CollaborationType.PEER_TO_PEER: self._execute_peer_to_peer_collaboration,
            CollaborationType.PIPELINE: self._execute_pipeline_collaboration
        }
        
        # Performance tracking
        self.collaboration_metrics = {
            'total_sessions': 0,
            'successful_sessions': 0,
            'failed_sessions': 0,
            'average_duration': 0,
            'agent_participation': {}
        }
        
        logger.info("Collaboration Engine initialized")
    
    async def start(self):
        """Start collaboration engine services"""
        # Subscribe to collaboration messages
        await self.message_bus.subscribe("collaboration_engine", MessageType.COLLABORATION_REQUEST)
        await self.message_bus.subscribe("collaboration_engine", MessageType.COLLABORATION_RESPONSE)
        
        logger.info("Collaboration Engine services started")
    
    async def stop(self):
        """Stop collaboration engine services"""
        # Cancel all session monitors
        for monitor_task in self.session_monitors.values():
            monitor_task.cancel()
        
        # Unsubscribe from messages
        await self.message_bus.unsubscribe("collaboration_engine", MessageType.COLLABORATION_REQUEST)
        await self.message_bus.unsubscribe("collaboration_engine", MessageType.COLLABORATION_RESPONSE)
        
        logger.info("Collaboration Engine services stopped")
    
    async def initiate_collaboration(self,
                                   initiator_id: str,
                                   participant_ids: List[str],
                                   collaboration_type: CollaborationType,
                                   objective: str,
                                   context: Dict[str, Any]) -> str:
        """Initiate a new collaboration session"""
        
        session_id = str(uuid.uuid4())
        
        session = CollaborationSession(
            session_id=session_id,
            initiator_id=initiator_id,
            participant_ids=participant_ids,
            collaboration_type=collaboration_type,
            objective=objective,
            context=context,
            status=CollaborationStatus.PLANNING,
            created_at=datetime.utcnow()
        )
        
        # Store session
        self.active_sessions[session_id] = session
        await self._store_collaboration_session(session)
        
        # Send collaboration invitations
        await self._send_collaboration_invitations(session)
        
        # Start session monitoring
        monitor_task = asyncio.create_task(self._monitor_collaboration_session(session_id))
        self.session_monitors[session_id] = monitor_task
        
        # Update metrics
        self.collaboration_metrics['total_sessions'] += 1
        
        logger.info(f"Collaboration session {session_id} initiated by {initiator_id}")
        return session_id
    
    async def join_collaboration(self, session_id: str, agent_id: str) -> bool:
        """Agent joins a collaboration session"""
        
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        
        if agent_id not in session.participant_ids:
            return False
        
        # Update agent participation metrics
        if agent_id not in self.collaboration_metrics['agent_participation']:
            self.collaboration_metrics['agent_participation'][agent_id] = 0
        self.collaboration_metrics['agent_participation'][agent_id] += 1
        
        # Notify other participants
        await self._notify_agent_joined(session, agent_id)
        
        logger.info(f"Agent {agent_id} joined collaboration session {session_id}")
        return True
    
    async def start_collaboration(self, session_id: str) -> bool:
        """Start executing a collaboration session"""
        
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        
        if session.status != CollaborationStatus.PLANNING:
            return False
        
        # Update session status
        session.status = CollaborationStatus.ACTIVE
        session.started_at = datetime.utcnow()
        
        await self._update_collaboration_session(session)
        
        # Execute collaboration based on type
        collaboration_func = self.collaboration_patterns.get(session.collaboration_type)
        if collaboration_func:
            asyncio.create_task(collaboration_func(session))
        
        logger.info(f"Collaboration session {session_id} started")
        return True
    
    async def complete_collaboration(self, session_id: str, results: Dict[str, Any]) -> bool:
        """Complete a collaboration session"""
        
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        
        # Update session
        session.status = CollaborationStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        session.results = results
        
        await self._update_collaboration_session(session)
        
        # Notify all participants
        await self._notify_collaboration_completed(session)
        
        # Clean up
        await self._cleanup_collaboration_session(session_id)
        
        # Update metrics
        self.collaboration_metrics['successful_sessions'] += 1
        duration = (session.completed_at - session.started_at).total_seconds()
        self._update_average_duration(duration)
        
        logger.info(f"Collaboration session {session_id} completed successfully")
        return True
    
    async def cancel_collaboration(self, session_id: str, reason: str = "Cancelled") -> bool:
        """Cancel a collaboration session"""
        
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        
        # Update session
        session.status = CollaborationStatus.CANCELLED
        session.results = {'cancellation_reason': reason}
        
        await self._update_collaboration_session(session)
        
        # Notify all participants
        await self._notify_collaboration_cancelled(session, reason)
        
        # Clean up
        await self._cleanup_collaboration_session(session_id)
        
        # Update metrics
        self.collaboration_metrics['failed_sessions'] += 1
        
        logger.info(f"Collaboration session {session_id} cancelled: {reason}")
        return True
    
    async def get_active_collaborations(self) -> List[CollaborationSession]:
        """Get all active collaboration sessions"""
        return list(self.active_sessions.values())
    
    async def get_collaboration_history(self, limit: int = 50) -> List[CollaborationSession]:
        """Get collaboration session history"""
        try:
            sessions_data = await self.db.find_documents(
                self.collection_name,
                {},
                limit=limit,
                sort=[('created_at', -1)]
            )
            
            return [CollaborationSession.from_dict(data) for data in sessions_data]
            
        except Exception as e:
            logger.error(f"Failed to get collaboration history: {e}")
            return []
    
    async def get_collaboration_metrics(self) -> Dict[str, Any]:
        """Get collaboration metrics and statistics"""
        
        active_sessions = len(self.active_sessions)
        
        # Session type distribution
        type_distribution = {}
        for session in self.active_sessions.values():
            session_type = session.collaboration_type.value
            type_distribution[session_type] = type_distribution.get(session_type, 0) + 1
        
        return {
            'active_sessions': active_sessions,
            'session_type_distribution': type_distribution,
            **self.collaboration_metrics
        }
    
    async def _execute_sequential_collaboration(self, session: CollaborationSession):
        """Execute sequential collaboration pattern"""
        
        try:
            results = {}
            
            # Execute tasks sequentially
            for i, agent_id in enumerate(session.participant_ids):
                task_description = f"Sequential task {i+1} for {session.objective}"
                
                # Create task for agent
                task_id = await self.task_delegator.submit_task(
                    requester_id=session.initiator_id,
                    task_type="collaboration_task",
                    description=task_description,
                    requirements={
                        'collaboration_session': session.session_id,
                        'sequence_number': i + 1,
                        'previous_results': results
                    }
                )
                
                session.tasks.append(task_id)
                
                # Assign task to specific agent
                await self.task_delegator.assign_task(task_id, agent_id)
                
                # Wait for task completion
                task_completed = await self._wait_for_task_completion(task_id, timeout=300)
                
                if task_completed:
                    task_assignment = await self.task_delegator.get_task_status(task_id)
                    if task_assignment and task_assignment.result:
                        results[agent_id] = task_assignment.result
                else:
                    # Task failed or timed out
                    await self.cancel_collaboration(session.session_id, f"Task {task_id} failed")
                    return
            
            # Complete collaboration
            await self.complete_collaboration(session.session_id, results)
            
        except Exception as e:
            logger.error(f"Sequential collaboration failed for session {session.session_id}: {e}")
            await self.cancel_collaboration(session.session_id, f"Execution error: {str(e)}")
    
    async def _execute_parallel_collaboration(self, session: CollaborationSession):
        """Execute parallel collaboration pattern"""
        
        try:
            # Create tasks for all agents simultaneously
            task_ids = []
            
            for i, agent_id in enumerate(session.participant_ids):
                task_description = f"Parallel task {i+1} for {session.objective}"
                
                task_id = await self.task_delegator.submit_task(
                    requester_id=session.initiator_id,
                    task_type="collaboration_task",
                    description=task_description,
                    requirements={
                        'collaboration_session': session.session_id,
                        'parallel_execution': True
                    }
                )
                
                task_ids.append(task_id)
                session.tasks.append(task_id)
                
                # Assign task to specific agent
                await self.task_delegator.assign_task(task_id, agent_id)
            
            # Wait for all tasks to complete
            completion_tasks = [
                self._wait_for_task_completion(task_id, timeout=300)
                for task_id in task_ids
            ]
            
            completed = await asyncio.gather(*completion_tasks, return_exceptions=True)
            
            # Collect results
            results = {}
            all_successful = True
            
            for i, (task_id, agent_id) in enumerate(zip(task_ids, session.participant_ids)):
                if completed[i] is True:
                    task_assignment = await self.task_delegator.get_task_status(task_id)
                    if task_assignment and task_assignment.result:
                        results[agent_id] = task_assignment.result
                else:
                    all_successful = False
                    results[agent_id] = {'error': 'Task failed or timed out'}
            
            if all_successful:
                await self.complete_collaboration(session.session_id, results)
            else:
                await self.cancel_collaboration(session.session_id, "Some parallel tasks failed")
            
        except Exception as e:
            logger.error(f"Parallel collaboration failed for session {session.session_id}: {e}")
            await self.cancel_collaboration(session.session_id, f"Execution error: {str(e)}")
    
    async def _execute_hierarchical_collaboration(self, session: CollaborationSession):
        """Execute hierarchical collaboration pattern"""
        
        try:
            # First agent is the coordinator
            coordinator_id = session.participant_ids[0]
            subordinate_ids = session.participant_ids[1:]
            
            # Coordinator creates subtasks
            coordinator_task_id = await self.task_delegator.submit_task(
                requester_id=session.initiator_id,
                task_type="coordination_task",
                description=f"Coordinate hierarchical collaboration for {session.objective}",
                requirements={
                    'collaboration_session': session.session_id,
                    'role': 'coordinator',
                    'subordinates': subordinate_ids
                }
            )
            
            session.tasks.append(coordinator_task_id)
            await self.task_delegator.assign_task(coordinator_task_id, coordinator_id)
            
            # Wait for coordinator to define subtasks
            coordinator_completed = await self._wait_for_task_completion(coordinator_task_id, timeout=180)
            
            if not coordinator_completed:
                await self.cancel_collaboration(session.session_id, "Coordinator task failed")
                return
            
            # Get coordination results
            coordinator_task = await self.task_delegator.get_task_status(coordinator_task_id)
            coordination_plan = coordinator_task.result if coordinator_task else {}
            
            # Execute subordinate tasks
            subordinate_results = {}
            
            for agent_id in subordinate_ids:
                subtask_description = coordination_plan.get(f'{agent_id}_task', f"Subordinate task for {agent_id}")
                
                task_id = await self.task_delegator.submit_task(
                    requester_id=coordinator_id,
                    task_type="subordinate_task",
                    description=subtask_description,
                    requirements={
                        'collaboration_session': session.session_id,
                        'role': 'subordinate',
                        'coordinator': coordinator_id
                    }
                )
                
                session.tasks.append(task_id)
                await self.task_delegator.assign_task(task_id, agent_id)
                
                # Wait for completion
                task_completed = await self._wait_for_task_completion(task_id, timeout=300)
                
                if task_completed:
                    task_assignment = await self.task_delegator.get_task_status(task_id)
                    if task_assignment and task_assignment.result:
                        subordinate_results[agent_id] = task_assignment.result
            
            # Combine results
            final_results = {
                'coordinator': coordination_plan,
                'subordinates': subordinate_results
            }
            
            await self.complete_collaboration(session.session_id, final_results)
            
        except Exception as e:
            logger.error(f"Hierarchical collaboration failed for session {session.session_id}: {e}")
            await self.cancel_collaboration(session.session_id, f"Execution error: {str(e)}")
    
    async def _execute_peer_to_peer_collaboration(self, session: CollaborationSession):
        """Execute peer-to-peer collaboration pattern"""
        
        try:
            # All agents work as equals, sharing information
            results = {}
            
            # Create initial tasks for all agents
            for agent_id in session.participant_ids:
                task_id = await self.task_delegator.submit_task(
                    requester_id=session.initiator_id,
                    task_type="peer_collaboration_task",
                    description=f"Peer collaboration task for {session.objective}",
                    requirements={
                        'collaboration_session': session.session_id,
                        'role': 'peer',
                        'other_peers': [a for a in session.participant_ids if a != agent_id]
                    }
                )
                
                session.tasks.append(task_id)
                await self.task_delegator.assign_task(task_id, agent_id)
            
            # Monitor peer interactions and results
            # (Simplified - would involve more complex peer communication)
            
            # Wait for all peer tasks to complete
            for task_id in session.tasks:
                task_completed = await self._wait_for_task_completion(task_id, timeout=300)
                
                if task_completed:
                    task_assignment = await self.task_delegator.get_task_status(task_id)
                    if task_assignment and task_assignment.result:
                        results[task_assignment.assigned_agent_id] = task_assignment.result
            
            await self.complete_collaboration(session.session_id, results)
            
        except Exception as e:
            logger.error(f"Peer-to-peer collaboration failed for session {session.session_id}: {e}")
            await self.cancel_collaboration(session.session_id, f"Execution error: {str(e)}")
    
    async def _execute_pipeline_collaboration(self, session: CollaborationSession):
        """Execute pipeline collaboration pattern"""
        
        try:
            # Data flows through agents in pipeline fashion
            pipeline_data = session.context.get('initial_data', {})
            
            for i, agent_id in enumerate(session.participant_ids):
                task_description = f"Pipeline stage {i+1} for {session.objective}"
                
                task_id = await self.task_delegator.submit_task(
                    requester_id=session.initiator_id,
                    task_type="pipeline_task",
                    description=task_description,
                    requirements={
                        'collaboration_session': session.session_id,
                        'pipeline_stage': i + 1,
                        'input_data': pipeline_data
                    }
                )
                
                session.tasks.append(task_id)
                await self.task_delegator.assign_task(task_id, agent_id)
                
                # Wait for stage completion
                task_completed = await self._wait_for_task_completion(task_id, timeout=300)
                
                if task_completed:
                    task_assignment = await self.task_delegator.get_task_status(task_id)
                    if task_assignment and task_assignment.result:
                        # Output becomes input for next stage
                        pipeline_data = task_assignment.result
                else:
                    await self.cancel_collaboration(session.session_id, f"Pipeline stage {i+1} failed")
                    return
            
            # Final pipeline result
            final_results = {
                'pipeline_output': pipeline_data,
                'stages_completed': len(session.participant_ids)
            }
            
            await self.complete_collaboration(session.session_id, final_results)
            
        except Exception as e:
            logger.error(f"Pipeline collaboration failed for session {session.session_id}: {e}")
            await self.cancel_collaboration(session.session_id, f"Execution error: {str(e)}")
    
    async def _wait_for_task_completion(self, task_id: str, timeout: int = 300) -> bool:
        """Wait for a task to complete"""
        
        start_time = datetime.utcnow()
        
        while (datetime.utcnow() - start_time).total_seconds() < timeout:
            task_assignment = await self.task_delegator.get_task_status(task_id)
            
            if task_assignment:
                if task_assignment.status == TaskStatus.COMPLETED:
                    return True
                elif task_assignment.status == TaskStatus.FAILED:
                    return False
            
            await asyncio.sleep(5)  # Check every 5 seconds
        
        return False  # Timeout
    
    async def _send_collaboration_invitations(self, session: CollaborationSession):
        """Send collaboration invitations to participants"""
        
        for agent_id in session.participant_ids:
            message = Message(
                id=str(uuid.uuid4()),
                sender_id="collaboration_engine",
                recipient_id=agent_id,
                message_type=MessageType.COLLABORATION_REQUEST,
                priority=MessagePriority.NORMAL,
                content={
                    'session_id': session.session_id,
                    'initiator': session.initiator_id,
                    'collaboration_type': session.collaboration_type.value,
                    'objective': session.objective,
                    'participants': session.participant_ids,
                    'context': session.context
                },
                timestamp=datetime.utcnow(),
                requires_response=True
            )
            
            await self.message_bus.send_message(message)
    
    async def _notify_agent_joined(self, session: CollaborationSession, joined_agent_id: str):
        """Notify other participants that an agent joined"""
        
        for agent_id in session.participant_ids:
            if agent_id != joined_agent_id:
                message = Message(
                    id=str(uuid.uuid4()),
                    sender_id="collaboration_engine",
                    recipient_id=agent_id,
                    message_type=MessageType.COLLABORATION_RESPONSE,
                    priority=MessagePriority.LOW,
                    content={
                        'session_id': session.session_id,
                        'event': 'agent_joined',
                        'joined_agent': joined_agent_id
                    },
                    timestamp=datetime.utcnow()
                )
                
                await self.message_bus.send_message(message)
    
    async def _notify_collaboration_completed(self, session: CollaborationSession):
        """Notify all participants of collaboration completion"""
        
        all_participants = [session.initiator_id] + session.participant_ids
        
        for agent_id in set(all_participants):
            message = Message(
                id=str(uuid.uuid4()),
                sender_id="collaboration_engine",
                recipient_id=agent_id,
                message_type=MessageType.COLLABORATION_RESPONSE,
                priority=MessagePriority.NORMAL,
                content={
                    'session_id': session.session_id,
                    'event': 'collaboration_completed',
                    'results': session.results,
                    'duration_seconds': (session.completed_at - session.started_at).total_seconds()
                },
                timestamp=datetime.utcnow()
            )
            
            await self.message_bus.send_message(message)
    
    async def _notify_collaboration_cancelled(self, session: CollaborationSession, reason: str):
        """Notify all participants of collaboration cancellation"""
        
        all_participants = [session.initiator_id] + session.participant_ids
        
        for agent_id in set(all_participants):
            message = Message(
                id=str(uuid.uuid4()),
                sender_id="collaboration_engine",
                recipient_id=agent_id,
                message_type=MessageType.COLLABORATION_RESPONSE,
                priority=MessagePriority.NORMAL,
                content={
                    'session_id': session.session_id,
                    'event': 'collaboration_cancelled',
                    'reason': reason
                },
                timestamp=datetime.utcnow()
            )
            
            await self.message_bus.send_message(message)
    
    async def _monitor_collaboration_session(self, session_id: str):
        """Monitor a collaboration session"""
        
        try:
            while session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                
                # Check for timeout
                if session.status == CollaborationStatus.ACTIVE:
                    duration = (datetime.utcnow() - session.started_at).total_seconds()
                    max_duration = session.context.get('max_duration_seconds', 3600)  # 1 hour default
                    
                    if duration > max_duration:
                        await self.cancel_collaboration(session_id, "Session timeout")
                        break
                
                # Check if session is stuck
                if session.status == CollaborationStatus.PLANNING:
                    planning_duration = (datetime.utcnow() - session.created_at).total_seconds()
                    if planning_duration > 300:  # 5 minutes
                        await self.cancel_collaboration(session_id, "Planning timeout")
                        break
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Session monitoring error for {session_id}: {e}")
    
    async def _cleanup_collaboration_session(self, session_id: str):
        """Clean up collaboration session resources"""
        
        # Cancel monitoring task
        if session_id in self.session_monitors:
            self.session_monitors[session_id].cancel()
            del self.session_monitors[session_id]
        
        # Remove from active sessions
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    def _update_average_duration(self, duration: float):
        """Update average collaboration duration"""
        
        current_avg = self.collaboration_metrics['average_duration']
        successful_count = self.collaboration_metrics['successful_sessions']
        
        if successful_count == 1:
            self.collaboration_metrics['average_duration'] = duration
        else:
            # Moving average
            self.collaboration_metrics['average_duration'] = \
                (current_avg * (successful_count - 1) + duration) / successful_count
    
    async def _store_collaboration_session(self, session: CollaborationSession):
        """Store collaboration session in database"""
        try:
            await self.db.create_document(self.collection_name, session.to_dict())
        except Exception as e:
            logger.error(f"Failed to store collaboration session {session.session_id}: {e}")
    
    async def _update_collaboration_session(self, session: CollaborationSession):
        """Update collaboration session in database"""
        try:
            await self.db.update_document(self.collection_name, session.session_id, session.to_dict())
        except Exception as e:
            logger.error(f"Failed to update collaboration session {session.session_id}: {e}")
