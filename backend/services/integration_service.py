
"""
Integration Service for Enhanced CPAS
Handles external service integrations and API management
"""

import asyncio
import json
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.integration import (
    Integration, IntegrationEvent, SyncJob, GoogleWorkspaceConfig,
    EmailRule, CalendarEvent, SlackConfig, SlackChannel, FileProcessor,
    ProcessedFile, IntegrationType, IntegrationStatus, AuthType
)

class IntegrationService:
    """Service for managing external integrations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.integrations = db.integrations
        self.events = db.integration_events
        self.sync_jobs = db.sync_jobs
        self.email_rules = db.email_rules
        self.calendar_events = db.calendar_events
        self.slack_channels = db.slack_channels
        self.file_processors = db.file_processors
        self.processed_files = db.processed_files
        
        # Integration handlers
        self.handlers = {
            IntegrationType.GOOGLE_WORKSPACE: self._handle_google_workspace,
            IntegrationType.SLACK: self._handle_slack,
            IntegrationType.MICROSOFT_365: self._handle_microsoft_365,
            IntegrationType.CUSTOM_API: self._handle_custom_api
        }
    
    async def create_integration(self, integration_data: Dict[str, Any]) -> Integration:
        """Create new integration"""
        integration = Integration(**integration_data)
        
        # Validate integration configuration
        await self._validate_integration_config(integration)
        
        # Test connection
        connection_test = await self._test_integration_connection(integration)
        if not connection_test["success"]:
            integration.status = IntegrationStatus.ERROR
        
        # Store integration
        result = await self.integrations.insert_one(integration.dict())
        integration.id = str(result.inserted_id)
        
        logger.info(f"Created integration: {integration.name} ({integration.type})")
        return integration
    
    async def get_integration(self, integration_id: str) -> Optional[Integration]:
        """Get integration by ID"""
        doc = await self.integrations.find_one({"_id": integration_id})
        return Integration(**doc) if doc else None
    
    async def list_integrations(self, 
                              integration_type: Optional[IntegrationType] = None,
                              status: Optional[IntegrationStatus] = None) -> List[Integration]:
        """List integrations with filtering"""
        query = {}
        if integration_type:
            query["type"] = integration_type
        if status:
            query["status"] = status
        
        cursor = self.integrations.find(query)
        return [Integration(**doc) async for doc in cursor]
    
    async def update_integration(self, integration_id: str, updates: Dict[str, Any]) -> Optional[Integration]:
        """Update integration"""
        updates["updated_at"] = datetime.utcnow()
        
        result = await self.integrations.update_one(
            {"_id": integration_id},
            {"$set": updates}
        )
        
        if result.modified_count > 0:
            return await self.get_integration(integration_id)
        return None
    
    async def delete_integration(self, integration_id: str) -> bool:
        """Delete integration"""
        # Clean up related data
        await self.events.delete_many({"integration_id": integration_id})
        await self.sync_jobs.delete_many({"integration_id": integration_id})
        
        result = await self.integrations.delete_one({"_id": integration_id})
        return result.deleted_count > 0
    
    async def sync_integration(self, integration_id: str, sync_type: str = "incremental") -> SyncJob:
        """Start synchronization job for integration"""
        integration = await self.get_integration(integration_id)
        if not integration:
            raise ValueError(f"Integration {integration_id} not found")
        
        # Create sync job
        sync_job = SyncJob(
            integration_id=integration_id,
            job_type=sync_type,
            started_at=datetime.utcnow()
        )
        
        result = await self.sync_jobs.insert_one(sync_job.dict())
        sync_job.id = str(result.inserted_id)
        
        # Start sync in background
        asyncio.create_task(self._execute_sync_job(integration, sync_job))
        
        logger.info(f"Started sync job: {sync_job.id} for integration: {integration.name}")
        return sync_job
    
    async def _execute_sync_job(self, integration: Integration, sync_job: SyncJob):
        """Execute synchronization job"""
        try:
            sync_job.status = "running"
            await self._update_sync_job(sync_job)
            
            # Get handler for integration type
            handler = self.handlers.get(integration.type)
            if not handler:
                raise ValueError(f"No handler for integration type: {integration.type}")
            
            # Execute sync
            sync_result = await handler(integration, sync_job)
            
            # Update job status
            sync_job.status = "completed"
            sync_job.completed_at = datetime.utcnow()
            sync_job.processed_items = sync_result.get("processed_items", 0)
            sync_job.total_items = sync_result.get("total_items", 0)
            sync_job.progress = 1.0
            
        except Exception as e:
            logger.error(f"Sync job failed: {e}")
            sync_job.status = "failed"
            sync_job.error_message = str(e)
            sync_job.completed_at = datetime.utcnow()
        
        finally:
            await self._update_sync_job(sync_job)
    
    async def _handle_google_workspace(self, integration: Integration, sync_job: SyncJob) -> Dict[str, Any]:
        """Handle Google Workspace integration"""
        config = GoogleWorkspaceConfig(**integration.config)
        
        # Sync Gmail
        gmail_result = await self._sync_gmail(integration, config, sync_job)
        
        # Sync Calendar
        calendar_result = await self._sync_google_calendar(integration, config, sync_job)
        
        # Sync Drive (if enabled)
        drive_result = {}
        if "drive" in integration.permissions:
            drive_result = await self._sync_google_drive(integration, config, sync_job)
        
        return {
            "gmail": gmail_result,
            "calendar": calendar_result,
            "drive": drive_result,
            "processed_items": (
                gmail_result.get("processed", 0) + 
                calendar_result.get("processed", 0) + 
                drive_result.get("processed", 0)
            ),
            "total_items": (
                gmail_result.get("total", 0) + 
                calendar_result.get("total", 0) + 
                drive_result.get("total", 0)
            )
        }
    
    async def _sync_gmail(self, integration: Integration, config: GoogleWorkspaceConfig, sync_job: SyncJob) -> Dict[str, Any]:
        """Sync Gmail emails"""
        # This would integrate with Gmail API
        logger.info(f"Syncing Gmail for integration: {integration.id}")
        
        # Mock implementation
        processed_emails = 0
        total_emails = 100
        
        # Process emails in batches
        batch_size = 10
        for i in range(0, total_emails, batch_size):
            batch_emails = min(batch_size, total_emails - i)
            
            # Process batch
            await self._process_email_batch(integration, batch_emails)
            
            processed_emails += batch_emails
            sync_job.progress = processed_emails / total_emails
            await self._update_sync_job(sync_job)
            
            # Small delay to avoid rate limits
            await asyncio.sleep(0.1)
        
        return {"processed": processed_emails, "total": total_emails}
    
    async def _sync_google_calendar(self, integration: Integration, config: GoogleWorkspaceConfig, sync_job: SyncJob) -> Dict[str, Any]:
        """Sync Google Calendar events"""
        logger.info(f"Syncing Google Calendar for integration: {integration.id}")
        
        # Mock implementation
        processed_events = 0
        total_events = 50
        
        for i in range(total_events):
            # Create mock calendar event
            event = CalendarEvent(
                id=f"event_{i}",
                title=f"Event {i}",
                start_time=datetime.utcnow() + timedelta(days=i),
                end_time=datetime.utcnow() + timedelta(days=i, hours=1),
                calendar_id="primary",
                integration_id=integration.id,
                external_id=f"google_event_{i}"
            )
            
            # Store event
            await self.calendar_events.insert_one(event.dict())
            
            processed_events += 1
            sync_job.progress = processed_events / total_events
            await self._update_sync_job(sync_job)
        
        return {"processed": processed_events, "total": total_events}
    
    async def _handle_slack(self, integration: Integration, sync_job: SyncJob) -> Dict[str, Any]:
        """Handle Slack integration"""
        config = SlackConfig(**integration.config)
        
        # Sync channels
        channels_result = await self._sync_slack_channels(integration, config, sync_job)
        
        # Sync messages
        messages_result = await self._sync_slack_messages(integration, config, sync_job)
        
        return {
            "channels": channels_result,
            "messages": messages_result,
            "processed_items": channels_result.get("processed", 0) + messages_result.get("processed", 0),
            "total_items": channels_result.get("total", 0) + messages_result.get("total", 0)
        }
    
    async def _sync_slack_channels(self, integration: Integration, config: SlackConfig, sync_job: SyncJob) -> Dict[str, Any]:
        """Sync Slack channels"""
        logger.info(f"Syncing Slack channels for integration: {integration.id}")
        
        # Mock implementation
        channels = [
            {"id": "C1234567890", "name": "general", "is_private": False},
            {"id": "C2345678901", "name": "random", "is_private": False},
            {"id": "C3456789012", "name": "dev-team", "is_private": True}
        ]
        
        for channel_data in channels:
            channel = SlackChannel(
                id=channel_data["id"],
                name=channel_data["name"],
                is_private=channel_data["is_private"],
                integration_id=integration.id
            )
            
            # Upsert channel
            await self.slack_channels.update_one(
                {"id": channel.id, "integration_id": integration.id},
                {"$set": channel.dict()},
                upsert=True
            )
        
        return {"processed": len(channels), "total": len(channels)}
    
    async def _handle_microsoft_365(self, integration: Integration, sync_job: SyncJob) -> Dict[str, Any]:
        """Handle Microsoft 365 integration"""
        # Similar to Google Workspace but for Microsoft services
        logger.info(f"Syncing Microsoft 365 for integration: {integration.id}")
        
        return {"processed_items": 0, "total_items": 0}
    
    async def _handle_custom_api(self, integration: Integration, sync_job: SyncJob) -> Dict[str, Any]:
        """Handle custom API integration"""
        logger.info(f"Syncing custom API for integration: {integration.id}")
        
        api_config = integration.config
        endpoint = api_config.get("endpoint", "")
        method = api_config.get("method", "GET")
        headers = api_config.get("headers", {})
        
        # Make API call
        async with aiohttp.ClientSession() as session:
            async with session.request(method, endpoint, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Process API response
                    processed_items = await self._process_api_response(integration, data)
                    
                    return {"processed_items": processed_items, "total_items": processed_items}
                else:
                    raise Exception(f"API call failed with status: {response.status}")
    
    # Email management methods
    async def send_email(self, to: List[str], subject: str, body: str, 
                        cc: List[str] = None, bcc: List[str] = None) -> Dict[str, Any]:
        """Send email through integrated email service"""
        # Find active email integration
        email_integrations = await self.list_integrations(
            integration_type=IntegrationType.GOOGLE_WORKSPACE,
            status=IntegrationStatus.ACTIVE
        )
        
        if not email_integrations:
            raise ValueError("No active email integration found")
        
        integration = email_integrations[0]
        
        # Send email using integration
        result = await self._send_email_via_integration(integration, to, subject, body, cc, bcc)
        
        return result
    
    async def create_calendar_event(self, title: str, description: str, 
                                  start_time: datetime, end_time: datetime,
                                  attendees: List[str] = None) -> Dict[str, Any]:
        """Create calendar event through integrated calendar service"""
        # Find active calendar integration
        calendar_integrations = await self.list_integrations(
            integration_type=IntegrationType.GOOGLE_WORKSPACE,
            status=IntegrationStatus.ACTIVE
        )
        
        if not calendar_integrations:
            raise ValueError("No active calendar integration found")
        
        integration = calendar_integrations[0]
        
        # Create event using integration
        result = await self._create_calendar_event_via_integration(
            integration, title, description, start_time, end_time, attendees
        )
        
        return result
    
    async def process_file(self, file_path: str, processor_type: str = "text_extraction") -> Dict[str, Any]:
        """Process file using configured processors"""
        # Find appropriate file processor
        processors = await self.file_processors.find(
            {"file_types": {"$regex": file_path.split('.')[-1]}, "enabled": True}
        ).to_list(None)
        
        if not processors:
            raise ValueError(f"No processor found for file type: {file_path.split('.')[-1]}")
        
        processor = FileProcessor(**processors[0])
        
        # Process file
        result = await self._process_file_with_processor(file_path, processor)
        
        # Store processed file record
        processed_file = ProcessedFile(
            original_filename=file_path.split('/')[-1],
            file_path=file_path,
            file_type=file_path.split('.')[-1],
            file_size=0,  # Would get actual file size
            extracted_content=result.get("content", ""),
            processor_id=processor.id,
            processed_at=datetime.utcnow()
        )
        
        await self.processed_files.insert_one(processed_file.dict())
        
        return result
    
    async def make_api_call(self, url: str, method: str = "GET", 
                          headers: Dict[str, str] = None, 
                          data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make API call to external service"""
        headers = headers or {}
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=data) as response:
                result = {
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "data": await response.json() if response.content_type == 'application/json' else await response.text()
                }
                
                return result
    
    # Helper methods
    async def _validate_integration_config(self, integration: Integration):
        """Validate integration configuration"""
        if integration.type == IntegrationType.GOOGLE_WORKSPACE:
            required_fields = ["client_id", "client_secret", "redirect_uri"]
            for field in required_fields:
                if field not in integration.config:
                    raise ValueError(f"Missing required field: {field}")
        
        elif integration.type == IntegrationType.SLACK:
            required_fields = ["bot_token", "app_token"]
            for field in required_fields:
                if field not in integration.config:
                    raise ValueError(f"Missing required field: {field}")
    
    async def _test_integration_connection(self, integration: Integration) -> Dict[str, Any]:
        """Test integration connection"""
        try:
            # Mock connection test
            await asyncio.sleep(0.1)  # Simulate API call
            
            return {"success": True, "message": "Connection successful"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _update_sync_job(self, sync_job: SyncJob):
        """Update sync job in database"""
        await self.sync_jobs.update_one(
            {"_id": sync_job.id},
            {"$set": sync_job.dict()}
        )
    
    async def _process_email_batch(self, integration: Integration, batch_size: int):
        """Process batch of emails"""
        # Mock email processing
        await asyncio.sleep(0.1)
    
    async def _process_api_response(self, integration: Integration, data: Dict[str, Any]) -> int:
        """Process API response data"""
        # Mock API response processing
        return len(data) if isinstance(data, list) else 1
    
    async def _send_email_via_integration(self, integration: Integration, to: List[str], 
                                        subject: str, body: str, cc: List[str], bcc: List[str]) -> Dict[str, Any]:
        """Send email via integration"""
        # Mock email sending
        return {"message_id": f"msg_{datetime.utcnow().timestamp()}", "success": True}
    
    async def _create_calendar_event_via_integration(self, integration: Integration, title: str, 
                                                   description: str, start_time: datetime, 
                                                   end_time: datetime, attendees: List[str]) -> Dict[str, Any]:
        """Create calendar event via integration"""
        # Mock event creation
        return {"event_id": f"event_{datetime.utcnow().timestamp()}", "success": True}
    
    async def _process_file_with_processor(self, file_path: str, processor: FileProcessor) -> Dict[str, Any]:
        """Process file with specific processor"""
        # Mock file processing
        return {"content": f"Processed content from {file_path}", "success": True}
