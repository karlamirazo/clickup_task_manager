"""
Esquemas Pydantic para validación de datos
"""

from .task import TaskCreate, TaskUpdate, TaskResponse, TaskList
from .workspace import WorkspaceResponse, WorkspaceList
from .user import UserResponse, UserList
from .automation import AutomationCreate, AutomationUpdate, AutomationResponse
from .report import ReportCreate, ReportResponse, ReportList
from .integration import IntegrationCreate, IntegrationUpdate, IntegrationResponse

__all__ = [
    "TaskCreate",
    "TaskUpdate", 
    "TaskResponse",
    "TaskList",
    "WorkspaceResponse",
    "WorkspaceList",
    "UserResponse",
    "UserList",
    "AutomationCreate",
    "AutomationUpdate",
    "AutomationResponse",
    "ReportCreate",
    "ReportResponse",
    "ReportList",
    "IntegrationCreate",
    "IntegrationUpdate",
    "IntegrationResponse"
]
