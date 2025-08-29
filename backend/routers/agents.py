
"""
Enhanced Agent Management API Router
Phase 3: Dynamic Agent Building and Multi-Agent Coordination
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

from ..agent_builder import (
    AgentTemplateManager, AgentFactory, AgentRegistry, AgentLifecycleManager
)
from ..agent_builder.agent_template import AgentTemplate, PREDEFINED_TEMPLATES
from ..specialized_agents import (
    TaskManagerAgent, ResearchAgent, CreativeAgent, 
    TechnicalAgent, PersonalAssistantAgent
)
from ..multi_agent import (
    MessageBus, TaskDelegator, ConflictResolver, 
    CollaborationEngine, SharedKnowledgeBase
)
from ..multi_agent.message_bus import MessageType, MessagePriority
from ..multi_agent.task_delegator import TaskPriority, TaskStatus
from ..multi_agent.conflict_resolver import ConflictType, ConflictSeverity
from ..multi_agent.collaboration_engine import CollaborationType
from ..multi_agent.shared_knowledge import KnowledgeType, AccessLevel
from ..database import Database
from ..services.llm_service import LLMService

router = APIRouter()

# Global instances (will be initialized in main.py)
template_manager: Optional[AgentTemplateManager] = None
agent_factory: Optional[AgentFactory] = None
agent_registry: Optional[AgentRegistry] = None
lifecycle_manager: Optional[AgentLifecycleManager] = None
message_bus: Optional[MessageBus] = None
task_delegator: Optional[TaskDelegator] = None
conflict_resolver: Optional[ConflictResolver] = None
collaboration_engine: Optional[CollaborationEngine] = None
shared_knowledge: Optional[SharedKnowledgeBase] = None

async def get_database():
    """Dependency to get database instance"""
    from ..database import db
    return db

async def get_llm_service():
    """Dependency to get LLM service instance"""
    from ..services.llm_service import llm_service
    return llm_service

# Agent Template Management Endpoints

@router.post("/templates", response_model=Dict[str, str])
async def create_agent_template(
    template_data: Dict[str, Any],
    db: Database = Depends(get_database)
):
    """Create a new agent template"""
    try:
        template = AgentTemplate(**template_data)
        template_id = await template_manager.create_template(template)
        return {"template_id": template_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/templates", response_model=List[Dict[str, Any]])
async def list_agent_templates(
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    public_only: bool = False,
    limit: int = 50
):
    """List available agent templates"""
    try:
        templates = await template_manager.list_templates(
            category=category,
            tags=tags,
            public_only=public_only,
            limit=limit
        )
        return [template.to_dict() for template in templates]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}", response_model=Dict[str, Any])
async def get_agent_template(template_id: str):
    """Get specific agent template"""
    try:
        template = await template_manager.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/predefined", response_model=Dict[str, Any])
async def get_predefined_templates():
    """Get all predefined agent templates"""
    return PREDEFINED_TEMPLATES

@router.delete("/templates/{template_id}")
async def delete_agent_template(template_id: str):
    """Delete an agent template"""
    try:
        success = await template_manager.delete_template(template_id)
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Agent Instance Management Endpoints

@router.post("/agents", response_model=Dict[str, str])
async def create_agent(
    template_id: str,
    agent_name: Optional[str] = None,
    custom_config: Optional[Dict[str, Any]] = None,
    auto_start: bool = True
):
    """Create a new agent instance"""
    try:
        agent_id = await lifecycle_manager.create_agent_with_lifecycle(
            template_id=template_id,
            agent_name=agent_name,
            custom_config=custom_config,
            auto_start=auto_start
        )
        return {"agent_id": agent_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/agents/predefined", response_model=Dict[str, str])
async def create_predefined_agent(
    template_key: str,
    agent_name: Optional[str] = None,
    creator: str = "user"
):
    """Create agent from predefined template"""
    try:
        agent_id = await agent_factory.create_agent_from_predefined(
            template_key=template_key,
            agent_name=agent_name,
            creator=creator
        )
        return {"agent_id": agent_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/agents", response_model=List[Dict[str, Any]])
async def list_active_agents():
    """List all active agents"""
    try:
        agents = await agent_factory.list_active_agents()
        return agents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_id}", response_model=Dict[str, Any])
async def get_agent_status(agent_id: str):
    """Get agent status and information"""
    try:
        agent_info = await agent_registry.get_agent_info(agent_id)
        if not agent_info:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/{agent_id}/message", response_model=Dict[str, Any])
async def send_message_to_agent(
    agent_id: str,
    message: str,
    context: Optional[Dict[str, Any]] = None
):
    """Send a message to an agent"""
    try:
        agent = await agent_factory.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        response = await agent.process_message(message, context)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/{agent_id}/start")
async def start_agent(agent_id: str):
    """Start an agent"""
    try:
        success = await lifecycle_manager.start_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found or cannot be started")
        return {"status": "started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/{agent_id}/stop")
async def stop_agent(agent_id: str, reason: Optional[str] = None):
    """Stop an agent"""
    try:
        success = await lifecycle_manager.stop_agent(agent_id, reason)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"status": "stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/{agent_id}/pause")
async def pause_agent(agent_id: str):
    """Pause an agent"""
    try:
        success = await lifecycle_manager.pause_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"status": "paused"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/{agent_id}/resume")
async def resume_agent(agent_id: str):
    """Resume a paused agent"""
    try:
        success = await lifecycle_manager.resume_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"status": "resumed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str, permanent: bool = False):
    """Delete an agent"""
    try:
        success = await lifecycle_manager.delete_agent(agent_id, permanent)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"status": "deleted", "permanent": permanent}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Task Delegation Endpoints

@router.post("/tasks", response_model=Dict[str, str])
async def submit_task(
    requester_id: str,
    task_type: str,
    description: str,
    requirements: Dict[str, Any],
    priority: TaskPriority = TaskPriority.NORMAL,
    deadline: Optional[datetime] = None,
    dependencies: Optional[List[str]] = None
):
    """Submit a new task for delegation"""
    try:
        task_id = await task_delegator.submit_task(
            requester_id=requester_id,
            task_type=task_type,
            description=description,
            requirements=requirements,
            priority=priority,
            deadline=deadline,
            dependencies=dependencies
        )
        return {"task_id": task_id, "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tasks/{task_id}", response_model=Dict[str, Any])
async def get_task_status(task_id: str):
    """Get task status and details"""
    try:
        task = await task_delegator.get_task_status(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/{task_id}/assign")
async def assign_task_to_agent(
    task_id: str,
    agent_id: str,
    force: bool = False
):
    """Manually assign a task to a specific agent"""
    try:
        success = await task_delegator.assign_task(task_id, agent_id, force)
        if not success:
            raise HTTPException(status_code=400, detail="Task assignment failed")
        return {"status": "assigned", "agent_id": agent_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str, reason: str = "Cancelled by user"):
    """Cancel a task"""
    try:
        success = await task_delegator.cancel_task(task_id, reason)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"status": "cancelled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/agent/{agent_id}", response_model=List[Dict[str, Any]])
async def get_agent_tasks(agent_id: str):
    """Get all tasks assigned to an agent"""
    try:
        tasks = await task_delegator.get_agent_tasks(agent_id)
        return [task.to_dict() for task in tasks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/pending", response_model=List[Dict[str, Any]])
async def get_pending_tasks():
    """Get all pending tasks"""
    try:
        tasks = await task_delegator.get_pending_tasks()
        return [task.to_dict() for task in tasks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Collaboration Endpoints

@router.post("/collaborations", response_model=Dict[str, str])
async def initiate_collaboration(
    initiator_id: str,
    participant_ids: List[str],
    collaboration_type: CollaborationType,
    objective: str,
    context: Dict[str, Any]
):
    """Initiate a new collaboration session"""
    try:
        session_id = await collaboration_engine.initiate_collaboration(
            initiator_id=initiator_id,
            participant_ids=participant_ids,
            collaboration_type=collaboration_type,
            objective=objective,
            context=context
        )
        return {"session_id": session_id, "status": "initiated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/collaborations/{session_id}/start")
async def start_collaboration(session_id: str):
    """Start a collaboration session"""
    try:
        success = await collaboration_engine.start_collaboration(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Collaboration session not found")
        return {"status": "started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/collaborations/{session_id}/join")
async def join_collaboration(session_id: str, agent_id: str):
    """Agent joins a collaboration session"""
    try:
        success = await collaboration_engine.join_collaboration(session_id, agent_id)
        if not success:
            raise HTTPException(status_code=400, detail="Cannot join collaboration")
        return {"status": "joined"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collaborations", response_model=List[Dict[str, Any]])
async def get_active_collaborations():
    """Get all active collaboration sessions"""
    try:
        sessions = await collaboration_engine.get_active_collaborations()
        return [session.to_dict() for session in sessions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/collaborations/{session_id}")
async def cancel_collaboration(session_id: str, reason: str = "Cancelled"):
    """Cancel a collaboration session"""
    try:
        success = await collaboration_engine.cancel_collaboration(session_id, reason)
        if not success:
            raise HTTPException(status_code=404, detail="Collaboration session not found")
        return {"status": "cancelled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Conflict Resolution Endpoints

@router.post("/conflicts", response_model=Dict[str, str])
async def report_conflict(
    conflict_type: ConflictType,
    involved_agents: List[str],
    description: str,
    context: Dict[str, Any],
    severity: ConflictSeverity = ConflictSeverity.MEDIUM
):
    """Report a new conflict"""
    try:
        conflict_id = await conflict_resolver.detect_conflict(
            conflict_type=conflict_type,
            involved_agents=involved_agents,
            description=description,
            context=context,
            severity=severity
        )
        return {"conflict_id": conflict_id, "status": "reported"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/conflicts", response_model=List[Dict[str, Any]])
async def get_active_conflicts():
    """Get all active conflicts"""
    try:
        conflicts = await conflict_resolver.get_active_conflicts()
        return [conflict.to_dict() for conflict in conflicts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conflicts/history", response_model=List[Dict[str, Any]])
async def get_conflict_history(limit: int = 50):
    """Get conflict resolution history"""
    try:
        conflicts = await conflict_resolver.get_conflict_history(limit)
        return [conflict.to_dict() for conflict in conflicts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Knowledge Management Endpoints

@router.post("/knowledge", response_model=Dict[str, str])
async def store_knowledge(
    source_agent_id: str,
    knowledge_type: KnowledgeType,
    title: str,
    content: Dict[str, Any],
    tags: List[str] = None,
    access_level: AccessLevel = AccessLevel.PUBLIC,
    confidence: float = 1.0,
    metadata: Dict[str, Any] = None
):
    """Store new knowledge item"""
    try:
        knowledge_id = await shared_knowledge.store_knowledge(
            source_agent_id=source_agent_id,
            knowledge_type=knowledge_type,
            title=title,
            content=content,
            tags=tags,
            access_level=access_level,
            confidence=confidence,
            metadata=metadata
        )
        return {"knowledge_id": knowledge_id, "status": "stored"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/knowledge/{knowledge_id}", response_model=Dict[str, Any])
async def get_knowledge(knowledge_id: str, requester_agent_id: str):
    """Retrieve specific knowledge item"""
    try:
        knowledge_item = await shared_knowledge.retrieve_knowledge(
            requester_agent_id, knowledge_id
        )
        if not knowledge_item:
            raise HTTPException(status_code=404, detail="Knowledge not found or access denied")
        return knowledge_item.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge/search", response_model=List[Dict[str, Any]])
async def search_knowledge(
    requester_agent_id: str,
    query: str,
    knowledge_types: Optional[List[KnowledgeType]] = None,
    tags: Optional[List[str]] = None,
    limit: int = 20
):
    """Search knowledge base"""
    try:
        results = await shared_knowledge.search_knowledge(
            requester_agent_id=requester_agent_id,
            query=query,
            knowledge_types=knowledge_types,
            tags=tags,
            limit=limit
        )
        return [item.to_dict() for item in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Statistics and Monitoring Endpoints

@router.get("/statistics/agents", response_model=Dict[str, Any])
async def get_agent_statistics():
    """Get agent system statistics"""
    try:
        registry_stats = await agent_registry.get_registry_statistics()
        factory_stats = await agent_factory.get_agent_performance_summary()
        lifecycle_stats = await lifecycle_manager.get_lifecycle_statistics()
        
        return {
            "registry": registry_stats,
            "factory": factory_stats,
            "lifecycle": lifecycle_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/tasks", response_model=Dict[str, Any])
async def get_task_statistics():
    """Get task delegation statistics"""
    try:
        return await task_delegator.get_delegation_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/collaborations", response_model=Dict[str, Any])
async def get_collaboration_statistics():
    """Get collaboration statistics"""
    try:
        return await collaboration_engine.get_collaboration_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/conflicts", response_model=Dict[str, Any])
async def get_conflict_statistics():
    """Get conflict resolution statistics"""
    try:
        return await conflict_resolver.get_conflict_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/knowledge", response_model=Dict[str, Any])
async def get_knowledge_statistics():
    """Get knowledge base statistics"""
    try:
        return await shared_knowledge.get_knowledge_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/messages", response_model=Dict[str, Any])
async def get_message_statistics():
    """Get message bus statistics"""
    try:
        return await message_bus.get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# System Management Endpoints

@router.post("/system/initialize")
async def initialize_agent_system(
    background_tasks: BackgroundTasks,
    db: Database = Depends(get_database),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Initialize the agent system components"""
    try:
        global template_manager, agent_factory, agent_registry, lifecycle_manager
        global message_bus, task_delegator, conflict_resolver, collaboration_engine, shared_knowledge
        
        # Initialize components
        template_manager = AgentTemplateManager(db)
        agent_registry = AgentRegistry(db)
        agent_factory = AgentFactory(template_manager, llm_service)
        lifecycle_manager = AgentLifecycleManager(agent_factory, agent_registry, db)
        
        message_bus = MessageBus(db)
        task_delegator = TaskDelegator(message_bus, agent_registry, db)
        conflict_resolver = ConflictResolver(message_bus, agent_registry, db)
        collaboration_engine = CollaborationEngine(message_bus, task_delegator, agent_registry, db)
        shared_knowledge = SharedKnowledgeBase(db)
        
        # Start services
        background_tasks.add_task(message_bus.start)
        background_tasks.add_task(task_delegator.start)
        background_tasks.add_task(conflict_resolver.start)
        background_tasks.add_task(collaboration_engine.start)
        background_tasks.add_task(shared_knowledge.start)
        background_tasks.add_task(lifecycle_manager.start_lifecycle_management)
        
        return {"status": "initialized", "message": "Agent system components initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")

@router.post("/system/shutdown")
async def shutdown_agent_system():
    """Shutdown the agent system components"""
    try:
        # Stop all services
        if message_bus:
            await message_bus.stop()
        if task_delegator:
            await task_delegator.stop()
        if conflict_resolver:
            await conflict_resolver.stop()
        if collaboration_engine:
            await collaboration_engine.stop()
        if shared_knowledge:
            await shared_knowledge.stop()
        if lifecycle_manager:
            await lifecycle_manager.stop_lifecycle_management()
        
        return {"status": "shutdown", "message": "Agent system components shutdown successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shutdown failed: {str(e)}")

@router.get("/system/health", response_model=Dict[str, Any])
async def get_system_health():
    """Get overall system health status"""
    try:
        health_status = {
            "message_bus": "healthy" if message_bus else "not_initialized",
            "task_delegator": "healthy" if task_delegator else "not_initialized",
            "conflict_resolver": "healthy" if conflict_resolver else "not_initialized",
            "collaboration_engine": "healthy" if collaboration_engine else "not_initialized",
            "shared_knowledge": "healthy" if shared_knowledge else "not_initialized",
            "lifecycle_manager": "healthy" if lifecycle_manager else "not_initialized",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        overall_status = "healthy" if all(status == "healthy" for status in health_status.values() if status != health_status["timestamp"]) else "degraded"
        
        return {
            "overall_status": overall_status,
            "components": health_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
