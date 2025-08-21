"""
Pydantic schemas for automations
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class AutomationBase(BaseModel):
    """Base schema for automations"""
    name: str = Field(..., min_length=1, max_length=255, description="Automation name")
    description: Optional[str] = Field(None, description="Automation description")
    trigger_type: str = Field(..., description="Trigger type")
    action_type: str = Field(..., description="Action type")
    is_active: bool = True
    config: Dict[str, Any] = Field(default_factory=dict, description="Automation configuration")

class AutomationCreate(AutomationBase):
    """Schema for creating an automation"""
    pass

class AutomationUpdate(BaseModel):
    """Schema for updating an automation"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Automation name")
    description: Optional[str] = Field(None, description="Automation description")
    trigger_type: Optional[str] = None
    action_type: Optional[str] = None
    is_active: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None

class AutomationResponse(AutomationBase):
    """Response schema for automations"""
    id: int
    workspace_id: str
    created_at: datetime
    updated_at: datetime
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    success_count: int = 0
    error_count: int = 0
    
    class Config:
        from_attributes = True

class AutomationList(BaseModel):
    """Schema for automation list"""
    automations: List[AutomationResponse]
    total: int
    page: int
    limit: int
    has_more: bool
