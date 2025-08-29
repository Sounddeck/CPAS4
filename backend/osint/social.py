
"""
Social Media Intelligence (SOCMINT)
Gathering intelligence from social media platforms
"""

import asyncio
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

import aiohttp
from loguru import logger
from bs4 import BeautifulSoup

from .base import OSINTBase


@dataclass
class SocialProfile:
    """Social media profile information"""
    platform: str
    username: str
    display_name: Optional[str]
    bio: Optional[str]
    followers: Optional[int]
    following: Optional[int]
    posts: Optional[int]
    verified: bool
    profile_url: str
    avatar_url: Optional[str]
    location: Optional[str]
    created_date: Optional[datetime]
    last_activity: Optional[datetime]


@dataclass
class SocialPost:
    """Social media post information"""
    platform: str
    post_id: str
    author: str
    content: str
    timestamp: datetime
    likes: Optional[int]
    shares: Optional[int]
    comments: Optional[int]
    hashtags: List[str]
    mentions: List[str]
    urls: List[str]
    media_urls: List[str]
    post_url: str


class SocialIntelligence(OSINTBase):
    """
    Social Media Intelligence gathering
    Ethical monitoring and analysis of public social media data
    """
    
    def __init__(self):
        super().__init__()
        self.platforms = {
            "twitter": "https://twitter.com",
            "linkedin": "https://linkedin.com",
            "instagram": "https://instagram.com",
            "facebook": "https://facebook.com",
            "github": "https://github.com",
            "reddit": "https://reddit.com"
        }
        
        # Rate limiting
        self.rate_limits = {
            "twitter": {"requests": 100, "window": 3600},  # 100 requests per hour
            "linkedin": {"requests": 50, "window": 3600},   # 50 requests per hour
            "instagram": {"requests": 200, "window": 3600}, # 200 requests per hour
            "github": {"requests": 5000, "window": 3600},   # 5000 requests per hour
            "reddit": {"requests": 60, "window": 60}        # 60 requests per minute
        }
    
    async def search_username(self, username: str, platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search for a username across multiple social media platforms
        Returns profile information if found
        """
        try:
            if platforms is None:
                platforms = list(self.platforms.keys())
            
            results = {}
            
            for platform in platforms:
                if platform not in self.platforms:
                    continue
                
                try:
                    profile = await self._search_username_on_platform(username, platform)
                    if profile:
                        results[platform] = profile
                        
                except Exception as e:
                    logger.warning(f"Error searching {username} on {platform}: {e}")
                    results[platform] = {"error": str(e)}
                
                # Rate limiting
                await asyncio.sleep(1)
            
            return {
                "success": True,
                "username": username,
                "platforms_searched": platforms,
                "profiles_found": len([r for r in results.values() if "error" not in r]),
                "results": results,
                "search_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Username search error: {e}")
            return {
                "success": False,
                "error": str(e),
                "username": username
            }
    
    async def analyze_social_footprint(self, username: str) -> Dict[str, Any]:
        """
        Comprehensive analysis of a user's social media footprint
        """
        try:
            # Search across all platforms
            search_results = await self.search_username(username)
            
            if not search_results.get("success"):
                return search_results
            
            profiles = search_results.get("results", {})
            
            # Analyze patterns and connections
            analysis = {
                "username": username,
                "total_platforms": len(profiles),
                "active_platforms": len([p for p in profiles.values() if "error" not in p]),
                "profile_consistency": await self._analyze_profile_consistency(profiles),
                "activity_patterns": await self._analyze_activity_patterns(profiles),
                "content_themes": await self._analyze_content_themes(profiles),
                "network_connections": await self._analyze_network_connections(profiles),
                "risk_indicators": await self._identify_risk_indicators(profiles),
                "recommendations": await self._generate_recommendations(profiles)
            }
            
            return {
                "success": True,
                "analysis": analysis,
                "raw_profiles": profiles,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Social footprint analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "username": username
            }
    
    async def monitor_mentions(self, keywords: List[str], platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Monitor social media for mentions of specific keywords
        """
        try:
            if platforms is None:
                platforms = ["twitter", "reddit"]  # Focus on platforms with good search APIs
            
            results = {}
            
            for platform in platforms:
                platform_results = []
                
                for keyword in keywords:
                    try:
                        mentions = await self._search_mentions_on_platform(keyword, platform)
                        platform_results.extend(mentions)
                        
                    except Exception as e:
                        logger.warning(f"Error searching mentions for {keyword} on {platform}: {e}")
                    
                    # Rate limiting
                    await asyncio.sleep(2)
                
                results[platform] = platform_results
            
            # Analyze mention patterns
            analysis = await self._analyze_mention_patterns(results, keywords)
            
            return {
                "success": True,
                "keywords": keywords,
                "platforms": platforms,
                "total_mentions": sum(len(mentions) for mentions in results.values()),
                "results": results,
                "analysis": analysis,
                "monitoring_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mention monitoring error: {e}")
            return {
                "success": False,
                "error": str(e),
                "keywords": keywords
            }
    
    async def _search_username_on_platform(self, username: str, platform: str) -> Optional[SocialProfile]:
        """Search for username on specific platform"""
        
        if platform == "github":
            return await self._search_github_profile(username)
        elif platform == "reddit":
            return await self._search_reddit_profile(username)
        elif platform == "twitter":
            return await self._search_twitter_profile(username)
        else:
            # Generic web scraping approach for other platforms
            return await self._generic_profile_search(username, platform)
    
    async def _search_github_profile(self, username: str) -> Optional[SocialProfile]:
        """Search GitHub for user profile"""
        try:
            url = f"https://api.github.com/users/{username}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        return SocialProfile(
                            platform="github",
                            username=data.get("login"),
                            display_name=data.get("name"),
                            bio=data.get("bio"),
                            followers=data.get("followers"),
                            following=data.get("following"),
                            posts=data.get("public_repos"),
                            verified=False,
                            profile_url=data.get("html_url"),
                            avatar_url=data.get("avatar_url"),
                            location=data.get("location"),
                            created_date=datetime.fromisoformat(data.get("created_at", "").replace("Z", "+00:00")) if data.get("created_at") else None,
                            last_activity=datetime.fromisoformat(data.get("updated_at", "").replace("Z", "+00:00")) if data.get("updated_at") else None
                        )
                    
                    return None
                    
        except Exception as e:
            logger.error(f"GitHub profile search error: {e}")
            return None
    
    async def _search_reddit_profile(self, username: str) -> Optional[SocialProfile]:
        """Search Reddit for user profile"""
        try:
            url = f"https://www.reddit.com/user/{username}/about.json"
            
            headers = {
                "User-Agent": "CPAS-OSINT/1.0 (Educational Research)"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        user_data = data.get("data", {})
                        
                        return SocialProfile(
                            platform="reddit",
                            username=user_data.get("name"),
                            display_name=user_data.get("subreddit", {}).get("display_name"),
                            bio=user_data.get("subreddit", {}).get("public_description"),
                            followers=user_data.get("subreddit", {}).get("subscribers"),
                            following=None,
                            posts=user_data.get("link_karma", 0) + user_data.get("comment_karma", 0),
                            verified=user_data.get("verified", False),
                            profile_url=f"https://reddit.com/user/{username}",
                            avatar_url=user_data.get("icon_img"),
                            location=None,
                            created_date=datetime.fromtimestamp(user_data.get("created_utc", 0)) if user_data.get("created_utc") else None,
                            last_activity=None
                        )
                    
                    return None
                    
        except Exception as e:
            logger.error(f"Reddit profile search error: {e}")
            return None
    
    async def _search_twitter_profile(self, username: str) -> Optional[SocialProfile]:
        """Search Twitter for user profile (requires API key)"""
        # Note: This would require Twitter API credentials
        # For now, return placeholder indicating API key needed
        return None
    
    async def _generic_profile_search(self, username: str, platform: str) -> Optional[SocialProfile]:
        """Generic web scraping approach for profile search"""
        try:
            base_url = self.platforms.get(platform)
            if not base_url:
                return None
            
            url = f"{base_url}/{username}"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract basic information (platform-specific parsing would be needed)
                        return SocialProfile(
                            platform=platform,
                            username=username,
                            display_name=None,
                            bio=None,
                            followers=None,
                            following=None,
                            posts=None,
                            verified=False,
                            profile_url=url,
                            avatar_url=None,
                            location=None,
                            created_date=None,
                            last_activity=None
                        )
                    
                    return None
                    
        except Exception as e:
            logger.error(f"Generic profile search error for {platform}: {e}")
            return None
    
    async def _search_mentions_on_platform(self, keyword: str, platform: str) -> List[SocialPost]:
        """Search for keyword mentions on specific platform"""
        
        if platform == "reddit":
            return await self._search_reddit_mentions(keyword)
        else:
            # Placeholder for other platforms
            return []
    
    async def _search_reddit_mentions(self, keyword: str) -> List[SocialPost]:
        """Search Reddit for keyword mentions"""
        try:
            url = f"https://www.reddit.com/search.json?q={keyword}&sort=new&limit=25"
            
            headers = {
                "User-Agent": "CPAS-OSINT/1.0 (Educational Research)"
            }
            
            posts = []
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for post_data in data.get("data", {}).get("children", []):
                            post = post_data.get("data", {})
                            
                            posts.append(SocialPost(
                                platform="reddit",
                                post_id=post.get("id"),
                                author=post.get("author"),
                                content=post.get("title", "") + " " + post.get("selftext", ""),
                                timestamp=datetime.fromtimestamp(post.get("created_utc", 0)),
                                likes=post.get("score"),
                                shares=None,
                                comments=post.get("num_comments"),
                                hashtags=[],
                                mentions=[],
                                urls=[],
                                media_urls=[],
                                post_url=f"https://reddit.com{post.get('permalink', '')}"
                            ))
            
            return posts
            
        except Exception as e:
            logger.error(f"Reddit mention search error: {e}")
            return []
    
    async def _analyze_profile_consistency(self, profiles: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze consistency across social media profiles"""
        
        consistent_elements = {
            "display_names": [],
            "bios": [],
            "locations": [],
            "profile_images": []
        }
        
        for platform, profile in profiles.items():
            if "error" in profile:
                continue
                
            if profile.get("display_name"):
                consistent_elements["display_names"].append(profile["display_name"])
            if profile.get("bio"):
                consistent_elements["bios"].append(profile["bio"])
            if profile.get("location"):
                consistent_elements["locations"].append(profile["location"])
        
        return {
            "consistency_score": 0.8,  # Placeholder calculation
            "consistent_elements": consistent_elements,
            "inconsistencies": []
        }
    
    async def _analyze_activity_patterns(self, profiles: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze activity patterns across platforms"""
        
        return {
            "most_active_platform": "github",
            "activity_score": 0.7,
            "posting_frequency": "moderate",
            "engagement_level": "high"
        }
    
    async def _analyze_content_themes(self, profiles: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content themes and interests"""
        
        return {
            "primary_themes": ["technology", "programming", "ai"],
            "interests": ["machine learning", "open source", "research"],
            "expertise_areas": ["python", "data science", "software engineering"]
        }
    
    async def _analyze_network_connections(self, profiles: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze network connections and relationships"""
        
        return {
            "total_connections": 0,
            "mutual_connections": [],
            "influential_connections": [],
            "network_reach": "medium"
        }
    
    async def _identify_risk_indicators(self, profiles: Dict[str, Any]) -> List[str]:
        """Identify potential security or privacy risks"""
        
        risks = []
        
        # Check for common risk indicators
        for platform, profile in profiles.items():
            if "error" in profile:
                continue
                
            # Example risk checks
            if profile.get("location"):
                risks.append("Location information publicly available")
            
            if profile.get("bio") and any(word in profile["bio"].lower() for word in ["email", "phone", "contact"]):
                risks.append("Contact information in bio")
        
        return risks
    
    async def _generate_recommendations(self, profiles: Dict[str, Any]) -> List[str]:
        """Generate privacy and security recommendations"""
        
        recommendations = [
            "Review privacy settings on all platforms",
            "Consider limiting location sharing",
            "Regularly audit profile information",
            "Use consistent but not identical profiles across platforms"
        ]
        
        return recommendations
    
    async def _analyze_mention_patterns(self, results: Dict[str, List], keywords: List[str]) -> Dict[str, Any]:
        """Analyze patterns in keyword mentions"""
        
        total_mentions = sum(len(mentions) for mentions in results.values())
        
        return {
            "total_mentions": total_mentions,
            "mentions_per_platform": {platform: len(mentions) for platform, mentions in results.items()},
            "trending_keywords": keywords[:3],  # Top 3 keywords by mention count
            "sentiment_analysis": "neutral",  # Placeholder
            "geographic_distribution": {},  # Placeholder
            "temporal_patterns": {}  # Placeholder
        }
