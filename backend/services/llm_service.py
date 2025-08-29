
"""
LLM interaction service for Ollama and future API-based models
"""

import asyncio
import time
from typing import List, Optional, Dict, Any, AsyncGenerator
import httpx
from loguru import logger

from models.llm import LLMRequest, LLMResponse, ModelInfo, ModelListResponse, ChatRequest, ChatMessage
from config import settings
from services.memory_service import MemoryService

class LLMService:
    """Service for LLM interactions"""
    
    def __init__(self):
        self.ollama_base_url = settings.ollama_base_url
        self.default_model = settings.default_model
        self.memory_service = MemoryService()
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text using LLM"""
        start_time = time.time()
        
        try:
            # Use specified model or default
            model = request.model or self.default_model
            
            # Prepare context if memory is enabled
            context = []
            if request.use_memory and request.context:
                context = request.context
            elif request.use_memory:
                # Retrieve relevant memories
                context = await self._get_memory_context(request.prompt)
            
            # Build prompt with context
            full_prompt = self._build_prompt_with_context(
                request.prompt,
                context,
                request.system_prompt
            )
            
            # Make request to Ollama
            response_text = await self._call_ollama_generate(
                model=model,
                prompt=full_prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            processing_time = time.time() - start_time
            
            # Save to memory if enabled
            memory_id = None
            if request.save_to_memory:
                memory_id = await self._save_interaction_to_memory(
                    request.prompt,
                    response_text,
                    model
                )
            
            return LLMResponse(
                response=response_text,
                model=model,
                tokens_used=None,  # Ollama doesn't return token count
                processing_time=processing_time,
                memory_id=memory_id,
                context_used=len(context) > 0
            )
            
        except Exception as e:
            logger.error(f"Failed to generate text: {e}")
            raise
    
    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate streaming text response"""
        try:
            model = request.model or self.default_model
            
            # Prepare context
            context = []
            if request.use_memory:
                context = await self._get_memory_context(request.prompt)
            
            full_prompt = self._build_prompt_with_context(
                request.prompt,
                context,
                request.system_prompt
            )
            
            # Stream from Ollama
            async for chunk in self._call_ollama_stream(
                model=model,
                prompt=full_prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ):
                yield chunk
                
        except Exception as e:
            logger.error(f"Failed to generate streaming text: {e}")
            yield f"Error: {str(e)}"
    
    async def chat(self, request: ChatRequest) -> LLMResponse:
        """Chat with LLM using conversation context"""
        start_time = time.time()
        
        try:
            model = request.model or self.default_model
            
            # Convert chat messages to prompt format
            prompt = self._messages_to_prompt(request.messages)
            
            # Add memory context if needed
            if len(request.messages) > 0:
                last_message = request.messages[-1].content
                memory_context = await self._get_memory_context(last_message)
                if memory_context:
                    context_prompt = "\n".join([f"Context: {ctx['content']}" for ctx in memory_context])
                    prompt = f"{context_prompt}\n\n{prompt}"
            
            # Generate response
            response_text = await self._call_ollama_generate(
                model=model,
                prompt=prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            processing_time = time.time() - start_time
            
            # Save conversation to memory
            memory_id = await self._save_conversation_to_memory(
                request.messages,
                response_text,
                model,
                request.session_id
            )
            
            return LLMResponse(
                response=response_text,
                model=model,
                tokens_used=None,
                processing_time=processing_time,
                memory_id=memory_id,
                context_used=True
            )
            
        except Exception as e:
            logger.error(f"Failed to process chat: {e}")
            raise
    
    async def list_models(self) -> ModelListResponse:
        """List available models"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ollama_base_url}/api/tags")
                response.raise_for_status()
                
                data = response.json()
                models = []
                
                for model_data in data.get("models", []):
                    model_info = ModelInfo(
                        name=model_data.get("name", ""),
                        size=model_data.get("size"),
                        family=model_data.get("details", {}).get("family"),
                        format=model_data.get("details", {}).get("format"),
                        parameter_size=model_data.get("details", {}).get("parameter_size"),
                        quantization_level=model_data.get("details", {}).get("quantization_level"),
                        modified_at=model_data.get("modified_at"),
                        digest=model_data.get("digest"),
                        details=model_data.get("details", {})
                    )
                    models.append(model_info)
                
                local_models = [model.name for model in models]
                api_models = []  # Future: Add API-based models
                
                return ModelListResponse(
                    models=models,
                    total_count=len(models),
                    local_models=local_models,
                    api_models=api_models
                )
                
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            raise
    
    async def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get information about a specific model"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/show",
                    json={"name": model_name}
                )
                
                if response.status_code == 404:
                    return None
                
                response.raise_for_status()
                data = response.json()
                
                return ModelInfo(
                    name=model_name,
                    size=data.get("size"),
                    family=data.get("details", {}).get("family"),
                    format=data.get("details", {}).get("format"),
                    parameter_size=data.get("details", {}).get("parameter_size"),
                    quantization_level=data.get("details", {}).get("quantization_level"),
                    modified_at=data.get("modified_at"),
                    digest=data.get("digest"),
                    details=data.get("details", {})
                )
                
        except Exception as e:
            logger.error(f"Failed to get model info for {model_name}: {e}")
            raise
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull/download a model"""
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/pull",
                    json={"name": model_name}
                )
                response.raise_for_status()
                
                logger.info(f"Successfully pulled model: {model_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False
    
    async def delete_model(self, model_name: str) -> bool:
        """Delete a local model"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.ollama_base_url}/api/delete",
                    json={"name": model_name}
                )
                
                if response.status_code == 404:
                    return False
                
                response.raise_for_status()
                logger.info(f"Successfully deleted model: {model_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete model {model_name}: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check LLM service health"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.ollama_base_url}/api/tags")
                response.raise_for_status()
                
                return {
                    "status": "healthy",
                    "ollama_url": self.ollama_base_url,
                    "default_model": self.default_model,
                    "models_available": len(response.json().get("models", []))
                }
                
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "ollama_url": self.ollama_base_url
            }
    
    async def _call_ollama_generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Call Ollama generate API"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
            
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                return data.get("response", "")
                
        except Exception as e:
            logger.error(f"Ollama generate call failed: {e}")
            raise
    
    async def _call_ollama_stream(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """Call Ollama streaming generate API"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": temperature
                }
            }
            
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.ollama_base_url}/api/generate",
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line:
                            import json
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    yield data["response"]
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            logger.error(f"Ollama streaming call failed: {e}")
            yield f"Error: {str(e)}"
    
    async def _get_memory_context(self, query: str) -> List[Dict[str, Any]]:
        """Get relevant memory context for a query"""
        try:
            from models.memory import MemorySearchRequest
            
            search_request = MemorySearchRequest(
                query=query,
                limit=5,
                similarity_threshold=0.6
            )
            
            memories = await self.memory_service.search_memories(search_request)
            
            context = []
            for memory in memories:
                context.append({
                    "content": memory.content,
                    "type": memory.memory_type,
                    "importance": memory.importance
                })
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get memory context: {e}")
            return []
    
    def _build_prompt_with_context(
        self,
        prompt: str,
        context: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> str:
        """Build prompt with memory context"""
        parts = []
        
        if system_prompt:
            parts.append(f"System: {system_prompt}")
        
        if context:
            parts.append("Relevant context from memory:")
            for ctx in context:
                parts.append(f"- {ctx['content']}")
            parts.append("")
        
        parts.append(f"User: {prompt}")
        parts.append("Assistant:")
        
        return "\n".join(parts)
    
    def _messages_to_prompt(self, messages: List[ChatMessage]) -> str:
        """Convert chat messages to prompt format"""
        parts = []
        
        for message in messages:
            role = message.role.capitalize()
            parts.append(f"{role}: {message.content}")
        
        parts.append("Assistant:")
        return "\n".join(parts)
    
    async def _save_interaction_to_memory(
        self,
        prompt: str,
        response: str,
        model: str
    ) -> Optional[str]:
        """Save LLM interaction to memory"""
        try:
            from models.memory import MemoryCreate
            
            memory_data = MemoryCreate(
                content=f"Q: {prompt}\nA: {response}",
                memory_type="llm_interaction",
                tags=["llm", "conversation", model],
                metadata={
                    "model": model,
                    "prompt": prompt,
                    "response": response
                },
                importance=0.6
            )
            
            memory = await self.memory_service.create_memory(memory_data)
            return memory.id
            
        except Exception as e:
            logger.error(f"Failed to save interaction to memory: {e}")
            return None
    
    async def _save_conversation_to_memory(
        self,
        messages: List[ChatMessage],
        response: str,
        model: str,
        session_id: Optional[str] = None
    ) -> Optional[str]:
        """Save conversation to memory"""
        try:
            from models.memory import MemoryCreate
            
            # Build conversation content
            conversation_parts = []
            for message in messages[-3:]:  # Last 3 messages for context
                conversation_parts.append(f"{message.role}: {message.content}")
            conversation_parts.append(f"assistant: {response}")
            
            content = "\n".join(conversation_parts)
            
            memory_data = MemoryCreate(
                content=content,
                memory_type="conversation",
                tags=["chat", "conversation", model],
                metadata={
                    "model": model,
                    "session_id": session_id,
                    "message_count": len(messages) + 1,
                    "latest_response": response
                },
                importance=0.7
            )
            
            memory = await self.memory_service.create_memory(memory_data)
            return memory.id
            
        except Exception as e:
            logger.error(f"Failed to save conversation to memory: {e}")
            return None
