
"""
Message Bus for Inter-Agent Communication
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
from loguru import logger
import uuid

class MessageType(str, Enum):
    """Types of messages in the system"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    COLLABORATION_REQUEST = "collaboration_request"
    COLLABORATION_RESPONSE = "collaboration_response"
    STATUS_UPDATE = "status_update"
    RESOURCE_REQUEST = "resource_request"
    RESOURCE_RESPONSE = "resource_response"
    CONFLICT_NOTIFICATION = "conflict_notification"
    SYSTEM_BROADCAST = "system_broadcast"
    HEARTBEAT = "heartbeat"

class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class Message:
    """Message structure for inter-agent communication"""
    id: str
    sender_id: str
    recipient_id: Optional[str]  # None for broadcast messages
    message_type: MessageType
    priority: MessagePriority
    content: Dict[str, Any]
    timestamp: datetime
    expires_at: Optional[datetime] = None
    correlation_id: Optional[str] = None  # For request-response correlation
    requires_response: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        # Convert string timestamps back to datetime
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if isinstance(data.get('expires_at'), str):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        
        return cls(**data)

class MessageBus:
    """Central message bus for agent communication"""
    
    def __init__(self, database):
        self.db = database
        self.collection_name = "agent_messages"
        
        # In-memory message queues for active agents
        self.agent_queues: Dict[str, asyncio.Queue] = {}
        self.subscribers: Dict[MessageType, Set[str]] = {}
        self.message_handlers: Dict[str, Dict[MessageType, Callable]] = {}
        
        # Message routing and filtering
        self.routing_rules: List[Dict[str, Any]] = []
        self.message_filters: List[Callable] = []
        
        # Statistics and monitoring
        self.message_stats = {
            'total_sent': 0,
            'total_delivered': 0,
            'total_failed': 0,
            'messages_by_type': {},
            'messages_by_priority': {}
        }
        
        # Background tasks
        self.cleanup_task = None
        self.heartbeat_task = None
        
        logger.info("Message Bus initialized")
    
    async def start(self):
        """Start the message bus services"""
        # Start cleanup task for expired messages
        self.cleanup_task = asyncio.create_task(self._cleanup_expired_messages())
        
        # Start heartbeat monitoring
        self.heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
        
        logger.info("Message Bus services started")
    
    async def stop(self):
        """Stop the message bus services"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
        
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        
        # Clear all queues
        for queue in self.agent_queues.values():
            while not queue.empty():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
        
        logger.info("Message Bus services stopped")
    
    async def register_agent(self, agent_id: str) -> bool:
        """Register an agent with the message bus"""
        if agent_id not in self.agent_queues:
            self.agent_queues[agent_id] = asyncio.Queue()
            self.message_handlers[agent_id] = {}
            logger.info(f"Registered agent {agent_id} with message bus")
            return True
        return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the message bus"""
        if agent_id in self.agent_queues:
            # Clear the queue
            queue = self.agent_queues[agent_id]
            while not queue.empty():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            
            del self.agent_queues[agent_id]
            del self.message_handlers[agent_id]
            
            # Remove from subscribers
            for message_type, subscribers in self.subscribers.items():
                subscribers.discard(agent_id)
            
            logger.info(f"Unregistered agent {agent_id} from message bus")
            return True
        return False
    
    async def send_message(self, message: Message) -> bool:
        """Send a message through the bus"""
        try:
            # Store message in database for persistence
            await self._store_message(message)
            
            # Apply message filters
            if not self._apply_filters(message):
                logger.debug(f"Message {message.id} filtered out")
                return False
            
            # Route message
            delivered = await self._route_message(message)
            
            # Update statistics
            self.message_stats['total_sent'] += 1
            if delivered:
                self.message_stats['total_delivered'] += 1
            else:
                self.message_stats['total_failed'] += 1
            
            # Update type and priority stats
            msg_type = message.message_type.value
            self.message_stats['messages_by_type'][msg_type] = \
                self.message_stats['messages_by_type'].get(msg_type, 0) + 1
            
            priority = message.priority.value
            self.message_stats['messages_by_priority'][priority] = \
                self.message_stats['messages_by_priority'].get(priority, 0) + 1
            
            return delivered
            
        except Exception as e:
            logger.error(f"Failed to send message {message.id}: {e}")
            self.message_stats['total_failed'] += 1
            return False
    
    async def receive_message(self, agent_id: str, timeout: Optional[float] = None) -> Optional[Message]:
        """Receive a message for an agent"""
        if agent_id not in self.agent_queues:
            return None
        
        try:
            queue = self.agent_queues[agent_id]
            if timeout:
                message = await asyncio.wait_for(queue.get(), timeout=timeout)
            else:
                message = await queue.get()
            
            logger.debug(f"Agent {agent_id} received message {message.id}")
            return message
            
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Failed to receive message for agent {agent_id}: {e}")
            return None
    
    async def subscribe(self, agent_id: str, message_type: MessageType) -> bool:
        """Subscribe an agent to a message type"""
        if message_type not in self.subscribers:
            self.subscribers[message_type] = set()
        
        self.subscribers[message_type].add(agent_id)
        logger.debug(f"Agent {agent_id} subscribed to {message_type.value}")
        return True
    
    async def unsubscribe(self, agent_id: str, message_type: MessageType) -> bool:
        """Unsubscribe an agent from a message type"""
        if message_type in self.subscribers:
            self.subscribers[message_type].discard(agent_id)
            logger.debug(f"Agent {agent_id} unsubscribed from {message_type.value}")
            return True
        return False
    
    async def register_handler(self, agent_id: str, message_type: MessageType, handler: Callable) -> bool:
        """Register a message handler for an agent"""
        if agent_id not in self.message_handlers:
            self.message_handlers[agent_id] = {}
        
        self.message_handlers[agent_id][message_type] = handler
        logger.debug(f"Registered handler for agent {agent_id}, message type {message_type.value}")
        return True
    
    async def broadcast_message(self, sender_id: str, message_type: MessageType, 
                              content: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL) -> int:
        """Broadcast a message to all subscribed agents"""
        
        message = Message(
            id=str(uuid.uuid4()),
            sender_id=sender_id,
            recipient_id=None,  # Broadcast
            message_type=message_type,
            priority=priority,
            content=content,
            timestamp=datetime.utcnow()
        )
        
        # Get subscribers for this message type
        subscribers = self.subscribers.get(message_type, set())
        delivered_count = 0
        
        for subscriber_id in subscribers:
            if subscriber_id != sender_id:  # Don't send to sender
                message.recipient_id = subscriber_id
                message.id = str(uuid.uuid4())  # New ID for each recipient
                
                if await self.send_message(message):
                    delivered_count += 1
        
        logger.info(f"Broadcast message delivered to {delivered_count} agents")
        return delivered_count
    
    async def send_request_response(self, sender_id: str, recipient_id: str,
                                  message_type: MessageType, content: Dict[str, Any],
                                  timeout: float = 30.0) -> Optional[Message]:
        """Send a request and wait for response"""
        
        correlation_id = str(uuid.uuid4())
        
        request_message = Message(
            id=str(uuid.uuid4()),
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=message_type,
            priority=MessagePriority.NORMAL,
            content=content,
            timestamp=datetime.utcnow(),
            correlation_id=correlation_id,
            requires_response=True
        )
        
        # Send the request
        if not await self.send_message(request_message):
            return None
        
        # Wait for response
        start_time = datetime.utcnow()
        while (datetime.utcnow() - start_time).total_seconds() < timeout:
            response = await self.receive_message(sender_id, timeout=1.0)
            if response and response.correlation_id == correlation_id:
                return response
        
        logger.warning(f"Request-response timeout for correlation {correlation_id}")
        return None
    
    async def get_message_history(self, agent_id: str, limit: int = 50) -> List[Message]:
        """Get message history for an agent"""
        try:
            # Query messages from database
            filters = {
                '$or': [
                    {'sender_id': agent_id},
                    {'recipient_id': agent_id}
                ]
            }
            
            messages_data = await self.db.find_documents(
                self.collection_name,
                filters,
                limit=limit,
                sort=[('timestamp', -1)]
            )
            
            return [Message.from_dict(data) for data in messages_data]
            
        except Exception as e:
            logger.error(f"Failed to get message history for {agent_id}: {e}")
            return []
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get message bus statistics"""
        active_agents = len(self.agent_queues)
        total_subscriptions = sum(len(subs) for subs in self.subscribers.values())
        
        # Get queue sizes
        queue_sizes = {}
        for agent_id, queue in self.agent_queues.items():
            queue_sizes[agent_id] = queue.qsize()
        
        return {
            'active_agents': active_agents,
            'total_subscriptions': total_subscriptions,
            'queue_sizes': queue_sizes,
            'message_statistics': self.message_stats.copy(),
            'routing_rules': len(self.routing_rules),
            'message_filters': len(self.message_filters)
        }
    
    def add_routing_rule(self, rule: Dict[str, Any]):
        """Add a message routing rule"""
        self.routing_rules.append(rule)
        logger.debug(f"Added routing rule: {rule}")
    
    def add_message_filter(self, filter_func: Callable[[Message], bool]):
        """Add a message filter"""
        self.message_filters.append(filter_func)
        logger.debug("Added message filter")
    
    async def _store_message(self, message: Message):
        """Store message in database"""
        try:
            message_data = message.to_dict()
            # Convert datetime objects to ISO strings for storage
            message_data['timestamp'] = message.timestamp.isoformat()
            if message.expires_at:
                message_data['expires_at'] = message.expires_at.isoformat()
            
            await self.db.create_document(self.collection_name, message_data)
            
        except Exception as e:
            logger.error(f"Failed to store message {message.id}: {e}")
    
    def _apply_filters(self, message: Message) -> bool:
        """Apply message filters"""
        for filter_func in self.message_filters:
            try:
                if not filter_func(message):
                    return False
            except Exception as e:
                logger.error(f"Message filter error: {e}")
        return True
    
    async def _route_message(self, message: Message) -> bool:
        """Route message to appropriate recipients"""
        try:
            # Handle broadcast messages
            if message.recipient_id is None:
                subscribers = self.subscribers.get(message.message_type, set())
                delivered = False
                
                for subscriber_id in subscribers:
                    if subscriber_id != message.sender_id and subscriber_id in self.agent_queues:
                        await self.agent_queues[subscriber_id].put(message)
                        delivered = True
                
                return delivered
            
            # Handle direct messages
            else:
                if message.recipient_id in self.agent_queues:
                    await self.agent_queues[message.recipient_id].put(message)
                    return True
                else:
                    logger.warning(f"Recipient {message.recipient_id} not found")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to route message {message.id}: {e}")
            return False
    
    async def _cleanup_expired_messages(self):
        """Background task to clean up expired messages"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Remove expired messages from database
                current_time = datetime.utcnow()
                filters = {
                    'expires_at': {'$lt': current_time.isoformat()}
                }
                
                result = await self.db.delete_documents(self.collection_name, filters)
                if result.get('deleted_count', 0) > 0:
                    logger.info(f"Cleaned up {result['deleted_count']} expired messages")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Message cleanup error: {e}")
    
    async def _heartbeat_monitor(self):
        """Monitor agent heartbeats"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Send heartbeat requests to all agents
                heartbeat_message = Message(
                    id=str(uuid.uuid4()),
                    sender_id="message_bus",
                    recipient_id=None,
                    message_type=MessageType.HEARTBEAT,
                    priority=MessagePriority.LOW,
                    content={'timestamp': datetime.utcnow().isoformat()},
                    timestamp=datetime.utcnow()
                )
                
                await self.broadcast_message(
                    "message_bus",
                    MessageType.HEARTBEAT,
                    heartbeat_message.content,
                    MessagePriority.LOW
                )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat monitor error: {e}")
