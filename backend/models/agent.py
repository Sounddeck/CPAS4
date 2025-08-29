
"""
Agent-related data models (Future Phase)
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AgentStatus(str, Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    STOPPED = "stopped"

class AgentType(str, Enum):
    """Agent type enumeration"""
    GENERAL = "general"
    SPECIALIST = "specialist"
    REASONING = "reasoning"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    CUSTOM = "custom"

class Agent(BaseModel):
    """Agent model"""
    id: Optional[str] = Field(default=None, alias="_id")
    agent_id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Agent name")
    description: Optional[str] = Field(default=None, description="Agent description")
    agent_type: AgentType = Field(default=AgentType.GENERAL)
    status: AgentStatus = Field(default=AgentStatus.IDLE)
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    system_prompt: Optional[str] = Field(default=None, description="Agent system prompt")
    model: str = Field(..., description="LLM model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None)
    memory_enabled: bool = Field(default=True)
    tools: List[str] = Field(default_factory=list, description="Available tools")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None
    task_count: int = Field(default=0)
    
    class Config:
        populate_by_name = True
        use_enum_values = True

class AgentCreate(BaseModel):
    """Model for creating new agents"""
    name: str
    description: Optional[str] = None
    agent_type: AgentType = AgentType.GENERAL
    capabilities: List[str] = Field(default_factory=list)
    system_prompt: Optional[str] = None
    model: str = "llama3.2:3b"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = None
    memory_enabled: bool = True
    tools: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentUpdate(BaseModel):
    """Model for updating agents"""
    name: Optional[str] = None
    description: Optional[str] = None
    agent_type: Optional[AgentType] = None
    status: Optional[AgentStatus] = None
    capabilities: Optional[List[str]] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = None
    memory_enabled: Optional[bool] = None
    tools: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class AgentTask(BaseModel):
    """Agent task model"""
    task_id: str
    agent_id: str
    prompt: str
    status: str = "pending"
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None
