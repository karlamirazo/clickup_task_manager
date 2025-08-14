"""
Esquemas Pydantic para reportes
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ReportBase(BaseModel):
    """Esquema base para reportes"""
    name: str = Field(..., min_length=1, max_length=255, description="Nombre del reporte")
    description: Optional[str] = Field(None, description="Descripción del reporte")
    report_type: str = Field(..., description="Tipo de reporte")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parámetros del reporte")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtros aplicados")
    date_range: Optional[Dict[str, Any]] = Field(None, description="Rango de fechas")
    workspace_id: Optional[str] = Field(None, description="ID del workspace")

class ReportCreate(ReportBase):
    """Esquema para crear un reporte"""
    pass

class ReportResponse(ReportBase):
    """Esquema de respuesta para reportes"""
    id: int
    data: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None
    status: str
    generated: bool
    created_at: datetime
    updated_at: datetime
    generated_at: Optional[datetime] = None
    created_by: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    
    class Config:
        from_attributes = True

class ReportList(BaseModel):
    """Esquema para lista de reportes"""
    reports: list[ReportResponse]
    total: int
    page: int
    limit: int
    has_more: bool

class ReportFilter(BaseModel):
    """Esquema para filtros de reportes"""
    report_type: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = 0
    limit: int = 20
