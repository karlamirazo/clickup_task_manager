"""
Pydantic schemas for reports
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ReportBase(BaseModel):
    """Base schema for reports"""
    name: str = Field(..., min_length=1, max_length=255, description="Report name")
    description: Optional[str] = Field(None, description="Report description")
    report_type: str = Field(..., description="Report type")
    config: Dict[str, Any] = Field(default_factory=dict, description="Report configuration")
    schedule: Optional[str] = Field(None, description="Report schedule (cron expression)")

class ReportCreate(ReportBase):
    """Schema for creating a report"""
    pass

class ReportUpdate(BaseModel):
    """Response schema for reports"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Report name")
    description: Optional[str] = Field(None, description="Report description")
    report_type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    schedule: Optional[str] = None
    is_active: Optional[bool] = None

class ReportResponse(ReportBase):
    """Response schema for reports"""
    id: int
    workspace_id: str
    created_at: datetime
    updated_at: datetime
    last_generated: Optional[datetime] = None
    generation_count: int = 0
    is_active: bool = True
    
    class Config:
        from_attributes = True

class ReportList(BaseModel):
    """Schema for report list"""
    reports: List[ReportResponse]
    total: int
    page: int
    limit: int
    has_more: bool

class ReportFilter(BaseModel):
    """Schema for report filters"""
    report_type: Optional[str] = None
    is_active: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    page: int = 0
    limit: int = 50
