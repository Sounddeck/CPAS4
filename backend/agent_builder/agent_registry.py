
"""
Agent Registry for Managing Agent Instances and Metadata
"""

import asyncio
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from loguru import logger
from collections import defaultdict

from .agent_factory import AgentInstance
from ..models.agent import AgentStatus

class AgentRegistry:
    """Central registry for managing all agent instances"""
    
    def __init__(self, database):
        self.db = database
        self.collection_name = "agent_registry"
        
        # In-memory tracking
        self.registered_agents: Dict[str, Dict[str, Any]] = {}
        self.agent_relationships: Dict[str, Set[str]] = defaultdict(set)
        self.agent_groups: Dict[str, Set[str]] = defaultdict(set)
        self.agent_tags: Dict[str, Set[str]] = defaultdict(set)
        
        # Performance tracking
        self.performance_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        logger.info("Agent Registry initialized")
    
    async def register_agent(self, 
                           agent_instance: AgentInstance,
                           metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Register an agent instance in the registry"""
        
        agent_id = agent_instance.agent_id
        
        # Prepare registration data
        registration_data = {
            'agent_id': agent_id,
            'template_id': agent_instance.config.get('template_id'),
            'template_name': agent_instance.template.name,
            'agent_name': agent_instance.config.get('name'),
            'category': agent_instance.template.category,
            'capabilities': [cap.value for cap in agent_instance.template.capabilities],
            'status': agent_instance.status.value,
            'created_at': agent_instance.created_at,
            'last_active': agent_instance.last_active,
            'task_count': agent_instance.task_count,
            'error_count': agent_instance.error_count,
            'metadata': metadata or {},
            'registered_at': datetime.utcnow()
        }
        
        try:
            # Store in database
            await self.db.create_document(self.collection_name, registration_data)
            
            # Store in memory
            self.registered_agents[agent_id] = registration_data
            
            # Add to category-based grouping
            category = agent_instance.template.category
            self.agent_groups[category].add(agent_id)
            
            # Add capability tags
            for capability in agent_instance.template.capabilities:
                self.agent_tags[capability.value].add(agent_id)
            
            logger.info(f"Registered agent {agent_id} ({agent_instance.template.name})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {e}")
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the registry"""
        try:
            # Remove from database
            await self.db.delete_document(self.collection_name, agent_id)
            
            # Remove from memory structures
            if agent_id in self.registered_agents:
                agent_data = self.registered_agents[agent_id]
                
                # Remove from groups
                category = agent_data.get('category')
                if category and agent_id in self.agent_groups[category]:
                    self.agent_groups[category].remove(agent_id)
                
                # Remove from tags
                capabilities = agent_data.get('capabilities', [])
                for capability in capabilities:
                    if agent_id in self.agent_tags[capability]:
                        self.agent_tags[capability].remove(agent_id)
                
                # Remove from relationships
                if agent_id in self.agent_relationships:
                    del self.agent_relationships[agent_id]
                
                # Remove from performance history
                if agent_id in self.performance_history:
                    del self.performance_history[agent_id]
                
                # Remove main registration
                del self.registered_agents[agent_id]
            
            logger.info(f"Unregistered agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False
    
    async def update_agent_status(self, agent_id: str, status: AgentStatus, metadata: Optional[Dict] = None) -> bool:
        """Update agent status in registry"""
        if agent_id not in self.registered_agents:
            return False
        
        try:
            updates = {
                'status': status.value,
                'last_updated': datetime.utcnow()
            }
            
            if metadata:
                updates['metadata'] = metadata
            
            # Update database
            await self.db.update_document(self.collection_name, agent_id, updates)
            
            # Update memory
            self.registered_agents[agent_id].update(updates)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update agent status {agent_id}: {e}")
            return False
    
    async def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent information from registry"""
        if agent_id in self.registered_agents:
            return self.registered_agents[agent_id].copy()
        
        # Try to load from database
        try:
            agent_data = await self.db.get_document(self.collection_name, agent_id)
            if agent_data:
                self.registered_agents[agent_id] = agent_data
                return agent_data
        except Exception as e:
            logger.error(f"Failed to get agent info {agent_id}: {e}")
        
        return None
    
    async def find_agents_by_capability(self, capability: str) -> List[str]:
        """Find agents with specific capability"""
        return list(self.agent_tags.get(capability, set()))
    
    async def find_agents_by_category(self, category: str) -> List[str]:
        """Find agents in specific category"""
        return list(self.agent_groups.get(category, set()))
    
    async def find_agents_by_status(self, status: AgentStatus) -> List[str]:
        """Find agents with specific status"""
        matching_agents = []
        for agent_id, agent_data in self.registered_agents.items():
            if agent_data.get('status') == status.value:
                matching_agents.append(agent_id)
        return matching_agents
    
    async def get_available_agents(self, 
                                 capability: Optional[str] = None,
                                 category: Optional[str] = None,
                                 exclude_busy: bool = True) -> List[str]:
        """Get list of available agents for task assignment"""
        
        candidate_agents = set(self.registered_agents.keys())
        
        # Filter by capability
        if capability:
            capability_agents = set(await self.find_agents_by_capability(capability))
            candidate_agents &= capability_agents
        
        # Filter by category
        if category:
            category_agents = set(await self.find_agents_by_category(category))
            candidate_agents &= category_agents
        
        # Filter out busy agents
        if exclude_busy:
            busy_agents = set(await self.find_agents_by_status(AgentStatus.BUSY))
            candidate_agents -= busy_agents
        
        return list(candidate_agents)
    
    async def create_agent_relationship(self, agent1_id: str, agent2_id: str, relationship_type: str = "collaborates") -> bool:
        """Create relationship between two agents"""
        if agent1_id not in self.registered_agents or agent2_id not in self.registered_agents:
            return False
        
        # Add bidirectional relationship
        self.agent_relationships[agent1_id].add(agent2_id)
        self.agent_relationships[agent2_id].add(agent1_id)
        
        # Store in database
        relationship_data = {
            'agent1_id': agent1_id,
            'agent2_id': agent2_id,
            'relationship_type': relationship_type,
            'created_at': datetime.utcnow()
        }
        
        try:
            await self.db.create_document("agent_relationships", relationship_data)
            logger.info(f"Created relationship between {agent1_id} and {agent2_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create agent relationship: {e}")
            return False
    
    async def get_agent_collaborators(self, agent_id: str) -> List[str]:
        """Get list of agents that collaborate with given agent"""
        return list(self.agent_relationships.get(agent_id, set()))
    
    async def record_performance_metric(self, agent_id: str, metric_data: Dict[str, Any]):
        """Record performance metric for an agent"""
        if agent_id not in self.registered_agents:
            return
        
        metric_entry = {
            'timestamp': datetime.utcnow(),
            'agent_id': agent_id,
            **metric_data
        }
        
        # Store in memory (keep last 100 entries)
        self.performance_history[agent_id].append(metric_entry)
        if len(self.performance_history[agent_id]) > 100:
            self.performance_history[agent_id] = self.performance_history[agent_id][-100:]
        
        # Store in database
        try:
            await self.db.create_document("agent_performance", metric_entry)
        except Exception as e:
            logger.error(f"Failed to record performance metric: {e}")
    
    async def get_agent_performance_history(self, agent_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get performance history for an agent"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter recent metrics
        recent_metrics = []
        for metric in self.performance_history.get(agent_id, []):
            if metric['timestamp'] > cutoff_time:
                recent_metrics.append(metric)
        
        return recent_metrics
    
    async def get_registry_statistics(self) -> Dict[str, Any]:
        """Get overall registry statistics"""
        total_agents = len(self.registered_agents)
        
        # Count by status
        status_counts = defaultdict(int)
        for agent_data in self.registered_agents.values():
            status_counts[agent_data.get('status', 'unknown')] += 1
        
        # Count by category
        category_counts = {category: len(agents) for category, agents in self.agent_groups.items()}
        
        # Count by capability
        capability_counts = {capability: len(agents) for capability, agents in self.agent_tags.items()}
        
        # Calculate total tasks and errors
        total_tasks = sum(agent_data.get('task_count', 0) for agent_data in self.registered_agents.values())
        total_errors = sum(agent_data.get('error_count', 0) for agent_data in self.registered_agents.values())
        
        return {
            'total_agents': total_agents,
            'status_distribution': dict(status_counts),
            'category_distribution': category_counts,
            'capability_distribution': capability_counts,
            'total_tasks_processed': total_tasks,
            'total_errors': total_errors,
            'overall_error_rate': total_errors / max(total_tasks, 1),
            'total_relationships': sum(len(relations) for relations in self.agent_relationships.values()) // 2,
            'performance_entries': sum(len(history) for history in self.performance_history.values())
        }
    
    async def find_best_agent_for_task(self, 
                                     task_description: str,
                                     required_capabilities: List[str],
                                     preferred_category: Optional[str] = None) -> Optional[str]:
        """Find the best agent for a specific task"""
        
        # Get candidate agents
        candidates = set(self.registered_agents.keys())
        
        # Filter by required capabilities
        for capability in required_capabilities:
            capability_agents = set(await self.find_agents_by_capability(capability))
            candidates &= capability_agents
        
        # Filter by preferred category
        if preferred_category:
            category_agents = set(await self.find_agents_by_category(preferred_category))
            candidates &= category_agents
        
        # Filter out busy agents
        available_candidates = []
        for agent_id in candidates:
            agent_data = self.registered_agents[agent_id]
            if agent_data.get('status') not in [AgentStatus.BUSY.value, AgentStatus.ERROR.value]:
                available_candidates.append(agent_id)
        
        if not available_candidates:
            return None
        
        # Score candidates based on performance and suitability
        best_agent = None
        best_score = -1
        
        for agent_id in available_candidates:
            score = await self._calculate_agent_suitability_score(agent_id, task_description)
            if score > best_score:
                best_score = score
                best_agent = agent_id
        
        return best_agent
    
    async def _calculate_agent_suitability_score(self, agent_id: str, task_description: str) -> float:
        """Calculate suitability score for an agent for a specific task"""
        agent_data = self.registered_agents[agent_id]
        
        # Base score
        score = 0.5
        
        # Performance-based scoring
        task_count = agent_data.get('task_count', 0)
        error_count = agent_data.get('error_count', 0)
        
        if task_count > 0:
            success_rate = 1 - (error_count / task_count)
            score += success_rate * 0.3
        
        # Recency bonus (more recently active agents get higher score)
        last_active = agent_data.get('last_active')
        if last_active:
            if isinstance(last_active, str):
                last_active = datetime.fromisoformat(last_active.replace('Z', '+00:00'))
            
            hours_since_active = (datetime.utcnow() - last_active).total_seconds() / 3600
            recency_bonus = max(0, 0.2 - (hours_since_active / 24) * 0.2)
            score += recency_bonus
        
        # Experience bonus (agents with more tasks get slight bonus)
        experience_bonus = min(0.1, task_count / 100 * 0.1)
        score += experience_bonus
        
        return score
    
    async def cleanup_stale_registrations(self, max_age_hours: int = 168) -> int:  # 1 week
        """Clean up stale agent registrations"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        stale_agents = []
        
        for agent_id, agent_data in self.registered_agents.items():
            last_active = agent_data.get('last_active')
            if last_active:
                if isinstance(last_active, str):
                    last_active = datetime.fromisoformat(last_active.replace('Z', '+00:00'))
                
                if last_active < cutoff_time:
                    stale_agents.append(agent_id)
        
        # Remove stale registrations
        for agent_id in stale_agents:
            await self.unregister_agent(agent_id)
        
        logger.info(f"Cleaned up {len(stale_agents)} stale agent registrations")
        return len(stale_agents)
