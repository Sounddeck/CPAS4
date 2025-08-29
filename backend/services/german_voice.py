
"""
German-Accented Voice Interface
Implements TTS with German-English accent and personality
"""

import asyncio
import os
import tempfile
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from loguru import logger
import pyttsx3

try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logger.warning("TTS library not available, falling back to pyttsx3")


class GermanVoiceInterface:
    """
    German-accented English voice interface for Greta
    Implements professional, precise, warm personality
    """
    
    def __init__(self):
        self.personality = {
            "name": "Greta",
            "accent": "german-english",
            "traits": ["precise", "analytical", "warm", "intelligent"],
            "speaking_style": "professional_warm",
            "pace": "measured",
            "tone": "confident"
        }
        
        # Voice settings
        self.voice_settings = {
            "rate": 180,        # Words per minute (slightly slower for precision)
            "volume": 0.8,      # Volume level
            "pitch": 0.0,       # Pitch adjustment
            "emphasis": True    # Add emphasis to important words
        }
        
        # Initialize TTS engines
        self.tts_engine = None
        self.coqui_tts = None
        self.initialize_engines()
        
        # German accent patterns
        self.accent_patterns = {
            # Consonant substitutions
            "th": "z",          # "the" -> "ze"
            "w": "v",           # "with" -> "vith" 
            "v": "f",           # "very" -> "fery"
            
            # Vowel modifications
            "a": "ah",          # More open 'a' sound
            "i": "ee",          # Longer 'i' sound in some contexts
            
            # Rhythm patterns
            "stress_pattern": "initial",  # German tends to stress first syllable
            "intonation": "falling"       # Falling intonation pattern
        }
        
        # Professional vocabulary with German precision
        self.professional_phrases = {
            "greeting": [
                "Guten Tag, I am Greta, your Master Agent.",
                "Good morning, zis is Greta speaking.",
                "Hello, I am here to assist you vith precision and care."
            ],
            "acknowledgment": [
                "Verstanden - I understand completely.",
                "Ja, zat makes perfect sense.",
                "Precisely, let me analyze zis for you.",
                "Excellent question, I vill investigate zis thoroughly."
            ],
            "thinking": [
                "Let me consider zis carefully...",
                "I am analyzing ze available information...",
                "Vait one moment vhile I process zis...",
                "Allow me to examine zis from multiple perspectives..."
            ],
            "results": [
                "Based on my analysis, here are ze findings:",
                "I have completed ze investigation vith zese results:",
                "My research indicates ze following:",
                "After thorough examination, I can report:"
            ],
            "uncertainty": [
                "I must be honest - zis requires further investigation.",
                "Ze evidence is not yet conclusive, but I can share vhat I know.",
                "Zis is a complex matter zat deserves careful consideration."
            ],
            "farewell": [
                "I hope zis has been helpful to you.",
                "Please do not hesitate to ask if you need further assistance.",
                "Auf Wiedersehen, until next time."
            ]
        }
    
    def initialize_engines(self):
        """Initialize available TTS engines"""
        try:
            # Initialize pyttsx3 as fallback
            self.tts_engine = pyttsx3.init()
            
            # Configure pyttsx3 for German accent
            voices = self.tts_engine.getProperty('voices')
            
            # Try to find a female voice
            female_voice = None
            for voice in voices:
                if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                    female_voice = voice
                    break
            
            if female_voice:
                self.tts_engine.setProperty('voice', female_voice.id)
            
            # Set voice properties
            self.tts_engine.setProperty('rate', self.voice_settings['rate'])
            self.tts_engine.setProperty('volume', self.voice_settings['volume'])
            
            logger.info("✅ pyttsx3 TTS engine initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
        
        # Initialize Coqui TTS if available
        if TTS_AVAILABLE:
            try:
                # Try to load a German-English model
                self.coqui_tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
                logger.info("✅ Coqui TTS engine initialized")
            except Exception as e:
                logger.warning(f"Coqui TTS initialization failed: {e}")
    
    async def speak(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Convert text to speech with German accent
        """
        try:
            # Apply German accent to text
            accented_text = self.apply_german_accent(text)
            
            # Add personality markers
            styled_text = self.apply_personality_style(accented_text, **kwargs)
            
            # Generate speech
            audio_file = await self.generate_speech(styled_text, **kwargs)
            
            return {
                "success": True,
                "original_text": text,
                "accented_text": styled_text,
                "audio_file": audio_file,
                "personality": self.personality,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Speech generation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": text
            }
    
    def apply_german_accent(self, text: str) -> str:
        """
        Apply German accent patterns to English text
        """
        accented = text
        
        # Apply consonant substitutions
        accented = accented.replace("th", "z")
        accented = accented.replace("Th", "Z")
        
        # W -> V substitution (but not at word boundaries where it might be awkward)
        words = accented.split()
        for i, word in enumerate(words):
            if word.lower().startswith('w') and len(word) > 2:
                if word.lower() in ['with', 'will', 'what', 'when', 'where', 'why', 'who']:
                    words[i] = 'v' + word[1:] if word[0].islower() else 'V' + word[1:]
        
        accented = ' '.join(words)
        
        # V -> F in middle of words
        accented = accented.replace("very", "fery")
        accented = accented.replace("Very", "Fery")
        
        return accented
    
    def apply_personality_style(self, text: str, **kwargs) -> str:
        """
        Apply Greta's personality style to the text
        """
        context = kwargs.get("context", "general")
        emotion = kwargs.get("emotion", "neutral")
        
        # Add appropriate introductory phrases based on context
        if context == "greeting":
            return f"{self.get_phrase('greeting')} {text}"
        elif context == "thinking":
            return f"{self.get_phrase('thinking')} {text}"
        elif context == "results":
            return f"{self.get_phrase('results')} {text}"
        elif context == "uncertainty":
            return f"{self.get_phrase('uncertainty')} {text}"
        elif context == "farewell":
            return f"{text} {self.get_phrase('farewell')}"
        
        # Add acknowledgment for questions
        if text.strip().endswith('?') or 'question' in kwargs.get("type", ""):
            return f"{self.get_phrase('acknowledgment')} {text}"
        
        return text
    
    def get_phrase(self, category: str) -> str:
        """Get a random phrase from the specified category"""
        import random
        phrases = self.professional_phrases.get(category, [""])
        return random.choice(phrases)
    
    async def generate_speech(self, text: str, **kwargs) -> Optional[str]:
        """
        Generate speech audio file
        """
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                audio_path = tmp_file.name
            
            # Try Coqui TTS first if available
            if self.coqui_tts:
                try:
                    self.coqui_tts.tts_to_file(text=text, file_path=audio_path)
                    logger.info(f"Generated speech with Coqui TTS: {audio_path}")
                    return audio_path
                except Exception as e:
                    logger.warning(f"Coqui TTS failed, falling back to pyttsx3: {e}")
            
            # Fallback to pyttsx3
            if self.tts_engine:
                self.tts_engine.save_to_file(text, audio_path)
                self.tts_engine.runAndWait()
                logger.info(f"Generated speech with pyttsx3: {audio_path}")
                return audio_path
            
            logger.error("No TTS engine available")
            return None
            
        except Exception as e:
            logger.error(f"Speech generation error: {e}")
            return None
    
    async def speak_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Master Agent response to speech with appropriate context
        """
        try:
            response_text = response_data.get("response", "")
            reasoning_level = response_data.get("reasoning_level", "deliberative")
            confidence = response_data.get("confidence", 0.5)
            
            # Determine context based on response characteristics
            context = "general"
            if confidence < 0.5:
                context = "uncertainty"
            elif "analysis" in response_text.lower() or "research" in response_text.lower():
                context = "results"
            elif "?" in response_text:
                context = "thinking"
            
            # Add confidence indicators for German precision
            if confidence > 0.8:
                prefix = "I am confident zat "
            elif confidence > 0.6:
                prefix = "Based on my analysis, "
            elif confidence > 0.4:
                prefix = "It appears zat "
            else:
                prefix = "I must note zat zis is preliminary, but "
            
            # Combine prefix with response
            full_text = f"{prefix}{response_text}"
            
            # Generate speech
            speech_result = await self.speak(
                full_text,
                context=context,
                reasoning_level=reasoning_level,
                confidence=confidence
            )
            
            return {
                **speech_result,
                "reasoning_level": reasoning_level,
                "confidence": confidence,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"Response speech generation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def speak_osint_results(self, osint_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert OSINT investigation results to speech
        """
        try:
            investigation_type = osint_data.get("type", "unknown")
            target = osint_data.get("target", "")
            confidence_score = osint_data.get("confidence_score", 0.5)
            
            # Create summary text
            if investigation_type == "person":
                text = f"I have completed ze person investigation for {target}. "
            elif investigation_type == "domain":
                text = f"Ze domain analysis for {target} is complete. "
            elif investigation_type == "image":
                text = f"My image investigation has finished. "
            else:
                text = f"Ze {investigation_type} investigation is complete. "
            
            # Add confidence assessment
            if confidence_score > 0.8:
                text += "Ze results are highly reliable. "
            elif confidence_score > 0.6:
                text += "I have good confidence in zese findings. "
            elif confidence_score > 0.4:
                text += "Ze results are moderately reliable. "
            else:
                text += "Please note zat zese results require further verification. "
            
            # Add key findings summary
            results = osint_data.get("results", {})
            key_findings = []
            
            for module, result in results.items():
                if result.get("success"):
                    if module == "social" and result.get("profiles_found", 0) > 0:
                        key_findings.append(f"found {result['profiles_found']} social media profiles")
                    elif module == "technical" and result.get("domain_info"):
                        key_findings.append("completed technical analysis")
                    elif module == "breach" and result.get("breach_count", 0) > 0:
                        key_findings.append(f"identified {result['breach_count']} data breaches")
                    elif module == "media" and result.get("total_results", 0) > 0:
                        key_findings.append(f"found {result['total_results']} similar images")
            
            if key_findings:
                text += f"Key findings include: {', '.join(key_findings)}. "
            
            text += "Vould you like me to provide more detailed analysis?"
            
            # Generate speech
            return await self.speak(
                text,
                context="results",
                investigation_type=investigation_type,
                confidence=confidence_score
            )
            
        except Exception as e:
            logger.error(f"OSINT speech generation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_voice_settings(self) -> Dict[str, Any]:
        """Get current voice settings"""
        return {
            "personality": self.personality,
            "voice_settings": self.voice_settings,
            "accent_patterns": self.accent_patterns,
            "engines_available": {
                "pyttsx3": self.tts_engine is not None,
                "coqui_tts": self.coqui_tts is not None
            }
        }
    
    def update_voice_settings(self, settings: Dict[str, Any]) -> bool:
        """Update voice settings"""
        try:
            if "rate" in settings:
                self.voice_settings["rate"] = settings["rate"]
                if self.tts_engine:
                    self.tts_engine.setProperty('rate', settings["rate"])
            
            if "volume" in settings:
                self.voice_settings["volume"] = settings["volume"]
                if self.tts_engine:
                    self.tts_engine.setProperty('volume', settings["volume"])
            
            if "personality_traits" in settings:
                self.personality["traits"] = settings["personality_traits"]
            
            logger.info("Voice settings updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update voice settings: {e}")
            return False
    
    async def test_voice(self) -> Dict[str, Any]:
        """Test the voice interface"""
        test_text = "Hello, zis is Greta, your Master Agent. I am ready to assist you vith precision and intelligence."
        
        return await self.speak(
            test_text,
            context="greeting",
            test=True
        )
