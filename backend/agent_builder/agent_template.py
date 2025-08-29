
"""
Agent Template System for Dynamic Agent Creation
"""

import json
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

class AgentCapability(str, Enum):
    """Standard agent capabilities"""
    REASONING = "reasoning"
    MEMORY = "memory"
    VOICE = "voice"
    RESEARCH = "research"
    COMMUNICATION = "communication"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    PLANNING = "planning"
    ANALYSIS = "analysis"
    LEARNING = "learning"

class AgentPersonality(BaseModel):
    """Agent personality configuration"""
    name: str = Field(..., description="Agent name")
    traits: List[str] = Field(default_factory=list, description="Personality traits")
    communication_style: str = Field(default="professional", description="Communication style")
    expertise_level: str = Field(default="intermediate", description="Expertise level")
    response_tone: str = Field(default="helpful", description="Response tone")
    creativity_level: float = Field(default=0.7, ge=0.0, le=1.0, description="Creativity level")
    formality_level: float = Field(default=0.5, ge=0.0, le=1.0, description="Formality level")

class AgentSkills(BaseModel):
    """Agent skills and knowledge domains"""
    primary_skills: List[str] = Field(default_factory=list, description="Primary skills")
    secondary_skills: List[str] = Field(default_factory=list, description="Secondary skills")
    knowledge_domains: List[str] = Field(default_factory=list, description="Knowledge domains")
    languages: List[str] = Field(default=["english"], description="Supported languages")
    tools: List[str] = Field(default_factory=list, description="Available tools")
    integrations: List[str] = Field(default_factory=list, description="External integrations")

class AgentBehavior(BaseModel):
    """Agent behavior configuration"""
    proactive: bool = Field(default=True, description="Proactive behavior")
    collaborative: bool = Field(default=True, description="Collaborative behavior")
    learning_enabled: bool = Field(default=True, description="Learning enabled")
    memory_retention: str = Field(default="medium", description="Memory retention level")
    task_delegation: bool = Field(default=False, description="Can delegate tasks")
    multi_tasking: bool = Field(default=False, description="Multi-tasking capability")
    error_recovery: str = Field(default="retry", description="Error recovery strategy")

class AgentTemplate(BaseModel):
    """Complete agent template for dynamic instantiation"""
    
    # Template metadata
    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    version: str = Field(default="1.0.0", description="Template version")
    category: str = Field(..., description="Agent category")
    tags: List[str] = Field(default_factory=list, description="Template tags")
    
    # Agent configuration
    personality: AgentPersonality = Field(..., description="Agent personality")
    skills: AgentSkills = Field(..., description="Agent skills")
    behavior: AgentBehavior = Field(..., description="Agent behavior")
    capabilities: List[AgentCapability] = Field(default_factory=list, description="Agent capabilities")
    
    # LLM configuration
    model_config: Dict[str, Any] = Field(default_factory=dict, description="LLM model configuration")
    system_prompt: str = Field(..., description="System prompt template")
    prompt_templates: Dict[str, str] = Field(default_factory=dict, description="Prompt templates")
    
    # Operational settings
    max_tokens: Optional[int] = Field(default=None, description="Max tokens per response")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Response temperature")
    timeout: int = Field(default=30, description="Response timeout in seconds")
    retry_attempts: int = Field(default=3, description="Retry attempts on failure")
    
    # Metadata
    created_by: str = Field(..., description="Template creator")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    usage_count: int = Field(default=0, description="Template usage count")
    rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Template rating")
    
    # Template validation
    is_public: bool = Field(default=False, description="Public template")
    is_verified: bool = Field(default=False, description="Verified template")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('system_prompt')
    def validate_system_prompt(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('System prompt must be at least 10 characters long')
        return v
    
    @validator('capabilities')
    def validate_capabilities(cls, v):
        if not v:
            raise ValueError('At least one capability must be specified')
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary"""
        return self.dict()
    
    def to_json(self) -> str:
        """Convert template to JSON string"""
        return self.json()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentTemplate':
        """Create template from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentTemplate':
        """Create template from JSON string"""
        return cls.parse_raw(json_str)

class AgentTemplateManager:
    """Manager for agent templates"""
    
    def __init__(self, database):
        self.db = database
        self.collection_name = "agent_templates"
    
    async def create_template(self, template: AgentTemplate) -> str:
        """Create a new agent template"""
        template_dict = template.to_dict()
        result = await self.db.create_document(self.collection_name, template_dict)
        return result.get('_id', template.template_id)
    
    async def get_template(self, template_id: str) -> Optional[AgentTemplate]:
        """Get agent template by ID"""
        template_data = await self.db.get_document(self.collection_name, template_id)
        if template_data:
            return AgentTemplate.from_dict(template_data)
        return None
    
    async def update_template(self, template_id: str, updates: Dict[str, Any]) -> bool:
        """Update agent template"""
        updates['updated_at'] = datetime.utcnow()
        result = await self.db.update_document(self.collection_name, template_id, updates)
        return result.get('modified_count', 0) > 0
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete agent template"""
        result = await self.db.delete_document(self.collection_name, template_id)
        return result.get('deleted_count', 0) > 0
    
    async def list_templates(self, 
                           category: Optional[str] = None,
                           tags: Optional[List[str]] = None,
                           public_only: bool = False,
                           limit: int = 50) -> List[AgentTemplate]:
        """List agent templates with filters"""
        filters = {}
        
        if category:
            filters['category'] = category
        
        if tags:
            filters['tags'] = {'$in': tags}
        
        if public_only:
            filters['is_public'] = True
        
        templates_data = await self.db.find_documents(
            self.collection_name, 
            filters, 
            limit=limit,
            sort=[('rating', -1), ('usage_count', -1)]
        )
        
        return [AgentTemplate.from_dict(data) for data in templates_data]
    
    async def search_templates(self, query: str, limit: int = 20) -> List[AgentTemplate]:
        """Search agent templates by text"""
        # MongoDB text search
        filters = {
            '$text': {'$search': query}
        }
        
        templates_data = await self.db.find_documents(
            self.collection_name,
            filters,
            limit=limit,
            sort=[('score', {'$meta': 'textScore'})]
        )
        
        return [AgentTemplate.from_dict(data) for data in templates_data]
    
    async def increment_usage(self, template_id: str) -> bool:
        """Increment template usage count"""
        return await self.update_template(template_id, {
            '$inc': {'usage_count': 1}
        })
    
    async def rate_template(self, template_id: str, rating: float) -> bool:
        """Rate an agent template"""
        if not 0.0 <= rating <= 5.0:
            raise ValueError("Rating must be between 0.0 and 5.0")
        
        # In a real implementation, you'd calculate average rating
        return await self.update_template(template_id, {
            'rating': rating
        })
    
    async def get_popular_templates(self, limit: int = 10) -> List[AgentTemplate]:
        """Get most popular templates"""
        return await self.list_templates(limit=limit)
    
    async def get_templates_by_creator(self, creator: str, limit: int = 50) -> List[AgentTemplate]:
        """Get templates by creator"""
        filters = {'created_by': creator}
        templates_data = await self.db.find_documents(
            self.collection_name,
            filters,
            limit=limit,
            sort=[('created_at', -1)]
        )
        
        return [AgentTemplate.from_dict(data) for data in templates_data]

# Predefined agent templates
PREDEFINED_TEMPLATES = {
    "task_manager": {
        "name": "Task Manager Agent",
        "description": "Specialized agent for project planning, scheduling, and deadline tracking",
        "category": "productivity",
        "tags": ["planning", "scheduling", "productivity"],
        "personality": {
            "name": "TaskMaster",
            "traits": ["organized", "efficient", "detail-oriented", "proactive"],
            "communication_style": "professional",
            "expertise_level": "expert",
            "response_tone": "helpful",
            "creativity_level": 0.3,
            "formality_level": 0.7
        },
        "skills": {
            "primary_skills": ["project_planning", "task_scheduling", "deadline_management"],
            "secondary_skills": ["time_estimation", "resource_allocation", "progress_tracking"],
            "knowledge_domains": ["project_management", "productivity_methods", "scheduling_algorithms"],
            "tools": ["calendar", "task_tracker", "reminder_system"]
        },
        "behavior": {
            "proactive": True,
            "collaborative": True,
            "learning_enabled": True,
            "memory_retention": "high",
            "task_delegation": True,
            "multi_tasking": True
        },
        "capabilities": [AgentCapability.PLANNING, AgentCapability.MEMORY, AgentCapability.REASONING],
        "system_prompt": "You are TaskMaster, a specialized task management agent. You excel at breaking down complex projects into manageable tasks, creating realistic schedules, and tracking progress. You're proactive in identifying potential bottlenecks and suggesting optimizations."
    },
    
    "research_agent": {
        "name": "Research Agent",
        "description": "Specialized agent for information gathering, analysis, and report generation",
        "category": "research",
        "tags": ["research", "analysis", "information"],
        "personality": {
            "name": "ResearchBot",
            "traits": ["analytical", "thorough", "curious", "objective"],
            "communication_style": "academic",
            "expertise_level": "expert",
            "response_tone": "informative",
            "creativity_level": 0.5,
            "formality_level": 0.8
        },
        "skills": {
            "primary_skills": ["information_gathering", "data_analysis", "report_writing"],
            "secondary_skills": ["fact_checking", "source_verification", "synthesis"],
            "knowledge_domains": ["research_methodology", "data_analysis", "academic_writing"],
            "tools": ["web_search", "database_access", "citation_manager"]
        },
        "behavior": {
            "proactive": True,
            "collaborative": True,
            "learning_enabled": True,
            "memory_retention": "high",
            "task_delegation": False,
            "multi_tasking": True
        },
        "capabilities": [AgentCapability.RESEARCH, AgentCapability.ANALYSIS, AgentCapability.MEMORY],
        "system_prompt": "You are ResearchBot, a specialized research agent. You excel at gathering comprehensive information from multiple sources, analyzing data objectively, and presenting findings in clear, well-structured reports. You always verify sources and maintain academic rigor."
    },
    
    "creative_agent": {
        "name": "Creative Agent", 
        "description": "Specialized agent for content creation, brainstorming, and design assistance",
        "category": "creative",
        "tags": ["creative", "content", "brainstorming"],
        "personality": {
            "name": "CreativeGenius",
            "traits": ["imaginative", "innovative", "expressive", "inspiring"],
            "communication_style": "casual",
            "expertise_level": "expert",
            "response_tone": "enthusiastic",
            "creativity_level": 0.9,
            "formality_level": 0.3
        },
        "skills": {
            "primary_skills": ["content_creation", "brainstorming", "creative_writing"],
            "secondary_skills": ["design_thinking", "storytelling", "ideation"],
            "knowledge_domains": ["creative_arts", "design_principles", "marketing"],
            "tools": ["text_generation", "idea_mapper", "style_guide"]
        },
        "behavior": {
            "proactive": True,
            "collaborative": True,
            "learning_enabled": True,
            "memory_retention": "medium",
            "task_delegation": False,
            "multi_tasking": True
        },
        "capabilities": [AgentCapability.CREATIVE, AgentCapability.REASONING, AgentCapability.MEMORY],
        "system_prompt": "You are CreativeGenius, a specialized creative agent. You excel at generating original ideas, creating engaging content, and helping with creative problem-solving. You think outside the box and inspire innovative solutions."
    }
}
