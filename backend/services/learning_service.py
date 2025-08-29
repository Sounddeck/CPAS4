
"""
Learning Service for CPAS
Implements learning mechanisms and user preference tracking
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import numpy as np

# from .memory_service import memory_service  # Will be imported when needed

@dataclass
class UserPreference:
    """User preference data structure"""
    preference_type: str
    value: Any
    confidence: float
    last_updated: datetime
    frequency: int

@dataclass
class LearningPattern:
    """Learning pattern data structure"""
    pattern_id: str
    pattern_type: str
    description: str
    frequency: int
    confidence: float
    last_seen: datetime
    metadata: Dict[str, Any]

@dataclass
class InteractionFeedback:
    """Feedback from user interactions"""
    interaction_id: str
    user_id: str
    feedback_type: str  # positive, negative, neutral
    feedback_score: float  # -1.0 to 1.0
    feedback_text: Optional[str]
    timestamp: datetime

class LearningService:
    """Service for learning from user interactions and improving responses"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Learning data storage
        self.user_preferences: Dict[str, Dict[str, UserPreference]] = defaultdict(dict)
        self.interaction_patterns: Dict[str, List[LearningPattern]] = defaultdict(list)
        self.feedback_history: List[InteractionFeedback] = []
        
        # Learning parameters
        self.learning_rate = 0.1
        self.confidence_threshold = 0.7
        self.pattern_min_frequency = 3
        self.preference_decay_rate = 0.95  # Daily decay
        
        self.logger.info("Learning Service initialized")
    
    def learn_from_interaction(self, user_id: str, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Learn from a user interaction
        
        Args:
            user_id: User identifier
            interaction_data: Data from the interaction
            
        Returns:
            Dict containing learning insights
        """
        try:
            insights = {
                'preferences_updated': [],
                'patterns_detected': [],
                'learning_score': 0.0
            }
            
            # Extract learning signals
            signals = self._extract_learning_signals(interaction_data)
            
            # Update user preferences
            preference_updates = self._update_user_preferences(user_id, signals)
            insights['preferences_updated'] = preference_updates
            
            # Detect interaction patterns
            patterns = self._detect_interaction_patterns(user_id, interaction_data)
            insights['patterns_detected'] = patterns
            
            # Calculate learning score
            insights['learning_score'] = self._calculate_learning_score(signals, preference_updates, patterns)
            
            # Store learning data
            self._store_learning_data(user_id, interaction_data, insights)
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Learning from interaction failed: {e}")
            return {'error': str(e)}
    
    def _extract_learning_signals(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract learning signals from interaction data"""
        signals = {
            'response_time': interaction_data.get('processing_time', 0),
            'confidence': interaction_data.get('confidence', 0.5),
            'response_type': interaction_data.get('response_type', 'general'),
            'message_length': len(interaction_data.get('user_message', '')),
            'response_length': len(interaction_data.get('agent_response', '')),
            'reasoning_used': interaction_data.get('reasoning_chain') is not None,
            'voice_used': 'voice' in interaction_data.get('metadata', {}),
            'timestamp': datetime.now()
        }
        
        # Extract topic/intent signals
        user_message = interaction_data.get('user_message', '').lower()
        
        # Detect topics
        topic_keywords = {
            'technical': ['code', 'programming', 'software', 'computer', 'algorithm'],
            'creative': ['write', 'create', 'design', 'art', 'story'],
            'analytical': ['analyze', 'calculate', 'solve', 'problem', 'data'],
            'personal': ['feel', 'think', 'opinion', 'prefer', 'like'],
            'informational': ['what', 'how', 'when', 'where', 'why', 'explain']
        }
        
        detected_topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in user_message for keyword in keywords):
                detected_topics.append(topic)
        
        signals['topics'] = detected_topics
        
        # Detect communication style preferences
        if len(user_message.split()) < 5:
            signals['communication_style'] = 'brief'
        elif len(user_message.split()) > 20:
            signals['communication_style'] = 'detailed'
        else:
            signals['communication_style'] = 'moderate'
        
        return signals
    
    def _update_user_preferences(self, user_id: str, signals: Dict[str, Any]) -> List[str]:
        """Update user preferences based on signals"""
        updates = []
        
        try:
            # Communication style preference
            style = signals.get('communication_style', 'moderate')
            self._update_preference(user_id, 'communication_style', style, 0.8)
            updates.append(f"communication_style: {style}")
            
            # Topic preferences
            for topic in signals.get('topics', []):
                self._update_preference(user_id, f'topic_interest_{topic}', True, 0.7)
                updates.append(f"topic_interest_{topic}: increased")
            
            # Response type preferences
            response_type = signals.get('response_type', 'general')
            if response_type != 'error':
                self._update_preference(user_id, f'response_type_{response_type}', True, 0.6)
                updates.append(f"response_type_{response_type}: positive")
            
            # Voice usage preference
            if signals.get('voice_used', False):
                self._update_preference(user_id, 'voice_interaction', True, 0.8)
                updates.append("voice_interaction: positive")
            
            # Reasoning preference
            if signals.get('reasoning_used', False):
                self._update_preference(user_id, 'detailed_reasoning', True, 0.7)
                updates.append("detailed_reasoning: positive")
            
        except Exception as e:
            self.logger.error(f"Failed to update preferences: {e}")
        
        return updates
    
    def _update_preference(self, user_id: str, pref_type: str, value: Any, confidence: float):
        """Update a specific user preference"""
        current_pref = self.user_preferences[user_id].get(pref_type)
        
        if current_pref:
            # Update existing preference
            if current_pref.value == value:
                # Reinforce existing preference
                current_pref.confidence = min(1.0, current_pref.confidence + self.learning_rate)
                current_pref.frequency += 1
            else:
                # Conflicting preference - adjust based on confidence
                if confidence > current_pref.confidence:
                    current_pref.value = value
                    current_pref.confidence = confidence
                else:
                    current_pref.confidence *= 0.9  # Slight decay
            
            current_pref.last_updated = datetime.now()
        else:
            # Create new preference
            self.user_preferences[user_id][pref_type] = UserPreference(
                preference_type=pref_type,
                value=value,
                confidence=confidence,
                last_updated=datetime.now(),
                frequency=1
            )
    
    def _detect_interaction_patterns(self, user_id: str, interaction_data: Dict[str, Any]) -> List[str]:
        """Detect patterns in user interactions"""
        patterns = []
        
        try:
            # Time-based patterns
            current_hour = datetime.now().hour
            if 6 <= current_hour < 12:
                time_pattern = "morning_user"
            elif 12 <= current_hour < 18:
                time_pattern = "afternoon_user"
            else:
                time_pattern = "evening_user"
            
            self._update_pattern(user_id, time_pattern, "temporal", "User active during this time period")
            patterns.append(time_pattern)
            
            # Response length patterns
            response_length = len(interaction_data.get('agent_response', ''))
            if response_length > 200:
                length_pattern = "prefers_detailed_responses"
            elif response_length < 50:
                length_pattern = "prefers_brief_responses"
            else:
                length_pattern = "prefers_moderate_responses"
            
            self._update_pattern(user_id, length_pattern, "response_style", "User's preferred response length")
            patterns.append(length_pattern)
            
            # Topic consistency patterns
            topics = self._extract_learning_signals(interaction_data).get('topics', [])
            for topic in topics:
                topic_pattern = f"frequent_{topic}_queries"
                self._update_pattern(user_id, topic_pattern, "topic_consistency", f"User frequently asks about {topic}")
                patterns.append(topic_pattern)
            
        except Exception as e:
            self.logger.error(f"Pattern detection failed: {e}")
        
        return patterns
    
    def _update_pattern(self, user_id: str, pattern_id: str, pattern_type: str, description: str):
        """Update or create an interaction pattern"""
        # Find existing pattern
        existing_pattern = None
        for pattern in self.interaction_patterns[user_id]:
            if pattern.pattern_id == pattern_id:
                existing_pattern = pattern
                break
        
        if existing_pattern:
            # Update existing pattern
            existing_pattern.frequency += 1
            existing_pattern.confidence = min(1.0, existing_pattern.confidence + 0.1)
            existing_pattern.last_seen = datetime.now()
        else:
            # Create new pattern
            new_pattern = LearningPattern(
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                description=description,
                frequency=1,
                confidence=0.5,
                last_seen=datetime.now(),
                metadata={}
            )
            self.interaction_patterns[user_id].append(new_pattern)
    
    def _calculate_learning_score(self, signals: Dict[str, Any], preference_updates: List[str], patterns: List[str]) -> float:
        """Calculate a learning score for the interaction"""
        score = 0.0
        
        # Base score from confidence
        score += signals.get('confidence', 0.5) * 0.3
        
        # Score from preference updates
        score += len(preference_updates) * 0.1
        
        # Score from pattern detection
        score += len(patterns) * 0.1
        
        # Bonus for successful reasoning
        if signals.get('reasoning_used', False):
            score += 0.2
        
        # Penalty for errors
        if signals.get('response_type') == 'error':
            score -= 0.3
        
        return max(0.0, min(1.0, score))
    
    def _store_learning_data(self, user_id: str, interaction_data: Dict[str, Any], insights: Dict[str, Any]):
        """Store learning data in memory"""
        try:
            learning_record = {
                'user_id': user_id,
                'interaction_data': interaction_data,
                'learning_insights': insights,
                'timestamp': datetime.now().isoformat()
            }
            
            # Store in memory when available
            try:
                from .memory_service import memory_service
                memory_service.store_memory(
                    user_id=user_id,
                    content=f"Learning from interaction: {insights['learning_score']:.2f} score",
                    metadata={
                        'type': 'learning_record',
                        'learning_data': learning_record
                    }
                )
            except ImportError:
                self.logger.warning("Memory service not available for learning storage")
            
        except Exception as e:
            self.logger.error(f"Failed to store learning data: {e}")
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences"""
        if user_id not in self.user_preferences:
            return {}
        
        preferences = {}
        for pref_type, pref in self.user_preferences[user_id].items():
            if pref.confidence >= self.confidence_threshold:
                preferences[pref_type] = {
                    'value': pref.value,
                    'confidence': pref.confidence,
                    'frequency': pref.frequency,
                    'last_updated': pref.last_updated.isoformat()
                }
        
        return preferences
    
    def get_user_patterns(self, user_id: str) -> List[Dict[str, Any]]:
        """Get detected user patterns"""
        if user_id not in self.interaction_patterns:
            return []
        
        patterns = []
        for pattern in self.interaction_patterns[user_id]:
            if pattern.frequency >= self.pattern_min_frequency:
                patterns.append({
                    'pattern_id': pattern.pattern_id,
                    'pattern_type': pattern.pattern_type,
                    'description': pattern.description,
                    'frequency': pattern.frequency,
                    'confidence': pattern.confidence,
                    'last_seen': pattern.last_seen.isoformat()
                })
        
        return patterns
    
    def record_feedback(self, user_id: str, interaction_id: str, feedback_type: str, feedback_score: float, feedback_text: Optional[str] = None):
        """Record user feedback for learning"""
        feedback = InteractionFeedback(
            interaction_id=interaction_id,
            user_id=user_id,
            feedback_type=feedback_type,
            feedback_score=feedback_score,
            feedback_text=feedback_text,
            timestamp=datetime.now()
        )
        
        self.feedback_history.append(feedback)
        
        # Learn from feedback
        self._learn_from_feedback(feedback)
    
    def _learn_from_feedback(self, feedback: InteractionFeedback):
        """Learn from user feedback"""
        try:
            # Adjust preferences based on feedback
            if feedback.feedback_score > 0.5:
                # Positive feedback - reinforce current preferences
                self._reinforce_preferences(feedback.user_id, feedback.feedback_score)
            elif feedback.feedback_score < -0.5:
                # Negative feedback - adjust preferences
                self._adjust_preferences_from_negative_feedback(feedback.user_id, feedback.feedback_score)
            
        except Exception as e:
            self.logger.error(f"Learning from feedback failed: {e}")
    
    def _reinforce_preferences(self, user_id: str, feedback_score: float):
        """Reinforce user preferences based on positive feedback"""
        if user_id in self.user_preferences:
            for pref in self.user_preferences[user_id].values():
                pref.confidence = min(1.0, pref.confidence + feedback_score * 0.1)
    
    def _adjust_preferences_from_negative_feedback(self, user_id: str, feedback_score: float):
        """Adjust preferences based on negative feedback"""
        if user_id in self.user_preferences:
            for pref in self.user_preferences[user_id].values():
                pref.confidence = max(0.0, pref.confidence + feedback_score * 0.1)
    
    def get_learning_summary(self, user_id: str) -> Dict[str, Any]:
        """Get learning summary for a user"""
        preferences = self.get_user_preferences(user_id)
        patterns = self.get_user_patterns(user_id)
        
        # Get feedback statistics
        user_feedback = [f for f in self.feedback_history if f.user_id == user_id]
        feedback_stats = {
            'total_feedback': len(user_feedback),
            'positive_feedback': len([f for f in user_feedback if f.feedback_score > 0]),
            'negative_feedback': len([f for f in user_feedback if f.feedback_score < 0]),
            'average_score': np.mean([f.feedback_score for f in user_feedback]) if user_feedback else 0.0
        }
        
        return {
            'user_id': user_id,
            'preferences_count': len(preferences),
            'patterns_count': len(patterns),
            'feedback_stats': feedback_stats,
            'preferences': preferences,
            'patterns': patterns,
            'learning_active': len(preferences) > 0 or len(patterns) > 0
        }
    
    def optimize_response_for_user(self, user_id: str, base_response: str) -> str:
        """Optimize response based on user preferences"""
        try:
            preferences = self.get_user_preferences(user_id)
            
            # Adjust response length based on communication style preference
            comm_style = preferences.get('communication_style', {}).get('value', 'moderate')
            
            if comm_style == 'brief' and len(base_response) > 100:
                # Shorten response
                sentences = base_response.split('. ')
                optimized_response = '. '.join(sentences[:2]) + '.'
            elif comm_style == 'detailed' and len(base_response) < 50:
                # Expand response
                optimized_response = base_response + " Let me provide more details on this topic."
            else:
                optimized_response = base_response
            
            return optimized_response
            
        except Exception as e:
            self.logger.error(f"Response optimization failed: {e}")
            return base_response
    
    def decay_preferences(self):
        """Apply daily decay to preferences to keep them current"""
        try:
            current_time = datetime.now()
            
            for user_id in self.user_preferences:
                for pref in self.user_preferences[user_id].values():
                    # Calculate days since last update
                    days_since_update = (current_time - pref.last_updated).days
                    
                    if days_since_update > 0:
                        # Apply decay
                        decay_factor = self.preference_decay_rate ** days_since_update
                        pref.confidence *= decay_factor
                        
                        # Remove preferences with very low confidence
                        if pref.confidence < 0.1:
                            # Mark for removal (would need to implement cleanup)
                            pass
            
        except Exception as e:
            self.logger.error(f"Preference decay failed: {e}")

# Global learning service instance
learning_service = LearningService()
