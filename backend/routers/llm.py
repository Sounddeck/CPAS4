
"""
LLM interaction API routes
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List
from loguru import logger

from models.llm import LLMRequest, LLMResponse, ModelListResponse, ChatRequest, ChatMessage
from services.llm_service import LLMService

router = APIRouter()

async def get_llm_service() -> LLMService:
    """Dependency to get LLM service instance"""
    return LLMService()

@router.post("/generate", response_model=LLMResponse)
async def generate_text(
    request: LLMRequest,
    service: LLMService = Depends(get_llm_service)
):
    """Generate text using LLM"""
    try:
        if request.stream:
            # Return streaming response
            return StreamingResponse(
                service.generate_stream(request),
                media_type="text/plain"
            )
        else:
            # Return complete response
            response = await service.generate(request)
            return response
    except Exception as e:
        logger.error(f"Failed to generate text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=LLMResponse)
async def chat(
    request: ChatRequest,
    service: LLMService = Depends(get_llm_service)
):
    """Chat with LLM using conversation context"""
    try:
        response = await service.chat(request)
        return response
    except Exception as e:
        logger.error(f"Failed to process chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models", response_model=ModelListResponse)
async def list_models(
    service: LLMService = Depends(get_llm_service)
):
    """List available LLM models"""
    try:
        models_info = await service.list_models()
        return models_info
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/{model_name}")
async def get_model_info(
    model_name: str,
    service: LLMService = Depends(get_llm_service)
):
    """Get information about a specific model"""
    try:
        model_info = await service.get_model_info(model_name)
        if not model_info:
            raise HTTPException(status_code=404, detail="Model not found")
        
        return {
            "success": True,
            "message": "Model information retrieved",
            "model": model_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models/{model_name}/pull")
async def pull_model(
    model_name: str,
    service: LLMService = Depends(get_llm_service)
):
    """Pull/download a model"""
    try:
        success = await service.pull_model(model_name)
        if success:
            return {
                "success": True,
                "message": f"Model {model_name} pulled successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to pull model")
    except Exception as e:
        logger.error(f"Failed to pull model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/models/{model_name}")
async def delete_model(
    model_name: str,
    service: LLMService = Depends(get_llm_service)
):
    """Delete a local model"""
    try:
        success = await service.delete_model(model_name)
        if success:
            return {
                "success": True,
                "message": f"Model {model_name} deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Model not found")
    except Exception as e:
        logger.error(f"Failed to delete model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def llm_health_check(
    service: LLMService = Depends(get_llm_service)
):
    """Check LLM service health"""
    try:
        health_status = await service.health_check()
        return {
            "success": True,
            "message": "LLM service health check",
            "status": health_status
        }
    except Exception as e:
        logger.error(f"LLM health check failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))
