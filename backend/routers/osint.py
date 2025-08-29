
"""
OSINT API Routes
FastAPI endpoints for OSINT intelligence gathering operations
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from ..osint.osint_coordinator import OSINTCoordinator
from ..services.german_voice import GermanVoiceInterface

router = APIRouter(prefix="/osint", tags=["osint"])

# Global instances
osint_coordinator = OSINTCoordinator()
voice_interface = GermanVoiceInterface()


class OSINTRequest(BaseModel):
    """Request model for OSINT operations"""
    target: str = Field(..., description="Target for investigation")
    investigation_type: str = Field(default="comprehensive", description="Type of investigation")
    include_voice: bool = Field(default=False, description="Include voice response")
    modules: Optional[List[str]] = Field(default=None, description="Specific modules to use")


class PersonInvestigationRequest(BaseModel):
    """Request model for person investigation"""
    identifier: str = Field(..., description="Person identifier (username, email, etc.)")
    include_voice: bool = Field(default=False, description="Include voice response")


class DomainInvestigationRequest(BaseModel):
    """Request model for domain investigation"""
    domain: str = Field(..., description="Domain to investigate")
    include_voice: bool = Field(default=False, description="Include voice response")


class ImageInvestigationRequest(BaseModel):
    """Request model for image investigation"""
    image_source: str = Field(..., description="Image URL or file path")
    include_voice: bool = Field(default=False, description="Include voice response")


@router.post("/investigate")
async def investigate_target(request: OSINTRequest):
    """
    Perform comprehensive OSINT investigation on target
    """
    try:
        # Perform investigation
        result = await osint_coordinator.search(
            query=request.target,
            type=request.investigation_type
        )
        
        # Add voice response if requested
        if request.include_voice and result.get("success"):
            voice_result = await voice_interface.speak_osint_results(result)
            result["voice_response"] = voice_result
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Investigation error: {str(e)}")


@router.post("/investigate/person")
async def investigate_person(request: PersonInvestigationRequest):
    """
    Perform comprehensive person investigation
    """
    try:
        result = await osint_coordinator.investigate_person(request.identifier)
        
        # Add voice response if requested
        if request.include_voice and result.get("success"):
            voice_result = await voice_interface.speak_osint_results(result)
            result["voice_response"] = voice_result
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Person investigation error: {str(e)}")


@router.post("/investigate/domain")
async def investigate_domain(request: DomainInvestigationRequest):
    """
    Perform comprehensive domain investigation
    """
    try:
        result = await osint_coordinator.investigate_domain(request.domain)
        
        # Add voice response if requested
        if request.include_voice and result.get("success"):
            voice_result = await voice_interface.speak_osint_results(result)
            result["voice_response"] = voice_result
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Domain investigation error: {str(e)}")


@router.post("/investigate/image")
async def investigate_image(request: ImageInvestigationRequest):
    """
    Perform comprehensive image investigation
    """
    try:
        result = await osint_coordinator.investigate_image(request.image_source)
        
        # Add voice response if requested
        if request.include_voice and result.get("success"):
            voice_result = await voice_interface.speak_osint_results(result)
            result["voice_response"] = voice_result
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image investigation error: {str(e)}")


@router.get("/investigation/{investigation_id}")
async def get_investigation_status(investigation_id: str):
    """
    Get status of specific investigation
    """
    try:
        status = await osint_coordinator.get_investigation_status(investigation_id)
        
        if status is None:
            raise HTTPException(status_code=404, detail="Investigation not found")
        
        return {
            "success": True,
            "investigation": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving investigation: {str(e)}")


@router.get("/status")
async def get_osint_status():
    """
    Get overall OSINT coordinator status
    """
    try:
        status = await osint_coordinator.get_coordinator_status()
        
        return {
            "success": True,
            "osint_status": status,
            "voice_interface": voice_interface.get_voice_settings()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving status: {str(e)}")


@router.get("/modules")
async def get_available_modules():
    """
    Get information about available OSINT modules
    """
    return {
        "success": True,
        "modules": {
            "social": {
                "name": "Social Intelligence",
                "description": "Social media monitoring and analysis",
                "capabilities": ["username_search", "social_footprint", "mention_monitoring"]
            },
            "technical": {
                "name": "Technical Intelligence", 
                "description": "Domain and IP analysis",
                "capabilities": ["domain_analysis", "ip_investigation", "ssl_analysis", "subdomain_enumeration"]
            },
            "breach": {
                "name": "Breach Intelligence",
                "description": "Data breach monitoring",
                "capabilities": ["email_breach_check", "username_exposure", "domain_breaches"]
            },
            "media": {
                "name": "Media Intelligence",
                "description": "Image and media analysis",
                "capabilities": ["reverse_image_search", "metadata_extraction", "similarity_search"]
            }
        },
        "investigation_types": [
            "person",
            "domain", 
            "ip_address",
            "email",
            "username",
            "image",
            "comprehensive"
        ]
    }


@router.post("/voice/test")
async def test_voice_interface():
    """
    Test the German voice interface
    """
    try:
        result = await voice_interface.test_voice()
        
        return {
            "success": True,
            "voice_test": result,
            "settings": voice_interface.get_voice_settings()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice test error: {str(e)}")


@router.post("/voice/speak")
async def speak_text(
    text: str = Field(..., description="Text to speak"),
    context: str = Field(default="general", description="Speaking context"),
    include_accent: bool = Field(default=True, description="Apply German accent")
):
    """
    Convert text to speech with German accent
    """
    try:
        result = await voice_interface.speak(
            text,
            context=context,
            apply_accent=include_accent
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech generation error: {str(e)}")


@router.put("/voice/settings")
async def update_voice_settings(settings: Dict[str, Any]):
    """
    Update voice interface settings
    """
    try:
        success = voice_interface.update_voice_settings(settings)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update voice settings")
        
        return {
            "success": True,
            "message": "Voice settings updated successfully",
            "current_settings": voice_interface.get_voice_settings()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Settings update error: {str(e)}")
