
"""
Integration Router for Enhanced CPAS
Handles external service integrations and API management
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from datetime import datetime

from models.integration import (
    Integration, IntegrationEvent, SyncJob, CreateIntegrationRequest,
    UpdateIntegrationRequest, IntegrationListResponse, SyncJobResponse,
    IntegrationType, IntegrationStatus, AuthType
)
from services.integration_service import IntegrationService
from database import get_database

router = APIRouter()

async def get_integration_service():
    """Dependency to get integration service"""
    db = await get_database()
    return IntegrationService(db)

@router.post("/integrations", response_model=Integration)
async def create_integration(
    request: CreateIntegrationRequest,
    service: IntegrationService = Depends(get_integration_service)
):
    """Create a new integration"""
    try:
        integration = await service.create_integration(request.dict())
        return integration
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/integrations/{integration_id}", response_model=Integration)
async def get_integration(
    integration_id: str,
    service: IntegrationService = Depends(get_integration_service)
):
    """Get integration by ID"""
    integration = await service.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration

@router.get("/integrations", response_model=IntegrationListResponse)
async def list_integrations(
    integration_type: Optional[IntegrationType] = Query(None),
    status: Optional[IntegrationStatus] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: IntegrationService = Depends(get_integration_service)
):
    """List integrations with filtering"""
    integrations = await service.list_integrations(
        integration_type=integration_type,
        status=status
    )
    
    # Simple pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated_integrations = integrations[start:end]
    
    return IntegrationListResponse(
        integrations=paginated_integrations,
        total=len(integrations),
        page=page,
        page_size=page_size
    )

@router.put("/integrations/{integration_id}", response_model=Integration)
async def update_integration(
    integration_id: str,
    request: UpdateIntegrationRequest,
    service: IntegrationService = Depends(get_integration_service)
):
    """Update integration"""
    # Filter out None values
    updates = {k: v for k, v in request.dict().items() if v is not None}
    
    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")
    
    integration = await service.update_integration(integration_id, updates)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    return integration

@router.delete("/integrations/{integration_id}")
async def delete_integration(
    integration_id: str,
    service: IntegrationService = Depends(get_integration_service)
):
    """Delete integration"""
    success = await service.delete_integration(integration_id)
    if not success:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    return {"message": "Integration deleted successfully"}

@router.post("/integrations/{integration_id}/sync", response_model=SyncJobResponse)
async def sync_integration(
    integration_id: str,
    sync_type: str = Query("incremental", regex="^(full|incremental)$"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    service: IntegrationService = Depends(get_integration_service)
):
    """Start synchronization for integration"""
    try:
        sync_job = await service.sync_integration(integration_id, sync_type)
        integration = await service.get_integration(integration_id)
        
        return SyncJobResponse(
            job=sync_job,
            integration=integration
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/integrations/{integration_id}/sync-jobs")
async def get_sync_jobs(
    integration_id: str,
    status: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    service: IntegrationService = Depends(get_integration_service)
):
    """Get sync jobs for integration"""
    # This would be implemented in the service
    return {"sync_jobs": [], "total": 0}

@router.get("/sync-jobs/{job_id}", response_model=SyncJob)
async def get_sync_job(
    job_id: str,
    service: IntegrationService = Depends(get_integration_service)
):
    """Get specific sync job"""
    # This would be implemented in the service
    raise HTTPException(status_code=501, detail="Not implemented yet")

@router.post("/integrations/{integration_id}/test")
async def test_integration(
    integration_id: str,
    service: IntegrationService = Depends(get_integration_service)
):
    """Test integration connection"""
    integration = await service.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    try:
        result = await service._test_integration_connection(integration)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Google Workspace specific endpoints
@router.post("/integrations/google-workspace/oauth")
async def google_workspace_oauth(
    code: str,
    state: str,
    service: IntegrationService = Depends(get_integration_service)
):
    """Handle Google Workspace OAuth callback"""
    # This would handle OAuth flow
    return {"message": "OAuth flow completed", "integration_id": "temp_id"}

@router.get("/integrations/{integration_id}/gmail/emails")
async def get_gmail_emails(
    integration_id: str,
    query: Optional[str] = Query(None),
    max_results: int = Query(10, ge=1, le=100),
    service: IntegrationService = Depends(get_integration_service)
):
    """Get Gmail emails through integration"""
    # This would be implemented in the service
    return {"emails": [], "total": 0}

@router.post("/integrations/{integration_id}/gmail/send")
async def send_gmail_email(
    integration_id: str,
    email_data: Dict[str, Any],
    service: IntegrationService = Depends(get_integration_service)
):
    """Send email through Gmail integration"""
    try:
        result = await service.send_email(
            to=email_data.get("to", []),
            subject=email_data.get("subject", ""),
            body=email_data.get("body", ""),
            cc=email_data.get("cc", []),
            bcc=email_data.get("bcc", [])
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/integrations/{integration_id}/calendar/events")
async def get_calendar_events(
    integration_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    service: IntegrationService = Depends(get_integration_service)
):
    """Get calendar events through integration"""
    # This would be implemented in the service
    return {"events": [], "total": 0}

@router.post("/integrations/{integration_id}/calendar/events")
async def create_calendar_event(
    integration_id: str,
    event_data: Dict[str, Any],
    service: IntegrationService = Depends(get_integration_service)
):
    """Create calendar event through integration"""
    try:
        result = await service.create_calendar_event(
            title=event_data.get("title", ""),
            description=event_data.get("description", ""),
            start_time=datetime.fromisoformat(event_data.get("start_time")),
            end_time=datetime.fromisoformat(event_data.get("end_time")),
            attendees=event_data.get("attendees", [])
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Slack specific endpoints
@router.post("/integrations/slack/oauth")
async def slack_oauth(
    code: str,
    state: str,
    service: IntegrationService = Depends(get_integration_service)
):
    """Handle Slack OAuth callback"""
    # This would handle OAuth flow
    return {"message": "OAuth flow completed", "integration_id": "temp_id"}

@router.get("/integrations/{integration_id}/slack/channels")
async def get_slack_channels(
    integration_id: str,
    service: IntegrationService = Depends(get_integration_service)
):
    """Get Slack channels through integration"""
    # This would be implemented in the service
    return {"channels": []}

@router.post("/integrations/{integration_id}/slack/message")
async def send_slack_message(
    integration_id: str,
    message_data: Dict[str, Any],
    service: IntegrationService = Depends(get_integration_service)
):
    """Send Slack message through integration"""
    # This would be implemented in the service
    return {"message": "Message sent", "timestamp": datetime.utcnow()}

# File processing endpoints
@router.post("/integrations/files/process")
async def process_file(
    file_path: str,
    processor_type: str = Query("text_extraction"),
    service: IntegrationService = Depends(get_integration_service)
):
    """Process file through integration"""
    try:
        result = await service.process_file(file_path, processor_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/integrations/files/processors")
async def get_file_processors(
    service: IntegrationService = Depends(get_integration_service)
):
    """Get available file processors"""
    # This would be implemented in the service
    return {
        "processors": [
            {
                "id": "text_extraction",
                "name": "Text Extraction",
                "supported_types": ["pdf", "docx", "txt"],
                "description": "Extract text content from documents"
            },
            {
                "id": "image_analysis",
                "name": "Image Analysis",
                "supported_types": ["jpg", "png", "gif"],
                "description": "Analyze and extract information from images"
            },
            {
                "id": "spreadsheet_parser",
                "name": "Spreadsheet Parser",
                "supported_types": ["xlsx", "csv"],
                "description": "Parse and extract data from spreadsheets"
            }
        ]
    }

@router.get("/integrations/files/processed")
async def get_processed_files(
    file_type: Optional[str] = Query(None),
    processor_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    service: IntegrationService = Depends(get_integration_service)
):
    """Get processed files"""
    # This would be implemented in the service
    return {"files": [], "total": 0}

# Custom API endpoints
@router.post("/integrations/{integration_id}/api-call")
async def make_api_call(
    integration_id: str,
    api_request: Dict[str, Any],
    service: IntegrationService = Depends(get_integration_service)
):
    """Make API call through integration"""
    try:
        result = await service.make_api_call(
            url=api_request.get("url", ""),
            method=api_request.get("method", "GET"),
            headers=api_request.get("headers", {}),
            data=api_request.get("data", {})
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Integration analytics
@router.get("/integrations/analytics/summary")
async def get_integration_analytics(
    time_period: str = Query("week", regex="^(day|week|month|year)$"),
    service: IntegrationService = Depends(get_integration_service)
):
    """Get integration analytics summary"""
    # This would be implemented in the service
    return {
        "total_integrations": 0,
        "active_integrations": 0,
        "sync_jobs_completed": 0,
        "sync_success_rate": 0.0,
        "data_synced": 0,
        "most_used_integrations": [],
        "error_trends": []
    }

@router.get("/integrations/{integration_id}/analytics")
async def get_integration_performance(
    integration_id: str,
    service: IntegrationService = Depends(get_integration_service)
):
    """Get specific integration performance analytics"""
    # This would be implemented in the service
    return {
        "integration_id": integration_id,
        "sync_count": 0,
        "success_rate": 0.0,
        "avg_sync_time": 0.0,
        "data_volume": 0,
        "error_frequency": 0,
        "performance_over_time": []
    }

# Integration events and webhooks
@router.get("/integrations/{integration_id}/events")
async def get_integration_events(
    integration_id: str,
    event_type: Optional[str] = Query(None),
    processed: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    service: IntegrationService = Depends(get_integration_service)
):
    """Get integration events"""
    # This would be implemented in the service
    return {"events": [], "total": 0}

@router.post("/integrations/{integration_id}/webhook")
async def handle_webhook(
    integration_id: str,
    webhook_data: Dict[str, Any],
    service: IntegrationService = Depends(get_integration_service)
):
    """Handle webhook from integrated service"""
    # This would be implemented in the service
    return {"message": "Webhook processed", "event_id": "temp_id"}

# Integration templates and marketplace
@router.get("/integration-templates")
async def get_integration_templates(
    category: Optional[str] = Query(None),
    service: IntegrationService = Depends(get_integration_service)
):
    """Get integration templates"""
    templates = [
        {
            "id": "google_workspace_basic",
            "name": "Google Workspace Basic",
            "description": "Basic Google Workspace integration with Gmail and Calendar",
            "type": IntegrationType.GOOGLE_WORKSPACE,
            "category": "productivity",
            "permissions": ["gmail.readonly", "calendar.readonly"],
            "config_template": {
                "client_id": "",
                "client_secret": "",
                "redirect_uri": "http://localhost:8000/integrations/google-workspace/oauth"
            }
        },
        {
            "id": "slack_team",
            "name": "Slack Team Integration",
            "description": "Connect with Slack workspace for team communication",
            "type": IntegrationType.SLACK,
            "category": "communication",
            "permissions": ["channels:read", "chat:write"],
            "config_template": {
                "bot_token": "",
                "app_token": "",
                "signing_secret": ""
            }
        }
    ]
    
    if category:
        templates = [t for t in templates if t["category"] == category]
    
    return {"templates": templates}

@router.post("/integration-templates/{template_id}/instantiate")
async def instantiate_integration_template(
    template_id: str,
    config: Dict[str, Any],
    service: IntegrationService = Depends(get_integration_service)
):
    """Create integration from template"""
    # This would be implemented in the service
    return {"message": "Integration created from template", "integration_id": "temp_id"}

# Integration health and monitoring
@router.get("/integrations/{integration_id}/health")
async def check_integration_health(
    integration_id: str,
    service: IntegrationService = Depends(get_integration_service)
):
    """Check integration health status"""
    integration = await service.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # This would be implemented in the service
    return {
        "status": "healthy",
        "last_sync": None,
        "connection_status": "connected",
        "error_count": 0,
        "performance_score": 0.95
    }

@router.get("/integrations/health/summary")
async def get_integrations_health_summary(
    service: IntegrationService = Depends(get_integration_service)
):
    """Get overall integrations health summary"""
    # This would be implemented in the service
    return {
        "total_integrations": 0,
        "healthy_integrations": 0,
        "unhealthy_integrations": 0,
        "integrations_with_errors": 0,
        "overall_health_score": 0.0
    }
