
"""
Agent Lifecycle Management System
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger

from .agent_factory import AgentInstance, AgentFactory
from .agent_registry import AgentRegistry
from ..models.agent import AgentStatus

class LifecycleEvent(str, Enum):
    """Agent lifecycle events"""
    CREATED = "created"
    STARTED = "started"
    PAUSED = "paused"
    RESUMED = "resumed"
    STOPPED = "stopped"
    ERROR = "error"
    ARCHIVED = "archived"
    DELETED = "deleted"

class AgentLifecycleManager:
    """Manages the complete lifecycle of agents"""
    
    def __init__(self, agent_factory: AgentFactory, agent_registry: AgentRegistry, database):
        self.agent_factory = agent_factory
        self.agent_registry = agent_registry
        self.db = database
        
        # Lifecycle tracking
        self.lifecycle_history: Dict[str, List[Dict[str, Any]]] = {}
        self.event_handlers: Dict[LifecycleEvent, List[Callable]] = {}
        self.scheduled_tasks: Dict[str, asyncio.Task] = {}
        
        # Health monitoring
        self.health_check_interval = 300  # 5 minutes
        self.health_check_task = None
        
        logger.info("Agent Lifecycle Manager initialized")
    
    async def start_lifecycle_management(self):
        """Start lifecycle management services"""
        # Start health monitoring
        self.health_check_task = asyncio.create_task(self._health_monitor_loop())
        logger.info("Agent lifecycle management started")
    
    async def stop_lifecycle_management(self):
        """Stop lifecycle management services"""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all scheduled tasks
        for task in self.scheduled_tasks.values():
            task.cancel()
        
        logger.info("Agent lifecycle management stopped")
    
    async def create_agent_with_lifecycle(self, 
                                        template_id: str,
                                        agent_name: Optional[str] = None,
                                        custom_config: Optional[Dict[str, Any]] = None,
                                        auto_start: bool = True) -> str:
        """Create agent with full lifecycle management"""
        
        # Create the agent
        agent_id = await self.agent_factory.create_agent(template_id, agent_name, custom_config)
        
        # Record lifecycle event
        await self._record_lifecycle_event(agent_id, LifecycleEvent.CREATED, {
            'template_id': template_id,
            'agent_name': agent_name,
            'auto_start': auto_start
        })
        
        # Register with registry
        agent_instance = await self.agent_factory.get_agent(agent_id)
        if agent_instance:
            await self.agent_registry.register_agent(agent_instance)
        
        # Auto-start if requested
        if auto_start:
            await self.start_agent(agent_id)
        
        # Trigger event handlers
        await self._trigger_event_handlers(LifecycleEvent.CREATED, agent_id)
        
        return agent_id
    
    async def start_agent(self, agent_id: str) -> bool:
        """Start an agent"""
        agent = await self.agent_factory.get_agent(agent_id)
        if not agent:
            return False
        
        try:
            agent.status = AgentStatus.IDLE
            await self.agent_registry.update_agent_status(agent_id, AgentStatus.IDLE)
            
            await self._record_lifecycle_event(agent_id, LifecycleEvent.STARTED)
            await self._trigger_event_handlers(LifecycleEvent.STARTED, agent_id)
            
            logger.info(f"Started agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start agent {agent_id}: {e}")
            await self._handle_agent_error(agent_id, str(e))
            return False
    
    async def pause_agent(self, agent_id: str) -> bool:
        """Pause an agent"""
        agent = await self.agent_factory.get_agent(agent_id)
        if not agent:
            return False
        
        try:
            # Store current status for resume
            previous_status = agent.status
            agent.status = AgentStatus.STOPPED
            agent.working_memory['paused_from_status'] = previous_status.value
            
            await self.agent_registry.update_agent_status(agent_id, AgentStatus.STOPPED)
            
            await self._record_lifecycle_event(agent_id, LifecycleEvent.PAUSED, {
                'previous_status': previous_status.value
            })
            await self._trigger_event_handlers(LifecycleEvent.PAUSED, agent_id)
            
            logger.info(f"Paused agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause agent {agent_id}: {e}")
            return False
    
    async def resume_agent(self, agent_id: str) -> bool:
        """Resume a paused agent"""
        agent = await self.agent_factory.get_agent(agent_id)
        if not agent:
            return False
        
        try:
            # Restore previous status
            previous_status = agent.working_memory.get('paused_from_status', 'idle')
            agent.status = AgentStatus(previous_status)
            
            await self.agent_registry.update_agent_status(agent_id, agent.status)
            
            await self._record_lifecycle_event(agent_id, LifecycleEvent.RESUMED, {
                'restored_status': previous_status
            })
            await self._trigger_event_handlers(LifecycleEvent.RESUMED, agent_id)
            
            logger.info(f"Resumed agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume agent {agent_id}: {e}")
            return False
    
    async def stop_agent(self, agent_id: str, reason: Optional[str] = None) -> bool:
        """Stop an agent"""
        agent = await self.agent_factory.get_agent(agent_id)
        if not agent:
            return False
        
        try:
            agent.status = AgentStatus.STOPPED
            await self.agent_registry.update_agent_status(agent_id, AgentStatus.STOPPED)
            
            await self._record_lifecycle_event(agent_id, LifecycleEvent.STOPPED, {
                'reason': reason
            })
            await self._trigger_event_handlers(LifecycleEvent.STOPPED, agent_id)
            
            logger.info(f"Stopped agent {agent_id}" + (f" - {reason}" if reason else ""))
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop agent {agent_id}: {e}")
            return False
    
    async def archive_agent(self, agent_id: str, archive_data: bool = True) -> bool:
        """Archive an agent (preserve data but remove from active pool)"""
        agent = await self.agent_factory.get_agent(agent_id)
        if not agent:
            return False
        
        try:
            # Stop the agent first
            await self.stop_agent(agent_id, "archiving")
            
            # Archive agent data if requested
            if archive_data:
                archive_record = {
                    'agent_id': agent_id,
                    'template_id': agent.config.get('template_id'),
                    'agent_name': agent.config.get('name'),
                    'conversation_history': agent.conversation_history,
                    'learned_preferences': agent.learned_preferences,
                    'performance_metrics': agent.get_performance_metrics(),
                    'archived_at': datetime.utcnow(),
                    'lifecycle_history': self.lifecycle_history.get(agent_id, [])
                }
                
                await self.db.create_document("archived_agents", archive_record)
            
            # Remove from active systems
            await self.agent_registry.unregister_agent(agent_id)
            await self.agent_factory.delete_agent(agent_id)
            
            await self._record_lifecycle_event(agent_id, LifecycleEvent.ARCHIVED, {
                'data_archived': archive_data
            })
            await self._trigger_event_handlers(LifecycleEvent.ARCHIVED, agent_id)
            
            logger.info(f"Archived agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to archive agent {agent_id}: {e}")
            return False
    
    async def delete_agent(self, agent_id: str, permanent: bool = False) -> bool:
        """Delete an agent (with optional permanent deletion)"""
        try:
            # Archive first if not permanent deletion
            if not permanent:
                await self.archive_agent(agent_id, archive_data=True)
            else:
                # Stop and remove from active systems
                await self.stop_agent(agent_id, "permanent deletion")
                await self.agent_registry.unregister_agent(agent_id)
                await self.agent_factory.delete_agent(agent_id)
                
                # Remove all data
                await self.db.delete_document("archived_agents", agent_id)
                if agent_id in self.lifecycle_history:
                    del self.lifecycle_history[agent_id]
            
            await self._record_lifecycle_event(agent_id, LifecycleEvent.DELETED, {
                'permanent': permanent
            })
            await self._trigger_event_handlers(LifecycleEvent.DELETED, agent_id)
            
            logger.info(f"Deleted agent {agent_id} (permanent: {permanent})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete agent {agent_id}: {e}")
            return False
    
    async def restore_agent(self, agent_id: str) -> bool:
        """Restore an archived agent"""
        try:
            # Get archived data
            archived_data = await self.db.get_document("archived_agents", agent_id)
            if not archived_data:
                logger.error(f"No archived data found for agent {agent_id}")
                return False
            
            # Recreate agent from archived data
            template_id = archived_data['template_id']
            agent_name = archived_data['agent_name']
            
            new_agent_id = await self.create_agent_with_lifecycle(
                template_id=template_id,
                agent_name=agent_name,
                auto_start=False
            )
            
            # Restore agent data
            new_agent = await self.agent_factory.get_agent(new_agent_id)
            if new_agent:
                new_agent.conversation_history = archived_data.get('conversation_history', [])
                new_agent.learned_preferences = archived_data.get('learned_preferences', {})
                
                # Restore lifecycle history
                self.lifecycle_history[new_agent_id] = archived_data.get('lifecycle_history', [])
            
            # Remove from archive
            await self.db.delete_document("archived_agents", agent_id)
            
            logger.info(f"Restored agent {agent_id} as {new_agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore agent {agent_id}: {e}")
            return False
    
    async def schedule_agent_task(self, 
                                agent_id: str,
                                task_name: str,
                                delay_seconds: int,
                                task_func: Callable,
                                *args, **kwargs) -> str:
        """Schedule a task for an agent"""
        task_id = f"{agent_id}_{task_name}_{datetime.utcnow().timestamp()}"
        
        async def scheduled_task():
            await asyncio.sleep(delay_seconds)
            try:
                await task_func(*args, **kwargs)
                logger.info(f"Completed scheduled task {task_name} for agent {agent_id}")
            except Exception as e:
                logger.error(f"Scheduled task {task_name} failed for agent {agent_id}: {e}")
        
        self.scheduled_tasks[task_id] = asyncio.create_task(scheduled_task())
        return task_id
    
    async def cancel_scheduled_task(self, task_id: str) -> bool:
        """Cancel a scheduled task"""
        if task_id in self.scheduled_tasks:
            self.scheduled_tasks[task_id].cancel()
            del self.scheduled_tasks[task_id]
            return True
        return False
    
    def register_event_handler(self, event: LifecycleEvent, handler: Callable):
        """Register an event handler for lifecycle events"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    async def get_agent_lifecycle_history(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get lifecycle history for an agent"""
        return self.lifecycle_history.get(agent_id, [])
    
    async def get_lifecycle_statistics(self) -> Dict[str, Any]:
        """Get lifecycle statistics"""
        total_events = sum(len(history) for history in self.lifecycle_history.values())
        
        event_counts = {}
        for history in self.lifecycle_history.values():
            for event in history:
                event_type = event.get('event')
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        active_agents = len(await self.agent_factory.list_active_agents())
        
        # Get archived agents count
        try:
            archived_count = await self.db.count_documents("archived_agents")
        except:
            archived_count = 0
        
        return {
            'total_lifecycle_events': total_events,
            'event_distribution': event_counts,
            'active_agents': active_agents,
            'archived_agents': archived_count,
            'scheduled_tasks': len(self.scheduled_tasks),
            'agents_with_history': len(self.lifecycle_history)
        }
    
    async def _record_lifecycle_event(self, agent_id: str, event: LifecycleEvent, metadata: Optional[Dict] = None):
        """Record a lifecycle event"""
        event_record = {
            'event': event.value,
            'timestamp': datetime.utcnow(),
            'metadata': metadata or {}
        }
        
        if agent_id not in self.lifecycle_history:
            self.lifecycle_history[agent_id] = []
        
        self.lifecycle_history[agent_id].append(event_record)
        
        # Store in database
        try:
            db_record = {
                'agent_id': agent_id,
                **event_record
            }
            await self.db.create_document("agent_lifecycle_events", db_record)
        except Exception as e:
            logger.error(f"Failed to store lifecycle event: {e}")
    
    async def _trigger_event_handlers(self, event: LifecycleEvent, agent_id: str):
        """Trigger registered event handlers"""
        handlers = self.event_handlers.get(event, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(agent_id, event)
                else:
                    handler(agent_id, event)
            except Exception as e:
                logger.error(f"Event handler failed for {event.value}: {e}")
    
    async def _handle_agent_error(self, agent_id: str, error_message: str):
        """Handle agent errors"""
        agent = await self.agent_factory.get_agent(agent_id)
        if agent:
            agent.status = AgentStatus.ERROR
            agent.error_count += 1
            
            await self.agent_registry.update_agent_status(agent_id, AgentStatus.ERROR, {
                'error_message': error_message,
                'error_time': datetime.utcnow().isoformat()
            })
            
            await self._record_lifecycle_event(agent_id, LifecycleEvent.ERROR, {
                'error_message': error_message
            })
            await self._trigger_event_handlers(LifecycleEvent.ERROR, agent_id)
    
    async def _health_monitor_loop(self):
        """Health monitoring loop"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
    
    async def _perform_health_checks(self):
        """Perform health checks on all agents"""
        active_agents = await self.agent_factory.list_active_agents()
        
        for agent_info in active_agents:
            agent_id = agent_info['agent_id']
            
            try:
                # Check if agent is responsive
                agent = await self.agent_factory.get_agent(agent_id)
                if not agent:
                    continue
                
                # Check for stuck agents (active for too long)
                if agent.status == AgentStatus.ACTIVE:
                    if agent.last_active:
                        time_active = datetime.utcnow() - agent.last_active
                        if time_active.total_seconds() > 300:  # 5 minutes
                            logger.warning(f"Agent {agent_id} stuck in active state")
                            agent.status = AgentStatus.IDLE
                            await self.agent_registry.update_agent_status(agent_id, AgentStatus.IDLE)
                
                # Check error rate
                if agent.task_count > 0:
                    error_rate = agent.error_count / agent.task_count
                    if error_rate > 0.5:  # More than 50% error rate
                        logger.warning(f"Agent {agent_id} has high error rate: {error_rate:.2%}")
                        # Could trigger automatic restart or notification
                
                # Record performance metrics
                await self.agent_registry.record_performance_metric(agent_id, {
                    'status': agent.status.value,
                    'task_count': agent.task_count,
                    'error_count': agent.error_count,
                    'conversation_length': len(agent.conversation_history)
                })
                
            except Exception as e:
                logger.error(f"Health check failed for agent {agent_id}: {e}")
                await self._handle_agent_error(agent_id, f"Health check failed: {str(e)}")
    
    async def cleanup_completed_tasks(self):
        """Clean up completed scheduled tasks"""
        completed_tasks = []
        for task_id, task in self.scheduled_tasks.items():
            if task.done():
                completed_tasks.append(task_id)
        
        for task_id in completed_tasks:
            del self.scheduled_tasks[task_id]
        
        if completed_tasks:
            logger.info(f"Cleaned up {len(completed_tasks)} completed scheduled tasks")
