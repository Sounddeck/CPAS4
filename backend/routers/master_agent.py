
"""
Master Agent API Routes
FastAPI endpoints for Master Agent operations
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from ..services.master_agent import MasterAgent, ReasoningLevel
from ..services.orchestration import AgentOrchestrator, TaskPriority
from ..services.llm_service import LLMService
from ..services.memory_service import MemoryService
from ..database import get_database

router = APIRouter(prefix="/master-agent", tags=["master-agent"])


class MasterAgentRequest(BaseModel):
    """Request model for Master Agent processing"""
    input: str = Field(..., description="User input to process")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")
    priority: Optional[str] = Field(default="normal", description="Task priority")
    user_id: Optional[str] = Field(default=None, description="User identifier")


class TaskSubmissionRequest(BaseModel):
    """Request model for task submission"""
    description: str = Field(..., description="Task description")
    priority: Optional[str] = Field(default="normal", description="Task priority")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Task context")


class MasterAgentResponse(BaseModel):
    """Response model for Master Agent"""
    success: bool
    response: str
    reasoning_level: Optional[str] = None
    confidence: Optional[float] = None
    processing_time: Optional[str] = None
    delegated_to: Optional[str] = None
    task_id: Optional[str] = None


# Global instances (will be initialized in main.py)
master_agent: Optional[MasterAgent] = None
orchestrator: Optional[AgentOrchestrator] = None


async def get_master_agent() -> MasterAgent:
    """Dependency to get Master Agent instance"""
    if master_agent is None:
        raise HTTPException(status_code=503, detail="Master Agent not initialized")
    return master_agent


async def get_orchestrator() -> AgentOrchestrator:
    """Dependency to get Orchestrator instance"""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    return orchestrator


@router.post("/process", response_model=MasterAgentResponse)
async def process_request(
    request: MasterAgentRequest,
    agent: MasterAgent = Depends(get_master_agent)
):
    """
    Process a request through the Master Agent
    Uses HRM reasoning to provide intelligent responses
    """
    try:
        # Prepare request for Master Agent
        agent_request = {
            "input": request.input,
            "context": request.context,
            "priority": request.priority,
            "user_id": request.user_id
        }
        
        # Process through Master Agent
        result = await agent.process_request(agent_request)
        
        return MasterAgentResponse(
            success=result.get("success", False),
            response=result.get("response", ""),
            reasoning_level=result.get("reasoning_level"),
            confidence=result.get("confidence"),
            processing_time=result.get("processing_time"),
            delegated_to=result.get("delegated_to")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Master Agent processing error: {str(e)}")


@router.post("/submit-task")
async def submit_task(
    request: TaskSubmissionRequest,
    background_tasks: BackgroundTasks,
    orch: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Submit a task for asynchronous processing
    Returns task ID for tracking
    """
    try:
        # Convert priority string to enum
        priority_map = {
            "urgent": TaskPriority.URGENT,
            "high": TaskPriority.HIGH,
            "normal": TaskPriority.NORMAL,
            "low": TaskPriority.LOW
        }
        
        priority = priority_map.get(request.priority.lower(), TaskPriority.NORMAL)
        
        # Submit task to orchestrator
        task_id = await orch.submit_task(
            description=request.description,
            priority=priority,
            context=request.context
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": "Task submitted successfully",
            "priority": request.priority
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task submission error: {str(e)}")


@router.get("/task/{task_id}")
async def get_task_status(
    task_id: str,
    orch: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Get the status of a submitted task
    """
    try:
        status = await orch.get_task_status(task_id)
        
        if status is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "success": True,
            "task": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task status: {str(e)}")


@router.delete("/task/{task_id}")
async def cancel_task(
    task_id: str,
    orch: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Cancel a pending or in-progress task
    """
    try:
        cancelled = await orch.cancel_task(task_id)
        
        if not cancelled:
            raise HTTPException(status_code=400, detail="Task cannot be cancelled")
        
        return {
            "success": True,
            "message": f"Task {task_id} cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling task: {str(e)}")


@router.get("/status")
async def get_master_agent_status(
    agent: MasterAgent = Depends(get_master_agent)
):
    """
    Get Master Agent status and performance metrics
    """
    try:
        status = await agent.get_status()
        
        return {
            "success": True,
            "status": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving status: {str(e)}")


@router.get("/orchestration-status")
async def get_orchestration_status(
    orch: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Get overall orchestration status and metrics
    """
    try:
        status = await orch.get_orchestration_status()
        
        return {
            "success": True,
            "orchestration": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving orchestration status: {str(e)}")


@router.post("/reasoning-level")
async def set_reasoning_level(
    level: str,
    agent: MasterAgent = Depends(get_master_agent)
):
    """
    Manually set the reasoning level for testing
    """
    try:
        valid_levels = ["reactive", "deliberative", "reflective", "strategic"]
        
        if level.lower() not in valid_levels:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid reasoning level. Must be one of: {valid_levels}"
            )
        
        # This would be implemented in the Master Agent
        return {
            "success": True,
            "message": f"Reasoning level set to {level}",
            "note": "This is a development feature"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting reasoning level: {str(e)}")


@router.get("/capabilities")
async def get_capabilities():
    """
    Get Master Agent capabilities and features
    """
    return {
        "success": True,
        "capabilities": {
            "reasoning_levels": [
                {
                    "level": "reactive",
                    "description": "Fast, immediate responses for simple queries"
                },
                {
                    "level": "deliberative", 
                    "description": "Thoughtful, planned responses with analysis"
                },
                {
                    "level": "reflective",
                    "description": "Multi-perspective analysis with historical context"
                },
                {
                    "level": "strategic",
                    "description": "Long-term planning and comprehensive analysis"
                }
            ],
            "features": [
                "HRM Hierarchical Reasoning",
                "Intelligent Task Delegation",
                "Multi-Agent Coordination",
                "OSINT Intelligence Gathering",
                "Predictive Suggestions",
                "Context Switching",
                "Learning from Interactions",
                "German-English Communication Style"
            ],
            "supported_tasks": [
                "Research and Analysis",
                "Content Creation",
                "Technical Problem Solving",
                "Personal Organization",
                "Intelligence Gathering",
                "Strategic Planning",
                "Multi-step Task Execution"
            ]
        }
    }


@router.post("/feedback")
async def submit_feedback(
    task_id: str,
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5"),
    feedback: Optional[str] = Field(default="", description="Optional feedback text"),
    agent: MasterAgent = Depends(get_master_agent)
):
    """
    Submit feedback for a completed task
    Used for learning and improvement
    """
    try:
        if rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Store feedback in memory for learning
        feedback_data = {
            "task_id": task_id,
            "rating": rating,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        }
        
        # This would be implemented to store in memory service
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "task_id": task_id,
            "rating": rating
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")


# Initialize function to be called from main.py
async def initialize_master_agent_router(llm_service: LLMService, memory_service: MemoryService):
    """Initialize Master Agent and Orchestrator instances"""
    global master_agent, orchestrator
    
    # Create Master Agent
    master_agent = MasterAgent(llm_service, memory_service)
    
    # Create Orchestrator
    orchestrator = AgentOrchestrator(master_agent, memory_service)
    
    # Start orchestrator
    await orchestrator.start()
    
    return master_agent, orchestrator
