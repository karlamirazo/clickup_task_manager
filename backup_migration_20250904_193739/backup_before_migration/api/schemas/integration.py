"""
Pydantic schemas for integrations
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class IntegrationBase(BaseModel):
    """Base schema for integrations"""
    name: str = Field(..., min_length=1, max_length=255, description="Integration name")
    description: Optional[str] = Field(None, description="Integration description")
    integration_type: str = Field(..., description="Integration type")
    provider: str = Field(..., description="Integration provider")
    config: Dict[str, Any] = Field(..., description="Integration configuration")

class IntegrationCreate(IntegrationBase):
    """Schema for creating an integration"""
    credentials: Optional[Dict[str, Any]] = Field(None, description="Integration credentials")

class IntegrationUpdate(BaseModel):
    """Schema for updating an integration"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Integration name")
    description: Optional[str] = Field(None, description="Integration description")
    integration_type: Optional[str] = None
    provider: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    credentials: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    sync_interval: Optional[int] = Field(None, ge=60, description="Sync interval in seconds")

class IntegrationResponse(IntegrationBase):
    """Response schema for integrations"""
    id: int
    workspace_id: str
    created_at: datetime
    updated_at: datetime
    last_sync: Optional[datetime] = None
    sync_count: int = 0
    error_count: int = 0
    is_active: bool = True
    status: str = "active"
    last_error: Optional[str] = None
    
    class Config:
        from_attributes = True

class IntegrationList(BaseModel):
    """Schema for integration list"""
    integrations: List[IntegrationResponse]
    total: int
    page: int
    limit: int
    has_more: bool

class IntegrationTest(BaseModel):
    """Schema for testing an integration"""
    config: Dict[str, Any] = Field(..., description="Test configuration")
    credentials: Optional[Dict[str, Any]] = Field(None, description="Test credentials")
