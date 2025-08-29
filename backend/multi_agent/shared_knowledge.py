
"""
Shared Knowledge Base for Multi-Agent Systems
Provides centralized knowledge storage and retrieval for all agents
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from loguru import logger
import uuid

class KnowledgeType(str, Enum):
    """Types of knowledge in the system"""
    FACTUAL = "factual"
    PROCEDURAL = "procedural"
    EXPERIENTIAL = "experiential"
    CONTEXTUAL = "contextual"
    COLLABORATIVE = "collaborative"
    LEARNED = "learned"

class AccessLevel(str, Enum):
    """Access levels for knowledge items"""
    PUBLIC = "public"
    RESTRICTED = "restricted"
    PRIVATE = "private"
    SYSTEM = "system"

@dataclass
class KnowledgeItem:
    """Individual knowledge item"""
    knowledge_id: str
    knowledge_type: KnowledgeType
    title: str
    content: Dict[str, Any]
    tags: List[str]
    source_agent_id: str
    access_level: AccessLevel
    created_at: datetime
    updated_at: datetime
    version: int = 1
    confidence: float = 1.0
    usage_count: int = 0
    related_items: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.related_items is None:
            self.related_items = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeItem':
        """Create from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)

class SharedKnowledgeBase:
    """Centralized knowledge base for multi-agent systems"""
    
    def __init__(self, database, memory_service=None):
        self.db = database
        self.memory_service = memory_service
        self.collection_name = "shared_knowledge"
        
        # In-memory knowledge cache for fast access
        self.knowledge_cache: Dict[str, KnowledgeItem] = {}
        self.tag_index: Dict[str, Set[str]] = {}
        self.agent_knowledge: Dict[str, Set[str]] = {}
        
        # Knowledge relationships and graph
        self.knowledge_graph: Dict[str, Set[str]] = {}
        self.similarity_index: Dict[str, List[Tuple[str, float]]] = {}
        
        # Access control and permissions
        self.agent_permissions: Dict[str, Set[AccessLevel]] = {}
        self.knowledge_subscriptions: Dict[str, Set[str]] = {}  # agent_id -> knowledge_ids
        
        # Learning and adaptation
        self.knowledge_patterns: Dict[str, Any] = {}
        self.usage_analytics: Dict[str, Dict[str, Any]] = {}
        
        # Background tasks
        self.cache_refresh_task = None
        self.analytics_task = None
        
        logger.info("Shared Knowledge Base initialized")
    
    async def start(self):
        """Start knowledge base services"""
        # Load initial knowledge cache
        await self._load_knowledge_cache()
        
        # Start background tasks
        self.cache_refresh_task = asyncio.create_task(self._refresh_cache_periodically())
        self.analytics_task = asyncio.create_task(self._update_analytics_periodically())
        
        logger.info("Shared Knowledge Base services started")
    
    async def stop(self):
        """Stop knowledge base services"""
        if self.cache_refresh_task:
            self.cache_refresh_task.cancel()
        
        if self.analytics_task:
            self.analytics_task.cancel()
        
        # Save cache to database
        await self._save_cache_to_database()
        
        logger.info("Shared Knowledge Base services stopped")
    
    async def store_knowledge(self,
                            source_agent_id: str,
                            knowledge_type: KnowledgeType,
                            title: str,
                            content: Dict[str, Any],
                            tags: List[str] = None,
                            access_level: AccessLevel = AccessLevel.PUBLIC,
                            confidence: float = 1.0,
                            metadata: Dict[str, Any] = None) -> str:
        """Store new knowledge item"""
        
        knowledge_id = str(uuid.uuid4())
        
        knowledge_item = KnowledgeItem(
            knowledge_id=knowledge_id,
            knowledge_type=knowledge_type,
            title=title,
            content=content,
            tags=tags or [],
            source_agent_id=source_agent_id,
            access_level=access_level,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            confidence=confidence,
            metadata=metadata or {}
        )
        
        # Store in database
        await self._store_knowledge_item(knowledge_item)
        
        # Update cache and indices
        self.knowledge_cache[knowledge_id] = knowledge_item
        await self._update_indices(knowledge_item)
        
        # Update agent knowledge tracking
        if source_agent_id not in self.agent_knowledge:
            self.agent_knowledge[source_agent_id] = set()
        self.agent_knowledge[source_agent_id].add(knowledge_id)
        
        # Notify subscribers
        await self._notify_knowledge_subscribers(knowledge_item, "created")
        
        logger.info(f"Knowledge item {knowledge_id} stored by agent {source_agent_id}")
        return knowledge_id
    
    async def retrieve_knowledge(self,
                               requester_agent_id: str,
                               knowledge_id: str) -> Optional[KnowledgeItem]:
        """Retrieve specific knowledge item"""
        
        # Check cache first
        if knowledge_id in self.knowledge_cache:
            knowledge_item = self.knowledge_cache[knowledge_id]
        else:
            # Load from database
            knowledge_data = await self.db.get_document(self.collection_name, knowledge_id)
            if not knowledge_data:
                return None
            
            knowledge_item = KnowledgeItem.from_dict(knowledge_data)
            self.knowledge_cache[knowledge_id] = knowledge_item
        
        # Check access permissions
        if not await self._check_access_permission(requester_agent_id, knowledge_item):
            logger.warning(f"Agent {requester_agent_id} denied access to knowledge {knowledge_id}")
            return None
        
        # Update usage statistics
        knowledge_item.usage_count += 1
        await self._update_usage_analytics(requester_agent_id, knowledge_item)
        
        return knowledge_item
    
    async def search_knowledge(self,
                             requester_agent_id: str,
                             query: str,
                             knowledge_types: List[KnowledgeType] = None,
                             tags: List[str] = None,
                             limit: int = 20) -> List[KnowledgeItem]:
        """Search knowledge base"""
        
        # Build search filters
        filters = {}
        
        if knowledge_types:
            filters['knowledge_type'] = {'$in': [kt.value for kt in knowledge_types]}
        
        if tags:
            filters['tags'] = {'$in': tags}
        
        # Add text search
        if query:
            filters['$or'] = [
                {'title': {'$regex': query, '$options': 'i'}},
                {'content': {'$regex': query, '$options': 'i'}},
                {'tags': {'$regex': query, '$options': 'i'}}
            ]
        
        try:
            # Search database
            knowledge_data = await self.db.find_documents(
                self.collection_name,
                filters,
                limit=limit,
                sort=[('confidence', -1), ('usage_count', -1)]
            )
            
            # Convert to knowledge items and filter by access
            results = []
            for data in knowledge_data:
                knowledge_item = KnowledgeItem.from_dict(data)
                
                if await self._check_access_permission(requester_agent_id, knowledge_item):
                    results.append(knowledge_item)
                    
                    # Update cache
                    self.knowledge_cache[knowledge_item.knowledge_id] = knowledge_item
            
            # Update search analytics
            await self._update_search_analytics(requester_agent_id, query, len(results))
            
            return results
            
        except Exception as e:
            logger.error(f"Knowledge search failed: {e}")
            return []
    
    async def update_knowledge(self,
                             requester_agent_id: str,
                             knowledge_id: str,
                             updates: Dict[str, Any]) -> bool:
        """Update existing knowledge item"""
        
        # Get existing knowledge
        knowledge_item = await self.retrieve_knowledge(requester_agent_id, knowledge_id)
        if not knowledge_item:
            return False
        
        # Check if agent can update (must be owner or have system access)
        if (knowledge_item.source_agent_id != requester_agent_id and 
            not await self._has_system_access(requester_agent_id)):
            logger.warning(f"Agent {requester_agent_id} denied update access to knowledge {knowledge_id}")
            return False
        
        # Apply updates
        for field, value in updates.items():
            if hasattr(knowledge_item, field):
                setattr(knowledge_item, field, value)
        
        knowledge_item.updated_at = datetime.utcnow()
        knowledge_item.version += 1
        
        # Update database
        await self._update_knowledge_item(knowledge_item)
        
        # Update cache and indices
        self.knowledge_cache[knowledge_id] = knowledge_item
        await self._update_indices(knowledge_item)
        
        # Notify subscribers
        await self._notify_knowledge_subscribers(knowledge_item, "updated")
        
        logger.info(f"Knowledge item {knowledge_id} updated by agent {requester_agent_id}")
        return True
    
    async def delete_knowledge(self,
                             requester_agent_id: str,
                             knowledge_id: str) -> bool:
        """Delete knowledge item"""
        
        # Get existing knowledge
        knowledge_item = await self.retrieve_knowledge(requester_agent_id, knowledge_id)
        if not knowledge_item:
            return False
        
        # Check if agent can delete (must be owner or have system access)
        if (knowledge_item.source_agent_id != requester_agent_id and 
            not await self._has_system_access(requester_agent_id)):
            logger.warning(f"Agent {requester_agent_id} denied delete access to knowledge {knowledge_id}")
            return False
        
        # Delete from database
        await self.db.delete_document(self.collection_name, knowledge_id)
        
        # Remove from cache and indices
        if knowledge_id in self.knowledge_cache:
            del self.knowledge_cache[knowledge_id]
        
        await self._remove_from_indices(knowledge_item)
        
        # Update agent knowledge tracking
        if requester_agent_id in self.agent_knowledge:
            self.agent_knowledge[requester_agent_id].discard(knowledge_id)
        
        # Notify subscribers
        await self._notify_knowledge_subscribers(knowledge_item, "deleted")
        
        logger.info(f"Knowledge item {knowledge_id} deleted by agent {requester_agent_id}")
        return True
    
    async def get_related_knowledge(self,
                                  requester_agent_id: str,
                                  knowledge_id: str,
                                  limit: int = 10) -> List[KnowledgeItem]:
        """Get knowledge items related to a specific item"""
        
        knowledge_item = await self.retrieve_knowledge(requester_agent_id, knowledge_id)
        if not knowledge_item:
            return []
        
        related_items = []
        
        # Get explicitly related items
        for related_id in knowledge_item.related_items:
            related_item = await self.retrieve_knowledge(requester_agent_id, related_id)
            if related_item:
                related_items.append(related_item)
        
        # Get similar items based on tags and content
        similar_items = await self._find_similar_knowledge(requester_agent_id, knowledge_item, limit - len(related_items))
        related_items.extend(similar_items)
        
        return related_items[:limit]
    
    async def subscribe_to_knowledge(self,
                                   agent_id: str,
                                   knowledge_types: List[KnowledgeType] = None,
                                   tags: List[str] = None) -> bool:
        """Subscribe agent to knowledge updates"""
        
        subscription_key = f"{agent_id}_{datetime.utcnow().timestamp()}"
        
        subscription_info = {
            'agent_id': agent_id,
            'knowledge_types': [kt.value for kt in knowledge_types] if knowledge_types else [],
            'tags': tags or [],
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Store subscription
        await self.db.create_document("knowledge_subscriptions", subscription_info)
        
        # Update in-memory subscriptions
        if agent_id not in self.knowledge_subscriptions:
            self.knowledge_subscriptions[agent_id] = set()
        
        logger.info(f"Agent {agent_id} subscribed to knowledge updates")
        return True
    
    async def get_knowledge_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        
        total_knowledge = len(self.knowledge_cache)
        
        # Count by type
        type_counts = {}
        for item in self.knowledge_cache.values():
            knowledge_type = item.knowledge_type.value
            type_counts[knowledge_type] = type_counts.get(knowledge_type, 0) + 1
        
        # Count by access level
        access_counts = {}
        for item in self.knowledge_cache.values():
            access_level = item.access_level.value
            access_counts[access_level] = access_counts.get(access_level, 0) + 1
        
        # Agent contributions
        agent_contributions = {}
        for agent_id, knowledge_ids in self.agent_knowledge.items():
            agent_contributions[agent_id] = len(knowledge_ids)
        
        # Most used knowledge
        most_used = sorted(
            self.knowledge_cache.values(),
            key=lambda x: x.usage_count,
            reverse=True
        )[:10]
        
        most_used_info = [
            {
                'knowledge_id': item.knowledge_id,
                'title': item.title,
                'usage_count': item.usage_count,
                'confidence': item.confidence
            }
            for item in most_used
        ]
        
        return {
            'total_knowledge_items': total_knowledge,
            'knowledge_by_type': type_counts,
            'knowledge_by_access_level': access_counts,
            'agent_contributions': agent_contributions,
            'most_used_knowledge': most_used_info,
            'total_tags': len(self.tag_index),
            'cache_size': len(self.knowledge_cache)
        }
    
    async def export_agent_knowledge(self, agent_id: str) -> Dict[str, Any]:
        """Export all knowledge created by an agent"""
        
        if agent_id not in self.agent_knowledge:
            return {'knowledge_items': []}
        
        knowledge_items = []
        for knowledge_id in self.agent_knowledge[agent_id]:
            if knowledge_id in self.knowledge_cache:
                knowledge_items.append(self.knowledge_cache[knowledge_id].to_dict())
        
        return {
            'agent_id': agent_id,
            'knowledge_count': len(knowledge_items),
            'knowledge_items': knowledge_items,
            'exported_at': datetime.utcnow().isoformat()
        }
    
    async def import_knowledge_batch(self,
                                   requester_agent_id: str,
                                   knowledge_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Import multiple knowledge items"""
        
        imported_count = 0
        failed_count = 0
        imported_ids = []
        
        for item_data in knowledge_items:
            try:
                # Create knowledge item
                knowledge_id = await self.store_knowledge(
                    source_agent_id=requester_agent_id,
                    knowledge_type=KnowledgeType(item_data['knowledge_type']),
                    title=item_data['title'],
                    content=item_data['content'],
                    tags=item_data.get('tags', []),
                    access_level=AccessLevel(item_data.get('access_level', 'public')),
                    confidence=item_data.get('confidence', 1.0),
                    metadata=item_data.get('metadata', {})
                )
                
                imported_ids.append(knowledge_id)
                imported_count += 1
                
            except Exception as e:
                logger.error(f"Failed to import knowledge item: {e}")
                failed_count += 1
        
        return {
            'imported_count': imported_count,
            'failed_count': failed_count,
            'imported_ids': imported_ids
        }
    
    async def _load_knowledge_cache(self):
        """Load knowledge items into cache"""
        try:
            # Load recent and frequently used knowledge
            knowledge_data = await self.db.find_documents(
                self.collection_name,
                {},
                limit=1000,  # Cache top 1000 items
                sort=[('usage_count', -1), ('updated_at', -1)]
            )
            
            for data in knowledge_data:
                knowledge_item = KnowledgeItem.from_dict(data)
                self.knowledge_cache[knowledge_item.knowledge_id] = knowledge_item
                await self._update_indices(knowledge_item)
            
            logger.info(f"Loaded {len(self.knowledge_cache)} knowledge items into cache")
            
        except Exception as e:
            logger.error(f"Failed to load knowledge cache: {e}")
    
    async def _update_indices(self, knowledge_item: KnowledgeItem):
        """Update search indices"""
        
        # Update tag index
        for tag in knowledge_item.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(knowledge_item.knowledge_id)
        
        # Update knowledge graph
        knowledge_id = knowledge_item.knowledge_id
        if knowledge_id not in self.knowledge_graph:
            self.knowledge_graph[knowledge_id] = set()
        
        for related_id in knowledge_item.related_items:
            self.knowledge_graph[knowledge_id].add(related_id)
            
            # Add bidirectional relationship
            if related_id not in self.knowledge_graph:
                self.knowledge_graph[related_id] = set()
            self.knowledge_graph[related_id].add(knowledge_id)
    
    async def _remove_from_indices(self, knowledge_item: KnowledgeItem):
        """Remove knowledge item from indices"""
        
        knowledge_id = knowledge_item.knowledge_id
        
        # Remove from tag index
        for tag in knowledge_item.tags:
            if tag in self.tag_index:
                self.tag_index[tag].discard(knowledge_id)
                if not self.tag_index[tag]:
                    del self.tag_index[tag]
        
        # Remove from knowledge graph
        if knowledge_id in self.knowledge_graph:
            # Remove relationships
            for related_id in self.knowledge_graph[knowledge_id]:
                if related_id in self.knowledge_graph:
                    self.knowledge_graph[related_id].discard(knowledge_id)
            
            del self.knowledge_graph[knowledge_id]
    
    async def _check_access_permission(self, agent_id: str, knowledge_item: KnowledgeItem) -> bool:
        """Check if agent has access to knowledge item"""
        
        # Public knowledge is accessible to all
        if knowledge_item.access_level == AccessLevel.PUBLIC:
            return True
        
        # Private knowledge only accessible to owner
        if knowledge_item.access_level == AccessLevel.PRIVATE:
            return knowledge_item.source_agent_id == agent_id
        
        # System knowledge requires system access
        if knowledge_item.access_level == AccessLevel.SYSTEM:
            return await self._has_system_access(agent_id)
        
        # Restricted knowledge requires specific permissions
        if knowledge_item.access_level == AccessLevel.RESTRICTED:
            agent_permissions = self.agent_permissions.get(agent_id, set())
            return AccessLevel.RESTRICTED in agent_permissions
        
        return False
    
    async def _has_system_access(self, agent_id: str) -> bool:
        """Check if agent has system-level access"""
        agent_permissions = self.agent_permissions.get(agent_id, set())
        return AccessLevel.SYSTEM in agent_permissions
    
    async def _find_similar_knowledge(self,
                                    requester_agent_id: str,
                                    reference_item: KnowledgeItem,
                                    limit: int) -> List[KnowledgeItem]:
        """Find knowledge items similar to reference item"""
        
        similar_items = []
        
        # Find items with overlapping tags
        reference_tags = set(reference_item.tags)
        
        for knowledge_id, knowledge_item in self.knowledge_cache.items():
            if knowledge_id == reference_item.knowledge_id:
                continue
            
            # Check access permission
            if not await self._check_access_permission(requester_agent_id, knowledge_item):
                continue
            
            # Calculate similarity based on tags
            item_tags = set(knowledge_item.tags)
            tag_overlap = len(reference_tags & item_tags)
            
            if tag_overlap > 0:
                similarity_score = tag_overlap / len(reference_tags | item_tags)
                similar_items.append((knowledge_item, similarity_score))
        
        # Sort by similarity and return top items
        similar_items.sort(key=lambda x: x[1], reverse=True)
        return [item for item, score in similar_items[:limit]]
    
    async def _notify_knowledge_subscribers(self, knowledge_item: KnowledgeItem, event_type: str):
        """Notify subscribers of knowledge changes"""
        
        # Get relevant subscribers
        relevant_subscribers = []
        
        for agent_id in self.knowledge_subscriptions:
            # Check if subscriber is interested in this type of knowledge
            # (Simplified - would implement more sophisticated matching)
            relevant_subscribers.append(agent_id)
        
        # Send notifications (would integrate with message bus)
        notification_data = {
            'event_type': event_type,
            'knowledge_id': knowledge_item.knowledge_id,
            'knowledge_type': knowledge_item.knowledge_type.value,
            'title': knowledge_item.title,
            'tags': knowledge_item.tags,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.debug(f"Notifying {len(relevant_subscribers)} subscribers of knowledge {event_type}")
    
    async def _update_usage_analytics(self, agent_id: str, knowledge_item: KnowledgeItem):
        """Update usage analytics"""
        
        if agent_id not in self.usage_analytics:
            self.usage_analytics[agent_id] = {
                'total_accesses': 0,
                'knowledge_types_accessed': {},
                'most_accessed_items': {}
            }
        
        analytics = self.usage_analytics[agent_id]
        analytics['total_accesses'] += 1
        
        # Track knowledge type access
        knowledge_type = knowledge_item.knowledge_type.value
        if knowledge_type not in analytics['knowledge_types_accessed']:
            analytics['knowledge_types_accessed'][knowledge_type] = 0
        analytics['knowledge_types_accessed'][knowledge_type] += 1
        
        # Track most accessed items
        knowledge_id = knowledge_item.knowledge_id
        if knowledge_id not in analytics['most_accessed_items']:
            analytics['most_accessed_items'][knowledge_id] = 0
        analytics['most_accessed_items'][knowledge_id] += 1
    
    async def _update_search_analytics(self, agent_id: str, query: str, result_count: int):
        """Update search analytics"""
        
        search_record = {
            'agent_id': agent_id,
            'query': query,
            'result_count': result_count,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store search analytics (simplified)
        logger.debug(f"Search analytics: {search_record}")
    
    async def _refresh_cache_periodically(self):
        """Periodically refresh knowledge cache"""
        while True:
            try:
                await asyncio.sleep(3600)  # Refresh every hour
                
                # Remove least used items if cache is too large
                if len(self.knowledge_cache) > 1500:
                    # Sort by usage and keep top 1000
                    sorted_items = sorted(
                        self.knowledge_cache.items(),
                        key=lambda x: x[1].usage_count,
                        reverse=True
                    )
                    
                    # Keep top 1000 items
                    new_cache = dict(sorted_items[:1000])
                    self.knowledge_cache = new_cache
                    
                    logger.info("Knowledge cache pruned to 1000 items")
                
                # Load new high-usage items
                await self._load_knowledge_cache()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache refresh error: {e}")
    
    async def _update_analytics_periodically(self):
        """Periodically update analytics"""
        while True:
            try:
                await asyncio.sleep(1800)  # Update every 30 minutes
                
                # Update knowledge patterns
                await self._analyze_knowledge_patterns()
                
                # Clean up old analytics
                await self._cleanup_old_analytics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Analytics update error: {e}")
    
    async def _analyze_knowledge_patterns(self):
        """Analyze knowledge usage patterns"""
        
        # Analyze tag co-occurrence
        tag_cooccurrence = {}
        for item in self.knowledge_cache.values():
            tags = item.tags
            for i, tag1 in enumerate(tags):
                for tag2 in tags[i+1:]:
                    pair = tuple(sorted([tag1, tag2]))
                    tag_cooccurrence[pair] = tag_cooccurrence.get(pair, 0) + 1
        
        self.knowledge_patterns['tag_cooccurrence'] = tag_cooccurrence
        
        # Analyze knowledge type relationships
        type_relationships = {}
        for item in self.knowledge_cache.values():
            for related_id in item.related_items:
                if related_id in self.knowledge_cache:
                    related_item = self.knowledge_cache[related_id]
                    type_pair = tuple(sorted([item.knowledge_type.value, related_item.knowledge_type.value]))
                    type_relationships[type_pair] = type_relationships.get(type_pair, 0) + 1
        
        self.knowledge_patterns['type_relationships'] = type_relationships
    
    async def _cleanup_old_analytics(self):
        """Clean up old analytics data"""
        
        # Remove analytics older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Clean up usage analytics (simplified)
        for agent_id in list(self.usage_analytics.keys()):
            # Reset counters periodically to prevent unbounded growth
            if len(self.usage_analytics[agent_id]['most_accessed_items']) > 100:
                # Keep only top 50 most accessed items
                most_accessed = self.usage_analytics[agent_id]['most_accessed_items']
                top_items = dict(sorted(most_accessed.items(), key=lambda x: x[1], reverse=True)[:50])
                self.usage_analytics[agent_id]['most_accessed_items'] = top_items
    
    async def _save_cache_to_database(self):
        """Save cache changes to database"""
        try:
            # Update usage counts in database
            for knowledge_item in self.knowledge_cache.values():
                await self._update_knowledge_item(knowledge_item)
            
            logger.info("Knowledge cache saved to database")
            
        except Exception as e:
            logger.error(f"Failed to save cache to database: {e}")
    
    async def _store_knowledge_item(self, knowledge_item: KnowledgeItem):
        """Store knowledge item in database"""
        try:
            await self.db.create_document(self.collection_name, knowledge_item.to_dict())
        except Exception as e:
            logger.error(f"Failed to store knowledge item {knowledge_item.knowledge_id}: {e}")
    
    async def _update_knowledge_item(self, knowledge_item: KnowledgeItem):
        """Update knowledge item in database"""
        try:
            await self.db.update_document(self.collection_name, knowledge_item.knowledge_id, knowledge_item.to_dict())
        except Exception as e:
            logger.error(f"Failed to update knowledge item {knowledge_item.knowledge_id}: {e}")
