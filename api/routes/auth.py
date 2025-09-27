"""
Rutas de autenticación y OAuth
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session

from core.database import get_db
from models.user import User
from auth.auth import AuthManager, RoleManager, require_auth, get_current_user
from auth.oauth import clickup_oauth, oauth_state_manager, authenticate_with_clickup
from api.schemas.auth import (
    LoginRequest, RegisterRequest, TokenResponse, 
    UserResponse, PasswordResetRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["autenticación"])

@router.get("/login", response_class=HTMLResponse)
async def login_page():
    """Página de login"""
    with open("static/auth.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Iniciar sesión con email y contraseña"""
    try:
        # Buscar usuario por email
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cuenta desactivada"
            )
        
        # Verificar contraseña
        if not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Debe autenticarse con ClickUp OAuth"
            )
        
        if not AuthManager.verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        # Actualizar último login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Generar token JWT
        access_token = AuthManager.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(**user.to_dict()),
            expires_in=1440  # 24 horas
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/register", response_model=TokenResponse)
async def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Registrar nuevo usuario"""
    try:
        # Verificar si el email ya existe
        existing_user = db.query(User).filter(User.email == register_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Verificar si el username ya existe
        existing_username = db.query(User).filter(User.username == register_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )
        
        # Crear nuevo usuario
        user = User(
            email=register_data.email,
            username=register_data.username,
            password_hash=AuthManager.get_password_hash(register_data.password),
            first_name=register_data.first_name or "",
            last_name=register_data.last_name or "",
            role="user",
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Generar token JWT
        access_token = AuthManager.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        logger.info(f"Usuario registrado: {user.username} ({user.email})")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(**user.to_dict()),
            expires_in=1440
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en registro: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/clickup")
async def clickup_oauth_login():
    """Iniciar proceso de OAuth con ClickUp"""
    try:
        state = oauth_state_manager.create_state()
        auth_url = clickup_oauth.get_authorization_url(state)
        
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        logger.error(f"Error iniciando OAuth: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error iniciando autenticación con ClickUp"
        )

@router.get("/callback")
async def clickup_oauth_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Callback de OAuth de ClickUp"""
    try:
        logger.info(f"🔐 Procesando OAuth callback - Code: {code[:20]}..., State: {state}")
        
        # Autenticar con ClickUp
        auth_result = await authenticate_with_clickup(code, state, db)
        
        logger.info(f"✅ OAuth exitoso - Token generado: {auth_result['access_token'][:20]}...")
        
        # Redirigir al dashboard con el token
        redirect_url = f"/dashboard?token={auth_result['access_token']}"
        
        logger.info(f"🔗 Redirigiendo a: {redirect_url}")
        
        return RedirectResponse(url=redirect_url, status_code=302)
        
    except HTTPException as e:
        logger.error(f"❌ Error HTTPException en callback OAuth: {e.detail}")
        # Redirigir a la página de login con error
        error_url = f"/api/auth/login?error={e.detail}"
        return RedirectResponse(url=error_url, status_code=302)
    except Exception as e:
        logger.error(f"❌ Error general en callback OAuth: {e}")
        error_url = f"/api/auth/login?error=Error_procesando_autenticacion"
        return RedirectResponse(url=error_url, status_code=302)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(require_auth)
):
    """Obtener información del usuario actual"""
    return UserResponse(**current_user.to_dict())

@router.post("/logout")
async def logout(
    current_user: User = Depends(require_auth)
):
    """Cerrar sesión"""
    # En un sistema más complejo, aquí invalidarías el token
    # Por ahora, el cliente debe eliminar el token localmente
    return {"message": "Sesión cerrada exitosamente"}

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: User = Depends(require_auth)
):
    """Renovar token de acceso"""
    access_token = AuthManager.create_access_token(
        data={"sub": str(current_user.id), "email": current_user.email}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(**current_user.to_dict()),
        expires_in=1440
    )

@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Solicitar restablecimiento de contraseña"""
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Por seguridad, no revelar si el email existe
        return {"message": "Si el email existe, se enviará un enlace de restablecimiento"}
    
    # Aquí implementarías el envío de email
    # Por ahora, solo log
    logger.info(f"Solicitud de restablecimiento para: {request.email}")
    
    return {"message": "Si el email existe, se enviará un enlace de restablecimiento"}

@router.get("/roles")
async def get_available_roles():
    """Obtener roles disponibles"""
    return {
        "roles": RoleManager.get_available_roles(),
        "permissions": {
            role: RoleManager.get_role_permissions(role) 
            for role in RoleManager.ROLES.keys()
        }
    }

@router.get("/permissions")
async def get_user_permissions(
    current_user: User = Depends(require_auth)
):
    """Obtener permisos del usuario actual"""
    return {
        "role": current_user.role,
        "permissions": RoleManager.get_role_permissions(current_user.role),
        "can_read_all_tasks": RoleManager.has_permission(current_user.role, "read_all_tasks"),
        "can_write_all_tasks": RoleManager.has_permission(current_user.role, "write_all_tasks"),
        "can_manage_users": RoleManager.has_permission(current_user.role, "write_users")
    }

@router.put("/profile")
async def update_profile(
    profile_data: Dict[str, Any],
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Actualizar perfil del usuario"""
    try:
        # Campos permitidos para actualización
        allowed_fields = [
            'first_name', 'last_name', 'phone', 'timezone', 
            'language', 'preferences'
        ]
        
        for field, value in profile_data.items():
            if field in allowed_fields and hasattr(current_user, field):
                setattr(current_user, field, value)
        
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
        
        return UserResponse(**current_user.to_dict())
        
    except Exception as e:
        logger.error(f"Error actualizando perfil: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error actualizando perfil"
        )

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Cambiar contraseña del usuario"""
    try:
        if not current_user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este usuario no tiene contraseña configurada"
            )
        
        # Verificar contraseña actual
        if not AuthManager.verify_password(current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta"
            )
        
        # Actualizar contraseña
        current_user.password_hash = AuthManager.get_password_hash(new_password)
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Contraseña actualizada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cambiando contraseña: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error cambiando contraseña"
        )