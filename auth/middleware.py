"""
Middleware de autenticación y autorización
"""

from typing import Optional, List
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from core.database import get_db
from models.user import User
from auth.auth import get_current_user
from auth.permissions import PermissionManager, Permission

class AuthMiddleware:
    """Middleware para manejar autenticación y autorización"""
    
    # Rutas que no requieren autenticación
    PUBLIC_ROUTES = [
        "/",
        "/api",
        "/health",
        "/debug",
        "/test-simple",
        "/api/debug-tables",
        "/api/init-db",
        "/api/recreate-db",
        "/test-logging",
        "/static/",
        "/styles.css",
        "/script.js"
    ]
    
    # Rutas de autenticación
    AUTH_ROUTES = [
        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/clickup",
        "/api/auth/callback",
        "/api/auth/forgot-password"
    ]
    
    @classmethod
    def is_public_route(cls, path: str) -> bool:
        """Verificar si una ruta es pública"""
        # Verificar rutas exactas
        if path in cls.PUBLIC_ROUTES:
            return True
        
        # Verificar rutas que empiezan con patrones públicos
        for public_route in cls.PUBLIC_ROUTES:
            if public_route.endswith("/") and path.startswith(public_route):
                return True
        
        return False
    
    @classmethod
    def is_auth_route(cls, path: str) -> bool:
        """Verificar si una ruta es de autenticación"""
        return path in cls.AUTH_ROUTES
    
    @classmethod
    def requires_auth(cls, path: str) -> bool:
        """Verificar si una ruta requiere autenticación"""
        return not (cls.is_public_route(path) or cls.is_auth_route(path))

async def auth_middleware(request: Request, call_next):
    """Middleware de autenticación para FastAPI"""
    
    # Obtener la ruta
    path = request.url.path
    
    # Si es una ruta pública, continuar sin autenticación
    if AuthMiddleware.is_public_route(path):
        return await call_next(request)
    
    # Si es una ruta de autenticación, continuar sin verificación adicional
    if AuthMiddleware.is_auth_route(path):
        return await call_next(request)
    
    # Para rutas que requieren autenticación
    if AuthMiddleware.requires_auth(path):
        try:
            # Obtener usuario actual
            db = next(get_db())
            try:
                user = get_current_user(request, db)
                
                if not user:
                    # Si es una petición de API, devolver error 401
                    if path.startswith("/api/"):
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token de acceso requerido"
                        )
                    # Si es una página web, redirigir al login
                    else:
                        return RedirectResponse(url="/api/auth/login")
                
                # Agregar usuario a la request para uso posterior
                request.state.current_user = user
                
            finally:
                db.close()
                
        except HTTPException:
            raise
        except Exception as e:
            # Si es una petición de API, devolver error 401
            if path.startswith("/api/"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Error de autenticación"
                )
            # Si es una página web, redirigir al login
            else:
                return RedirectResponse(url="/api/auth/login")
    
    return await call_next(request)

class PermissionMiddleware:
    """Middleware para verificar permisos específicos"""
    
    @staticmethod
    def require_permission(permission: Permission):
        """Decorator para requerir un permiso específico"""
        def permission_checker(request: Request, call_next):
            # Obtener usuario de la request
            user = getattr(request.state, 'current_user', None)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            # Verificar permiso
            if not PermissionManager.has_permission(user.role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permiso requerido: {permission.value}"
                )
            
            return call_next(request)
        
        return permission_checker
    
    @staticmethod
    def require_any_permission(permissions: List[Permission]):
        """Decorator para requerir cualquiera de los permisos especificados"""
        def permission_checker(request: Request, call_next):
            # Obtener usuario de la request
            user = getattr(request.state, 'current_user', None)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            # Verificar si tiene alguno de los permisos
            if not PermissionManager.has_any_permission(user.role, permissions):
                permission_names = [p.value for p in permissions]
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Se requiere uno de los siguientes permisos: {', '.join(permission_names)}"
                )
            
            return call_next(request)
        
        return permission_checker
    
    @staticmethod
    def require_all_permissions(permissions: List[Permission]):
        """Decorator para requerir todos los permisos especificados"""
        def permission_checker(request: Request, call_next):
            # Obtener usuario de la request
            user = getattr(request.state, 'current_user', None)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            # Verificar si tiene todos los permisos
            if not PermissionManager.has_all_permissions(user.role, permissions):
                permission_names = [p.value for p in permissions]
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Se requieren todos los siguientes permisos: {', '.join(permission_names)}"
                )
            
            return call_next(request)
        
        return permission_checker

class RoleMiddleware:
    """Middleware para verificar roles específicos"""
    
    @staticmethod
    def require_role(required_role: str):
        """Decorator para requerir un rol específico"""
        def role_checker(request: Request, call_next):
            # Obtener usuario de la request
            user = getattr(request.state, 'current_user', None)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            # Verificar rol
            if user.role != required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Rol requerido: {required_role}"
                )
            
            return call_next(request)
        
        return role_checker
    
    @staticmethod
    def require_any_role(required_roles: List[str]):
        """Decorator para requerir cualquiera de los roles especificados"""
        def role_checker(request: Request, call_next):
            # Obtener usuario de la request
            user = getattr(request.state, 'current_user', None)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            # Verificar si tiene alguno de los roles
            if user.role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Se requiere uno de los siguientes roles: {', '.join(required_roles)}"
                )
            
            return call_next(request)
        
        return role_checker

class ClickUpAccessMiddleware:
    """Middleware para verificar acceso a ClickUp"""
    
    @staticmethod
    def require_clickup_access():
        """Decorator para requerir acceso a ClickUp"""
        def access_checker(request: Request, call_next):
            # Obtener usuario de la request
            user = getattr(request.state, 'current_user', None)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            # Verificar si tiene token de ClickUp
            if not user.clickup_access_token:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Acceso a ClickUp requerido. Por favor, auténticate con ClickUp OAuth."
                )
            
            # Verificar si el token no ha expirado
            if user.clickup_token_expires_at and user.clickup_token_expires_at < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Token de ClickUp expirado. Por favor, reauténticate."
                )
            
            return call_next(request)
        
        return access_checker

# Utilidades para decoradores
def require_auth_endpoint(func):
    """Decorator para endpoints que requieren autenticación"""
    async def wrapper(*args, **kwargs):
        # La autenticación se maneja en el middleware
        return await func(*args, **kwargs)
    return wrapper

def require_permission_endpoint(permission: Permission):
    """Decorator para endpoints que requieren un permiso específico"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # La verificación de permisos se maneja en el middleware
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role_endpoint(role: str):
    """Decorator para endpoints que requieren un rol específico"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # La verificación de roles se maneja en el middleware
            return await func(*args, **kwargs)
        return wrapper
    return decorator
