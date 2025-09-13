"""
Esquemas de datos para autenticación
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field, validator

class LoginRequest(BaseModel):
    """Solicitud de inicio de sesión"""
    email: EmailStr
    password: str = Field(..., min_length=6)

class RegisterRequest(BaseModel):
    """Solicitud de registro"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    
    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('El nombre de usuario solo puede contener letras, números, guiones y guiones bajos')
        return v.lower()

class PasswordResetRequest(BaseModel):
    """Solicitud de restablecimiento de contraseña"""
    email: EmailStr

class ChangePasswordRequest(BaseModel):
    """Solicitud de cambio de contraseña"""
    current_password: str
    new_password: str = Field(..., min_length=6)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v

class UserResponse(BaseModel):
    """Respuesta con información del usuario"""
    id: int
    clickup_id: Optional[str]
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    avatar: Optional[str]
    title: Optional[str]
    role: str
    clickup_role: Optional[str]
    active: bool
    timezone: Optional[str]
    language: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    preferences: Optional[Dict[str, Any]]
    workspaces: Optional[Dict[str, Any]]
    is_synced: bool
    last_sync: Optional[datetime]
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Respuesta con token de acceso"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    expires_in: int
    
class OAuthStateRequest(BaseModel):
    """Solicitud de estado OAuth"""
    state: str

class RoleInfo(BaseModel):
    """Información de rol"""
    name: str
    permissions: List[str]

class PermissionResponse(BaseModel):
    """Respuesta con permisos del usuario"""
    role: str
    permissions: List[str]
    can_read_all_tasks: bool
    can_write_all_tasks: bool
    can_manage_users: bool
    can_read_settings: bool
    can_write_settings: bool
    can_manage_webhooks: bool

class ProfileUpdateRequest(BaseModel):
    """Solicitud de actualización de perfil"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    timezone: Optional[str] = Field(None, max_length=100)
    language: Optional[str] = Field(None, max_length=10)
    preferences: Optional[Dict[str, Any]] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValueError('El teléfono debe contener solo números y caracteres de formato')
        return v

class ClickUpUserInfo(BaseModel):
    """Información del usuario desde ClickUp"""
    id: str
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    avatar: Optional[str]
    title: Optional[str]
    active: bool
    timezone: Optional[str]
    language: Optional[str]
    preferences: Optional[Dict[str, Any]]

class OAuthTokenData(BaseModel):
    """Datos del token OAuth"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None

class AuthStatusResponse(BaseModel):
    """Estado de autenticación"""
    is_authenticated: bool
    user: Optional[UserResponse] = None
    permissions: Optional[PermissionResponse] = None

class WorkspaceAccess(BaseModel):
    """Acceso a workspace de ClickUp"""
    workspace_id: str
    workspace_name: str
    role: str
    permissions: List[str]
    can_read_all_tasks: bool
    can_write_all_tasks: bool

class UserWorkspaceInfo(BaseModel):
    """Información de workspaces del usuario"""
    user: UserResponse
    workspaces: List[WorkspaceAccess]
    default_workspace: Optional[str]

class SessionInfo(BaseModel):
    """Información de sesión"""
    session_id: str
    user_id: int
    created_at: datetime
    last_activity: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    is_active: bool

class SecurityEvent(BaseModel):
    """Evento de seguridad"""
    event_type: str  # login, logout, failed_login, password_change, etc.
    user_id: Optional[int]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

class APIKeyRequest(BaseModel):
    """Solicitud de API key"""
    description: str = Field(..., max_length=255)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)

class APIKeyResponse(BaseModel):
    """Respuesta con API key"""
    api_key: str
    description: str
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool

class UserStats(BaseModel):
    """Estadísticas del usuario"""
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    tasks_this_week: int
    last_activity: Optional[datetime]
    login_count: int
    days_since_registration: int
