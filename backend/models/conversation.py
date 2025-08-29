
"""
Conversation-related data models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Message(BaseModel):
    """Individual message in a conversation"""
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    processing_time: Optional[float] = None

class Conversation(BaseModel):
    """Conversation model"""
    id: Optional[str] = Field(default=None, alias="_id")
    session_id: str = Field(..., description="Unique session identifier")
    title: Optional[str] = Field(default=None, description="Conversation title")
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    agent_id: Optional[str] = Field(default=None, description="Associated agent")
    memory_enabled: bool = Field(default=True)
    
    class Config:
        populate_by_name = True

class ConversationCreate(BaseModel):
    """Model for creating new conversations"""
    session_id: str
    title: Optional[str] = None
    agent_id: Optional[str] = None
    memory_enabled: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ConversationUpdate(BaseModel):
    """Model for updating conversations"""
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    memory_enabled: Optional[bool] = None
