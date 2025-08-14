"""
Sistema de autenticación para múltiples usuarios
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import hmac
import logging

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from models.user import User

# Configurar logging
auth_logger = logging.getLogger("auth")

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

# Configuración JWT
SECRET_KEY = getattr(settings, 'JWT_SECRET_KEY', secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 horas


class AuthManager:
    """Gestor de autenticación y autorización"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generar hash de contraseña"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crear token JWT"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verificar y decodificar token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError as e:
            auth_logger.warning(f"Token inválido: {e}")
            return None
    
    @staticmethod
    def create_api_key(user_id: int, description: str = "") -> str:
        """Crear API key para usuario"""
        # Generar API key con formato: usuario_timestamp_random
        timestamp = int(datetime.now().timestamp())
        random_part = secrets.token_urlsafe(16)
        api_key = f"ckm_{user_id}_{timestamp}_{random_part}"
        return api_key
    
    @staticmethod
    def verify_api_key(api_key: str, db: Session) -> Optional[User]:
        """Verificar API key y retornar usuario"""
        try:
            # Formato: ckm_user_id_timestamp_random
            parts = api_key.split('_')
            if len(parts) != 4 or parts[0] != 'ckm':
                return None
            
            user_id = int(parts[1])
            user = db.query(User).filter(User.id == user_id).first()
            
            if user and user.api_key == api_key and user.api_key_active:
                return user
            
            return None
            
        except (ValueError, IndexError):
            return None


class RoleManager:
    """Gestor de roles y permisos"""
    
    ROLES = {
        "admin": {
            "name": "Administrador",
            "permissions": [
                "read_all_tasks", "write_all_tasks", "delete_all_tasks",
                "read_users", "write_users", "delete_users",
                "read_settings", "write_settings",
                "read_dashboard", "manage_webhooks",
                "read_notifications", "write_notifications"
            ]
        },
        "manager": {
            "name": "Gerente",
            "permissions": [
                "read_all_tasks", "write_all_tasks",
                "read_users", "write_users",
                "read_dashboard", "read_notifications"
            ]
        },
        "user": {
            "name": "Usuario",
            "permissions": [
                "read_own_tasks", "write_own_tasks",
                "read_assigned_tasks", "write_assigned_tasks",
                "read_notifications"
            ]
        },
        "viewer": {
            "name": "Visualizador",
            "permissions": [
                "read_own_tasks", "read_assigned_tasks",
                "read_notifications"
            ]
        }
    }
    
    @classmethod
    def has_permission(cls, user_role: str, permission: str) -> bool:
        """Verificar si un rol tiene un permiso específico"""
        role_data = cls.ROLES.get(user_role, {})
        permissions = role_data.get("permissions", [])
        return permission in permissions
    
    @classmethod
    def get_role_permissions(cls, role: str) -> list:
        """Obtener permisos de un rol"""
        return cls.ROLES.get(role, {}).get("permissions", [])
    
    @classmethod
    def get_available_roles(cls) -> dict:
        """Obtener todos los roles disponibles"""
        return {k: v["name"] for k, v in cls.ROLES.items()}


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Obtener usuario actual desde token JWT o API key
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    
    # Intentar como JWT token primero
    payload = AuthManager.verify_token(token)
    if payload:
        user_id = payload.get("sub")
        if user_id:
            user = db.query(User).filter(User.id == int(user_id)).first()
            if user and user.is_active:
                return user
    
    # Intentar como API key
    user = AuthManager.verify_api_key(token, db)
    if user:
        return user
    
    return None


def require_auth(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    Requerir autenticación obligatoria
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def require_permission(permission: str):
    """
    Decorator para requerir un permiso específico
    """
    def permission_dependency(current_user: User = Depends(require_auth)) -> User:
        if not RoleManager.has_permission(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso requerido: {permission}",
            )
        return current_user
    
    return permission_dependency


def require_role(required_role: str):
    """
    Decorator para requerir un rol específico
    """
    def role_dependency(current_user: User = Depends(require_auth)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol requerido: {required_role}",
            )
        return current_user
    
    return role_dependency


def optional_auth(
    current_user: Optional[User] = Depends(get_current_user)
) -> Optional[User]:
    """
    Autenticación opcional (no requerida)
    """
    return current_user


# Utilidades de seguridad adicionales
class SecurityUtils:
    """Utilidades de seguridad"""
    
    @staticmethod
    def generate_session_id() -> str:
        """Generar ID de sesión único"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_data(data: str, salt: str = "") -> str:
        """Hash seguro de datos"""
        combined = f"{data}{salt}".encode('utf-8')
        return hashlib.sha256(combined).hexdigest()
    
    @staticmethod
    def verify_signature(data: str, signature: str, secret: str) -> bool:
        """Verificar firma HMAC"""
        expected = hmac.new(
            secret.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitizar entrada de usuario"""
        # Remover caracteres potencialmente peligrosos
        dangerous_chars = ['<', '>', '"', "'", '&', '\n', '\r', '\t']
        sanitized = text
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        return sanitized.strip()
    
    @staticmethod
    def is_safe_redirect_url(url: str, allowed_hosts: list) -> bool:
        """Verificar si URL de redirección es segura"""
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        
        # URL relativa es segura
        if not parsed.netloc:
            return True
        
        # Verificar host permitido
        return parsed.netloc in allowed_hosts


# Configurar logging
logging.basicConfig(level=logging.INFO)
auth_logger.setLevel(logging.INFO)
