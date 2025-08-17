"""
Rutas de autenticación y gestión de usuarios
"""

from datetime import datetime, timedelta
from typing import Optional, List
import logging

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from core.database import get_db
from core.auth import AuthManager, RoleManager, require_auth, require_permission, optional_auth
from models.user import User
# Modelos Pydantic locales para evitar importaciones incorrectas
class UserResponse(BaseModel):
    """Modelo de respuesta para usuarios"""
    id: int
    email: str
    username: Optional[str]
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    """Modelo para crear usuarios"""
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: str
    role: str = "user"

class UserUpdate(BaseModel):
    """Modelo para actualizar usuarios"""
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

auth_logger = logging.getLogger("auth")

router = APIRouter()


# Schemas específicos para autenticación
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class ApiKeyResponse(BaseModel):
    api_key: str
    description: str
    created_at: datetime
    expires_at: Optional[datetime]


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Iniciar sesión con email y contraseña
    """
    try:
        # Buscar usuario por email
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            auth_logger.warning(f"Intento de login con email inexistente: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
            )
        
        # Verificar contraseña
        if not AuthManager.verify_password(login_data.password, user.password_hash):
            auth_logger.warning(f"Contraseña incorrecta para usuario: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
            )
        
        # Verificar que el usuario esté activo
        if not user.is_active:
            auth_logger.warning(f"Intento de login con usuario inactivo: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo",
            )
        
        # Crear token JWT
        access_token_expires = timedelta(minutes=1440)  # 24 horas
        access_token = AuthManager.create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role},
            expires_delta=access_token_expires
        )
        
        # Actualizar último login
        user.last_login = datetime.now()
        db.commit()
        
        auth_logger.info(f"Login exitoso para usuario: {login_data.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(f"Error en login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(optional_auth)
):
    """
    Registrar nuevo usuario
    """
    try:
        # Verificar si el email ya existe
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ya registrado"
            )
        
        # Solo admins pueden crear otros usuarios con roles específicos
        role = "user"  # Rol por defecto
        if current_user and RoleManager.has_permission(current_user.role, "write_users"):
            role = getattr(user_data, 'role', 'user')
        
        # Crear usuario
        password_hash = AuthManager.get_password_hash(user_data.password)
        
        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            password_hash=password_hash,
            role=role,
            is_active=True,
            phone=getattr(user_data, 'phone', None),
            telegram_id=getattr(user_data, 'telegram_id', None),
            workspaces=getattr(user_data, 'workspaces', None),
            created_at=datetime.now()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        auth_logger.info(f"Usuario registrado: {user_data.email}")
        
        return UserResponse.model_validate(new_user)
        
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(f"Error en registro: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(require_auth)
):
    """
    Obtener información del usuario actual
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Actualizar información del usuario actual
    """
    try:
        # Actualizar campos permitidos
        update_data = user_update.dict(exclude_unset=True)
        
        # No permitir cambiar rol o estado activo por esta ruta
        update_data.pop('role', None)
        update_data.pop('is_active', None)
        
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        current_user.updated_at = datetime.now()
        db.commit()
        db.refresh(current_user)
        
        auth_logger.info(f"Usuario actualizado: {current_user.email}")
        
        return UserResponse.model_validate(current_user)
        
    except Exception as e:
        auth_logger.error(f"Error actualizando usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Cambiar contraseña del usuario actual
    """
    try:
        # Verificar contraseña actual
        if not AuthManager.verify_password(password_data.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta"
            )
        
        # Actualizar contraseña
        current_user.password_hash = AuthManager.get_password_hash(password_data.new_password)
        current_user.updated_at = datetime.now()
        db.commit()
        
        auth_logger.info(f"Contraseña cambiada para usuario: {current_user.email}")
        
        return {"message": "Contraseña actualizada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(f"Error cambiando contraseña: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/api-key", response_model=ApiKeyResponse)
async def create_api_key(
    description: str = "API Key generada desde interfaz",
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Crear API key para el usuario actual
    """
    try:
        # Generar API key
        api_key = AuthManager.create_api_key(current_user.id, description)
        
        # Guardar en base de datos
        current_user.api_key = api_key
        current_user.api_key_description = description
        current_user.api_key_active = True
        current_user.api_key_created_at = datetime.now()
        current_user.updated_at = datetime.now()
        
        db.commit()
        
        auth_logger.info(f"API key creada para usuario: {current_user.email}")
        
        return ApiKeyResponse(
            api_key=api_key,
            description=description,
            created_at=current_user.api_key_created_at,
            expires_at=None  # Sin expiración por ahora
        )
        
    except Exception as e:
        auth_logger.error(f"Error creando API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.delete("/api-key")
async def revoke_api_key(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Revocar API key del usuario actual
    """
    try:
        current_user.api_key_active = False
        current_user.updated_at = datetime.now()
        db.commit()
        
        auth_logger.info(f"API key revocada para usuario: {current_user.email}")
        
        return {"message": "API key revocada exitosamente"}
        
    except Exception as e:
        auth_logger.error(f"Error revocando API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_permission("read_users")),
    db: Session = Depends(get_db)
):
    """
    Listar usuarios (solo para admins/managers)
    """
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        return [UserResponse.model_validate(user) for user in users]
        
    except Exception as e:
        auth_logger.error(f"Error listando usuarios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_permission("read_users")),
    db: Session = Depends(get_db)
):
    """
    Obtener usuario específico (solo para admins/managers)
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return UserResponse.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(f"Error obteniendo usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_permission("write_users")),
    db: Session = Depends(get_db)
):
    """
    Actualizar usuario específico (solo para admins)
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Actualizar campos
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.now()
        db.commit()
        db.refresh(user)
        
        auth_logger.info(f"Usuario {user_id} actualizado por {current_user.email}")
        
        return UserResponse.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(f"Error actualizando usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_permission("delete_users")),
    db: Session = Depends(get_db)
):
    """
    Eliminar usuario (solo para admins)
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # No permitir auto-eliminación
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes eliminarte a ti mismo"
            )
        
        db.delete(user)
        db.commit()
        
        auth_logger.info(f"Usuario {user_id} eliminado por {current_user.email}")
        
        return {"message": "Usuario eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(f"Error eliminando usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/roles")
async def get_available_roles(
    current_user: User = Depends(require_permission("read_users"))
):
    """
    Obtener roles disponibles (solo para admins/managers)
    """
    return {
        "roles": RoleManager.get_available_roles(),
        "permissions": {
            role: RoleManager.get_role_permissions(role)
            for role in RoleManager.ROLES.keys()
        }
    }


@router.get("/validate-token")
async def validate_token(
    current_user: User = Depends(require_auth)
):
    """
    Validar token actual
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "permissions": RoleManager.get_role_permissions(current_user.role)
    }
