#!/usr/bin/env python3
"""
Versión de prueba del OAuth que simula el éxito para testing
"""

import logging
from typing import Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from core.config import settings

logger = logging.getLogger(__name__)

class ClickUpOAuthTest:
    """Versión de prueba del OAuth que simula el éxito"""

    def __init__(self):
        self.client_id = settings.CLICKUP_OAUTH_CLIENT_ID
        self.client_secret = settings.CLICKUP_OAUTH_CLIENT_SECRET
        self.redirect_uri = settings.CLICKUP_OAUTH_REDIRECT_URI
        
        logger.info(f"OAuth Test configurado - Client ID: {self.client_id[:20]}...")

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Simular intercambio de código por token"""
        logger.info(f"Simulando intercambio de código: {code[:20]}...")
        
        # Simular respuesta exitosa de ClickUp
        return {
            "access_token": f"test_access_token_{code}",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": f"test_refresh_token_{code}",
            "scope": "read:user read:workspace read:task write:task"
        }

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Simular obtención de información de usuario"""
        logger.info(f"Simulando obtención de usuario con token: {access_token[:20]}...")
        
        # Simular respuesta exitosa de ClickUp
        return {
            "id": "test_user_12345",
            "username": "test_user",
            "email": "test@example.com",
            "color": "#ff6b6b",
            "profilePicture": "https://example.com/avatar.jpg",
            "initials": "TU",
            "role": 1,
            "custom_role": None,
            "last_active": "2025-01-15T19:00:00.000Z",
            "date_joined": "2025-01-01T00:00:00.000Z",
            "date_invited": "2025-01-01T00:00:00.000Z"
        }

    async def authenticate_with_clickup(
        self,
        code: str,
        state: str,
        db: Session
    ) -> Dict[str, Any]:
        """Simular autenticación completa con ClickUp"""
        logger.info(f"Simulando autenticación con código: {code[:20]}...")
        
        try:
            # Simular intercambio de código por token
            token_data = await self.exchange_code_for_token(code)
            access_token = token_data["access_token"]
            
            # Simular obtención de información de usuario
            user_info = await self.get_user_info(access_token)
            
            # Simular creación/actualización de usuario en BD
            user_data = {
                "clickup_id": user_info["id"],
                "username": user_info["username"],
                "email": user_info["email"],
                "access_token": access_token,
                "refresh_token": token_data.get("refresh_token"),
                "token_expires": token_data.get("expires_in", 3600)
            }
            
            logger.info(f"Usuario simulado creado: {user_data['username']}")
            
            return {
                "access_token": access_token,
                "user": user_data,
                "message": "Autenticación simulada exitosa"
            }
            
        except Exception as e:
            logger.error(f"Error en autenticación simulada: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error en autenticación simulada"
            )

