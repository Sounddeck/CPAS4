
"""
Voice Input/Output Service for CPAS
Handles speech-to-text and text-to-speech functionality
"""

import os
import io
import wave
import tempfile
import asyncio
import logging
from typing import Optional, Dict, Any, BinaryIO
from pathlib import Path

try:
    import whisper
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Voice libraries not available: {e}")
    VOICE_AVAILABLE = False

class VoiceService:
    """Service for handling voice input and output"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.whisper_model = None
        self.tts_engine = None
        self.temp_dir = Path(tempfile.gettempdir()) / "cpas_voice"
        self.temp_dir.mkdir(exist_ok=True)
        
        if VOICE_AVAILABLE:
            self._initialize_services()
        else:
            self.logger.warning("Voice services not available")
    
    def _initialize_services(self):
        """Initialize Whisper and TTS services"""
        try:
            # Initialize Whisper for STT
            self.logger.info("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
            self.logger.info("Whisper model loaded successfully")
            
            # Initialize pyttsx3 for TTS
            self.logger.info("Initializing TTS engine...")
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS settings
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Use first available voice
                self.tts_engine.setProperty('voice', voices[0].id)
            
            # Set speech rate and volume
            self.tts_engine.setProperty('rate', 150)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.8)  # Volume level (0.0 to 1.0)
            
            self.logger.info("TTS engine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize voice services: {e}")
            self.whisper_model = None
            self.tts_engine = None
    
    async def speech_to_text(self, audio_data: bytes, audio_format: str = "wav") -> Dict[str, Any]:
        """
        Convert speech audio to text using Whisper
        
        Args:
            audio_data: Raw audio data
            audio_format: Audio format (wav, mp3, etc.)
            
        Returns:
            Dict containing transcription and metadata
        """
        if not self.whisper_model:
            return {
                "text": "",
                "error": "Whisper model not available",
                "confidence": 0.0
            }
        
        try:
            # Save audio data to temporary file
            temp_file = self.temp_dir / f"temp_audio_{asyncio.current_task().get_name()}.{audio_format}"
            
            with open(temp_file, "wb") as f:
                f.write(audio_data)
            
            # Transcribe using Whisper
            self.logger.info("Transcribing audio...")
            result = self.whisper_model.transcribe(str(temp_file))
            
            # Clean up temporary file
            temp_file.unlink(missing_ok=True)
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "confidence": self._calculate_confidence(result),
                "segments": result.get("segments", []),
                "error": None
            }
            
        except Exception as e:
            self.logger.error(f"Speech-to-text failed: {e}")
            return {
                "text": "",
                "error": str(e),
                "confidence": 0.0
            }
    
    def _calculate_confidence(self, whisper_result: Dict) -> float:
        """Calculate average confidence from Whisper segments"""
        segments = whisper_result.get("segments", [])
        if not segments:
            return 0.5  # Default confidence
        
        # Average the confidence scores from segments
        confidences = [seg.get("avg_logprob", -1.0) for seg in segments]
        # Convert log probabilities to confidence (rough approximation)
        avg_logprob = sum(confidences) / len(confidences)
        confidence = max(0.0, min(1.0, (avg_logprob + 1.0)))  # Normalize to 0-1
        
        return confidence
    
    async def text_to_speech(self, text: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert text to speech using pyttsx3
        
        Args:
            text: Text to convert to speech
            output_file: Optional output file path
            
        Returns:
            Dict containing result information
        """
        if not self.tts_engine:
            return {
                "success": False,
                "error": "TTS engine not available",
                "output_file": None
            }
        
        try:
            if output_file:
                # Save to file
                self.tts_engine.save_to_file(text, output_file)
                self.tts_engine.runAndWait()
                
                return {
                    "success": True,
                    "output_file": output_file,
                    "text": text,
                    "error": None
                }
            else:
                # Speak directly
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                
                return {
                    "success": True,
                    "output_file": None,
                    "text": text,
                    "error": None
                }
                
        except Exception as e:
            self.logger.error(f"Text-to-speech failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "output_file": None
            }
    
    async def process_voice_command(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Process a voice command end-to-end
        
        Args:
            audio_data: Raw audio data from microphone
            
        Returns:
            Dict containing command and processing results
        """
        # Convert speech to text
        stt_result = await self.speech_to_text(audio_data)
        
        if stt_result["error"]:
            return {
                "command": "",
                "confidence": 0.0,
                "error": stt_result["error"],
                "processed": False
            }
        
        command_text = stt_result["text"]
        confidence = stt_result["confidence"]
        
        # Basic command processing
        processed_command = self._process_command(command_text)
        
        return {
            "command": command_text,
            "processed_command": processed_command,
            "confidence": confidence,
            "language": stt_result.get("language", "unknown"),
            "error": None,
            "processed": True
        }
    
    def _process_command(self, command: str) -> Dict[str, Any]:
        """
        Process and categorize voice commands
        
        Args:
            command: Raw command text
            
        Returns:
            Dict containing processed command information
        """
        command_lower = command.lower().strip()
        
        # Define command categories
        if any(word in command_lower for word in ["hello", "hi", "hey"]):
            return {
                "type": "greeting",
                "action": "greet_user",
                "parameters": {}
            }
        elif any(word in command_lower for word in ["help", "assist", "support"]):
            return {
                "type": "help",
                "action": "provide_help",
                "parameters": {}
            }
        elif any(word in command_lower for word in ["remember", "save", "store"]):
            return {
                "type": "memory",
                "action": "store_information",
                "parameters": {"content": command}
            }
        elif any(word in command_lower for word in ["recall", "what", "tell me"]):
            return {
                "type": "memory",
                "action": "recall_information",
                "parameters": {"query": command}
            }
        elif any(word in command_lower for word in ["calculate", "compute", "solve"]):
            return {
                "type": "computation",
                "action": "solve_problem",
                "parameters": {"problem": command}
            }
        else:
            return {
                "type": "general",
                "action": "process_query",
                "parameters": {"query": command}
            }
    
    async def create_voice_response(self, response_text: str, speak_aloud: bool = True) -> Dict[str, Any]:
        """
        Create a voice response from text
        
        Args:
            response_text: Text to convert to speech
            speak_aloud: Whether to speak the response aloud
            
        Returns:
            Dict containing response information
        """
        if speak_aloud:
            tts_result = await self.text_to_speech(response_text)
            return {
                "text": response_text,
                "spoken": tts_result["success"],
                "error": tts_result.get("error")
            }
        else:
            return {
                "text": response_text,
                "spoken": False,
                "error": None
            }
    
    def get_supported_formats(self) -> Dict[str, list]:
        """Get supported audio formats"""
        return {
            "input_formats": ["wav", "mp3", "m4a", "flac", "ogg"],
            "output_formats": ["wav", "mp3"] if self.tts_engine else []
        }
    
    def get_voice_info(self) -> Dict[str, Any]:
        """Get information about available voices"""
        if not self.tts_engine:
            return {"available": False, "voices": []}
        
        try:
            voices = self.tts_engine.getProperty('voices')
            voice_info = []
            
            for voice in voices:
                voice_info.append({
                    "id": voice.id,
                    "name": voice.name,
                    "languages": getattr(voice, 'languages', []),
                    "gender": getattr(voice, 'gender', 'unknown')
                })
            
            return {
                "available": True,
                "voices": voice_info,
                "current_voice": self.tts_engine.getProperty('voice')
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get voice info: {e}")
            return {"available": False, "voices": [], "error": str(e)}

# Global voice service instance
voice_service = VoiceService()
