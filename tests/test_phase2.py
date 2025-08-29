
"""
Test Suite for Enhanced CPAS Phase 2
Tests for Intelligence, Reasoning, and Voice capabilities
"""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Import services to test
import sys
sys.path.append('/home/ubuntu/cpas_enhanced/backend')

from services.hrm_adapter import HRMAdapter, ReasoningChain
from services.voice_service import VoiceService
from services.agent_core import CPASAgent
from services.learning_service import LearningService

class TestHRMAdapter:
    """Test HRM reasoning adapter"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.hrm_adapter = HRMAdapter()
    
    def test_initialization(self):
        """Test HRM adapter initialization"""
        assert self.hrm_adapter is not None
        assert self.hrm_adapter.config is not None
        assert 'batch_size' in self.hrm_adapter.config
    
    def test_reasoning_basic(self):
        """Test basic reasoning functionality"""
        problem = "How to solve 2 + 2?"
        chain = self.hrm_adapter.reason(problem)
        
        assert isinstance(chain, ReasoningChain)
        assert len(chain.high_level_plan) > 0
        assert len(chain.low_level_steps) > 0
        assert len(chain.confidence_scores) > 0
        assert chain.reasoning_depth > 0
    
    def test_complex_problem_solving(self):
        """Test complex problem solving"""
        problem = "Plan a birthday party for 20 people"
        result = self.hrm_adapter.solve_complex_problem(problem, max_iterations=3)
        
        assert 'solution' in result
        assert 'reasoning_trace' in result
        assert 'iterations' in result
        assert 'final_confidence' in result
        assert result['iterations'] <= 3

class TestVoiceService:
    """Test voice processing service"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.voice_service = VoiceService()
    
    def test_initialization(self):
        """Test voice service initialization"""
        assert self.voice_service is not None
    
    def test_supported_formats(self):
        """Test getting supported formats"""
        formats = self.voice_service.get_supported_formats()
        
        assert 'input_formats' in formats
        assert 'output_formats' in formats
        assert isinstance(formats['input_formats'], list)
        assert isinstance(formats['output_formats'], list)
    
    def test_voice_info(self):
        """Test getting voice information"""
        voice_info = self.voice_service.get_voice_info()
        
        assert 'available' in voice_info
        assert 'voices' in voice_info
        assert isinstance(voice_info['voices'], list)
    
    @pytest.mark.asyncio
    async def test_text_to_speech(self):
        """Test text-to-speech functionality"""
        test_text = "Hello, this is a test."
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            result = await self.voice_service.text_to_speech(test_text, tmp_file.name)
            
            assert 'success' in result
            assert 'output_file' in result
            assert 'text' in result
            assert result['text'] == test_text
            
            # Clean up
            Path(tmp_file.name).unlink(missing_ok=True)
    
    def test_command_processing(self):
        """Test voice command processing"""
        test_commands = [
            "Hello there",
            "Help me with something",
            "Remember this information",
            "Calculate 5 plus 3"
        ]
        
        for command in test_commands:
            processed = self.voice_service._process_command(command)
            
            assert 'type' in processed
            assert 'action' in processed
            assert 'parameters' in processed
            assert processed['type'] in ['greeting', 'help', 'memory', 'computation', 'general']

class TestCPASAgent:
    """Test core AI agent"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.agent = CPASAgent()
    
    def test_initialization(self):
        """Test agent initialization"""
        assert self.agent is not None
        assert self.agent.config is not None
        assert self.agent.personality is not None
    
    @pytest.mark.asyncio
    async def test_message_processing(self):
        """Test message processing"""
        user_id = "test_user_123"
        message = "Hello, how are you?"
        
        response = await self.agent.process_message(user_id, message)
        
        assert response is not None
        assert hasattr(response, 'text')
        assert hasattr(response, 'confidence')
        assert hasattr(response, 'response_type')
        assert hasattr(response, 'timestamp')
        assert len(response.text) > 0
        assert 0 <= response.confidence <= 1
    
    def test_conversation_context(self):
        """Test conversation context management"""
        user_id = "test_user_456"
        
        # Get initial context
        context = self.agent._get_conversation_context(user_id)
        
        assert context.user_id == user_id
        assert context.interaction_count == 0
        assert len(context.conversation_history) == 0
        
        # Check that same context is returned
        context2 = self.agent._get_conversation_context(user_id)
        assert context.session_id == context2.session_id
    
    def test_response_classification(self):
        """Test response type classification"""
        test_cases = [
            ("hello", "greeting response", "greeting"),
            ("help me", "assistance response", "help"),
            ("solve this problem", "solution response", "problem_solving"),
            ("sorry, error occurred", "error response", "error")
        ]
        
        for message, response, expected_type in test_cases:
            response_type = self.agent._classify_response_type(message, response)
            assert response_type == expected_type
    
    def test_conversation_summary(self):
        """Test conversation summary"""
        user_id = "test_user_789"
        
        # Initially no conversation
        summary = self.agent.get_conversation_summary(user_id)
        assert summary['exists'] == False
        
        # Create conversation context
        self.agent._get_conversation_context(user_id)
        
        # Now should exist
        summary = self.agent.get_conversation_summary(user_id)
        assert summary['exists'] == True
        assert 'session_id' in summary
        assert 'interaction_count' in summary

class TestLearningService:
    """Test learning and adaptation service"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.learning_service = LearningService()
    
    def test_initialization(self):
        """Test learning service initialization"""
        assert self.learning_service is not None
        assert hasattr(self.learning_service, 'user_preferences')
        assert hasattr(self.learning_service, 'interaction_patterns')
        assert hasattr(self.learning_service, 'feedback_history')
    
    def test_learning_signal_extraction(self):
        """Test extraction of learning signals"""
        interaction_data = {
            'user_message': 'Can you help me write some code?',
            'agent_response': 'Sure! I can help you with programming.',
            'confidence': 0.8,
            'response_type': 'help',
            'processing_time': 0.5
        }
        
        signals = self.learning_service._extract_learning_signals(interaction_data)
        
        assert 'response_time' in signals
        assert 'confidence' in signals
        assert 'topics' in signals
        assert 'communication_style' in signals
        assert 'technical' in signals['topics']  # Should detect technical topic
    
    def test_preference_updates(self):
        """Test user preference updates"""
        user_id = "test_user_learning"
        signals = {
            'communication_style': 'brief',
            'topics': ['technical', 'creative'],
            'response_type': 'help',
            'voice_used': True
        }
        
        updates = self.learning_service._update_user_preferences(user_id, signals)
        
        assert len(updates) > 0
        assert any('communication_style' in update for update in updates)
        assert any('technical' in update for update in updates)
    
    def test_pattern_detection(self):
        """Test interaction pattern detection"""
        user_id = "test_user_patterns"
        interaction_data = {
            'user_message': 'Help me with programming',
            'agent_response': 'Here is some programming help...',
            'confidence': 0.9
        }
        
        patterns = self.learning_service._detect_interaction_patterns(user_id, interaction_data)
        
        assert len(patterns) > 0
        assert any('user' in pattern for pattern in patterns)  # Time-based pattern
    
    def test_feedback_recording(self):
        """Test feedback recording and learning"""
        user_id = "test_user_feedback"
        interaction_id = "interaction_123"
        
        # Record positive feedback
        self.learning_service.record_feedback(
            user_id=user_id,
            interaction_id=interaction_id,
            feedback_type="positive",
            feedback_score=0.8,
            feedback_text="Great response!"
        )
        
        assert len(self.learning_service.feedback_history) > 0
        feedback = self.learning_service.feedback_history[-1]
        assert feedback.user_id == user_id
        assert feedback.feedback_score == 0.8
    
    def test_learning_summary(self):
        """Test learning summary generation"""
        user_id = "test_user_summary"
        
        # Create some learning data
        interaction_data = {
            'user_message': 'Test message',
            'agent_response': 'Test response',
            'confidence': 0.7
        }
        
        self.learning_service.learn_from_interaction(user_id, interaction_data)
        
        # Get summary
        summary = self.learning_service.get_learning_summary(user_id)
        
        assert 'user_id' in summary
        assert 'preferences_count' in summary
        assert 'patterns_count' in summary
        assert 'feedback_stats' in summary
        assert 'learning_active' in summary

class TestIntegration:
    """Integration tests for Phase 2 components"""
    
    @pytest.mark.asyncio
    async def test_agent_with_reasoning(self):
        """Test agent using reasoning capabilities"""
        agent = CPASAgent()
        user_id = "integration_test_user"
        
        # Test with a problem that should trigger reasoning
        message = "How can I solve this complex math problem step by step?"
        
        response = await agent.process_message(user_id, message)
        
        assert response is not None
        assert len(response.text) > 0
        # Should have reasoning chain for complex problems
        # (Note: might be None if HRM not fully available)
    
    def test_learning_with_agent_interaction(self):
        """Test learning service integration with agent"""
        learning_service = LearningService()
        
        # Simulate agent interaction data
        interaction_data = {
            'user_message': 'Help me understand machine learning',
            'agent_response': 'Machine learning is a subset of AI...',
            'confidence': 0.85,
            'response_type': 'informational',
            'processing_time': 1.2,
            'reasoning_chain': None
        }
        
        insights = learning_service.learn_from_interaction("test_user", interaction_data)
        
        assert 'preferences_updated' in insights
        assert 'patterns_detected' in insights
        assert 'learning_score' in insights
        assert insights['learning_score'] > 0

# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
