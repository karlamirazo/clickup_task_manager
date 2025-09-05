"""
Pydantic schemas for users
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class UserResponse(BaseModel):
    """Response schema for users"""
    id: str
    username: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_picture: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    workspace_id: Optional[str] = None
    team_id: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class UserList(BaseModel):
    """Schema for user list"""
    users: List[UserResponse]
    total: int
    page: int
    limit: int
    has_more: bool
