
"""
Conflict Resolver for Multi-Agent Systems
Handles conflicts between agents and competing recommendations
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
from loguru import logger
import uuid

from .message_bus import MessageBus, Message, MessageType, MessagePriority

class ConflictType(str, Enum):
    """Types of conflicts in multi-agent systems"""
    RESOURCE_CONFLICT = "resource_conflict"
    TASK_CONFLICT = "task_conflict"
    PRIORITY_CONFLICT = "priority_conflict"
    RECOMMENDATION_CONFLICT = "recommendation_conflict"
    SCHEDULING_CONFLICT = "scheduling_conflict"
    DATA_CONFLICT = "data_conflict"
    GOAL_CONFLICT = "goal_conflict"

class ConflictSeverity(str, Enum):
    """Conflict severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ResolutionStrategy(str, Enum):
    """Conflict resolution strategies"""
    PRIORITY_BASED = "priority_based"
    CONSENSUS = "consensus"
    VOTING = "voting"
    ARBITRATION = "arbitration"
    NEGOTIATION = "negotiation"
    FIRST_COME_FIRST_SERVE = "first_come_first_serve"
    RESOURCE_SHARING = "resource_sharing"

@dataclass
class Conflict:
    """Conflict representation"""
    conflict_id: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    involved_agents: List[str]
    description: str
    context: Dict[str, Any]
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_strategy: Optional[ResolutionStrategy] = None
    resolution: Optional[Dict[str, Any]] = None
    resolution_confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        if self.resolved_at:
            data['resolved_at'] = self.resolved_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conflict':
        """Create from dictionary"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('resolved_at'):
            data['resolved_at'] = datetime.fromisoformat(data['resolved_at'])
        return cls(**data)

class ConflictResolver:
    """Manages and resolves conflicts between agents"""
    
    def __init__(self, message_bus: MessageBus, agent_registry, database):
        self.message_bus = message_bus
        self.agent_registry = agent_registry
        self.db = database
        self.collection_name = "agent_conflicts"
        
        # Conflict management
        self.active_conflicts: Dict[str, Conflict] = {}
        self.resolution_strategies = {
            ResolutionStrategy.PRIORITY_BASED: self._priority_based_resolution,
            ResolutionStrategy.CONSENSUS: self._consensus_resolution,
            ResolutionStrategy.VOTING: self._voting_resolution,
            ResolutionStrategy.ARBITRATION: self._arbitration_resolution,
            ResolutionStrategy.NEGOTIATION: self._negotiation_resolution,
            ResolutionStrategy.FIRST_COME_FIRST_SERVE: self._fcfs_resolution,
            ResolutionStrategy.RESOURCE_SHARING: self._resource_sharing_resolution
        }
        
        # Conflict detection patterns
        self.conflict_patterns = {
            ConflictType.RESOURCE_CONFLICT: self._detect_resource_conflicts,
            ConflictType.TASK_CONFLICT: self._detect_task_conflicts,
            ConflictType.PRIORITY_CONFLICT: self._detect_priority_conflicts,
            ConflictType.RECOMMENDATION_CONFLICT: self._detect_recommendation_conflicts,
            ConflictType.SCHEDULING_CONFLICT: self._detect_scheduling_conflicts
        }
        
        # Resolution history and learning
        self.resolution_history: List[Dict[str, Any]] = []
        self.strategy_effectiveness: Dict[ResolutionStrategy, float] = {}
        
        # Background monitoring
        self.conflict_monitor = None
        
        logger.info("Conflict Resolver initialized")
    
    async def start(self):
        """Start conflict resolution services"""
        # Start conflict monitoring
        self.conflict_monitor = asyncio.create_task(self._monitor_conflicts())
        
        # Subscribe to relevant message types
        await self.message_bus.subscribe("conflict_resolver", MessageType.CONFLICT_NOTIFICATION)
        
        logger.info("Conflict Resolver services started")
    
    async def stop(self):
        """Stop conflict resolution services"""
        if self.conflict_monitor:
            self.conflict_monitor.cancel()
        
        await self.message_bus.unsubscribe("conflict_resolver", MessageType.CONFLICT_NOTIFICATION)
        
        logger.info("Conflict Resolver services stopped")
    
    async def detect_conflict(self, 
                            conflict_type: ConflictType,
                            involved_agents: List[str],
                            description: str,
                            context: Dict[str, Any],
                            severity: ConflictSeverity = ConflictSeverity.MEDIUM) -> str:
        """Detect and register a new conflict"""
        
        conflict_id = str(uuid.uuid4())
        
        conflict = Conflict(
            conflict_id=conflict_id,
            conflict_type=conflict_type,
            severity=severity,
            involved_agents=involved_agents,
            description=description,
            context=context,
            created_at=datetime.utcnow()
        )
        
        # Store conflict
        self.active_conflicts[conflict_id] = conflict
        await self._store_conflict(conflict)
        
        # Notify involved agents
        await self._notify_conflict_detected(conflict)
        
        # Trigger resolution process
        asyncio.create_task(self._resolve_conflict(conflict_id))
        
        logger.warning(f"Conflict detected: {conflict_id} - {description}")
        return conflict_id
    
    async def resolve_conflict(self, 
                             conflict_id: str,
                             strategy: Optional[ResolutionStrategy] = None) -> bool:
        """Resolve a specific conflict"""
        
        if conflict_id not in self.active_conflicts:
            logger.error(f"Conflict {conflict_id} not found")
            return False
        
        conflict = self.active_conflicts[conflict_id]
        
        # Determine resolution strategy
        if not strategy:
            strategy = self._select_resolution_strategy(conflict)
        
        # Apply resolution strategy
        resolution_func = self.resolution_strategies.get(strategy)
        if not resolution_func:
            logger.error(f"Unknown resolution strategy: {strategy}")
            return False
        
        try:
            resolution, confidence = await resolution_func(conflict)
            
            # Update conflict with resolution
            conflict.resolved_at = datetime.utcnow()
            conflict.resolution_strategy = strategy
            conflict.resolution = resolution
            conflict.resolution_confidence = confidence
            
            # Store resolution
            await self._update_conflict(conflict)
            
            # Notify involved agents
            await self._notify_conflict_resolved(conflict)
            
            # Record resolution for learning
            self._record_resolution(conflict, strategy, confidence)
            
            # Remove from active conflicts
            del self.active_conflicts[conflict_id]
            
            logger.info(f"Conflict {conflict_id} resolved using {strategy.value} (confidence: {confidence:.2f})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resolve conflict {conflict_id}: {e}")
            return False
    
    async def get_active_conflicts(self) -> List[Conflict]:
        """Get all active conflicts"""
        return list(self.active_conflicts.values())
    
    async def get_conflict_history(self, limit: int = 50) -> List[Conflict]:
        """Get conflict resolution history"""
        try:
            conflicts_data = await self.db.find_documents(
                self.collection_name,
                {},
                limit=limit,
                sort=[('created_at', -1)]
            )
            
            return [Conflict.from_dict(data) for data in conflicts_data]
            
        except Exception as e:
            logger.error(f"Failed to get conflict history: {e}")
            return []
    
    async def get_conflict_statistics(self) -> Dict[str, Any]:
        """Get conflict resolution statistics"""
        
        total_conflicts = len(self.resolution_history)
        active_conflicts = len(self.active_conflicts)
        
        # Count by type
        type_counts = {}
        for record in self.resolution_history:
            conflict_type = record.get('conflict_type')
            type_counts[conflict_type] = type_counts.get(conflict_type, 0) + 1
        
        # Count by severity
        severity_counts = {}
        for record in self.resolution_history:
            severity = record.get('severity')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Strategy effectiveness
        strategy_stats = {}
        for strategy, effectiveness in self.strategy_effectiveness.items():
            strategy_stats[strategy.value] = effectiveness
        
        # Average resolution time
        resolution_times = [record.get('resolution_time', 0) for record in self.resolution_history]
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        return {
            'total_conflicts_resolved': total_conflicts,
            'active_conflicts': active_conflicts,
            'conflict_types': type_counts,
            'severity_distribution': severity_counts,
            'strategy_effectiveness': strategy_stats,
            'average_resolution_time_seconds': avg_resolution_time
        }
    
    def _select_resolution_strategy(self, conflict: Conflict) -> ResolutionStrategy:
        """Select the best resolution strategy for a conflict"""
        
        # Strategy selection based on conflict type and context
        if conflict.conflict_type == ConflictType.RESOURCE_CONFLICT:
            if conflict.context.get('shareable', False):
                return ResolutionStrategy.RESOURCE_SHARING
            else:
                return ResolutionStrategy.PRIORITY_BASED
        
        elif conflict.conflict_type == ConflictType.TASK_CONFLICT:
            return ResolutionStrategy.PRIORITY_BASED
        
        elif conflict.conflict_type == ConflictType.RECOMMENDATION_CONFLICT:
            if len(conflict.involved_agents) <= 3:
                return ResolutionStrategy.CONSENSUS
            else:
                return ResolutionStrategy.VOTING
        
        elif conflict.conflict_type == ConflictType.SCHEDULING_CONFLICT:
            return ResolutionStrategy.FIRST_COME_FIRST_SERVE
        
        elif conflict.severity == ConflictSeverity.CRITICAL:
            return ResolutionStrategy.ARBITRATION
        
        else:
            # Use most effective strategy based on history
            if self.strategy_effectiveness:
                best_strategy = max(self.strategy_effectiveness.items(), key=lambda x: x[1])[0]
                return best_strategy
            else:
                return ResolutionStrategy.PRIORITY_BASED
    
    async def _priority_based_resolution(self, conflict: Conflict) -> Tuple[Dict[str, Any], float]:
        """Resolve conflict based on agent priorities"""
        
        agent_priorities = {}
        
        # Get agent information and calculate priorities
        for agent_id in conflict.involved_agents:
            agent_info = await self.agent_registry.get_agent_info(agent_id)
            if agent_info:
                # Priority based on task count, success rate, etc.
                task_count = agent_info.get('task_count', 0)
                error_count = agent_info.get('error_count', 0)
                success_rate = 1 - (error_count / max(task_count, 1))
                
                priority_score = success_rate * 100 + task_count * 0.1
                agent_priorities[agent_id] = priority_score
        
        # Select agent with highest priority
        if agent_priorities:
            winner = max(agent_priorities.items(), key=lambda x: x[1])[0]
            
            resolution = {
                'winner': winner,
                'method': 'priority_based',
                'priorities': agent_priorities,
                'reason': f'Agent {winner} has highest priority score'
            }
            
            confidence = 0.8  # High confidence for priority-based resolution
            return resolution, confidence
        
        # Fallback to first agent
        resolution = {
            'winner': conflict.involved_agents[0],
            'method': 'fallback',
            'reason': 'No priority information available'
        }
        
        return resolution, 0.5
    
    async def _consensus_resolution(self, conflict: Conflict) -> Tuple[Dict[str, Any], float]:
        """Resolve conflict through consensus building"""
        
        # Send consensus request to all involved agents
        consensus_requests = []
        
        for agent_id in conflict.involved_agents:
            message = Message(
                id=str(uuid.uuid4()),
                sender_id="conflict_resolver",
                recipient_id=agent_id,
                message_type=MessageType.COLLABORATION_REQUEST,
                priority=MessagePriority.HIGH,
                content={
                    'conflict_id': conflict.conflict_id,
                    'type': 'consensus_request',
                    'context': conflict.context,
                    'other_agents': [a for a in conflict.involved_agents if a != agent_id]
                },
                timestamp=datetime.utcnow(),
                requires_response=True
            )
            
            consensus_requests.append(self.message_bus.send_message(message))
        
        # Wait for responses (with timeout)
        try:
            await asyncio.wait_for(asyncio.gather(*consensus_requests), timeout=30.0)
            
            # Collect responses (simplified - would need actual response collection)
            # For now, assume consensus reached
            resolution = {
                'method': 'consensus',
                'agreement': 'reached',
                'participants': conflict.involved_agents,
                'reason': 'Consensus reached among all agents'
            }
            
            return resolution, 0.9
            
        except asyncio.TimeoutError:
            # Fallback to voting if consensus fails
            return await self._voting_resolution(conflict)
    
    async def _voting_resolution(self, conflict: Conflict) -> Tuple[Dict[str, Any], float]:
        """Resolve conflict through voting"""
        
        # Get votes from all involved agents
        votes = {}
        
        for agent_id in conflict.involved_agents:
            # Simplified voting - each agent votes for themselves
            # In reality, would collect actual votes
            votes[agent_id] = agent_id
        
        # Count votes
        vote_counts = {}
        for vote in votes.values():
            vote_counts[vote] = vote_counts.get(vote, 0) + 1
        
        # Determine winner
        if vote_counts:
            winner = max(vote_counts.items(), key=lambda x: x[1])[0]
            
            resolution = {
                'winner': winner,
                'method': 'voting',
                'votes': votes,
                'vote_counts': vote_counts,
                'reason': f'Agent {winner} received most votes'
            }
            
            # Confidence based on vote margin
            total_votes = len(votes)
            winner_votes = vote_counts[winner]
            confidence = winner_votes / total_votes
            
            return resolution, confidence
        
        # Fallback
        return await self._priority_based_resolution(conflict)
    
    async def _arbitration_resolution(self, conflict: Conflict) -> Tuple[Dict[str, Any], float]:
        """Resolve conflict through arbitration (system decision)"""
        
        # System makes decision based on available information
        decision_factors = {
            'conflict_type': conflict.conflict_type.value,
            'severity': conflict.severity.value,
            'agent_count': len(conflict.involved_agents),
            'context': conflict.context
        }
        
        # Simple arbitration logic
        if conflict.conflict_type == ConflictType.RESOURCE_CONFLICT:
            # Allocate resource to agent with highest need
            winner = conflict.involved_agents[0]  # Simplified
        else:
            # Use priority-based decision
            return await self._priority_based_resolution(conflict)
        
        resolution = {
            'winner': winner,
            'method': 'arbitration',
            'decision_factors': decision_factors,
            'reason': 'System arbitration decision'
        }
        
        return resolution, 0.7
    
    async def _negotiation_resolution(self, conflict: Conflict) -> Tuple[Dict[str, Any], float]:
        """Resolve conflict through negotiation"""
        
        # Facilitate negotiation between agents
        negotiation_rounds = 3
        current_offers = {}
        
        for round_num in range(negotiation_rounds):
            # Send negotiation requests
            for agent_id in conflict.involved_agents:
                message = Message(
                    id=str(uuid.uuid4()),
                    sender_id="conflict_resolver",
                    recipient_id=agent_id,
                    message_type=MessageType.COLLABORATION_REQUEST,
                    priority=MessagePriority.NORMAL,
                    content={
                        'conflict_id': conflict.conflict_id,
                        'type': 'negotiation_request',
                        'round': round_num + 1,
                        'current_offers': current_offers,
                        'context': conflict.context
                    },
                    timestamp=datetime.utcnow()
                )
                
                await self.message_bus.send_message(message)
            
            # Wait for offers (simplified)
            await asyncio.sleep(5)
            
            # Update offers (would collect actual responses)
            for agent_id in conflict.involved_agents:
                current_offers[agent_id] = f"offer_round_{round_num + 1}"
        
        # Evaluate final offers
        resolution = {
            'method': 'negotiation',
            'final_offers': current_offers,
            'winner': conflict.involved_agents[0],  # Simplified
            'reason': 'Negotiation completed'
        }
        
        return resolution, 0.6
    
    async def _fcfs_resolution(self, conflict: Conflict) -> Tuple[Dict[str, Any], float]:
        """First-come-first-serve resolution"""
        
        # Determine order based on timestamps in context
        agent_timestamps = {}
        
        for agent_id in conflict.involved_agents:
            # Get timestamp from context or use current time
            timestamp = conflict.context.get(f'{agent_id}_timestamp', datetime.utcnow())
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            agent_timestamps[agent_id] = timestamp
        
        # Sort by timestamp
        sorted_agents = sorted(agent_timestamps.items(), key=lambda x: x[1])
        winner = sorted_agents[0][0]
        
        resolution = {
            'winner': winner,
            'method': 'first_come_first_serve',
            'order': [agent_id for agent_id, _ in sorted_agents],
            'timestamps': {k: v.isoformat() for k, v in agent_timestamps.items()},
            'reason': f'Agent {winner} was first'
        }
        
        return resolution, 0.9
    
    async def _resource_sharing_resolution(self, conflict: Conflict) -> Tuple[Dict[str, Any], float]:
        """Resolve through resource sharing"""
        
        # Determine if resource can be shared
        resource_info = conflict.context.get('resource', {})
        shareable = resource_info.get('shareable', False)
        capacity = resource_info.get('capacity', 1)
        
        if shareable and capacity >= len(conflict.involved_agents):
            # All agents can share the resource
            resolution = {
                'method': 'resource_sharing',
                'shared_agents': conflict.involved_agents,
                'allocation': {agent_id: 1/len(conflict.involved_agents) 
                             for agent_id in conflict.involved_agents},
                'reason': 'Resource shared among all agents'
            }
            
            return resolution, 0.8
        
        elif shareable and capacity > 1:
            # Partial sharing based on priority
            priority_resolution, _ = await self._priority_based_resolution(conflict)
            
            # Allocate to top agents based on capacity
            sorted_agents = conflict.involved_agents[:capacity]
            
            resolution = {
                'method': 'partial_resource_sharing',
                'shared_agents': sorted_agents,
                'allocation': {agent_id: 1/len(sorted_agents) 
                             for agent_id in sorted_agents},
                'reason': f'Resource shared among top {capacity} agents'
            }
            
            return resolution, 0.7
        
        else:
            # Cannot share, use priority-based resolution
            return await self._priority_based_resolution(conflict)
    
    async def _monitor_conflicts(self):
        """Background task to monitor for conflicts"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Run conflict detection patterns
                for conflict_type, detection_func in self.conflict_patterns.items():
                    try:
                        await detection_func()
                    except Exception as e:
                        logger.error(f"Conflict detection error for {conflict_type}: {e}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Conflict monitoring error: {e}")
    
    async def _detect_resource_conflicts(self):
        """Detect resource conflicts between agents"""
        # Implementation would check for resource contention
        pass
    
    async def _detect_task_conflicts(self):
        """Detect task conflicts between agents"""
        # Implementation would check for overlapping tasks
        pass
    
    async def _detect_priority_conflicts(self):
        """Detect priority conflicts between agents"""
        # Implementation would check for priority mismatches
        pass
    
    async def _detect_recommendation_conflicts(self):
        """Detect conflicting recommendations from agents"""
        # Implementation would analyze agent recommendations
        pass
    
    async def _detect_scheduling_conflicts(self):
        """Detect scheduling conflicts between agents"""
        # Implementation would check for scheduling overlaps
        pass
    
    async def _notify_conflict_detected(self, conflict: Conflict):
        """Notify involved agents of conflict detection"""
        
        for agent_id in conflict.involved_agents:
            message = Message(
                id=str(uuid.uuid4()),
                sender_id="conflict_resolver",
                recipient_id=agent_id,
                message_type=MessageType.CONFLICT_NOTIFICATION,
                priority=MessagePriority.HIGH,
                content={
                    'conflict_id': conflict.conflict_id,
                    'conflict_type': conflict.conflict_type.value,
                    'severity': conflict.severity.value,
                    'description': conflict.description,
                    'other_agents': [a for a in conflict.involved_agents if a != agent_id]
                },
                timestamp=datetime.utcnow()
            )
            
            await self.message_bus.send_message(message)
    
    async def _notify_conflict_resolved(self, conflict: Conflict):
        """Notify involved agents of conflict resolution"""
        
        for agent_id in conflict.involved_agents:
            message = Message(
                id=str(uuid.uuid4()),
                sender_id="conflict_resolver",
                recipient_id=agent_id,
                message_type=MessageType.CONFLICT_NOTIFICATION,
                priority=MessagePriority.NORMAL,
                content={
                    'conflict_id': conflict.conflict_id,
                    'status': 'resolved',
                    'resolution': conflict.resolution,
                    'strategy': conflict.resolution_strategy.value,
                    'confidence': conflict.resolution_confidence
                },
                timestamp=datetime.utcnow()
            )
            
            await self.message_bus.send_message(message)
    
    def _record_resolution(self, conflict: Conflict, strategy: ResolutionStrategy, confidence: float):
        """Record resolution for learning and improvement"""
        
        resolution_time = (conflict.resolved_at - conflict.created_at).total_seconds()
        
        record = {
            'conflict_id': conflict.conflict_id,
            'conflict_type': conflict.conflict_type.value,
            'severity': conflict.severity.value,
            'strategy': strategy.value,
            'confidence': confidence,
            'resolution_time': resolution_time,
            'agent_count': len(conflict.involved_agents),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.resolution_history.append(record)
        
        # Update strategy effectiveness
        if strategy not in self.strategy_effectiveness:
            self.strategy_effectiveness[strategy] = confidence
        else:
            # Moving average
            current_effectiveness = self.strategy_effectiveness[strategy]
            self.strategy_effectiveness[strategy] = (current_effectiveness * 0.8) + (confidence * 0.2)
    
    async def _resolve_conflict(self, conflict_id: str):
        """Background task to resolve a conflict"""
        try:
            await asyncio.sleep(1)  # Brief delay to allow conflict registration
            await self.resolve_conflict(conflict_id)
        except Exception as e:
            logger.error(f"Background conflict resolution failed for {conflict_id}: {e}")
    
    async def _store_conflict(self, conflict: Conflict):
        """Store conflict in database"""
        try:
            await self.db.create_document(self.collection_name, conflict.to_dict())
        except Exception as e:
            logger.error(f"Failed to store conflict {conflict.conflict_id}: {e}")
    
    async def _update_conflict(self, conflict: Conflict):
        """Update conflict in database"""
        try:
            await self.db.update_document(self.collection_name, conflict.conflict_id, conflict.to_dict())
        except Exception as e:
            logger.error(f"Failed to update conflict {conflict.conflict_id}: {e}")
