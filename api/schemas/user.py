"""
Esquemas Pydantic para usuarios
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class UserResponse(BaseModel):
    """Esquema de respuesta para usuarios"""
    id: int
    clickup_id: str
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None
    role: Optional[str] = None
    title: Optional[str] = None
    active: bool
    timezone: Optional[str] = None
    language: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    preferences: Optional[Dict[str, Any]] = None
    workspaces: Optional[Dict[str, Any]] = None
    is_synced: bool
    last_sync: Optional[datetime] = None
    full_name: str
    
    class Config:
        from_attributes = True

class UserList(BaseModel):
    """Esquema para lista de usuarios"""
    users: list[UserResponse]
    total: int
