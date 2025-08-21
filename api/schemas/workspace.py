"""
Pydantic schemas for workspaces
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class WorkspaceResponse(BaseModel):
    """Response schema for workspaces"""
    id: str
    name: str
    description: Optional[str] = None
    owner_id: Optional[str] = None
    owner_name: Optional[str] = None
    members_count: Optional[int] = None
    tasks_count: Optional[int] = None
    lists_count: Optional[int] = None
    folders_count: Optional[int] = None
    is_private: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    settings: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class WorkspaceList(BaseModel):
    """Schema for workspace list"""
    workspaces: List[WorkspaceResponse]
    total: int
    page: int
    limit: int
    has_more: bool
