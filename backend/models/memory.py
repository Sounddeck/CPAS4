
"""
Memory-related data models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

class Memory(BaseModel):
    """Memory document model"""
    id: Optional[str] = Field(default=None, alias="_id")
    content: str = Field(..., description="Memory content")
    memory_type: str = Field(default="general", description="Type of memory")
    tags: List[str] = Field(default_factory=list, description="Memory tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    embedding: Optional[List[float]] = Field(default=None, description="Vector embedding")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="Memory importance score")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    access_count: int = Field(default=0, description="Number of times accessed")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class MemoryCreate(BaseModel):
    """Model for creating new memories"""
    content: str
    memory_type: str = "general"
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)

class MemoryUpdate(BaseModel):
    """Model for updating memories"""
    content: Optional[str] = None
    memory_type: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    importance: Optional[float] = Field(default=None, ge=0.0, le=1.0)

class MemoryResponse(BaseModel):
    """Response model for memory operations"""
    success: bool
    message: str
    memory: Optional[Memory] = None
    memories: Optional[List[Memory]] = None
    total_count: Optional[int] = None

class MemorySearchRequest(BaseModel):
    """Model for memory search requests"""
    query: str
    memory_type: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = Field(default=10, ge=1, le=100)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
