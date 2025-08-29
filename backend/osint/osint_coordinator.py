
"""
OSINT Coordinator
Central coordination for all OSINT intelligence gathering operations
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from loguru import logger

from .social import SocialIntelligence
from .technical import TechnicalIntelligence
from .breach import BreachIntelligence
from .media import MediaIntelligence
from .base import OSINTBase


class InvestigationType(Enum):
    """Types of OSINT investigations"""
    PERSON = "person"
    DOMAIN = "domain"
    IP_ADDRESS = "ip_address"
    EMAIL = "email"
    USERNAME = "username"
    IMAGE = "image"
    COMPREHENSIVE = "comprehensive"


@dataclass
class Investigation:
    """OSINT investigation structure"""
    id: str
    type: InvestigationType
    target: str
    status: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0


class OSINTCoordinator(OSINTBase):
    """
    Central coordinator for all OSINT operations
    Orchestrates multiple intelligence gathering modules
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize intelligence modules
        self.social_intel = SocialIntelligence()
        self.technical_intel = TechnicalIntelligence()
        self.breach_intel = BreachIntelligence()
        self.media_intel = MediaIntelligence()
        
        # Active investigations
        self.active_investigations: Dict[str, Investigation] = {}
        self.completed_investigations: List[Investigation] = []
        
        # Coordination metrics
        self.metrics = {
            "total_investigations": 0,
            "completed_investigations": 0,
            "success_rate": 0.0,
            "average_investigation_time": 0.0,
            "module_usage": {
                "social": 0,
                "technical": 0,
                "breach": 0,
                "media": 0
            }
        }
    
    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Main search method that coordinates across all OSINT modules
        """
        try:
            investigation_type = kwargs.get("type", "comprehensive")
            investigation_id = kwargs.get("investigation_id", f"inv_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Create investigation
            investigation = Investigation(
                id=investigation_id,
                type=InvestigationType(investigation_type),
                target=query,
                status="in_progress"
            )
            
            self.active_investigations[investigation_id] = investigation
            
            # Coordinate search across modules
            results = await self._coordinate_search(query, investigation_type)
            
            # Update investigation
            investigation.results = results
            investigation.status = "completed"
            investigation.updated_at = datetime.now()
            investigation.confidence_score = await self._calculate_confidence_score(results)
            
            # Move to completed
            self.completed_investigations.append(investigation)
            del self.active_investigations[investigation_id]
            
            # Update metrics
            await self._update_metrics(investigation)
            
            self.log_osint_activity("coordinated_search", query, f"investigation {investigation_id} completed")
            
            return {
                "success": True,
                "investigation_id": investigation_id,
                "target": query,
                "type": investigation_type,
                "results": results,
                "confidence_score": investigation.confidence_score,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"OSINT coordination error: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def analyze(self, data: Any, **kwargs) -> Dict[str, Any]:
        """
        Coordinate analysis across all OSINT modules
        """
        try:
            analysis_type = kwargs.get("type", "comprehensive")
            
            # Coordinate analysis across modules
            analysis_results = {}
            
            if analysis_type in ["comprehensive", "social"]:
                analysis_results["social"] = await self.social_intel.analyze(data, **kwargs)
            
            if analysis_type in ["comprehensive", "technical"]:
                analysis_results["technical"] = await self.technical_intel.analyze(data, **kwargs)
            
            if analysis_type in ["comprehensive", "breach"]:
                analysis_results["breach"] = await self.breach_intel.analyze(data, **kwargs)
            
            if analysis_type in ["comprehensive", "media"]:
                analysis_results["media"] = await self.media_intel.analyze(data, **kwargs)
            
            # Synthesize results
            synthesis = await self._synthesize_analysis(analysis_results)
            
            return {
                "success": True,
                "analysis_type": analysis_type,
                "module_results": analysis_results,
                "synthesis": synthesis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"OSINT analysis coordination error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def investigate_person(self, identifier: str) -> Dict[str, Any]:
        """
        Comprehensive person investigation
        """
        try:
            logger.info(f"Starting person investigation: {identifier}")
            
            investigation_id = f"person_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Parallel investigation across modules
            tasks = []
            
            # Social media investigation
            if self.validate_input(identifier, "username"):
                tasks.append(self.social_intel.search_username(identifier))
                tasks.append(self.social_intel.analyze_social_footprint(identifier))
            
            # Email investigation
            if self.validate_input(identifier, "email"):
                tasks.append(self.breach_intel.check_email_breaches(identifier))
            
            # Execute investigations
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            investigation_results = {
                "social_profiles": [],
                "breach_data": {},
                "risk_assessment": {},
                "recommendations": []
            }
            
            for result in results:
                if not isinstance(result, Exception) and result.get("success"):
                    if "profiles_found" in result:
                        investigation_results["social_profiles"].append(result)
                    elif "breach_count" in result:
                        investigation_results["breach_data"] = result
            
            # Generate comprehensive analysis
            analysis = await self._analyze_person_investigation(investigation_results)
            
            self.log_osint_activity("person_investigation", identifier, f"investigation {investigation_id} completed")
            
            return {
                "success": True,
                "investigation_id": investigation_id,
                "target": identifier,
                "type": "person",
                "results": investigation_results,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Person investigation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "target": identifier
            }
    
    async def investigate_domain(self, domain: str) -> Dict[str, Any]:
        """
        Comprehensive domain investigation
        """
        try:
            logger.info(f"Starting domain investigation: {domain}")
            
            investigation_id = f"domain_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Parallel investigation
            tasks = [
                self.technical_intel.analyze_domain(domain),
                self.breach_intel.check_domain_breaches(domain),
                self.social_intel.monitor_mentions([domain])
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            investigation_results = {
                "technical_analysis": {},
                "breach_history": {},
                "social_mentions": {},
                "security_assessment": {}
            }
            
            for result in results:
                if not isinstance(result, Exception) and result.get("success"):
                    if "domain_info" in result:
                        investigation_results["technical_analysis"] = result
                    elif "breach_count" in result:
                        investigation_results["breach_history"] = result
                    elif "total_mentions" in result:
                        investigation_results["social_mentions"] = result
            
            # Generate comprehensive analysis
            analysis = await self._analyze_domain_investigation(investigation_results)
            
            self.log_osint_activity("domain_investigation", domain, f"investigation {investigation_id} completed")
            
            return {
                "success": True,
                "investigation_id": investigation_id,
                "target": domain,
                "type": "domain",
                "results": investigation_results,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Domain investigation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "target": domain
            }
    
    async def investigate_image(self, image_source: str) -> Dict[str, Any]:
        """
        Comprehensive image investigation
        """
        try:
            logger.info(f"Starting image investigation: {image_source}")
            
            investigation_id = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Parallel investigation
            tasks = [
                self.media_intel.reverse_image_search(image_source),
                self.media_intel.extract_metadata(image_source)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            investigation_results = {
                "reverse_search": {},
                "metadata": {},
                "forensic_analysis": {}
            }
            
            for result in results:
                if not isinstance(result, Exception) and result.get("success"):
                    if "total_results" in result:
                        investigation_results["reverse_search"] = result
                    elif "metadata" in result:
                        investigation_results["metadata"] = result
            
            # Generate comprehensive analysis
            analysis = await self._analyze_image_investigation(investigation_results)
            
            self.log_osint_activity("image_investigation", image_source, f"investigation {investigation_id} completed")
            
            return {
                "success": True,
                "investigation_id": investigation_id,
                "target": image_source,
                "type": "image",
                "results": investigation_results,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Image investigation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "target": image_source
            }
    
    async def _coordinate_search(self, query: str, investigation_type: str) -> Dict[str, Any]:
        """Coordinate search across appropriate modules"""
        
        results = {}
        
        try:
            if investigation_type in ["comprehensive", "social"]:
                self.metrics["module_usage"]["social"] += 1
                results["social"] = await self.social_intel.search(query)
            
            if investigation_type in ["comprehensive", "technical"]:
                self.metrics["module_usage"]["technical"] += 1
                results["technical"] = await self.technical_intel.search(query)
            
            if investigation_type in ["comprehensive", "breach"]:
                self.metrics["module_usage"]["breach"] += 1
                results["breach"] = await self.breach_intel.search(query)
            
            if investigation_type in ["comprehensive", "media"]:
                self.metrics["module_usage"]["media"] += 1
                results["media"] = await self.media_intel.search(query)
            
        except Exception as e:
            logger.error(f"Search coordination error: {e}")
        
        return results
    
    async def _calculate_confidence_score(self, results: Dict[str, Any]) -> float:
        """Calculate confidence score for investigation results"""
        
        total_score = 0.0
        module_count = 0
        
        for module, result in results.items():
            if result.get("success"):
                module_count += 1
                
                # Module-specific confidence scoring
                if module == "social":
                    if result.get("profiles_found", 0) > 0:
                        total_score += 0.8
                    else:
                        total_score += 0.3
                
                elif module == "technical":
                    if result.get("domain_info") or result.get("ip_info"):
                        total_score += 0.9
                    else:
                        total_score += 0.4
                
                elif module == "breach":
                    if result.get("breach_count", 0) > 0:
                        total_score += 0.7
                    else:
                        total_score += 0.5
                
                elif module == "media":
                    if result.get("total_results", 0) > 0:
                        total_score += 0.6
                    else:
                        total_score += 0.3
        
        return total_score / module_count if module_count > 0 else 0.0
    
    async def _synthesize_analysis(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize analysis results from multiple modules"""
        
        synthesis = {
            "overall_assessment": "unknown",
            "key_findings": [],
            "risk_factors": [],
            "recommendations": [],
            "confidence_level": "medium"
        }
        
        # Collect findings from all modules
        all_findings = []
        all_risks = []
        all_recommendations = []
        
        for module, result in analysis_results.items():
            if result.get("success"):
                # Extract findings
                if "analysis" in result:
                    analysis = result["analysis"]
                    if "key_findings" in analysis:
                        all_findings.extend(analysis["key_findings"])
                    if "risk_factors" in analysis:
                        all_risks.extend(analysis["risk_factors"])
                    if "recommendations" in analysis:
                        all_recommendations.extend(analysis["recommendations"])
        
        # Deduplicate and prioritize
        synthesis["key_findings"] = list(set(all_findings))[:10]  # Top 10
        synthesis["risk_factors"] = list(set(all_risks))[:10]     # Top 10
        synthesis["recommendations"] = list(set(all_recommendations))[:10]  # Top 10
        
        # Overall assessment
        if len(all_risks) > 5:
            synthesis["overall_assessment"] = "high_risk"
        elif len(all_risks) > 2:
            synthesis["overall_assessment"] = "medium_risk"
        elif len(all_findings) > 3:
            synthesis["overall_assessment"] = "informative"
        else:
            synthesis["overall_assessment"] = "limited_information"
        
        return synthesis
    
    async def _analyze_person_investigation(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze person investigation results"""
        
        analysis = {
            "digital_footprint": "unknown",
            "privacy_score": 0.5,
            "risk_assessment": "medium",
            "key_insights": [],
            "recommendations": []
        }
        
        # Analyze social presence
        if results.get("social_profiles"):
            profile_count = sum(len(profile.get("results", {})) for profile in results["social_profiles"])
            if profile_count > 5:
                analysis["digital_footprint"] = "extensive"
                analysis["privacy_score"] = 0.3
            elif profile_count > 2:
                analysis["digital_footprint"] = "moderate"
                analysis["privacy_score"] = 0.6
            else:
                analysis["digital_footprint"] = "minimal"
                analysis["privacy_score"] = 0.8
        
        # Analyze breach exposure
        if results.get("breach_data"):
            breach_count = results["breach_data"].get("breach_count", 0)
            if breach_count > 3:
                analysis["risk_assessment"] = "high"
                analysis["key_insights"].append(f"Found in {breach_count} data breaches")
                analysis["recommendations"].append("Immediately change all passwords")
            elif breach_count > 0:
                analysis["risk_assessment"] = "medium"
                analysis["key_insights"].append(f"Found in {breach_count} data breaches")
                analysis["recommendations"].append("Review and update passwords")
        
        return analysis
    
    async def _analyze_domain_investigation(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze domain investigation results"""
        
        analysis = {
            "security_posture": "unknown",
            "reputation": "neutral",
            "infrastructure_assessment": {},
            "key_insights": [],
            "recommendations": []
        }
        
        # Analyze technical data
        if results.get("technical_analysis"):
            tech_data = results["technical_analysis"]
            if tech_data.get("success"):
                analysis["infrastructure_assessment"] = tech_data.get("analysis", {})
                
                # SSL analysis
                if tech_data.get("domain_info", {}).get("ssl_info"):
                    analysis["key_insights"].append("SSL certificate present")
                    analysis["security_posture"] = "good"
                else:
                    analysis["key_insights"].append("No SSL certificate")
                    analysis["security_posture"] = "poor"
        
        # Analyze breach history
        if results.get("breach_history"):
            breach_data = results["breach_history"]
            if breach_data.get("breach_count", 0) > 0:
                analysis["reputation"] = "compromised"
                analysis["key_insights"].append(f"Domain involved in {breach_data['breach_count']} breaches")
                analysis["recommendations"].append("Review security practices")
        
        return analysis
    
    async def _analyze_image_investigation(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image investigation results"""
        
        analysis = {
            "authenticity": "unknown",
            "privacy_risks": [],
            "distribution": "unknown",
            "key_insights": [],
            "recommendations": []
        }
        
        # Analyze reverse search results
        if results.get("reverse_search"):
            search_data = results["reverse_search"]
            if search_data.get("success"):
                total_results = search_data.get("total_results", 0)
                
                if total_results == 0:
                    analysis["authenticity"] = "unique"
                    analysis["distribution"] = "original"
                elif total_results < 5:
                    analysis["authenticity"] = "rare"
                    analysis["distribution"] = "limited"
                else:
                    analysis["authenticity"] = "common"
                    analysis["distribution"] = "widespread"
                
                analysis["key_insights"].append(f"Found {total_results} similar images online")
        
        # Analyze metadata
        if results.get("metadata"):
            metadata = results["metadata"]
            if metadata.get("success"):
                meta_analysis = metadata.get("analysis", {})
                
                # Privacy risks
                privacy_risks = meta_analysis.get("privacy_risks", [])
                analysis["privacy_risks"] = privacy_risks
                
                if privacy_risks:
                    analysis["recommendations"].extend([
                        "Remove metadata before sharing",
                        "Review privacy settings"
                    ])
        
        return analysis
    
    async def _update_metrics(self, investigation: Investigation):
        """Update coordination metrics"""
        
        self.metrics["total_investigations"] += 1
        
        if investigation.status == "completed":
            self.metrics["completed_investigations"] += 1
            
            # Update success rate
            total = self.metrics["total_investigations"]
            completed = self.metrics["completed_investigations"]
            self.metrics["success_rate"] = completed / total
            
            # Update average investigation time
            investigation_time = (investigation.updated_at - investigation.created_at).total_seconds()
            current_avg = self.metrics["average_investigation_time"]
            self.metrics["average_investigation_time"] = (
                (current_avg * (completed - 1) + investigation_time) / completed
            )
    
    async def get_investigation_status(self, investigation_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific investigation"""
        
        # Check active investigations
        if investigation_id in self.active_investigations:
            investigation = self.active_investigations[investigation_id]
            return {
                "id": investigation.id,
                "type": investigation.type.value,
                "target": investigation.target,
                "status": investigation.status,
                "created_at": investigation.created_at.isoformat(),
                "updated_at": investigation.updated_at.isoformat()
            }
        
        # Check completed investigations
        for investigation in self.completed_investigations:
            if investigation.id == investigation_id:
                return {
                    "id": investigation.id,
                    "type": investigation.type.value,
                    "target": investigation.target,
                    "status": investigation.status,
                    "created_at": investigation.created_at.isoformat(),
                    "updated_at": investigation.updated_at.isoformat(),
                    "results": investigation.results,
                    "confidence_score": investigation.confidence_score
                }
        
        return None
    
    async def get_coordinator_status(self) -> Dict[str, Any]:
        """Get overall coordinator status and metrics"""
        
        return {
            "active_investigations": len(self.active_investigations),
            "completed_investigations": len(self.completed_investigations),
            "metrics": self.metrics,
            "available_modules": ["social", "technical", "breach", "media"],
            "investigation_types": [t.value for t in InvestigationType],
            "status": "operational"
        }
