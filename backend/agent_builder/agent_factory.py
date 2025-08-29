
"""
Agent Factory for Dynamic Agent Instantiation
"""

import uuid
import asyncio
from typing import Dict, List, Optional, Any, Type
from datetime import datetime
from loguru import logger

from .agent_template import AgentTemplate, AgentTemplateManager
from ..models.agent import Agent, AgentStatus, AgentType
from ..services.llm_service import LLMService

class AgentInstance:
    """Runtime instance of an agent"""
    
    def __init__(self, 
                 agent_id: str,
                 template: AgentTemplate,
                 config: Dict[str, Any],
                 llm_service: LLMService):
        self.agent_id = agent_id
        self.template = template
        self.config = config
        self.llm_service = llm_service
        
        # Runtime state
        self.status = AgentStatus.IDLE
        self.created_at = datetime.utcnow()
        self.last_active = None
        self.task_count = 0
        self.error_count = 0
        self.performance_metrics = {}
        
        # Agent memory and context
        self.conversation_history = []
        self.working_memory = {}
        self.learned_preferences = {}
        
        logger.info(f"Agent instance created: {agent_id} from template {template.name}")
    
    async def process_message(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a message using this agent instance"""
        try:
            self.status = AgentStatus.ACTIVE
            self.last_active = datetime.utcnow()
            
            # Prepare the prompt with agent personality and context
            system_prompt = self._build_system_prompt(context)
            
            # Add conversation history for context
            conversation_context = self._build_conversation_context()
            
            # Generate response using LLM service
            response = await self.llm_service.generate_response(
                prompt=message,
                system_prompt=system_prompt,
                context=conversation_context,
                model=self.config.get('model', 'llama3.2:3b'),
                temperature=self.template.temperature,
                max_tokens=self.template.max_tokens
            )
            
            # Update conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            self.conversation_history.append({
                'role': 'assistant', 
                'content': response['content'],
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Keep conversation history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            self.task_count += 1
            self.status = AgentStatus.IDLE
            
            return {
                'success': True,
                'response': response['content'],
                'agent_id': self.agent_id,
                'template_name': self.template.name,
                'processing_time': response.get('processing_time', 0),
                'metadata': {
                    'task_count': self.task_count,
                    'agent_status': self.status.value
                }
            }
            
        except Exception as e:
            self.error_count += 1
            self.status = AgentStatus.ERROR
            logger.error(f"Agent {self.agent_id} processing failed: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'agent_id': self.agent_id,
                'template_name': self.template.name
            }
    
    def _build_system_prompt(self, context: Optional[Dict] = None) -> str:
        """Build system prompt with agent personality and context"""
        base_prompt = self.template.system_prompt
        
        # Add personality traits
        personality_info = f"""
Agent Personality:
- Name: {self.template.personality.name}
- Traits: {', '.join(self.template.personality.traits)}
- Communication Style: {self.template.personality.communication_style}
- Expertise Level: {self.template.personality.expertise_level}
- Response Tone: {self.template.personality.response_tone}

Agent Skills:
- Primary: {', '.join(self.template.skills.primary_skills)}
- Knowledge Domains: {', '.join(self.template.skills.knowledge_domains)}

Agent Behavior:
- Proactive: {self.template.behavior.proactive}
- Collaborative: {self.template.behavior.collaborative}
- Learning Enabled: {self.template.behavior.learning_enabled}
"""
        
        # Add context if provided
        context_info = ""
        if context:
            context_info = f"\nCurrent Context:\n{context}"
        
        return f"{base_prompt}\n\n{personality_info}{context_info}"
    
    def _build_conversation_context(self) -> str:
        """Build conversation context from history"""
        if not self.conversation_history:
            return ""
        
        # Get last few messages for context
        recent_messages = self.conversation_history[-6:]
        context_lines = []
        
        for msg in recent_messages:
            role = msg['role'].title()
            content = msg['content'][:200]  # Truncate long messages
            context_lines.append(f"{role}: {content}")
        
        return "\n".join(context_lines)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            'agent_id': self.agent_id,
            'template_name': self.template.name,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'task_count': self.task_count,
            'error_count': self.error_count,
            'conversation_length': len(self.conversation_history)
        }
    
    def update_learned_preferences(self, preferences: Dict[str, Any]):
        """Update learned user preferences"""
        self.learned_preferences.update(preferences)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        uptime = (datetime.utcnow() - self.created_at).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'total_tasks': self.task_count,
            'error_rate': self.error_count / max(self.task_count, 1),
            'avg_tasks_per_hour': self.task_count / max(uptime / 3600, 1),
            'last_active': self.last_active.isoformat() if self.last_active else None
        }

class AgentFactory:
    """Factory for creating and managing agent instances"""
    
    def __init__(self, template_manager: AgentTemplateManager, llm_service: LLMService):
        self.template_manager = template_manager
        self.llm_service = llm_service
        self.active_agents: Dict[str, AgentInstance] = {}
        self.agent_configs: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Agent Factory initialized")
    
    async def create_agent(self, 
                          template_id: str,
                          agent_name: Optional[str] = None,
                          custom_config: Optional[Dict[str, Any]] = None) -> str:
        """Create a new agent instance from template"""
        
        # Get the template
        template = await self.template_manager.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Generate unique agent ID
        agent_id = str(uuid.uuid4())
        
        # Prepare agent configuration
        config = {
            'model': 'llama3.2:3b',
            'name': agent_name or f"{template.name}_{agent_id[:8]}",
            'template_id': template_id
        }
        
        if custom_config:
            config.update(custom_config)
        
        # Create agent instance
        agent_instance = AgentInstance(
            agent_id=agent_id,
            template=template,
            config=config,
            llm_service=self.llm_service
        )
        
        # Store the agent
        self.active_agents[agent_id] = agent_instance
        self.agent_configs[agent_id] = config
        
        # Increment template usage
        await self.template_manager.increment_usage(template_id)
        
        logger.info(f"Created agent {agent_id} from template {template.name}")
        return agent_id
    
    async def get_agent(self, agent_id: str) -> Optional[AgentInstance]:
        """Get agent instance by ID"""
        return self.active_agents.get(agent_id)
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent instance"""
        if agent_id in self.active_agents:
            del self.active_agents[agent_id]
            if agent_id in self.agent_configs:
                del self.agent_configs[agent_id]
            logger.info(f"Deleted agent {agent_id}")
            return True
        return False
    
    async def list_active_agents(self) -> List[Dict[str, Any]]:
        """List all active agents"""
        agents_info = []
        for agent_id, agent in self.active_agents.items():
            agents_info.append(agent.get_status())
        return agents_info
    
    async def get_agent_by_name(self, name: str) -> Optional[AgentInstance]:
        """Get agent by name"""
        for agent in self.active_agents.values():
            if agent.config.get('name') == name:
                return agent
        return None
    
    async def create_agent_from_predefined(self, 
                                         template_key: str,
                                         agent_name: Optional[str] = None,
                                         creator: str = "system") -> str:
        """Create agent from predefined template"""
        from .agent_template import PREDEFINED_TEMPLATES
        
        if template_key not in PREDEFINED_TEMPLATES:
            raise ValueError(f"Predefined template not found: {template_key}")
        
        # Create template from predefined data
        template_data = PREDEFINED_TEMPLATES[template_key].copy()
        template_data['created_by'] = creator
        template_data['template_id'] = str(uuid.uuid4())
        
        template = AgentTemplate(**template_data)
        
        # Store template if not exists
        existing_template = await self.template_manager.get_template(template.template_id)
        if not existing_template:
            await self.template_manager.create_template(template)
        
        # Create agent instance
        return await self.create_agent(template.template_id, agent_name)
    
    async def clone_agent(self, source_agent_id: str, new_name: Optional[str] = None) -> str:
        """Clone an existing agent"""
        source_agent = self.active_agents.get(source_agent_id)
        if not source_agent:
            raise ValueError(f"Source agent not found: {source_agent_id}")
        
        # Create new agent from same template
        new_agent_id = await self.create_agent(
            template_id=source_agent.config['template_id'],
            agent_name=new_name,
            custom_config=source_agent.config.copy()
        )
        
        # Copy learned preferences
        new_agent = self.active_agents[new_agent_id]
        new_agent.learned_preferences = source_agent.learned_preferences.copy()
        
        return new_agent_id
    
    async def update_agent_config(self, agent_id: str, config_updates: Dict[str, Any]) -> bool:
        """Update agent configuration"""
        if agent_id not in self.active_agents:
            return False
        
        self.agent_configs[agent_id].update(config_updates)
        return True
    
    async def get_agents_by_template(self, template_id: str) -> List[AgentInstance]:
        """Get all agents created from a specific template"""
        agents = []
        for agent in self.active_agents.values():
            if agent.config.get('template_id') == template_id:
                agents.append(agent)
        return agents
    
    async def get_agent_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary of all agents"""
        total_agents = len(self.active_agents)
        active_agents = sum(1 for agent in self.active_agents.values() 
                          if agent.status == AgentStatus.ACTIVE)
        total_tasks = sum(agent.task_count for agent in self.active_agents.values())
        total_errors = sum(agent.error_count for agent in self.active_agents.values())
        
        return {
            'total_agents': total_agents,
            'active_agents': active_agents,
            'idle_agents': total_agents - active_agents,
            'total_tasks_processed': total_tasks,
            'total_errors': total_errors,
            'overall_error_rate': total_errors / max(total_tasks, 1),
            'agents_by_template': self._get_agents_by_template_summary()
        }
    
    def _get_agents_by_template_summary(self) -> Dict[str, int]:
        """Get count of agents by template"""
        template_counts = {}
        for agent in self.active_agents.values():
            template_name = agent.template.name
            template_counts[template_name] = template_counts.get(template_name, 0) + 1
        return template_counts
    
    async def cleanup_inactive_agents(self, max_idle_hours: int = 24) -> int:
        """Clean up agents that have been inactive for too long"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_idle_hours)
        agents_to_remove = []
        
        for agent_id, agent in self.active_agents.items():
            if (agent.last_active is None or agent.last_active < cutoff_time) and \
               agent.status == AgentStatus.IDLE:
                agents_to_remove.append(agent_id)
        
        for agent_id in agents_to_remove:
            await self.delete_agent(agent_id)
        
        logger.info(f"Cleaned up {len(agents_to_remove)} inactive agents")
        return len(agents_to_remove)
