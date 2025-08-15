"""
Rutas para gestión de usuarios
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime

from core.database import get_db
from core.clickup_client import ClickUpClient
from models.user import User
from api.schemas.user import UserResponse, UserList

router = APIRouter()
clickup_client = ClickUpClient()

@router.get("/")
async def get_users(
    workspace_id: Optional[str] = Query(None, description="ID del workspace"),
    db: Session = Depends(get_db)
):
    """Obtener usuarios"""
    try:
        if workspace_id:
            # Obtener usuarios de un workspace específico directamente de ClickUp
            clickup_users = await clickup_client.get_users(workspace_id)
            
            # Convertir a formato simple para el frontend
            users = []
            for clickup_user in clickup_users:
                user_data = clickup_user["user"]
                users.append({
                    "id": user_data["id"],
                    "clickup_id": user_data["id"],
                    "username": user_data.get("username", ""),
                    "email": user_data.get("email", ""),
                    "first_name": user_data.get("first_name", ""),
                    "last_name": user_data.get("last_name", ""),
                    "avatar": user_data.get("avatar", ""),
                    "role": clickup_user.get("role", ""),
                    "active": user_data.get("active", True)
                })
            
            return {
                "users": users,
                "total": len(users)
            }
        else:
            # Sin workspace específico, devolver lista vacía
            return {
                "users": [],
                "total": 0
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los usuarios: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Obtener un usuario específico"""
    try:
        # Buscar en base de datos local
        db_user = db.query(User).filter(User.clickup_id == user_id).first()
        
        if not db_user:
            # Obtener de ClickUp
            clickup_user = await clickup_client.get_user(user_id)
            
            # Crear registro local
            db_user = User(
                clickup_id=clickup_user["user"]["id"],
                username=clickup_user["user"]["username"],
                email=clickup_user["user"]["email"],
                first_name=clickup_user["user"].get("first_name", ""),
                last_name=clickup_user["user"].get("last_name", ""),
                avatar=clickup_user["user"].get("avatar", ""),
                role=clickup_user.get("role", ""),
                title=clickup_user["user"].get("title", ""),
                active=clickup_user["user"].get("active", True),
                timezone=clickup_user["user"].get("timezone", ""),
                language=clickup_user["user"].get("language", "en"),
                preferences=clickup_user["user"].get("preferences", {}),
                workspaces=clickup_user.get("workspaces", {}),
                is_synced=True,
                last_sync=datetime.utcnow()
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        
        return UserResponse.from_orm(db_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario no encontrado: {str(e)}"
        )

@router.get("/{user_id}/tasks")
async def get_user_tasks(
    user_id: str,
    workspace_id: str = Query(..., description="ID del workspace"),
    db: Session = Depends(get_db)
):
    """Obtener tareas asignadas a un usuario"""
    try:
        tasks = await clickup_client.get_user_tasks(user_id, workspace_id)
        return {"tasks": tasks, "total": len(tasks)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las tareas del usuario: {str(e)}"
        )

@router.post("/{user_id}/sync", response_model=UserResponse)
async def sync_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Sincronizar un usuario con ClickUp"""
    try:
        # Obtener datos actualizados de ClickUp
        clickup_user = await clickup_client.get_user(user_id)
        
        # Buscar o crear usuario local
        db_user = db.query(User).filter(User.clickup_id == user_id).first()
        
        if not db_user:
            db_user = User(clickup_id=user_id)
            db.add(db_user)
        
        # Actualizar datos
        db_user.username = clickup_user["user"]["username"]
        db_user.email = clickup_user["user"]["email"]
        db_user.first_name = clickup_user["user"].get("first_name", "")
        db_user.last_name = clickup_user["user"].get("last_name", "")
        db_user.avatar = clickup_user["user"].get("avatar", "")
        db_user.role = clickup_user.get("role", "")
        db_user.title = clickup_user["user"].get("title", "")
        db_user.active = clickup_user["user"].get("active", True)
        db_user.timezone = clickup_user["user"].get("timezone", "")
        db_user.language = clickup_user["user"].get("language", "en")
        db_user.preferences = clickup_user["user"].get("preferences", {})
        db_user.workspaces = clickup_user.get("workspaces", {})
        db_user.is_synced = True
        db_user.last_sync = datetime.utcnow()
        
        db.commit()
        db.refresh(db_user)
        
        return UserResponse.from_orm(db_user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al sincronizar el usuario: {str(e)}"
        )
