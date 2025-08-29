
"""
Integration Models for Enhanced CPAS
Defines data structures for external service integrations
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from bson import ObjectId

class IntegrationType(str, Enum):
    GOOGLE_WORKSPACE = "google_workspace"
    SLACK = "slack"
    MICROSOFT_365 = "microsoft_365"
    NOTION = "notion"
    TRELLO = "trello"
    GITHUB = "github"
    JIRA = "jira"
    DROPBOX = "dropbox"
    ZOOM = "zoom"
    CUSTOM_API = "custom_api"

class IntegrationStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING_AUTH = "pending_auth"
    EXPIRED = "expired"

class AuthType(str, Enum):
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    CUSTOM = "custom"

class Integration(BaseModel):
    """External service integration configuration"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    name: str
    type: IntegrationType
    status: IntegrationStatus = IntegrationStatus.PENDING_AUTH
    auth_type: AuthType
    credentials: Dict[str, Any] = Field(default_factory=dict)  # Encrypted storage
    config: Dict[str, Any] = Field(default_factory=dict)
    permissions: List[str] = Field(default_factory=list)
    last_sync: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True

class IntegrationEvent(BaseModel):
    """Events from integrated services"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    integration_id: str
    event_type: str
    event_data: Dict[str, Any]
    processed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None

class SyncJob(BaseModel):
    """Background synchronization jobs"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    integration_id: str
    job_type: str  # full_sync, incremental_sync, webhook_process
    status: str = "pending"  # pending, running, completed, failed
    progress: float = 0.0
    total_items: int = 0
    processed_items: int = 0
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Google Workspace specific models
class GoogleWorkspaceConfig(BaseModel):
    """Google Workspace integration configuration"""
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: List[str] = Field(default_factory=list)
    domain: Optional[str] = None
    service_account_key: Optional[Dict[str, Any]] = None

class EmailRule(BaseModel):
    """Email processing rules"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    name: str
    conditions: Dict[str, Any]  # sender, subject, body patterns
    actions: List[Dict[str, Any]]  # auto-reply, categorize, create_task
    enabled: bool = True
    priority: int = 5
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CalendarEvent(BaseModel):
    """Calendar event representation"""
    id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    attendees: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    calendar_id: str
    integration_id: str
    external_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Slack specific models
class SlackConfig(BaseModel):
    """Slack integration configuration"""
    bot_token: str
    app_token: str
    signing_secret: str
    workspace_id: str
    team_name: str

class SlackChannel(BaseModel):
    """Slack channel representation"""
    id: str
    name: str
    is_private: bool
    members: List[str] = Field(default_factory=list)
    integration_id: str
    last_message_ts: Optional[str] = None

# File processing models
class FileProcessor(BaseModel):
    """File processing configuration"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    name: str
    file_types: List[str]  # pdf, docx, xlsx, etc.
    processing_rules: Dict[str, Any]
    output_format: str = "text"
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProcessedFile(BaseModel):
    """Processed file record"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    original_filename: str
    file_path: str
    file_type: str
    file_size: int
    processing_status: str = "pending"
    extracted_content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processor_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None

# API Request/Response models
class CreateIntegrationRequest(BaseModel):
    name: str
    type: IntegrationType
    auth_type: AuthType
    config: Dict[str, Any] = Field(default_factory=dict)
    permissions: List[str] = Field(default_factory=list)

class UpdateIntegrationRequest(BaseModel):
    name: Optional[str] = None
    status: Optional[IntegrationStatus] = None
    config: Optional[Dict[str, Any]] = None
    permissions: Optional[List[str]] = None

class IntegrationListResponse(BaseModel):
    integrations: List[Integration]
    total: int
    page: int
    page_size: int

class SyncJobResponse(BaseModel):
    job: SyncJob
    integration: Integration
