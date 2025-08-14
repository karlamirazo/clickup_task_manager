"""
Esquemas Pydantic para integraciones
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class IntegrationBase(BaseModel):
    """Esquema base para integraciones"""
    name: str = Field(..., min_length=1, max_length=255, description="Nombre de la integración")
    description: Optional[str] = Field(None, description="Descripción de la integración")
    integration_type: str = Field(..., description="Tipo de integración")
    provider: str = Field(..., description="Proveedor de la integración")
    config: Dict[str, Any] = Field(..., description="Configuración de la integración")
    workspace_id: str = Field(..., description="ID del workspace")

class IntegrationCreate(IntegrationBase):
    """Esquema para crear una integración"""
    credentials: Optional[Dict[str, Any]] = Field(None, description="Credenciales de la integración")

class IntegrationUpdate(BaseModel):
    """Esquema para actualizar una integración"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    credentials: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None
    enabled: Optional[bool] = None
    sync_interval: Optional[int] = Field(None, ge=60, description="Intervalo de sincronización en segundos")
    auto_sync: Optional[bool] = None

class IntegrationResponse(IntegrationBase):
    """Esquema de respuesta para integraciones"""
    id: int
    credentials: Optional[Dict[str, Any]] = None
    active: bool
    enabled: bool
    connected: bool
    created_at: datetime
    updated_at: datetime
    last_sync: Optional[datetime] = None
    created_by: str
    sync_count: int
    error_count: int
    last_error: Optional[str] = None
    sync_interval: int
    auto_sync: bool
    
    class Config:
        from_attributes = True

class IntegrationList(BaseModel):
    """Esquema para lista de integraciones"""
    integrations: list[IntegrationResponse]
    total: int
    page: int
    limit: int
    has_more: bool

class IntegrationTest(BaseModel):
    """Esquema para probar una integración"""
    integration_id: int
    test_type: str = Field(..., description="Tipo de prueba a realizar")
