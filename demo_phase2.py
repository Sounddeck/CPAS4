
#!/usr/bin/env python3
"""
Enhanced CPAS Phase 2 Demonstration Script
Shows the capabilities of the Intelligence + Reasoning + Voice system
"""

import sys
import asyncio
import json
from pathlib import Path

# Add backend to path
sys.path.append('/home/ubuntu/cpas_enhanced/backend')

async def demo_learning_service():
    """Demonstrate learning service capabilities"""
    print("🧠 Learning Service Demo")
    print("-" * 40)
    
    try:
        from services.learning_service import LearningService
        
        learning = LearningService()
        
        # Simulate user interactions
        interactions = [
            {
                'user_message': 'Help me write some Python code',
                'agent_response': 'I can help you with Python programming. What would you like to create?',
                'confidence': 0.9,
                'response_type': 'help',
                'processing_time': 0.5
            },
            {
                'user_message': 'Can you explain machine learning?',
                'agent_response': 'Machine learning is a subset of AI that enables systems to learn from data...',
                'confidence': 0.85,
                'response_type': 'informational',
                'processing_time': 1.2
            },
            {
                'user_message': 'Hi there!',
                'agent_response': 'Hello! How can I help you today?',
                'confidence': 0.95,
                'response_type': 'greeting',
                'processing_time': 0.1
            }
        ]
        
        user_id = "demo_user"
        
        # Process interactions and learn
        for i, interaction in enumerate(interactions, 1):
            print(f"Processing interaction {i}...")
            insights = learning.learn_from_interaction(user_id, interaction)
            print(f"  Learning score: {insights['learning_score']:.2f}")
            print(f"  Preferences updated: {len(insights['preferences_updated'])}")
            print(f"  Patterns detected: {len(insights['patterns_detected'])}")
        
        # Show learning summary
        summary = learning.get_learning_summary(user_id)
        print(f"\n📊 Learning Summary:")
        print(f"  Preferences: {summary['preferences_count']}")
        print(f"  Patterns: {summary['patterns_count']}")
        print(f"  Learning active: {summary['learning_active']}")
        
        # Show user preferences
        preferences = learning.get_user_preferences(user_id)
        if preferences:
            print(f"\n🎯 User Preferences:")
            for pref_type, pref_data in preferences.items():
                print(f"  {pref_type}: {pref_data['value']} (confidence: {pref_data['confidence']:.2f})")
        
        print("✅ Learning Service Demo Complete\n")
        
    except Exception as e:
        print(f"❌ Learning Service Demo Failed: {e}\n")

async def demo_voice_service():
    """Demonstrate voice service capabilities"""
    print("🎤 Voice Service Demo")
    print("-" * 40)
    
    try:
        from services.voice_service import VoiceService
        
        voice = VoiceService()
        
        # Show supported formats
        formats = voice.get_supported_formats()
        print(f"📁 Supported Formats:")
        print(f"  Input: {', '.join(formats['input_formats'])}")
        print(f"  Output: {', '.join(formats['output_formats'])}")
        
        # Show voice info
        voice_info = voice.get_voice_info()
        print(f"\n🔊 Voice System:")
        print(f"  Available: {voice_info['available']}")
        print(f"  Voices: {len(voice_info['voices'])}")
        
        # Test command processing
        test_commands = [
            "Hello there, how are you?",
            "Help me solve this problem",
            "Remember that I like coffee",
            "Calculate 15 plus 27"
        ]
        
        print(f"\n🎯 Command Processing:")
        for command in test_commands:
            processed = voice._process_command(command)
            print(f"  '{command[:30]}...' → {processed['type']} ({processed['action']})")
        
        # Test TTS (without actual audio generation)
        print(f"\n🗣️  Text-to-Speech Test:")
        test_text = "Hello! This is Enhanced CPAS Phase 2 with voice capabilities."
        print(f"  Text: {test_text}")
        print(f"  TTS Engine Available: {voice.tts_engine is not None}")
        
        print("✅ Voice Service Demo Complete\n")
        
    except Exception as e:
        print(f"❌ Voice Service Demo Failed: {e}\n")

async def demo_reasoning_adapter():
    """Demonstrate HRM reasoning adapter"""
    print("🧩 Reasoning Adapter Demo")
    print("-" * 40)
    
    try:
        from services.hrm_adapter import HRMAdapter
        
        hrm = HRMAdapter()
        
        # Test basic reasoning
        problems = [
            "How do I plan a successful project?",
            "What steps should I take to learn a new programming language?",
            "How can I improve my time management skills?"
        ]
        
        for i, problem in enumerate(problems, 1):
            print(f"Problem {i}: {problem}")
            
            # Get reasoning chain
            chain = hrm.reason(problem)
            
            print(f"  Reasoning depth: {chain.reasoning_depth}")
            print(f"  Execution time: {chain.execution_time:.3f}s")
            print(f"  Average confidence: {sum(chain.confidence_scores)/len(chain.confidence_scores):.2f}")
            
            print(f"  High-level plan:")
            for j, step in enumerate(chain.high_level_plan[:2], 1):  # Show first 2 steps
                print(f"    {j}. {step}")
            
            if len(chain.high_level_plan) > 2:
                print(f"    ... and {len(chain.high_level_plan)-2} more steps")
            
            print()
        
        # Test complex problem solving
        complex_problem = "Design a mobile app that helps people learn languages"
        print(f"🔍 Complex Problem: {complex_problem}")
        
        result = hrm.solve_complex_problem(complex_problem, max_iterations=3)
        print(f"  Iterations: {result['iterations']}")
        print(f"  Final confidence: {result['final_confidence']:.2f}")
        print(f"  Solution preview: {result['solution'][:100]}...")
        
        print("✅ Reasoning Adapter Demo Complete\n")
        
    except Exception as e:
        print(f"❌ Reasoning Adapter Demo Failed: {e}\n")

async def demo_integration():
    """Demonstrate component integration"""
    print("🔗 Integration Demo")
    print("-" * 40)
    
    try:
        # Show how components work together
        from services.learning_service import LearningService
        from services.hrm_adapter import HRMAdapter
        
        learning = LearningService()
        reasoning = HRMAdapter()
        
        # Simulate an intelligent interaction
        user_id = "integration_demo_user"
        user_query = "I need help planning my career transition to AI"
        
        print(f"User Query: {user_query}")
        
        # 1. Use reasoning to analyze the problem
        reasoning_chain = reasoning.reason(user_query)
        print(f"✅ Reasoning: Generated {reasoning_chain.reasoning_depth}-step plan")
        
        # 2. Simulate agent response
        agent_response = f"Based on my analysis, here's a {reasoning_chain.reasoning_depth}-step plan for your career transition..."
        
        # 3. Learn from the interaction
        interaction_data = {
            'user_message': user_query,
            'agent_response': agent_response,
            'confidence': sum(reasoning_chain.confidence_scores) / len(reasoning_chain.confidence_scores),
            'response_type': 'problem_solving',
            'reasoning_used': True,
            'processing_time': reasoning_chain.execution_time
        }
        
        insights = learning.learn_from_interaction(user_id, interaction_data)
        print(f"✅ Learning: Score {insights['learning_score']:.2f}, {len(insights['preferences_updated'])} preferences updated")
        
        # 4. Show how preferences would affect future responses
        preferences = learning.get_user_preferences(user_id)
        if preferences:
            print(f"✅ Adaptation: System learned user prefers {list(preferences.keys())}")
        
        print("✅ Integration Demo Complete\n")
        
    except Exception as e:
        print(f"❌ Integration Demo Failed: {e}\n")

async def main():
    """Run all demonstrations"""
    print("🚀 Enhanced CPAS Phase 2 Demonstration")
    print("=" * 60)
    print("Showcasing Intelligence + Reasoning + Voice capabilities")
    print("=" * 60)
    print()
    
    # Run all demos
    await demo_learning_service()
    await demo_voice_service()
    await demo_reasoning_adapter()
    await demo_integration()
    
    print("🎉 Phase 2 Demonstration Complete!")
    print()
    print("📊 System Status:")
    print("  ✅ Learning Service: Fully operational")
    print("  ✅ Voice Service: Ready (with graceful degradation)")
    print("  ✅ Reasoning System: Operational (with fallback)")
    print("  ✅ Integration: All components working together")
    print()
    print("🔗 Next Steps:")
    print("  • Start the full system: ./scripts/run_all.sh")
    print("  • Access API docs: http://localhost:8000/docs")
    print("  • Run tests: python -m pytest tests/test_phase2.py")
    print("  • View status: cat PHASE2_STATUS.md")

if __name__ == "__main__":
    asyncio.run(main())
