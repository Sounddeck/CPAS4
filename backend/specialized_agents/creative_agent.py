
"""
Creative Agent - Specialized agent for creative tasks and content generation
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

from models.agent import Agent, AgentCapability, AgentPersonality
from services.agent_core import AgentCore

class CreativeAgent(AgentCore):
    """Specialized agent for creative tasks, content generation, and artistic endeavors"""
    
    def __init__(self, agent_id: str, db):
        super().__init__(agent_id, db)
        self.agent_type = "creative_agent"
        self.capabilities = [
            AgentCapability(
                name="content_writing",
                description="Create engaging written content across various formats",
                confidence=0.92
            ),
            AgentCapability(
                name="creative_brainstorming",
                description="Generate innovative ideas and creative solutions",
                confidence=0.88
            ),
            AgentCapability(
                name="storytelling",
                description="Craft compelling narratives and stories",
                confidence=0.90
            ),
            AgentCapability(
                name="marketing_copy",
                description="Create persuasive marketing and advertising content",
                confidence=0.85
            ),
            AgentCapability(
                name="visual_concepts",
                description="Develop visual concepts and design ideas",
                confidence=0.80
            ),
            AgentCapability(
                name="brand_development",
                description="Create brand identity and messaging strategies",
                confidence=0.87
            )
        ]
        
        self.personality = AgentPersonality(
            traits={
                "creative": 0.95,
                "imaginative": 0.92,
                "expressive": 0.90,
                "innovative": 0.88,
                "inspiring": 0.85
            },
            communication_style="creative_engaging",
            decision_making="intuitive_innovative"
        )
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process creative requests"""
        task_type = task_data.get("type", "general_creative")
        
        if task_type == "content_writing":
            return await self._create_content(task_data)
        elif task_type == "brainstorming":
            return await self._brainstorm_ideas(task_data)
        elif task_type == "storytelling":
            return await self._create_story(task_data)
        elif task_type == "marketing_copy":
            return await self._create_marketing_copy(task_data)
        elif task_type == "brand_development":
            return await self._develop_brand(task_data)
        elif task_type == "visual_concept":
            return await self._develop_visual_concept(task_data)
        elif task_type == "campaign_creation":
            return await self._create_campaign(task_data)
        else:
            return await self._general_creative_assistance(task_data)
    
    async def _create_content(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create various types of written content"""
        content_type = task_data.get("content_type", "article")
        topic = task_data.get("topic", "")
        audience = task_data.get("target_audience", "general")
        tone = task_data.get("tone", "professional")
        length = task_data.get("length", "medium")
        
        # Generate content outline
        outline = await self._create_content_outline(topic, content_type, audience)
        
        # Create the content
        content = await self._generate_content(outline, topic, tone, length)
        
        # Enhance with creative elements
        enhanced_content = await self._enhance_content_creativity(content, content_type)
        
        # Generate variations
        variations = await self._create_content_variations(enhanced_content, 3)
        
        content_package = {
            "content_type": content_type,
            "topic": topic,
            "target_audience": audience,
            "tone": tone,
            "outline": outline,
            "main_content": enhanced_content,
            "variations": variations,
            "word_count": len(enhanced_content.split()),
            "readability_score": await self._calculate_readability(enhanced_content),
            "seo_suggestions": await self._generate_seo_suggestions(topic, enhanced_content),
            "engagement_tips": await self._suggest_engagement_improvements(enhanced_content),
            "created_at": datetime.utcnow()
        }
        
        # Store in memory
        await self.store_memory({
            "type": "content_created",
            "content_type": content_type,
            "topic": topic,
            "package": content_package
        })
        
        return {
            "success": True,
            "content_package": content_package
        }
    
    async def _brainstorm_ideas(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate creative ideas through brainstorming"""
        challenge = task_data.get("challenge", "")
        context = task_data.get("context", {})
        idea_count = task_data.get("idea_count", 10)
        creativity_level = task_data.get("creativity_level", "high")
        
        # Generate initial ideas
        initial_ideas = await self._generate_initial_ideas(challenge, context, idea_count)
        
        # Apply creative techniques
        enhanced_ideas = []
        for idea in initial_ideas:
            enhanced = await self._apply_creative_techniques(idea, creativity_level)
            enhanced_ideas.append(enhanced)
        
        # Categorize ideas
        categorized_ideas = await self._categorize_ideas(enhanced_ideas)
        
        # Evaluate feasibility and impact
        evaluated_ideas = await self._evaluate_ideas(enhanced_ideas, context)
        
        # Generate combination ideas
        combination_ideas = await self._generate_combination_ideas(enhanced_ideas)
        
        brainstorm_session = {
            "challenge": challenge,
            "context": context,
            "initial_ideas": initial_ideas,
            "enhanced_ideas": enhanced_ideas,
            "categorized_ideas": categorized_ideas,
            "evaluated_ideas": evaluated_ideas,
            "combination_ideas": combination_ideas,
            "top_recommendations": await self._select_top_ideas(evaluated_ideas, 5),
            "creative_techniques_used": [
                "SCAMPER method",
                "Mind mapping",
                "Reverse thinking",
                "Random word association",
                "What if scenarios"
            ],
            "session_summary": await self._summarize_brainstorm_session(enhanced_ideas),
            "generated_at": datetime.utcnow()
        }
        
        return {
            "success": True,
            "brainstorm_session": brainstorm_session
        }
    
    async def _create_story(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create compelling stories and narratives"""
        story_type = task_data.get("story_type", "short_story")
        genre = task_data.get("genre", "general")
        theme = task_data.get("theme", "")
        characters = task_data.get("characters", [])
        setting = task_data.get("setting", "")
        length = task_data.get("length", "medium")
        
        # Develop story structure
        story_structure = await self._develop_story_structure(story_type, genre, theme)
        
        # Create character profiles
        character_profiles = await self._develop_character_profiles(characters, genre, theme)
        
        # Build setting details
        setting_details = await self._develop_setting(setting, genre, story_structure)
        
        # Generate plot outline
        plot_outline = await self._create_plot_outline(story_structure, character_profiles, setting_details)
        
        # Write the story
        story_content = await self._write_story(plot_outline, character_profiles, setting_details, length)
        
        # Add narrative enhancements
        enhanced_story = await self._enhance_narrative(story_content, genre)
        
        story_package = {
            "story_type": story_type,
            "genre": genre,
            "theme": theme,
            "story_structure": story_structure,
            "character_profiles": character_profiles,
            "setting_details": setting_details,
            "plot_outline": plot_outline,
            "story_content": enhanced_story,
            "word_count": len(enhanced_story.split()),
            "narrative_analysis": await self._analyze_narrative_elements(enhanced_story),
            "improvement_suggestions": await self._suggest_story_improvements(enhanced_story),
            "alternative_endings": await self._generate_alternative_endings(plot_outline, 3),
            "created_at": datetime.utcnow()
        }
        
        return {
            "success": True,
            "story_package": story_package
        }
    
    async def _create_marketing_copy(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create persuasive marketing and advertising content"""
        campaign_type = task_data.get("campaign_type", "general")
        product_service = task_data.get("product_service", "")
        target_audience = task_data.get("target_audience", {})
        key_benefits = task_data.get("key_benefits", [])
        call_to_action = task_data.get("call_to_action", "")
        channels = task_data.get("channels", ["email", "social", "web"])
        
        # Analyze target audience
        audience_analysis = await self._analyze_target_audience(target_audience)
        
        # Develop messaging strategy
        messaging_strategy = await self._develop_messaging_strategy(
            product_service, key_benefits, audience_analysis
        )
        
        # Create copy for different channels
        channel_copy = {}
        for channel in channels:
            copy = await self._create_channel_specific_copy(
                channel, messaging_strategy, call_to_action, audience_analysis
            )
            channel_copy[channel] = copy
        
        # Generate headlines and taglines
        headlines = await self._generate_headlines(messaging_strategy, 10)
        taglines = await self._generate_taglines(product_service, key_benefits, 5)
        
        # Create A/B test variations
        ab_variations = await self._create_ab_test_variations(channel_copy, 3)
        
        marketing_package = {
            "campaign_type": campaign_type,
            "product_service": product_service,
            "target_audience": target_audience,
            "audience_analysis": audience_analysis,
            "messaging_strategy": messaging_strategy,
            "channel_copy": channel_copy,
            "headlines": headlines,
            "taglines": taglines,
            "ab_variations": ab_variations,
            "performance_predictions": await self._predict_copy_performance(channel_copy),
            "optimization_tips": await self._suggest_copy_optimizations(channel_copy),
            "created_at": datetime.utcnow()
        }
        
        return {
            "success": True,
            "marketing_package": marketing_package
        }
    
    async def _develop_brand(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Develop comprehensive brand identity and strategy"""
        company_name = task_data.get("company_name", "")
        industry = task_data.get("industry", "")
        target_market = task_data.get("target_market", {})
        values = task_data.get("values", [])
        competitors = task_data.get("competitors", [])
        
        # Analyze brand positioning
        positioning_analysis = await self._analyze_brand_positioning(
            company_name, industry, target_market, competitors
        )
        
        # Develop brand personality
        brand_personality = await self._develop_brand_personality(values, target_market, industry)
        
        # Create brand messaging
        brand_messaging = await self._create_brand_messaging(
            positioning_analysis, brand_personality, values
        )
        
        # Generate visual identity concepts
        visual_concepts = await self._generate_visual_identity_concepts(
            brand_personality, industry, target_market
        )
        
        # Develop brand voice and tone
        brand_voice = await self._develop_brand_voice(brand_personality, target_market)
        
        # Create brand guidelines
        brand_guidelines = await self._create_brand_guidelines(
            brand_messaging, visual_concepts, brand_voice
        )
        
        brand_package = {
            "company_name": company_name,
            "industry": industry,
            "positioning_analysis": positioning_analysis,
            "brand_personality": brand_personality,
            "brand_messaging": brand_messaging,
            "visual_concepts": visual_concepts,
            "brand_voice": brand_voice,
            "brand_guidelines": brand_guidelines,
            "implementation_roadmap": await self._create_implementation_roadmap(brand_guidelines),
            "success_metrics": await self._define_brand_success_metrics(positioning_analysis),
            "created_at": datetime.utcnow()
        }
        
        return {
            "success": True,
            "brand_package": brand_package
        }
    
    async def _generate_initial_ideas(self, challenge: str, context: Dict, count: int) -> List[str]:
        """Generate initial creative ideas"""
        prompt = f"""
        Generate {count} creative ideas to address this challenge:
        
        Challenge: {challenge}
        Context: {context}
        
        Think outside the box and provide diverse, innovative solutions.
        Each idea should be unique and actionable.
        """
        
        response = await self.llm_service.generate(
            prompt=prompt,
            model="llama3.2:3b",
            max_tokens=500
        )
        
        # Parse response into individual ideas
        ideas_text = response.get("response", "")
        ideas = [idea.strip() for idea in ideas_text.split("\n") if idea.strip()]
        
        return ideas[:count]
    
    async def _apply_creative_techniques(self, idea: str, creativity_level: str) -> Dict[str, Any]:
        """Apply creative thinking techniques to enhance ideas"""
        techniques = {
            "scamper": await self._apply_scamper_technique(idea),
            "reverse_thinking": await self._apply_reverse_thinking(idea),
            "random_association": await self._apply_random_association(idea),
            "what_if_scenarios": await self._generate_what_if_scenarios(idea)
        }
        
        return {
            "original_idea": idea,
            "enhanced_versions": techniques,
            "creativity_score": await self._calculate_creativity_score(idea, techniques),
            "feasibility_assessment": await self._assess_idea_feasibility(idea)
        }
    
    async def _create_content_outline(self, topic: str, content_type: str, audience: str) -> Dict[str, Any]:
        """Create structured outline for content"""
        prompt = f"""
        Create a detailed outline for {content_type} about "{topic}" for {audience} audience.
        
        Include:
        1. Hook/Opening
        2. Main sections with key points
        3. Supporting details
        4. Conclusion/Call to action
        
        Make it engaging and well-structured.
        """
        
        response = await self.llm_service.generate(
            prompt=prompt,
            model="llama3.2:3b",
            max_tokens=400
        )
        
        return {
            "outline_text": response.get("response", ""),
            "estimated_length": await self._estimate_content_length(response.get("response", "")),
            "key_sections": await self._extract_key_sections(response.get("response", ""))
        }
    
    async def _generate_content(self, outline: Dict, topic: str, tone: str, length: str) -> str:
        """Generate content based on outline"""
        length_map = {
            "short": "300-500 words",
            "medium": "800-1200 words", 
            "long": "1500-2500 words"
        }
        
        prompt = f"""
        Write engaging {length_map.get(length, "medium length")} content about "{topic}" with a {tone} tone.
        
        Follow this outline:
        {outline.get('outline_text', '')}
        
        Make it compelling, well-structured, and valuable to readers.
        """
        
        response = await self.llm_service.generate(
            prompt=prompt,
            model="deepseek-r1:7b",  # Use reasoning model for longer content
            max_tokens=1500
        )
        
        return response.get("response", "")
    
    async def _enhance_content_creativity(self, content: str, content_type: str) -> str:
        """Add creative elements to enhance content"""
        prompt = f"""
        Enhance this {content_type} with creative elements:
        
        {content}
        
        Add:
        - Engaging metaphors or analogies
        - Compelling examples
        - Thought-provoking questions
        - Vivid descriptions
        - Memorable phrases
        
        Keep the core message while making it more engaging.
        """
        
        response = await self.llm_service.generate(
            prompt=prompt,
            model="llama3.2:3b",
            max_tokens=800
        )
        
        return response.get("response", content)
    
    async def _general_creative_assistance(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general creative requests"""
        request = task_data.get("request", "")
        context = task_data.get("context", {})
        
        prompt = f"""
        As a creative expert, help with this request:
        
        Request: {request}
        Context: {context}
        
        Provide creative, innovative solutions and ideas.
        Be imaginative and think outside conventional boundaries.
        """
        
        response = await self.llm_service.generate(
            prompt=prompt,
            model="llama3.2:3b",
            max_tokens=500
        )
        
        return {
            "success": True,
            "creative_response": response.get("response", ""),
            "additional_ideas": await self._generate_additional_creative_ideas(request, 5),
            "inspiration_sources": [
                "Nature patterns and biomimicry",
                "Cross-industry innovations",
                "Historical creative solutions",
                "Emerging technology trends",
                "Cultural and artistic movements"
            ]
        }
    
    # Additional helper methods for creative techniques
    async def _apply_scamper_technique(self, idea: str) -> Dict[str, str]:
        """Apply SCAMPER creative thinking technique"""
        return {
            "substitute": f"What if we substitute elements in: {idea}",
            "combine": f"What if we combine {idea} with something else",
            "adapt": f"How can we adapt {idea} from other contexts",
            "modify": f"What if we modify or magnify aspects of: {idea}",
            "put_to_other_uses": f"How else could we use: {idea}",
            "eliminate": f"What if we remove elements from: {idea}",
            "reverse": f"What if we reverse or rearrange: {idea}"
        }
    
    async def _calculate_creativity_score(self, idea: str, techniques: Dict) -> float:
        """Calculate creativity score for an idea"""
        # Simplified creativity scoring
        base_score = 0.7
        
        # Bonus for uniqueness (simplified check)
        if len(idea.split()) > 10:  # More detailed ideas
            base_score += 0.1
        
        # Bonus for technique application
        if len(techniques) > 3:
            base_score += 0.1
        
        return min(base_score, 1.0)
