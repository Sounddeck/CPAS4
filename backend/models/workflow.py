
"""
Workflow Models for Enhanced CPAS
Defines data structures for workflow automation and agent coordination
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from bson import ObjectId

class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class TriggerType(str, Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EMAIL = "email"
    CALENDAR = "calendar"
    FILE = "file"
    WEBHOOK = "webhook"
    AGENT_COMPLETION = "agent_completion"

class ActionType(str, Enum):
    AGENT_TASK = "agent_task"
    EMAIL_SEND = "email_send"
    CALENDAR_CREATE = "calendar_create"
    FILE_PROCESS = "file_process"
    NOTIFICATION = "notification"
    API_CALL = "api_call"
    CONDITION = "condition"
    DELAY = "delay"

class WorkflowTrigger(BaseModel):
    """Defines what triggers a workflow execution"""
    type: TriggerType
    config: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True
    
    class Config:
        use_enum_values = True

class WorkflowAction(BaseModel):
    """Individual action within a workflow"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    name: str
    type: ActionType
    agent_id: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)  # IDs of actions that must complete first
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    
    class Config:
        use_enum_values = True

class WorkflowExecution(BaseModel):
    """Tracks execution of a workflow instance"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    workflow_id: str
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    trigger_data: Dict[str, Any] = Field(default_factory=dict)
    action_results: Dict[str, Any] = Field(default_factory=dict)  # action_id -> result
    error_message: Optional[str] = None
    
    class Config:
        use_enum_values = True

class Workflow(BaseModel):
    """Complete workflow definition"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    name: str
    description: Optional[str] = None
    status: WorkflowStatus = WorkflowStatus.DRAFT
    triggers: List[WorkflowTrigger] = Field(default_factory=list)
    actions: List[WorkflowAction] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = "system"
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        use_enum_values = True

class WorkflowTemplate(BaseModel):
    """Pre-built workflow templates"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    name: str
    description: str
    category: str
    template_data: Workflow
    usage_count: int = 0
    rating: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
class AgentCollaboration(BaseModel):
    """Defines how agents collaborate on tasks"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    name: str
    participating_agents: List[str]  # Agent IDs
    coordination_strategy: str = "sequential"  # sequential, parallel, hierarchical
    communication_protocol: Dict[str, Any] = Field(default_factory=dict)
    shared_context: Dict[str, Any] = Field(default_factory=dict)
    conflict_resolution: str = "voting"  # voting, priority, human_intervention
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TaskDelegation(BaseModel):
    """Task delegation between agents"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    task_description: str
    delegating_agent: str
    receiving_agent: str
    priority: int = 5  # 1-10 scale
    deadline: Optional[datetime] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True

# Request/Response Models for API

class CreateWorkflowRequest(BaseModel):
    name: str
    description: Optional[str] = None
    triggers: List[WorkflowTrigger] = Field(default_factory=list)
    actions: List[WorkflowAction] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

class UpdateWorkflowRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[WorkflowStatus] = None
    triggers: Optional[List[WorkflowTrigger]] = None
    actions: Optional[List[WorkflowAction]] = None
    tags: Optional[List[str]] = None

class ExecuteWorkflowRequest(BaseModel):
    workflow_id: str
    trigger_data: Dict[str, Any] = Field(default_factory=dict)
    override_config: Dict[str, Any] = Field(default_factory=dict)

class WorkflowListResponse(BaseModel):
    workflows: List[Workflow]
    total: int
    page: int
    page_size: int

class WorkflowExecutionResponse(BaseModel):
    execution: WorkflowExecution
    workflow: Workflow
