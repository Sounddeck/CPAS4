
"""
Core AI Agent with Memory Integration for CPAS
Implements intelligent agent using LangChain with MemOS integration
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import uuid

try:
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain.tools import Tool
    from langchain.memory import ConversationBufferWindowMemory
    from langchain_community.llms import Ollama
    from langchain.prompts import PromptTemplate
    from langchain.schema import BaseMessage, HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    logging.warning(f"LangChain not available: {e}")
    LANGCHAIN_AVAILABLE = False

# Import our services
from .hrm_adapter import hrm_adapter, ReasoningChain
from .voice_service import voice_service
from .memory_service import memory_service

@dataclass
class ConversationContext:
    """Context for ongoing conversations"""
    user_id: str
    session_id: str
    conversation_history: List[Dict[str, Any]]
    user_preferences: Dict[str, Any]
    current_topic: Optional[str]
    last_interaction: datetime
    interaction_count: int

@dataclass
class AgentResponse:
    """Response from the AI agent"""
    text: str
    reasoning_chain: Optional[ReasoningChain]
    confidence: float
    response_type: str
    metadata: Dict[str, Any]
    timestamp: datetime

class CPASAgent:
    """Core AI Agent with hierarchical reasoning and memory"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.llm = None
        self.agent_executor = None
        self.conversations: Dict[str, ConversationContext] = {}
        
        # Initialize LangChain components
        if LANGCHAIN_AVAILABLE:
            self._initialize_langchain()
        else:
            self.logger.warning("LangChain not available, using fallback agent")
        
        # Agent personality and behavior
        self.personality = self._load_personality()
        
        self.logger.info("CPAS Agent initialized successfully")
    
    def _default_config(self) -> Dict:
        """Default configuration for the agent"""
        return {
            'ollama_base_url': 'http://localhost:11434',
            'model_name': 'llama3.2:1b',
            'max_conversation_history': 20,
            'response_timeout': 30,
            'reasoning_enabled': True,
            'voice_enabled': True,
            'memory_enabled': True,
            'learning_enabled': True
        }
    
    def _initialize_langchain(self):
        """Initialize LangChain components"""
        try:
            # Initialize Ollama LLM
            self.llm = Ollama(
                base_url=self.config['ollama_base_url'],
                model=self.config['model_name'],
                temperature=0.7
            )
            
            # Create tools for the agent
            tools = self._create_agent_tools()
            
            # Create agent prompt
            prompt = self._create_agent_prompt()
            
            # Create ReAct agent
            agent = create_react_agent(self.llm, tools, prompt)
            
            # Create agent executor
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=True,
                max_iterations=5,
                handle_parsing_errors=True
            )
            
            self.logger.info("LangChain components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LangChain: {e}")
            self.llm = None
            self.agent_executor = None
    
    def _create_agent_tools(self) -> List[Tool]:
        """Create tools for the agent"""
        tools = []
        
        # Memory tool
        if self.config['memory_enabled']:
            memory_tool = Tool(
                name="memory",
                description="Store and retrieve information from long-term memory",
                func=self._memory_tool
            )
            tools.append(memory_tool)
        
        # Reasoning tool
        if self.config['reasoning_enabled']:
            reasoning_tool = Tool(
                name="reasoning",
                description="Perform hierarchical reasoning on complex problems",
                func=self._reasoning_tool
            )
            tools.append(reasoning_tool)
        
        # Voice tool
        if self.config['voice_enabled']:
            voice_tool = Tool(
                name="voice",
                description="Process voice commands and generate speech responses",
                func=self._voice_tool
            )
            tools.append(voice_tool)
        
        return tools
    
    def _create_agent_prompt(self) -> PromptTemplate:
        """Create the agent prompt template"""
        template = """You are CPAS (Cognitive Personal Assistant System), an advanced AI assistant with hierarchical reasoning capabilities, long-term memory, and voice interaction.

Your personality:
- Helpful and knowledgeable
- Curious and engaging
- Proactive in offering assistance
- Remembers user preferences and context
- Uses hierarchical reasoning for complex problems

You have access to the following tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
        
        return PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad"],
            partial_variables={
                "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in self._create_agent_tools()]),
                "tool_names": ", ".join([tool.name for tool in self._create_agent_tools()])
            }
        )
    
    def _memory_tool(self, query: str) -> str:
        """Tool for memory operations"""
        try:
            if query.startswith("store:"):
                content = query[6:].strip()
                result = memory_service.store_memory("user", content, {"type": "agent_storage"})
                return f"Stored in memory: {result.get('id', 'unknown')}"
            elif query.startswith("recall:"):
                search_query = query[7:].strip()
                results = memory_service.search_memories("user", search_query, limit=3)
                if results:
                    return f"Found memories: {[r['content'][:100] for r in results]}"
                else:
                    return "No relevant memories found"
            else:
                return "Invalid memory operation. Use 'store:' or 'recall:' prefix"
        except Exception as e:
            return f"Memory operation failed: {str(e)}"
    
    def _reasoning_tool(self, problem: str) -> str:
        """Tool for hierarchical reasoning"""
        try:
            chain = hrm_adapter.reason(problem)
            return f"Reasoning chain: {chain.high_level_plan[:2]} (confidence: {chain.confidence_scores[0]:.2f})"
        except Exception as e:
            return f"Reasoning failed: {str(e)}"
    
    def _voice_tool(self, command: str) -> str:
        """Tool for voice operations"""
        try:
            if command.startswith("speak:"):
                text = command[6:].strip()
                # This would be async in practice
                return f"Speaking: {text[:50]}..."
            else:
                return "Invalid voice command. Use 'speak:' prefix"
        except Exception as e:
            return f"Voice operation failed: {str(e)}"
    
    def _load_personality(self) -> Dict[str, Any]:
        """Load agent personality configuration"""
        return {
            'name': 'CPAS',
            'traits': ['helpful', 'curious', 'proactive', 'intelligent'],
            'communication_style': 'friendly_professional',
            'expertise_areas': ['problem_solving', 'information_retrieval', 'task_planning'],
            'learning_style': 'adaptive',
            'response_patterns': {
                'greeting': "Hello! I'm CPAS, your cognitive assistant. How can I help you today?",
                'farewell': "Goodbye! Feel free to ask me anything anytime.",
                'confusion': "I'm not sure I understand. Could you please clarify?",
                'thinking': "Let me think about this..."
            }
        }
    
    async def process_message(self, user_id: str, message: str, context: Optional[Dict] = None) -> AgentResponse:
        """
        Process a user message and generate a response
        
        Args:
            user_id: Unique user identifier
            message: User's message
            context: Additional context information
            
        Returns:
            AgentResponse: The agent's response
        """
        start_time = time.time()
        
        try:
            # Get or create conversation context
            conversation = self._get_conversation_context(user_id)
            
            # Update conversation history
            conversation.conversation_history.append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            })
            
            # Generate response
            if self.agent_executor:
                response_text = await self._generate_langchain_response(message, conversation)
            else:
                response_text = await self._generate_fallback_response(message, conversation)
            
            # Perform reasoning if enabled
            reasoning_chain = None
            if self.config['reasoning_enabled'] and self._should_use_reasoning(message):
                reasoning_chain = hrm_adapter.reason(message, context)
            
            # Calculate confidence
            confidence = self._calculate_response_confidence(response_text, reasoning_chain)
            
            # Determine response type
            response_type = self._classify_response_type(message, response_text)
            
            # Create response
            response = AgentResponse(
                text=response_text,
                reasoning_chain=reasoning_chain,
                confidence=confidence,
                response_type=response_type,
                metadata={
                    'processing_time': time.time() - start_time,
                    'user_id': user_id,
                    'context': context or {}
                },
                timestamp=datetime.now()
            )
            
            # Update conversation history
            conversation.conversation_history.append({
                'role': 'assistant',
                'content': response_text,
                'timestamp': datetime.now().isoformat(),
                'confidence': confidence
            })
            
            # Store in memory if enabled
            if self.config['memory_enabled']:
                await self._store_interaction_memory(user_id, message, response)
            
            # Update conversation context
            conversation.last_interaction = datetime.now()
            conversation.interaction_count += 1
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to process message: {e}")
            return AgentResponse(
                text="I apologize, but I encountered an error processing your request. Please try again.",
                reasoning_chain=None,
                confidence=0.0,
                response_type="error",
                metadata={'error': str(e)},
                timestamp=datetime.now()
            )
    
    async def _generate_langchain_response(self, message: str, conversation: ConversationContext) -> str:
        """Generate response using LangChain agent"""
        try:
            # Prepare input with conversation context
            context_summary = self._summarize_conversation_context(conversation)
            full_input = f"Context: {context_summary}\n\nUser: {message}"
            
            # Run agent
            result = await asyncio.wait_for(
                asyncio.to_thread(self.agent_executor.invoke, {"input": full_input}),
                timeout=self.config['response_timeout']
            )
            
            return result.get('output', 'I apologize, but I could not generate a response.')
            
        except asyncio.TimeoutError:
            return "I'm taking too long to respond. Let me give you a quick answer instead."
        except Exception as e:
            self.logger.error(f"LangChain response generation failed: {e}")
            return "I encountered an issue generating a response. Please try rephrasing your question."
    
    async def _generate_fallback_response(self, message: str, conversation: ConversationContext) -> str:
        """Generate fallback response when LangChain is not available"""
        message_lower = message.lower().strip()
        
        # Simple pattern matching for common queries
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return self.personality['response_patterns']['greeting']
        elif any(word in message_lower for word in ['bye', 'goodbye', 'farewell']):
            return self.personality['response_patterns']['farewell']
        elif any(word in message_lower for word in ['help', 'assist']):
            return "I'm here to help! I can assist with problem-solving, information retrieval, and task planning. What would you like to work on?"
        elif any(word in message_lower for word in ['remember', 'recall']):
            return "I can help you store and retrieve information. What would you like me to remember or recall?"
        else:
            return f"I understand you're asking about: {message[:50]}... Let me help you with that. Could you provide more specific details?"
    
    def _get_conversation_context(self, user_id: str) -> ConversationContext:
        """Get or create conversation context for user"""
        if user_id not in self.conversations:
            self.conversations[user_id] = ConversationContext(
                user_id=user_id,
                session_id=str(uuid.uuid4()),
                conversation_history=[],
                user_preferences={},
                current_topic=None,
                last_interaction=datetime.now(),
                interaction_count=0
            )
        
        return self.conversations[user_id]
    
    def _summarize_conversation_context(self, conversation: ConversationContext) -> str:
        """Summarize conversation context for the agent"""
        recent_history = conversation.conversation_history[-5:]  # Last 5 messages
        
        summary_parts = []
        if conversation.current_topic:
            summary_parts.append(f"Current topic: {conversation.current_topic}")
        
        if conversation.user_preferences:
            summary_parts.append(f"User preferences: {conversation.user_preferences}")
        
        if recent_history:
            summary_parts.append("Recent conversation:")
            for msg in recent_history:
                summary_parts.append(f"- {msg['role']}: {msg['content'][:100]}")
        
        return "\n".join(summary_parts) if summary_parts else "No prior context"
    
    def _should_use_reasoning(self, message: str) -> bool:
        """Determine if hierarchical reasoning should be used"""
        reasoning_keywords = [
            'solve', 'calculate', 'analyze', 'plan', 'strategy',
            'complex', 'problem', 'how to', 'step by step'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in reasoning_keywords)
    
    def _calculate_response_confidence(self, response: str, reasoning_chain: Optional[ReasoningChain]) -> float:
        """Calculate confidence score for the response"""
        base_confidence = 0.7
        
        # Adjust based on response length and content
        if len(response) > 50:
            base_confidence += 0.1
        
        # Adjust based on reasoning chain
        if reasoning_chain:
            avg_reasoning_confidence = sum(reasoning_chain.confidence_scores) / len(reasoning_chain.confidence_scores)
            base_confidence = (base_confidence + avg_reasoning_confidence) / 2
        
        # Adjust based on response content quality
        if any(word in response.lower() for word in ['sorry', 'apologize', 'error', 'failed']):
            base_confidence -= 0.2
        
        return max(0.0, min(1.0, base_confidence))
    
    def _classify_response_type(self, message: str, response: str) -> str:
        """Classify the type of response"""
        message_lower = message.lower()
        response_lower = response.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return 'greeting'
        elif any(word in message_lower for word in ['help', 'assist']):
            return 'help'
        elif any(word in message_lower for word in ['remember', 'store']):
            return 'memory_storage'
        elif any(word in message_lower for word in ['recall', 'what', 'tell me']):
            return 'memory_retrieval'
        elif any(word in message_lower for word in ['solve', 'calculate']):
            return 'problem_solving'
        elif any(word in response_lower for word in ['sorry', 'apologize', 'error']):
            return 'error'
        else:
            return 'general'
    
    async def _store_interaction_memory(self, user_id: str, message: str, response: AgentResponse):
        """Store interaction in long-term memory"""
        try:
            interaction_data = {
                'user_message': message,
                'agent_response': response.text,
                'confidence': response.confidence,
                'response_type': response.response_type,
                'timestamp': response.timestamp.isoformat()
            }
            
            memory_service.store_memory(
                user_id=user_id,
                content=f"User: {message}\nAgent: {response.text}",
                metadata={
                    'type': 'conversation',
                    'interaction_data': interaction_data
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to store interaction memory: {e}")
    
    async def process_voice_message(self, user_id: str, audio_data: bytes) -> Dict[str, Any]:
        """Process voice message end-to-end"""
        try:
            # Convert speech to text
            voice_result = await voice_service.process_voice_command(audio_data)
            
            if not voice_result['processed']:
                return {
                    'success': False,
                    'error': voice_result['error'],
                    'response': None
                }
            
            # Process the text message
            response = await self.process_message(user_id, voice_result['command'])
            
            # Generate voice response
            voice_response = await voice_service.create_voice_response(response.text)
            
            return {
                'success': True,
                'transcription': voice_result['command'],
                'confidence': voice_result['confidence'],
                'response': asdict(response),
                'voice_response': voice_response,
                'error': None
            }
            
        except Exception as e:
            self.logger.error(f"Voice message processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': None
            }
    
    def get_conversation_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user's conversation"""
        if user_id not in self.conversations:
            return {'exists': False}
        
        conversation = self.conversations[user_id]
        
        return {
            'exists': True,
            'session_id': conversation.session_id,
            'interaction_count': conversation.interaction_count,
            'last_interaction': conversation.last_interaction.isoformat(),
            'current_topic': conversation.current_topic,
            'message_count': len(conversation.conversation_history),
            'user_preferences': conversation.user_preferences
        }

# Global agent instance
cpas_agent = CPASAgent()
