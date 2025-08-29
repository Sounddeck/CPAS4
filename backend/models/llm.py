
"""
LLM-related data models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class LLMRequest(BaseModel):
    """Request model for LLM interactions"""
    prompt: str = Field(..., description="Input prompt for the LLM")
    model: Optional[str] = Field(default=None, description="Specific model to use")
    system_prompt: Optional[str] = Field(default=None, description="System prompt")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(default=None, ge=1, description="Maximum tokens to generate")
    stream: bool = Field(default=False, description="Stream response")
    context: Optional[List[Dict[str, str]]] = Field(default=None, description="Conversation context")
    use_memory: bool = Field(default=True, description="Use memory system")
    save_to_memory: bool = Field(default=True, description="Save interaction to memory")

class LLMResponse(BaseModel):
    """Response model for LLM interactions"""
    response: str = Field(..., description="LLM response text")
    model: str = Field(..., description="Model used")
    tokens_used: Optional[int] = Field(default=None, description="Tokens consumed")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    memory_id: Optional[str] = Field(default=None, description="Associated memory ID")
    context_used: bool = Field(default=False, description="Whether context was used")

class ModelInfo(BaseModel):
    """Model information"""
    name: str
    size: Optional[str] = None
    family: Optional[str] = None
    format: Optional[str] = None
    parameter_size: Optional[str] = None
    quantization_level: Optional[str] = None
    modified_at: Optional[datetime] = None
    digest: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class ModelListResponse(BaseModel):
    """Response for listing available models"""
    models: List[ModelInfo]
    total_count: int
    local_models: List[str]
    api_models: List[str]

class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    """Chat request model"""
    messages: List[ChatMessage]
    model: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = None
    stream: bool = Field(default=False)
    session_id: Optional[str] = None
