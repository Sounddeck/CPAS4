
"""
Multi-Agent Coordination System
Phase 3: Multi-Agent Communication and Coordination
"""

from .message_bus import MessageBus, Message, MessageType
from .task_delegator import TaskDelegator, TaskAssignment
from .conflict_resolver import ConflictResolver, ConflictType
from .collaboration_engine import CollaborationEngine
from .shared_knowledge import SharedKnowledgeBase

__all__ = [
    'MessageBus',
    'Message', 
    'MessageType',
    'TaskDelegator',
    'TaskAssignment',
    'ConflictResolver',
    'ConflictType',
    'CollaborationEngine',
    'SharedKnowledgeBase'
]
