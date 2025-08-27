"""
Pydantic schemas for tasks
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

class TaskBase(BaseModel):
    """Base schema for tasks"""
    name: str = Field(..., min_length=1, max_length=500, description="Nombre de la tarea")
    description: Optional[str] = Field(None, description="Task description")
    status: Optional[str] = Field(None, description="Estado de la tarea")
    priority: Optional[int] = Field(None, description="Prioridad (1=Urgente, 2=Alta, 3=Normal, 4=Baja)")
    due_date: Optional[Union[datetime, int, str]] = Field(None, description="Fecha limite (datetime, timestamp en milisegundos, o string)")
    start_date: Optional[datetime] = Field(None, description="Fecha de inicio")
    assignee_id: str = Field(..., description="ID del usuario asignado (obligatorio)")
    tags: Optional[List[str]] = Field(None, description="Lista de etiquetas")
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="Campos personalizados (email, Celular)")

class TaskCreate(TaskBase):
    """Schema for creating a task"""
    list_id: str = Field(..., description="ID de la lista donde crear la tarea")
    workspace_id: str = Field(..., description="ID del workspace")
    
    # Validar y convertir due_date si es timestamp o string
    def __init__(self, **data):
        super().__init__(**data)
        # Mantener due_date como timestamp (ms) si viene como int/str para evitar problemas de zona horaria.
        # If it comes as a numeric string, convert to int ms; if it comes as datetime, it will be handled in the route.
        if self.due_date:
            if isinstance(self.due_date, str):
                try:
                    self.due_date = int(self.due_date)
                except (ValueError, TypeError):
                    # leave the value as is; it will be ignored if not valid
                    pass
        
        # Los campos personalizados son opcionales ahora
        # El email se obtiene automáticamente del usuario asignado

class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = Field(None)
    due_date: Optional[Union[datetime, int, str]] = None
    start_date: Optional[datetime] = None
    assignee_id: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    
    # Validar y convertir due_date si es timestamp o string
    def __init__(self, **data):
        super().__init__(**data)
        # Mantener due_date como timestamp (ms) si viene como int/str para evitar problemas de zona horaria.
        if self.due_date:
            if isinstance(self.due_date, str):
                try:
                    self.due_date = int(self.due_date)
                except (ValueError, TypeError):
                    pass
        
        # Los campos personalizados son opcionales ahora

class TaskResponse(BaseModel):
    """Response schema for tasks"""
    id: Optional[int] = None
    clickup_id: str
    name: str
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    due_date: Optional[Union[datetime, int, str]] = None
    start_date: Optional[datetime] = None
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    list_name: Optional[str] = None
    workspace_name: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    workspace_id: str
    list_id: str
    creator_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    comments: Optional[List[Dict[str, Any]]] = None
    is_synced: bool
    last_sync: Optional[datetime] = None
    
    class Config:
        from_attributes = True
    


class TaskList(BaseModel):
    """Schema for task list"""
    tasks: List[TaskResponse]
    total: int
    page: int
    limit: int
    has_more: bool

class TaskFilter(BaseModel):
    """Schema for task filters"""
    status: Optional[str] = None
    assignee_id: Optional[str] = None
    priority: Optional[int] = None
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = None
    include_closed: bool = False
    page: int = 0
    limit: int = 50

class TaskBulkUpdate(BaseModel):
    """Schema for bulk task updates"""
    task_ids: List[str] = Field(..., min_items=1, description="IDs de las tareas a actualizar")
    updates: TaskUpdate = Field(..., description="Actualizaciones a aplicar")

class TaskBulkDelete(BaseModel):
    """Schema for bulk task deletion"""
    task_ids: List[str] = Field(..., min_items=1, description="IDs de las tareas a eliminar")
