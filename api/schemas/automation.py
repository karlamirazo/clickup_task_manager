"""
Esquemas Pydantic para automatizaciones
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class AutomationBase(BaseModel):
    """Esquema base para automatizaciones"""
    name: str = Field(..., min_length=1, max_length=255, description="Nombre de la automatización")
    description: Optional[str] = Field(None, description="Descripción de la automatización")
    trigger_type: str = Field(..., description="Tipo de trigger")
    trigger_conditions: Optional[Dict[str, Any]] = Field(None, description="Condiciones del trigger")
    actions: List[Dict[str, Any]] = Field(..., min_items=1, description="Acciones a ejecutar")
    workspace_id: str = Field(..., description="ID del workspace")

class AutomationCreate(AutomationBase):
    """Esquema para crear una automatización"""
    pass

class AutomationUpdate(BaseModel):
    """Esquema para actualizar una automatización"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    trigger_type: Optional[str] = None
    trigger_conditions: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = Field(None, min_items=1)
    active: Optional[bool] = None
    enabled: Optional[bool] = None

class AutomationResponse(AutomationBase):
    """Esquema de respuesta para automatizaciones"""
    id: int
    active: bool
    enabled: bool
    created_at: datetime
    updated_at: datetime
    last_executed: Optional[datetime] = None
    task_id: Optional[int] = None
    execution_count: int
    error_count: int
    last_error: Optional[str] = None
    
    class Config:
        from_attributes = True

class AutomationList(BaseModel):
    """Esquema para lista de automatizaciones"""
    automations: list[AutomationResponse]
    total: int
    page: int
    limit: int
    has_more: bool
