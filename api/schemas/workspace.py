"""
Esquemas Pydantic para espacios de trabajo
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class WorkspaceResponse(BaseModel):
    """Esquema de respuesta para espacios de trabajo"""
    id: int
    clickup_id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    private: bool
    multiple_assignees: bool
    created_at: datetime
    updated_at: datetime
    settings: Optional[Dict[str, Any]] = None
    features: Optional[Dict[str, Any]] = None
    is_synced: bool
    last_sync: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class WorkspaceList(BaseModel):
    """Esquema para lista de espacios de trabajo"""
    workspaces: list[WorkspaceResponse]
    total: int
