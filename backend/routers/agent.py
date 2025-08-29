
"""
Agent Router for CPAS
API endpoints for AI agent interactions
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import asyncio

from ..services.agent_core import cpas_agent
from ..services.learning_service import learning_service

router = APIRouter(prefix="/agent", tags=["agent"])
logger = logging.getLogger(__name__)

# Request/Response Models
class MessageRequest(BaseModel):
    user_id: str
    message: str
    context: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    success: bool
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class FeedbackRequest(BaseModel):
    user_id: str
    interaction_id: str
    feedback_type: str  # positive, negative, neutral
    feedback_score: float  # -1.0 to 1.0
    feedback_text: Optional[str] = None

@router.post("/message", response_model=MessageResponse)
async def process_message(request: MessageRequest):
    """Process a text message from user"""
    try:
        response = await cpas_agent.process_message(
            user_id=request.user_id,
            message=request.message,
            context=request.context
        )
        
        # Learn from interaction
        interaction_data = {
            'user_message': request.message,
            'agent_response': response.text,
            'confidence': response.confidence,
            'response_type': response.response_type,
            'processing_time': response.metadata.get('processing_time', 0),
            'reasoning_chain': response.reasoning_chain,
            'metadata': response.metadata
        }
        
        learning_insights = learning_service.learn_from_interaction(
            request.user_id, 
            interaction_data
        )
        
        return MessageResponse(
            success=True,
            response={
                'text': response.text,
                'confidence': response.confidence,
                'response_type': response.response_type,
                'reasoning_chain': response.reasoning_chain.__dict__ if response.reasoning_chain else None,
                'timestamp': response.timestamp.isoformat(),
                'metadata': response.metadata,
                'learning_insights': learning_insights
            }
        )
        
    except Exception as e:
        logger.error(f"Message processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice-message")
async def process_voice_message(
    user_id: str,
    audio: UploadFile = File(...)
):
    """Process a voice message from user"""
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Process voice message
        result = await cpas_agent.process_voice_message(user_id, audio_data)
        
        if result['success']:
            # Learn from interaction
            interaction_data = {
                'user_message': result['transcription'],
                'agent_response': result['response']['text'],
                'confidence': result['response']['confidence'],
                'response_type': result['response']['response_type'],
                'processing_time': result['response']['metadata'].get('processing_time', 0),
                'voice_used': True,
                'transcription_confidence': result['confidence']
            }
            
            learning_insights = learning_service.learn_from_interaction(
                user_id, 
                interaction_data
            )
            
            result['learning_insights'] = learning_insights
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Voice message processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/{user_id}")
async def get_conversation_summary(user_id: str):
    """Get conversation summary for a user"""
    try:
        summary = cpas_agent.get_conversation_summary(user_id)
        return JSONResponse(content=summary)
        
    except Exception as e:
        logger.error(f"Failed to get conversation summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def record_feedback(request: FeedbackRequest):
    """Record user feedback for learning"""
    try:
        learning_service.record_feedback(
            user_id=request.user_id,
            interaction_id=request.interaction_id,
            feedback_type=request.feedback_type,
            feedback_score=request.feedback_score,
            feedback_text=request.feedback_text
        )
        
        return JSONResponse(content={
            'success': True,
            'message': 'Feedback recorded successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to record feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """Get user preferences and learning data"""
    try:
        learning_summary = learning_service.get_learning_summary(user_id)
        return JSONResponse(content=learning_summary)
        
    except Exception as e:
        logger.error(f"Failed to get user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check for agent service"""
    try:
        # Check if core components are working
        health_status = {
            'agent_available': cpas_agent.agent_executor is not None,
            'llm_available': cpas_agent.llm is not None,
            'learning_active': True,
            'timestamp': cpas_agent.conversations.__len__() if hasattr(cpas_agent, 'conversations') else 0
        }
        
        return JSONResponse(content={
            'status': 'healthy',
            'components': health_status
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={'status': 'unhealthy', 'error': str(e)}
        )
