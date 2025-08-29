
"""
Voice Router for CPAS
API endpoints for voice processing functionality
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import json
import asyncio
import tempfile
from pathlib import Path

from ..services.voice_service import voice_service

router = APIRouter(prefix="/voice", tags=["voice"])
logger = logging.getLogger(__name__)

# Request/Response Models
class TTSRequest(BaseModel):
    text: str
    output_file: Optional[str] = None

class VoiceCommandResponse(BaseModel):
    success: bool
    command: Optional[str] = None
    confidence: Optional[float] = None
    error: Optional[str] = None

# WebSocket connection manager
class VoiceConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected connections
                self.disconnect(connection)

voice_manager = VoiceConnectionManager()

@router.post("/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    """Convert speech audio to text"""
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Get audio format from filename
        audio_format = audio.filename.split('.')[-1] if audio.filename else 'wav'
        
        # Process speech to text
        result = await voice_service.speech_to_text(audio_data, audio_format)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Speech-to-text failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text-to-speech")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech"""
    try:
        # Generate unique filename if not provided
        if not request.output_file:
            temp_dir = Path(tempfile.gettempdir()) / "cpas_tts"
            temp_dir.mkdir(exist_ok=True)
            request.output_file = str(temp_dir / f"tts_output_{hash(request.text)}.wav")
        
        # Process text to speech
        result = await voice_service.text_to_speech(request.text, request.output_file)
        
        if result['success'] and result['output_file']:
            return JSONResponse(content={
                'success': True,
                'message': 'Text-to-speech completed',
                'output_file': result['output_file'],
                'download_url': f"/voice/download/{Path(result['output_file']).name}"
            })
        else:
            return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Text-to-speech failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_audio_file(filename: str):
    """Download generated audio file"""
    try:
        temp_dir = Path(tempfile.gettempdir()) / "cpas_tts"
        file_path = temp_dir / filename
        
        if file_path.exists():
            return FileResponse(
                path=str(file_path),
                media_type='audio/wav',
                filename=filename
            )
        else:
            raise HTTPException(status_code=404, detail="File not found")
            
    except Exception as e:
        logger.error(f"File download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-command")
async def process_voice_command(audio: UploadFile = File(...)):
    """Process a complete voice command"""
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Process voice command
        result = await voice_service.process_voice_command(audio_data)
        
        return VoiceCommandResponse(
            success=result['processed'],
            command=result.get('command'),
            confidence=result.get('confidence'),
            error=result.get('error')
        )
        
    except Exception as e:
        logger.error(f"Voice command processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/supported-formats")
async def get_supported_formats():
    """Get supported audio formats"""
    try:
        formats = voice_service.get_supported_formats()
        return JSONResponse(content=formats)
        
    except Exception as e:
        logger.error(f"Failed to get supported formats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voice-info")
async def get_voice_info():
    """Get information about available voices"""
    try:
        voice_info = voice_service.get_voice_info()
        return JSONResponse(content=voice_info)
        
    except Exception as e:
        logger.error(f"Failed to get voice info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/{user_id}")
async def voice_websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time voice interaction"""
    await voice_manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get('type')
            
            if message_type == 'audio_data':
                # Process audio data
                audio_bytes = bytes.fromhex(message_data['data'])
                
                # Convert speech to text
                stt_result = await voice_service.speech_to_text(audio_bytes)
                
                # Send transcription back
                await voice_manager.send_personal_message(
                    json.dumps({
                        'type': 'transcription',
                        'text': stt_result['text'],
                        'confidence': stt_result['confidence'],
                        'error': stt_result.get('error')
                    }),
                    websocket
                )
                
                # If transcription successful, process as command
                if stt_result['text'] and not stt_result.get('error'):
                    command_result = await voice_service.process_voice_command(audio_bytes)
                    
                    await voice_manager.send_personal_message(
                        json.dumps({
                            'type': 'command_processed',
                            'command': command_result.get('command'),
                            'processed_command': command_result.get('processed_command'),
                            'confidence': command_result.get('confidence')
                        }),
                        websocket
                    )
            
            elif message_type == 'tts_request':
                # Generate speech from text
                text = message_data.get('text', '')
                
                # Create temporary file for TTS output
                temp_dir = Path(tempfile.gettempdir()) / "cpas_tts_ws"
                temp_dir.mkdir(exist_ok=True)
                output_file = str(temp_dir / f"ws_tts_{user_id}_{hash(text)}.wav")
                
                tts_result = await voice_service.text_to_speech(text, output_file)
                
                if tts_result['success']:
                    # Read the generated audio file
                    with open(output_file, 'rb') as f:
                        audio_data = f.read()
                    
                    # Send audio data back as hex
                    await voice_manager.send_personal_message(
                        json.dumps({
                            'type': 'audio_response',
                            'audio_data': audio_data.hex(),
                            'text': text
                        }),
                        websocket
                    )
                else:
                    await voice_manager.send_personal_message(
                        json.dumps({
                            'type': 'error',
                            'message': tts_result.get('error', 'TTS failed')
                        }),
                        websocket
                    )
            
            elif message_type == 'ping':
                # Respond to ping
                await voice_manager.send_personal_message(
                    json.dumps({'type': 'pong'}),
                    websocket
                )
            
    except WebSocketDisconnect:
        voice_manager.disconnect(websocket)
        logger.info(f"Voice WebSocket disconnected for user: {user_id}")
    except Exception as e:
        logger.error(f"Voice WebSocket error: {e}")
        voice_manager.disconnect(websocket)

@router.get("/health")
async def voice_health_check():
    """Health check for voice service"""
    try:
        # Check voice service components
        voice_info = voice_service.get_voice_info()
        formats = voice_service.get_supported_formats()
        
        health_status = {
            'whisper_available': voice_service.whisper_model is not None,
            'tts_available': voice_service.tts_engine is not None,
            'supported_formats': formats,
            'active_connections': len(voice_manager.active_connections)
        }
        
        return JSONResponse(content={
            'status': 'healthy',
            'components': health_status
        })
        
    except Exception as e:
        logger.error(f"Voice health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={'status': 'unhealthy', 'error': str(e)}
        )
