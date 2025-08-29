
"""
Master Agent - Central Intelligence Orchestrator
Implements HRM reasoning and intelligent task delegation
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from loguru import logger
from pydantic import BaseModel, Field

from .llm_service import LLMService
from .memory_service import MemoryService
from ..models.agent import Agent
from ..multi_agent.task_delegator import TaskDelegator
from ..multi_agent.collaboration_engine import CollaborationEngine


class ReasoningLevel(Enum):
    """HRM Reasoning Hierarchy Levels"""
    REACTIVE = "reactive"           # Immediate response
    DELIBERATIVE = "deliberative"   # Planned response
    REFLECTIVE = "reflective"       # Meta-cognitive analysis
    STRATEGIC = "strategic"         # Long-term planning


@dataclass
class ReasoningContext:
    """Context for HRM reasoning process"""
    level: ReasoningLevel
    task_complexity: float
    time_pressure: float
    available_resources: List[str]
    user_preferences: Dict[str, Any]
    historical_performance: Dict[str, float]


class MasterAgent:
    """
    Master Agent with HRM reasoning capabilities
    Central orchestrator for all CPAS operations
    """
    
    def __init__(self, llm_service: LLMService, memory_service: MemoryService):
        self.llm_service = llm_service
        self.memory_service = memory_service
        self.task_delegator = TaskDelegator()
        self.collaboration_engine = CollaborationEngine()
        
        # Master Agent personality and capabilities
        self.personality = {
            "name": "Greta",
            "accent": "german-english",
            "traits": ["precise", "analytical", "warm", "intelligent"],
            "expertise": ["research", "analysis", "coordination", "osint"],
            "communication_style": "professional_warm"
        }
        
        # Active reasoning contexts
        self.active_contexts: Dict[str, ReasoningContext] = {}
        
        # Performance metrics
        self.performance_metrics = {
            "tasks_completed": 0,
            "success_rate": 0.0,
            "average_response_time": 0.0,
            "user_satisfaction": 0.0
        }
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for Master Agent processing
        Implements HRM reasoning hierarchy
        """
        try:
            # Extract request details
            user_input = request.get("input", "")
            context = request.get("context", {})
            priority = request.get("priority", "normal")
            
            # Create reasoning context
            reasoning_context = await self._create_reasoning_context(
                user_input, context, priority
            )
            
            # Apply HRM reasoning
            response = await self._hrm_reasoning_process(
                user_input, reasoning_context
            )
            
            # Update performance metrics
            await self._update_performance_metrics(response)
            
            return response
            
        except Exception as e:
            logger.error(f"Master Agent processing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_response": "I apologize, but I encountered an error processing your request."
            }
    
    async def _create_reasoning_context(
        self, user_input: str, context: Dict, priority: str
    ) -> ReasoningContext:
        """Create reasoning context based on input analysis"""
        
        # Analyze task complexity
        complexity = await self._analyze_task_complexity(user_input)
        
        # Determine time pressure
        time_pressure = self._calculate_time_pressure(priority, context)
        
        # Get available resources
        resources = await self._get_available_resources()
        
        # Retrieve user preferences
        user_prefs = await self._get_user_preferences(context.get("user_id"))
        
        # Get historical performance data
        history = await self._get_historical_performance()
        
        # Determine reasoning level
        level = self._determine_reasoning_level(complexity, time_pressure)
        
        return ReasoningContext(
            level=level,
            task_complexity=complexity,
            time_pressure=time_pressure,
            available_resources=resources,
            user_preferences=user_prefs,
            historical_performance=history
        )
    
    async def _hrm_reasoning_process(
        self, user_input: str, context: ReasoningContext
    ) -> Dict[str, Any]:
        """
        Hierarchical Reasoning Model (HRM) processing
        Implements different reasoning levels based on context
        """
        
        if context.level == ReasoningLevel.REACTIVE:
            return await self._reactive_processing(user_input, context)
        
        elif context.level == ReasoningLevel.DELIBERATIVE:
            return await self._deliberative_processing(user_input, context)
        
        elif context.level == ReasoningLevel.REFLECTIVE:
            return await self._reflective_processing(user_input, context)
        
        elif context.level == ReasoningLevel.STRATEGIC:
            return await self._strategic_processing(user_input, context)
        
        else:
            # Default to deliberative
            return await self._deliberative_processing(user_input, context)
    
    async def _reactive_processing(
        self, user_input: str, context: ReasoningContext
    ) -> Dict[str, Any]:
        """Fast, immediate response processing"""
        
        # Quick pattern matching and direct response
        response = await self.llm_service.generate_response(
            prompt=f"Provide a quick, direct response to: {user_input}",
            model="llama3.2:3b",
            max_tokens=150
        )
        
        return {
            "success": True,
            "response": response,
            "reasoning_level": "reactive",
            "processing_time": "< 1s",
            "confidence": 0.7
        }
    
    async def _deliberative_processing(
        self, user_input: str, context: ReasoningContext
    ) -> Dict[str, Any]:
        """Planned, thoughtful response processing"""
        
        # Analyze intent and plan response
        intent_analysis = await self._analyze_intent(user_input)
        
        # Check if task delegation is needed
        if intent_analysis.get("requires_delegation"):
            return await self._delegate_task(user_input, intent_analysis, context)
        
        # Generate thoughtful response
        response = await self.llm_service.generate_response(
            prompt=self._create_deliberative_prompt(user_input, context),
            model="deepseek-r1:7b",
            max_tokens=500
        )
        
        return {
            "success": True,
            "response": response,
            "reasoning_level": "deliberative",
            "intent": intent_analysis,
            "confidence": 0.85
        }
    
    async def _reflective_processing(
        self, user_input: str, context: ReasoningContext
    ) -> Dict[str, Any]:
        """Meta-cognitive analysis and response"""
        
        # Analyze the problem from multiple perspectives
        perspectives = await self._multi_perspective_analysis(user_input)
        
        # Consider past similar situations
        similar_cases = await self.memory_service.search_memories(
            query=user_input,
            limit=5,
            memory_type="experience"
        )
        
        # Generate reflective response
        response = await self.llm_service.generate_response(
            prompt=self._create_reflective_prompt(user_input, perspectives, similar_cases),
            model="mixtral:8x7b",
            max_tokens=800
        )
        
        return {
            "success": True,
            "response": response,
            "reasoning_level": "reflective",
            "perspectives": perspectives,
            "similar_cases": len(similar_cases),
            "confidence": 0.9
        }
    
    async def _strategic_processing(
        self, user_input: str, context: ReasoningContext
    ) -> Dict[str, Any]:
        """Long-term strategic planning and response"""
        
        # Create comprehensive analysis
        strategic_analysis = await self._strategic_analysis(user_input, context)
        
        # Generate multi-step plan
        action_plan = await self._create_action_plan(strategic_analysis)
        
        # Consider resource allocation
        resource_plan = await self._plan_resource_allocation(action_plan)
        
        # Generate strategic response
        response = await self.llm_service.generate_response(
            prompt=self._create_strategic_prompt(user_input, strategic_analysis, action_plan),
            model="mixtral:8x7b",
            max_tokens=1200
        )
        
        return {
            "success": True,
            "response": response,
            "reasoning_level": "strategic",
            "analysis": strategic_analysis,
            "action_plan": action_plan,
            "resource_plan": resource_plan,
            "confidence": 0.95
        }
    
    async def _delegate_task(
        self, user_input: str, intent_analysis: Dict, context: ReasoningContext
    ) -> Dict[str, Any]:
        """Delegate task to appropriate specialized agent"""
        
        # Determine best agent for the task
        target_agent = await self._select_target_agent(intent_analysis)
        
        # Prepare delegation context
        delegation_context = {
            "original_request": user_input,
            "intent": intent_analysis,
            "reasoning_context": context,
            "master_agent_guidance": await self._create_guidance(intent_analysis)
        }
        
        # Delegate to specialized agent
        result = await self.task_delegator.delegate_task(
            task=user_input,
            target_agent=target_agent,
            context=delegation_context
        )
        
        # Monitor and coordinate if needed
        if result.get("requires_coordination"):
            result = await self.collaboration_engine.coordinate_agents(
                primary_agent=target_agent,
                task=user_input,
                context=delegation_context
            )
        
        return {
            "success": True,
            "response": result.get("response"),
            "delegated_to": target_agent,
            "reasoning_level": context.level.value,
            "coordination_used": result.get("requires_coordination", False)
        }
    
    async def _analyze_task_complexity(self, user_input: str) -> float:
        """Analyze the complexity of the user's request"""
        
        complexity_indicators = [
            len(user_input.split()),  # Word count
            user_input.count('?'),    # Number of questions
            user_input.count('and'),  # Conjunction complexity
            user_input.count('or'),   # Alternative complexity
        ]
        
        # Simple heuristic - can be enhanced with ML
        base_complexity = sum(complexity_indicators) / 100.0
        return min(max(base_complexity, 0.1), 1.0)
    
    def _calculate_time_pressure(self, priority: str, context: Dict) -> float:
        """Calculate time pressure based on priority and context"""
        
        priority_weights = {
            "urgent": 0.9,
            "high": 0.7,
            "normal": 0.5,
            "low": 0.3
        }
        
        return priority_weights.get(priority, 0.5)
    
    async def _get_available_resources(self) -> List[str]:
        """Get list of available system resources"""
        
        return [
            "task_manager_agent",
            "research_agent", 
            "creative_agent",
            "technical_agent",
            "personal_assistant",
            "osint_toolkit",
            "memory_system",
            "llm_models"
        ]
    
    async def _get_user_preferences(self, user_id: Optional[str]) -> Dict[str, Any]:
        """Retrieve user preferences from memory"""
        
        if not user_id:
            return {}
        
        prefs = await self.memory_service.get_user_preferences(user_id)
        return prefs or {}
    
    async def _get_historical_performance(self) -> Dict[str, float]:
        """Get historical performance metrics"""
        
        return self.performance_metrics.copy()
    
    def _determine_reasoning_level(self, complexity: float, time_pressure: float) -> ReasoningLevel:
        """Determine appropriate reasoning level based on context"""
        
        if time_pressure > 0.8:
            return ReasoningLevel.REACTIVE
        elif complexity < 0.3:
            return ReasoningLevel.DELIBERATIVE
        elif complexity < 0.7:
            return ReasoningLevel.REFLECTIVE
        else:
            return ReasoningLevel.STRATEGIC
    
    async def _analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyze user intent and determine required capabilities"""
        
        # Use LLM for intent analysis
        intent_prompt = f"""
        Analyze the following user request and determine:
        1. Primary intent (question, task, request, etc.)
        2. Required capabilities (research, analysis, creation, etc.)
        3. Whether task delegation is needed
        4. Estimated complexity (1-10)
        5. Suggested agent type if delegation needed
        
        User request: {user_input}
        
        Respond in JSON format.
        """
        
        response = await self.llm_service.generate_response(
            prompt=intent_prompt,
            model="deepseek-r1:7b",
            max_tokens=300
        )
        
        try:
            return json.loads(response)
        except:
            return {
                "primary_intent": "general_query",
                "required_capabilities": ["analysis"],
                "requires_delegation": False,
                "complexity": 5
            }
    
    def _create_deliberative_prompt(self, user_input: str, context: ReasoningContext) -> str:
        """Create prompt for deliberative reasoning"""
        
        return f"""
        You are Greta, a highly intelligent German-English AI assistant with expertise in research and analysis.
        
        User request: {user_input}
        
        Context:
        - Task complexity: {context.task_complexity}
        - Available resources: {', '.join(context.available_resources)}
        - User preferences: {context.user_preferences}
        
        Provide a thoughtful, well-reasoned response that demonstrates careful consideration of the request.
        Use your German precision and analytical skills while maintaining a warm, professional tone.
        """
    
    def _create_reflective_prompt(self, user_input: str, perspectives: List[str], similar_cases: List) -> str:
        """Create prompt for reflective reasoning"""
        
        return f"""
        You are Greta, conducting a deep reflective analysis.
        
        User request: {user_input}
        
        Multiple perspectives to consider:
        {chr(10).join(f"- {p}" for p in perspectives)}
        
        Similar past experiences: {len(similar_cases)} cases found
        
        Provide a comprehensive response that:
        1. Acknowledges the complexity of the request
        2. Considers multiple viewpoints
        3. Draws insights from past experiences
        4. Offers a nuanced, well-balanced perspective
        
        Maintain your characteristic German precision while being warm and approachable.
        """
    
    def _create_strategic_prompt(self, user_input: str, analysis: Dict, action_plan: List) -> str:
        """Create prompt for strategic reasoning"""
        
        return f"""
        You are Greta, providing strategic guidance and long-term planning.
        
        User request: {user_input}
        
        Strategic analysis: {analysis}
        
        Proposed action plan:
        {chr(10).join(f"{i+1}. {step}" for i, step in enumerate(action_plan))}
        
        Provide a comprehensive strategic response that:
        1. Outlines the long-term implications
        2. Presents the strategic plan clearly
        3. Identifies potential risks and mitigation strategies
        4. Offers implementation guidance
        5. Suggests success metrics
        
        Use your German engineering mindset for systematic planning while maintaining warmth.
        """
    
    async def _multi_perspective_analysis(self, user_input: str) -> List[str]:
        """Analyze request from multiple perspectives"""
        
        perspectives = [
            "Technical feasibility",
            "User experience impact", 
            "Resource requirements",
            "Risk assessment",
            "Long-term implications",
            "Alternative approaches"
        ]
        
        return perspectives
    
    async def _strategic_analysis(self, user_input: str, context: ReasoningContext) -> Dict[str, Any]:
        """Conduct comprehensive strategic analysis"""
        
        return {
            "scope": "comprehensive",
            "stakeholders": ["user", "system", "data"],
            "timeline": "long-term",
            "complexity": context.task_complexity,
            "resources_needed": context.available_resources
        }
    
    async def _create_action_plan(self, analysis: Dict) -> List[str]:
        """Create multi-step action plan"""
        
        return [
            "Analyze requirements thoroughly",
            "Identify necessary resources",
            "Create implementation timeline", 
            "Execute plan systematically",
            "Monitor progress and adjust",
            "Evaluate results and learn"
        ]
    
    async def _plan_resource_allocation(self, action_plan: List) -> Dict[str, Any]:
        """Plan resource allocation for action plan"""
        
        return {
            "agents_needed": ["research", "technical"],
            "estimated_time": "medium-term",
            "priority_level": "high",
            "monitoring_required": True
        }
    
    async def _select_target_agent(self, intent_analysis: Dict) -> str:
        """Select the most appropriate agent for task delegation"""
        
        intent = intent_analysis.get("primary_intent", "")
        capabilities = intent_analysis.get("required_capabilities", [])
        
        # Agent selection logic
        if "research" in capabilities or "analysis" in capabilities:
            return "research_agent"
        elif "creative" in capabilities or "content" in capabilities:
            return "creative_agent"
        elif "technical" in capabilities or "code" in capabilities:
            return "technical_agent"
        elif "schedule" in capabilities or "organize" in capabilities:
            return "personal_assistant"
        else:
            return "task_manager_agent"
    
    async def _create_guidance(self, intent_analysis: Dict) -> str:
        """Create guidance for delegated agents"""
        
        return f"""
        Master Agent Guidance:
        - Primary intent: {intent_analysis.get('primary_intent')}
        - Required capabilities: {intent_analysis.get('required_capabilities')}
        - Complexity level: {intent_analysis.get('complexity', 5)}/10
        - Expected quality: High precision with German attention to detail
        - Communication style: Professional yet warm
        """
    
    async def _update_performance_metrics(self, response: Dict[str, Any]) -> None:
        """Update Master Agent performance metrics"""
        
        if response.get("success"):
            self.performance_metrics["tasks_completed"] += 1
            
            # Update success rate
            total_tasks = self.performance_metrics["tasks_completed"]
            current_success_rate = self.performance_metrics["success_rate"]
            self.performance_metrics["success_rate"] = (
                (current_success_rate * (total_tasks - 1) + 1.0) / total_tasks
            )
        
        # Store metrics in memory for analysis
        await self.memory_service.store_memory(
            content=f"Performance update: {self.performance_metrics}",
            memory_type="system_metrics",
            importance=0.3
        )
    
    async def get_status(self) -> Dict[str, Any]:
        """Get Master Agent status and metrics"""
        
        return {
            "agent_name": "Greta (Master Agent)",
            "personality": self.personality,
            "active_contexts": len(self.active_contexts),
            "performance_metrics": self.performance_metrics,
            "available_capabilities": [
                "HRM Reasoning",
                "Task Delegation", 
                "Agent Coordination",
                "OSINT Analysis",
                "Strategic Planning",
                "Multi-perspective Analysis"
            ],
            "status": "active"
        }
