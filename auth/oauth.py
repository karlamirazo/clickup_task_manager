"""
Sistema de autenticación OAuth 2.0 con ClickUp
"""

import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from urllib.parse import urlencode, parse_qs
import aiohttp
import logging

from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from models.user import User
from auth.auth import AuthManager

logger = logging.getLogger(__name__)

class ClickUpOAuth:
    """Gestor de autenticación OAuth 2.0 con ClickUp"""
    
    # URLs de ClickUp OAuth
    AUTHORIZE_URL = "https://app.clickup.com/api/v2/oauth/authorize"
    TOKEN_URL = "https://app.clickup.com/api/v2/oauth/token"
    USER_INFO_URL = "https://api.clickup.com/api/v2/user"
    
    def __init__(self):
        self.client_id = getattr(settings, 'CLICKUP_OAUTH_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'CLICKUP_OAUTH_CLIENT_SECRET', '')
        self.redirect_uri = getattr(settings, 'CLICKUP_OAUTH_REDIRECT_URI', '')
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            logger.warning("ClickUp OAuth no configurado completamente")
    
    def get_authorization_url(self, state: str = None) -> str:
        """Generar URL de autorización de ClickUp"""
        if not self.client_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OAuth no configurado"
            )
        
        if not state:
            state = self.generate_state()
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'state': state,
            'scope': 'read:user read:workspace read:task write:task'  # Permisos necesarios
        }
        
        return f"{self.AUTHORIZE_URL}?{urlencode(params)}"
    
    def generate_state(self) -> str:
        """Generar state aleatorio para OAuth"""
        return secrets.token_urlsafe(32)
    
    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """Intercambiar código de autorización por token de acceso"""
        if not all([self.client_id, self.client_secret]):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OAuth no configurado"
            )
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.TOKEN_URL,
                    data=data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Error en OAuth token exchange: {response.status} - {error_text}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error al obtener token de ClickUp"
                        )
                    
                    token_data = await response.json()
                    return token_data
                    
            except aiohttp.ClientError as e:
                logger.error(f"Error de conexión en OAuth: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error de conexión con ClickUp"
                )
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Obtener información del usuario desde ClickUp"""
        headers = {
            'Authorization': access_token,
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    self.USER_INFO_URL,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Error obteniendo info de usuario: {response.status} - {error_text}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error al obtener información del usuario"
                        )
                    
                    user_data = await response.json()
                    return user_data
                    
            except aiohttp.ClientError as e:
                logger.error(f"Error de conexión obteniendo usuario: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error de conexión con ClickUp"
                )
    
    async def create_or_update_user_from_clickup(
        self, 
        clickup_user_data: Dict[str, Any], 
        access_token: str,
        db: Session
    ) -> User:
        """Crear o actualizar usuario desde datos de ClickUp"""
        clickup_id = str(clickup_user_data.get('id', ''))
        email = clickup_user_data.get('email', '')
        username = clickup_user_data.get('username', '')
        
        if not all([clickup_id, email, username]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Datos de usuario incompletos"
            )
        
        # Buscar usuario existente por clickup_id o email
        user = db.query(User).filter(
            (User.clickup_id == clickup_id) | (User.email == email)
        ).first()
        
        if user:
            # Actualizar usuario existente
            user.clickup_id = clickup_id
            user.email = email
            user.username = username
            user.first_name = clickup_user_data.get('first_name', '')
            user.last_name = clickup_user_data.get('last_name', '')
            user.avatar = clickup_user_data.get('avatar', '')
            user.title = clickup_user_data.get('title', '')
            user.timezone = clickup_user_data.get('timezone', '')
            user.language = clickup_user_data.get('language', 'es')
            user.active = clickup_user_data.get('active', True)
            user.last_login = datetime.utcnow()
            user.is_synced = True
            user.last_sync = datetime.utcnow()
            
            # Actualizar token de acceso (si se almacena)
            if hasattr(user, 'clickup_access_token'):
                user.clickup_access_token = access_token
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"Usuario actualizado: {user.username} ({user.email})")
        else:
            # Crear nuevo usuario
            user = User(
                clickup_id=clickup_id,
                email=email,
                username=username,
                first_name=clickup_user_data.get('first_name', ''),
                last_name=clickup_user_data.get('last_name', ''),
                avatar=clickup_user_data.get('avatar', ''),
                title=clickup_user_data.get('title', ''),
                timezone=clickup_user_data.get('timezone', ''),
                language=clickup_user_data.get('language', 'es'),
                active=clickup_user_data.get('active', True),
                role='user',  # Rol por defecto
                clickup_role='member',  # Rol en ClickUp
                is_active=True,
                last_login=datetime.utcnow(),
                is_synced=True,
                last_sync=datetime.utcnow()
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"Usuario creado: {user.username} ({user.email})")
        
        return user


class OAuthStateManager:
    """Gestor de estados OAuth para seguridad"""
    
    def __init__(self):
        self.states = {}  # En producción, usar Redis o base de datos
    
    def create_state(self, user_id: Optional[int] = None) -> str:
        """Crear state OAuth con información adicional"""
        state = secrets.token_urlsafe(32)
        self.states[state] = {
            'created_at': datetime.utcnow(),
            'user_id': user_id,
            'used': False
        }
        return state
    
    def validate_state(self, state: str) -> bool:
        """Validar state OAuth"""
        if state not in self.states:
            return False
        
        state_data = self.states[state]
        
        # Verificar si ya fue usado
        if state_data['used']:
            return False
        
        # Verificar expiración (5 minutos)
        if datetime.utcnow() - state_data['created_at'] > timedelta(minutes=5):
            del self.states[state]
            return False
        
        # Marcar como usado
        state_data['used'] = True
        return True
    
    def get_state_data(self, state: str) -> Optional[Dict[str, Any]]:
        """Obtener datos del state"""
        return self.states.get(state)


# Instancias globales
clickup_oauth = ClickUpOAuth()
oauth_state_manager = OAuthStateManager()


async def authenticate_with_clickup(
    code: str, 
    state: str, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Autenticar usuario con ClickUp OAuth"""
    
    # Validar state
    if not oauth_state_manager.validate_state(state):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State inválido o expirado"
        )
    
    try:
        # Intercambiar código por token
        token_data = await clickup_oauth.exchange_code_for_token(code, state)
        access_token = token_data.get('access_token')
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo obtener token de acceso"
            )
        
        # Obtener información del usuario
        user_info = await clickup_oauth.get_user_info(access_token)
        
        # Crear o actualizar usuario
        user = await clickup_oauth.create_or_update_user_from_clickup(
            user_info, access_token, db
        )
        
        # Generar token JWT para nuestra aplicación
        jwt_token = AuthManager.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user": user.to_dict(),
            "clickup_token": access_token,
            "expires_in": token_data.get('expires_in', 3600)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en autenticación OAuth: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno en autenticación"
        )


def get_clickup_oauth() -> ClickUpOAuth:
    """Dependencia para obtener instancia de ClickUpOAuth"""
    return clickup_oauth
