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
                "token_configured": False
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
            "token_configured": False
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al conectar con ClickUp API: {str(e)}",
            "token_configured": bool(clickup_client.api_token)
        }

@router.get("/", response_model=WorkspaceList)
async def get_workspaces(
    db: Session = Depends(get_db)
):
    """Obtener todos los espacios de trabajo"""
    try:
        # Obtener de ClickUp
        clickup_workspaces = await clickup_client.get_workspaces()
        
        workspaces = []
        for clickup_workspace in clickup_workspaces:
            # Buscar en base de datos local
            db_workspace = db.query(Workspace).filter(
                Workspace.clickup_id == clickup_workspace["id"]
            ).first()
            
            if not db_workspace:
                # Crear nuevo registro
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
                db.commit()  # Commit inmediato para obtener el ID
                db.refresh(db_workspace)  # Refrescar para obtener todos los campos
            else:
                # Actualizar datos existentes
                db_workspace.name = clickup_workspace["name"]
                db_workspace.color = clickup_workspace.get("color", "")
                db_workspace.is_synced = True
                db_workspace.last_sync = datetime.utcnow()
            
            workspaces.append(WorkspaceResponse.from_orm(db_workspace))
        
        db.commit()
        
        return WorkspaceList(
            workspaces=workspaces,
            total=len(workspaces)
        )
        
    except Exception as e:
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
