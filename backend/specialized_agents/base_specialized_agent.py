
"""
Base class for specialized agents
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger

from ..agent_builder.agent_factory import AgentInstance
from ..services.llm_service import LLMService

class BaseSpecializedAgent(ABC):
    """Base class for all specialized agents"""
    
    def __init__(self, agent_instance: AgentInstance, llm_service: LLMService):
        self.agent_instance = agent_instance
        self.llm_service = llm_service
        self.specialized_tools = {}
        self.specialized_memory = {}
        
        # Initialize specialized capabilities
        self._initialize_specialized_capabilities()
        
        logger.info(f"Initialized specialized agent: {self.__class__.__name__}")
    
    @abstractmethod
    def _initialize_specialized_capabilities(self):
        """Initialize agent-specific capabilities"""
        pass
    
    @abstractmethod
    async def process_specialized_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task specific to this agent type"""
        pass
    
    @abstractmethod
    def get_specialized_prompt_additions(self) -> str:
        """Get additional prompt content specific to this agent"""
        pass
    
    async def enhanced_process_message(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Enhanced message processing with specialized capabilities"""
        
        # Check if this is a specialized task
        task_type = self._identify_task_type(message)
        
        if task_type and task_type in self.get_supported_task_types():
            # Process as specialized task
            task = {
                'type': task_type,
                'message': message,
                'context': context or {}
            }
            return await self.process_specialized_task(task)
        else:
            # Use standard agent processing with enhanced prompt
            enhanced_prompt = self._build_enhanced_system_prompt()
            
            # Temporarily update the agent's system prompt
            original_prompt = self.agent_instance.template.system_prompt
            self.agent_instance.template.system_prompt = enhanced_prompt
            
            try:
                result = await self.agent_instance.process_message(message, context)
                return result
            finally:
                # Restore original prompt
                self.agent_instance.template.system_prompt = original_prompt
    
    def _build_enhanced_system_prompt(self) -> str:
        """Build enhanced system prompt with specialized additions"""
        base_prompt = self.agent_instance.template.system_prompt
        specialized_additions = self.get_specialized_prompt_additions()
        
        return f"{base_prompt}\n\n{specialized_additions}"
    
    def _identify_task_type(self, message: str) -> Optional[str]:
        """Identify if message contains a specialized task"""
        message_lower = message.lower()
        
        # Check against supported task types
        for task_type in self.get_supported_task_types():
            keywords = self.get_task_type_keywords(task_type)
            if any(keyword in message_lower for keyword in keywords):
                return task_type
        
        return None
    
    @abstractmethod
    def get_supported_task_types(self) -> List[str]:
        """Get list of supported specialized task types"""
        pass
    
    @abstractmethod
    def get_task_type_keywords(self, task_type: str) -> List[str]:
        """Get keywords that identify a specific task type"""
        pass
    
    def add_specialized_tool(self, name: str, tool_func, description: str):
        """Add a specialized tool for this agent"""
        self.specialized_tools[name] = {
            'function': tool_func,
            'description': description,
            'added_at': datetime.utcnow()
        }
    
    def get_specialized_tools(self) -> Dict[str, Any]:
        """Get all specialized tools"""
        return self.specialized_tools
    
    def store_specialized_memory(self, key: str, value: Any):
        """Store specialized memory"""
        self.specialized_memory[key] = {
            'value': value,
            'stored_at': datetime.utcnow()
        }
    
    def get_specialized_memory(self, key: str) -> Any:
        """Get specialized memory"""
        memory_item = self.specialized_memory.get(key)
        return memory_item['value'] if memory_item else None
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get enhanced agent status including specialized info"""
        base_status = self.agent_instance.get_status()
        
        specialized_status = {
            'specialized_type': self.__class__.__name__,
            'supported_task_types': self.get_supported_task_types(),
            'specialized_tools_count': len(self.specialized_tools),
            'specialized_memory_items': len(self.specialized_memory)
        }
        
        return {**base_status, **specialized_status}
