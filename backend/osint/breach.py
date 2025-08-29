
"""
Breach Intelligence (BREACHINT)
Data breach monitoring and credential exposure detection
"""

import asyncio
import hashlib
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

import aiohttp
from loguru import logger

from .base import OSINTBase


@dataclass
class BreachInfo:
    """Data breach information"""
    name: str
    title: str
    domain: str
    breach_date: datetime
    added_date: datetime
    modified_date: datetime
    pwn_count: int
    description: str
    data_classes: List[str]
    is_verified: bool
    is_fabricated: bool
    is_sensitive: bool
    is_retired: bool
    is_spam_list: bool
    logo_path: Optional[str]


@dataclass
class PasteInfo:
    """Paste information from data dumps"""
    source: str
    id: str
    title: Optional[str]
    date: datetime
    email_count: int


class BreachIntelligence(OSINTBase):
    """
    Breach Intelligence gathering
    Monitor data breaches and credential exposure
    """
    
    def __init__(self):
        super().__init__()
        
        # API endpoints (would require API keys)
        self.hibp_api_base = "https://haveibeenpwned.com/api/v3"
        self.dehashed_api_base = "https://api.dehashed.com/search"
        
        # Rate limiting for breach services
        self.setup_rate_limiters()
    
    def setup_rate_limiters(self):
        """Setup rate limiters for breach services"""
        self.get_rate_limiter("hibp", 1, 2)  # HIBP: 1 request per 1.5 seconds
        self.get_rate_limiter("dehashed", 10, 60)  # DeHashed: 10 requests per minute
        self.get_rate_limiter("general", 30, 60)  # General: 30 requests per minute
    
    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Main search method for breach intelligence
        Supports email addresses and usernames
        """
        try:
            search_type = kwargs.get("type", "email")
            
            if search_type == "email" and self.validate_input(query, "email"):
                return await self.check_email_breaches(query)
            elif search_type == "username":
                return await self.check_username_exposure(query)
            elif search_type == "domain":
                return await self.check_domain_breaches(query)
            else:
                return {
                    "success": False,
                    "error": "Invalid search type or query format",
                    "query": query
                }
                
        except Exception as e:
            logger.error(f"Breach intelligence search error: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def analyze(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Analyze breach data for patterns and risk assessment"""
        try:
            if isinstance(data, list):
                return await self._analyze_breach_list(data)
            elif isinstance(data, dict):
                return await self._analyze_single_breach(data)
            else:
                return {
                    "success": False,
                    "error": "Invalid data format for analysis"
                }
                
        except Exception as e:
            logger.error(f"Breach analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def check_email_breaches(self, email: str) -> Dict[str, Any]:
        """
        Check if email address has been involved in data breaches
        Uses Have I Been Pwned API (requires API key)
        """
        try:
            logger.info(f"Checking breaches for email: {email}")
            
            # Check breaches
            breaches = await self._check_hibp_breaches(email)
            
            # Check pastes
            pastes = await self._check_hibp_pastes(email)
            
            # Check password exposure
            password_exposed = await self._check_password_exposure(email)
            
            # Risk assessment
            risk_assessment = await self._assess_email_risk(breaches, pastes, password_exposed)
            
            self.log_osint_activity("email_breach_check", email, f"found {len(breaches)} breaches")
            
            return {
                "success": True,
                "email": email,
                "breach_count": len(breaches),
                "paste_count": len(pastes),
                "breaches": breaches,
                "pastes": pastes,
                "password_exposed": password_exposed,
                "risk_assessment": risk_assessment,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Email breach check error for {email}: {e}")
            return {
                "success": False,
                "error": str(e),
                "email": email
            }
    
    async def check_username_exposure(self, username: str) -> Dict[str, Any]:
        """
        Check if username has been exposed in data breaches
        """
        try:
            logger.info(f"Checking username exposure: {username}")
            
            # Search across multiple breach databases
            exposures = []
            
            # Check common breach databases (would require API access)
            databases = ["dehashed", "leakcheck", "snusbase"]
            
            for database in databases:
                try:
                    results = await self._search_username_in_database(username, database)
                    if results:
                        exposures.extend(results)
                except Exception as e:
                    logger.warning(f"Error checking {database} for {username}: {e}")
            
            # Analyze exposure patterns
            analysis = await self._analyze_username_exposure(username, exposures)
            
            self.log_osint_activity("username_exposure_check", username, f"found {len(exposures)} exposures")
            
            return {
                "success": True,
                "username": username,
                "exposure_count": len(exposures),
                "exposures": exposures,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Username exposure check error for {username}: {e}")
            return {
                "success": False,
                "error": str(e),
                "username": username
            }
    
    async def check_domain_breaches(self, domain: str) -> Dict[str, Any]:
        """
        Check if domain has been involved in data breaches
        """
        try:
            logger.info(f"Checking domain breaches: {domain}")
            
            # Get all breaches for domain
            domain_breaches = await self._get_domain_breaches(domain)
            
            # Analyze domain breach patterns
            analysis = await self._analyze_domain_breaches(domain, domain_breaches)
            
            self.log_osint_activity("domain_breach_check", domain, f"found {len(domain_breaches)} breaches")
            
            return {
                "success": True,
                "domain": domain,
                "breach_count": len(domain_breaches),
                "breaches": domain_breaches,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Domain breach check error for {domain}: {e}")
            return {
                "success": False,
                "error": str(e),
                "domain": domain
            }
    
    async def _check_hibp_breaches(self, email: str) -> List[BreachInfo]:
        """Check Have I Been Pwned for breaches"""
        try:
            await self.rate_limiters["hibp"].acquire()
            
            # Note: This requires HIBP API key
            # For demonstration, return mock data
            
            # In real implementation:
            # headers = {"hibp-api-key": "your-api-key"}
            # url = f"{self.hibp_api_base}/breachedaccount/{email}"
            
            # Mock breach data for demonstration
            mock_breaches = [
                BreachInfo(
                    name="Adobe",
                    title="Adobe",
                    domain="adobe.com",
                    breach_date=datetime(2013, 10, 4),
                    added_date=datetime(2013, 12, 4),
                    modified_date=datetime(2013, 12, 4),
                    pwn_count=152445165,
                    description="In October 2013, 153 million Adobe accounts were breached...",
                    data_classes=["Email addresses", "Password hints", "Passwords", "Usernames"],
                    is_verified=True,
                    is_fabricated=False,
                    is_sensitive=False,
                    is_retired=False,
                    is_spam_list=False,
                    logo_path="https://haveibeenpwned.com/Content/Images/PwnedLogos/Adobe.png"
                )
            ]
            
            return mock_breaches
            
        except Exception as e:
            logger.error(f"HIBP breach check error: {e}")
            return []
    
    async def _check_hibp_pastes(self, email: str) -> List[PasteInfo]:
        """Check Have I Been Pwned for paste exposures"""
        try:
            await self.rate_limiters["hibp"].acquire()
            
            # Note: This requires HIBP API key
            # Mock paste data for demonstration
            
            mock_pastes = [
                PasteInfo(
                    source="Pastebin",
                    id="8Q0BvKD8",
                    title="syslog",
                    date=datetime(2014, 3, 25),
                    email_count=139
                )
            ]
            
            return mock_pastes
            
        except Exception as e:
            logger.error(f"HIBP paste check error: {e}")
            return []
    
    async def _check_password_exposure(self, email: str) -> bool:
        """Check if passwords associated with email have been exposed"""
        try:
            # This would check password exposure databases
            # For demonstration, return False
            return False
            
        except Exception as e:
            logger.error(f"Password exposure check error: {e}")
            return False
    
    async def _search_username_in_database(self, username: str, database: str) -> List[Dict[str, Any]]:
        """Search for username in specific breach database"""
        try:
            if database == "dehashed":
                return await self._search_dehashed(username, "username")
            elif database == "leakcheck":
                return await self._search_leakcheck(username)
            elif database == "snusbase":
                return await self._search_snusbase(username)
            else:
                return []
                
        except Exception as e:
            logger.error(f"Database search error for {username} in {database}: {e}")
            return []
    
    async def _search_dehashed(self, query: str, field: str) -> List[Dict[str, Any]]:
        """Search DeHashed database"""
        try:
            await self.rate_limiters["dehashed"].acquire()
            
            # Note: This requires DeHashed API credentials
            # Mock data for demonstration
            
            return [
                {
                    "id": "1234567890",
                    "email": f"{query}@example.com",
                    "username": query,
                    "password": "[REDACTED]",
                    "hashed_password": "5d41402abc4b2a76b9719d911017c592",
                    "name": "John Doe",
                    "database_name": "Example Breach 2020"
                }
            ]
            
        except Exception as e:
            logger.error(f"DeHashed search error: {e}")
            return []
    
    async def _search_leakcheck(self, username: str) -> List[Dict[str, Any]]:
        """Search LeakCheck database"""
        # Mock implementation
        return []
    
    async def _search_snusbase(self, username: str) -> List[Dict[str, Any]]:
        """Search Snusbase database"""
        # Mock implementation
        return []
    
    async def _get_domain_breaches(self, domain: str) -> List[BreachInfo]:
        """Get all breaches associated with a domain"""
        try:
            # This would query breach databases for domain-specific breaches
            # Mock data for demonstration
            
            return [
                BreachInfo(
                    name=f"{domain.split('.')[0]}_breach",
                    title=f"{domain} Data Breach",
                    domain=domain,
                    breach_date=datetime(2020, 1, 1),
                    added_date=datetime(2020, 2, 1),
                    modified_date=datetime(2020, 2, 1),
                    pwn_count=1000000,
                    description=f"Data breach affecting {domain} users",
                    data_classes=["Email addresses", "Passwords", "Usernames"],
                    is_verified=True,
                    is_fabricated=False,
                    is_sensitive=False,
                    is_retired=False,
                    is_spam_list=False,
                    logo_path=None
                )
            ]
            
        except Exception as e:
            logger.error(f"Domain breach lookup error: {e}")
            return []
    
    async def _assess_email_risk(self, breaches: List[BreachInfo], pastes: List[PasteInfo], password_exposed: bool) -> Dict[str, Any]:
        """Assess risk level for email address"""
        
        risk_score = 0.0
        risk_factors = []
        recommendations = []
        
        # Breach analysis
        if breaches:
            risk_score += len(breaches) * 0.2
            risk_factors.append(f"Found in {len(breaches)} data breaches")
            recommendations.append("Change passwords for affected accounts")
        
        # Paste analysis
        if pastes:
            risk_score += len(pastes) * 0.1
            risk_factors.append(f"Found in {len(pastes)} paste dumps")
            recommendations.append("Monitor for suspicious activity")
        
        # Password exposure
        if password_exposed:
            risk_score += 0.5
            risk_factors.append("Passwords have been exposed")
            recommendations.append("Immediately change all passwords")
        
        # Determine risk level
        if risk_score >= 1.0:
            risk_level = "high"
        elif risk_score >= 0.5:
            risk_level = "medium"
        elif risk_score > 0:
            risk_level = "low"
        else:
            risk_level = "minimal"
        
        return {
            "risk_level": risk_level,
            "risk_score": min(risk_score, 1.0),
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "breach_timeline": [breach.breach_date.isoformat() for breach in breaches],
            "most_recent_breach": max([breach.breach_date for breach in breaches]).isoformat() if breaches else None
        }
    
    async def _analyze_username_exposure(self, username: str, exposures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze username exposure patterns"""
        
        analysis = {
            "exposure_count": len(exposures),
            "databases_affected": list(set(exp.get("database_name", "unknown") for exp in exposures)),
            "data_types_exposed": [],
            "password_reuse": False,
            "recommendations": []
        }
        
        # Analyze exposed data types
        for exposure in exposures:
            if exposure.get("password"):
                analysis["data_types_exposed"].append("passwords")
            if exposure.get("email"):
                analysis["data_types_exposed"].append("emails")
            if exposure.get("name"):
                analysis["data_types_exposed"].append("names")
        
        analysis["data_types_exposed"] = list(set(analysis["data_types_exposed"]))
        
        # Check for password reuse (simplified)
        passwords = [exp.get("password") for exp in exposures if exp.get("password")]
        if len(set(passwords)) < len(passwords):
            analysis["password_reuse"] = True
            analysis["recommendations"].append("Avoid password reuse across accounts")
        
        return analysis
    
    async def _analyze_domain_breaches(self, domain: str, breaches: List[BreachInfo]) -> Dict[str, Any]:
        """Analyze domain breach patterns"""
        
        analysis = {
            "total_breaches": len(breaches),
            "total_affected_accounts": sum(breach.pwn_count for breach in breaches),
            "breach_timeline": sorted([breach.breach_date.isoformat() for breach in breaches]),
            "most_recent_breach": max([breach.breach_date for breach in breaches]).isoformat() if breaches else None,
            "data_classes_affected": [],
            "security_posture": "unknown"
        }
        
        # Analyze data classes
        all_data_classes = []
        for breach in breaches:
            all_data_classes.extend(breach.data_classes)
        
        analysis["data_classes_affected"] = list(set(all_data_classes))
        
        # Assess security posture
        if len(breaches) == 0:
            analysis["security_posture"] = "good"
        elif len(breaches) <= 2:
            analysis["security_posture"] = "moderate"
        else:
            analysis["security_posture"] = "poor"
        
        return analysis
    
    async def _analyze_breach_list(self, breaches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a list of breaches for patterns"""
        
        return {
            "total_breaches": len(breaches),
            "analysis_type": "breach_list",
            "patterns": {
                "most_common_data_classes": [],
                "breach_frequency": "unknown",
                "severity_distribution": {}
            }
        }
    
    async def _analyze_single_breach(self, breach: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single breach for details"""
        
        return {
            "breach_name": breach.get("name", "unknown"),
            "severity": "medium",
            "affected_accounts": breach.get("pwn_count", 0),
            "data_sensitivity": "medium",
            "recommendations": [
                "Monitor affected accounts",
                "Change passwords if affected",
                "Enable two-factor authentication"
            ]
        }
