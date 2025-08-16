"""
Rutas para gestión de espacios de trabajo
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime

from core.database import get_db
from core.clickup_client import ClickUpClient
from models.workspace import Workspace
from api.schemas.workspace import WorkspaceResponse, WorkspaceList

router = APIRouter()
clickup_client = ClickUpClient()

@router.get("/test-connection")
async def test_clickup_connection():
    """Probar la conexión con ClickUp API"""
    try:
        # Verificar que tenemos token
        if not clickup_client.api_token:
            return {
                "status": "error",
                "message": "No se encontró CLICKUP_API_TOKEN en las variables de entorno",
                "token_configured": False,
                "error_type": "missing_token"
            }
        
        # Intentar obtener workspaces
        workspaces = await clickup_client.get_workspaces()
        
        return {
            "status": "success",
            "message": "Conexión exitosa con ClickUp API",
            "token_configured": True,
            "workspaces_count": len(workspaces),
            "workspaces": workspaces[:3] if workspaces else []  # Solo los primeros 3 para no sobrecargar
        }
        
    except ValueError as e:
        return {
            "status": "error",
            "message": str(e),
            "token_configured": False,
            "error_type": "configuration_error"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al conectar con ClickUp API: {str(e)}",
            "token_configured": bool(clickup_client.api_token),
            "error_type": "api_error"
        }

@router.get("/status")
async def get_clickup_status():
    """Obtener el estado de la conexión con ClickUp"""
    try:
        if not clickup_client.api_token:
            return {
                "status": "disconnected",
                "message": "CLICKUP_API_TOKEN no configurado",
                "token_configured": False,
                "can_connect": False
            }
        
        # Hacer una petición simple para verificar conectividad
        await clickup_client.get_workspaces()
        
        return {
            "status": "connected",
            "message": "Conectado a ClickUp API",
            "token_configured": True,
            "can_connect": True
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error de conexión: {str(e)}",
            "token_configured": bool(clickup_client.api_token),
            "can_connect": False
        }

@router.get("/")
async def get_workspaces(
    db: Session = Depends(get_db)
):
    """Obtener todos los espacios de trabajo"""
    try:
        # Verificar que tenemos token
        if not clickup_client.api_token:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="CLICKUP_API_TOKEN no está configurado. Por favor, configura la variable de entorno en Railway."
            )
        
        # Obtener de ClickUp directamente y devolver formato simple
        clickup_workspaces = await clickup_client.get_workspaces()
        
        # Convertir a formato simple para el frontend
        workspaces = []
        for workspace in clickup_workspaces:
            workspaces.append({
                "id": workspace.get("id"),
                "clickup_id": workspace.get("id"),
                "name": workspace.get("name"),
                "color": workspace.get("color", "#000000"),
                "private": False,
                "multiple_assignees": True,
                "is_synced": True
            })
        
        return {
            "workspaces": workspaces,
            "total": len(workspaces)
        }
        
    except ValueError as e:
        # Error de configuración (token faltante)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error de configuración: {str(e)}"
        )
    except Exception as e:
        # Error de ClickUp API o base de datos
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los espacios de trabajo: {str(e)}"
        )

@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """Obtener un espacio de trabajo específico"""
    try:
        # Buscar en base de datos local
        db_workspace = db.query(Workspace).filter(
            Workspace.clickup_id == workspace_id
        ).first()
        
        if not db_workspace:
            # Obtener de ClickUp
            clickup_workspace = await clickup_client.get_workspace(workspace_id)
            
            # Crear registro local
            db_workspace = Workspace(
                clickup_id=clickup_workspace["id"],
                name=clickup_workspace["name"],
                description="",  # ClickUp API no devuelve description en teams
                color=clickup_workspace.get("color", ""),
                private=False,  # ClickUp API no devuelve private en teams
                multiple_assignees=True,  # ClickUp API no devuelve multiple_assignees en teams
                settings={},  # ClickUp API no devuelve settings en teams
                features={},  # ClickUp API no devuelve features en teams
                is_synced=True,
                last_sync=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(db_workspace)
            db.commit()
            db.refresh(db_workspace)
        
        return WorkspaceResponse.from_orm(db_workspace)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Espacio de trabajo no encontrado: {str(e)}"
        )

@router.post("/{workspace_id}/sync", response_model=WorkspaceResponse)
async def sync_workspace(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """Sincronizar un espacio de trabajo con ClickUp"""
    try:
        # Obtener datos actualizados de ClickUp
        clickup_workspace = await clickup_client.get_workspace(workspace_id)
        
        # Buscar o crear workspace local
        db_workspace = db.query(Workspace).filter(
            Workspace.clickup_id == workspace_id
        ).first()
        
        if not db_workspace:
            db_workspace = Workspace(clickup_id=workspace_id)
            db.add(db_workspace)
        
        # Actualizar datos
        db_workspace.name = clickup_workspace["name"]
        db_workspace.color = clickup_workspace.get("color", "")
        db_workspace.is_synced = True
        db_workspace.last_sync = datetime.utcnow()
        
        db.commit()
        db.refresh(db_workspace)
        
        return WorkspaceResponse.from_orm(db_workspace)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al sincronizar el espacio de trabajo: {str(e)}"
        )

@router.get("/{workspace_id}/spaces")
async def get_workspace_spaces(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """Obtener todos los spaces de un workspace"""
    try:
        spaces = await clickup_client.get_spaces(workspace_id)
        return {"spaces": spaces, "total": len(spaces)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los spaces: {str(e)}"
        )

@router.get("/{workspace_id}/users")
async def get_workspace_users(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """Obtener usuarios de un workspace"""
    try:
        users = await clickup_client.get_users(workspace_id)
        return {"users": users, "total": len(users)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los usuarios: {str(e)}"
        )
