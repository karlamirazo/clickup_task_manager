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

@router.get("/", response_model=UserList)
async def get_users(
    workspace_id: Optional[str] = Query(None, description="ID del workspace"),
    db: Session = Depends(get_db)
):
    """Obtener usuarios"""
    try:
        if workspace_id:
            # Obtener usuarios de un workspace específico
            clickup_users = await clickup_client.get_users(workspace_id)
        else:
            # Obtener todos los usuarios de la base de datos local
            db_users = db.query(User).all()
            return UserList(
                users=[UserResponse.from_orm(user) for user in db_users],
                total=len(db_users)
            )
        
        users = []
        for clickup_user in clickup_users:
            # Buscar en base de datos local
            db_user = db.query(User).filter(
                User.clickup_id == clickup_user["user"]["id"]
            ).first()
            
            if not db_user:
                # Crear nuevo registro
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
            else:
                # Actualizar datos existentes
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
            
            try:
                users.append(UserResponse.from_orm(db_user))
            except Exception as e:
                print(f"Error validando usuario {db_user.clickup_id}: {e}")
                # Crear un usuario básico si falla la validación
                users.append(UserResponse(
                    id=db_user.id or 0,
                    clickup_id=str(db_user.clickup_id),
                    username=db_user.username or "",
                    email=db_user.email or "",
                    first_name=db_user.first_name or "",
                    last_name=db_user.last_name or "",
                    avatar=db_user.avatar or "",
                    role=db_user.role or "",
                    title=db_user.title or "",
                    active=db_user.active or True,
                    timezone=db_user.timezone or "",
                    language=db_user.language or "es",
                    created_at=db_user.created_at or datetime.utcnow(),
                    updated_at=db_user.updated_at or datetime.utcnow(),
                    last_login=db_user.last_login,
                    preferences=db_user.preferences or {},
                    workspaces=db_user.workspaces or {},
                    is_synced=db_user.is_synced or True,
                    last_sync=db_user.last_sync or datetime.utcnow(),
                    full_name=f"{db_user.first_name or ''} {db_user.last_name or ''}".strip() or db_user.username or ""
                ))
        
        db.commit()
        
        return UserList(
            users=users,
            total=len(users)
        )
        
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
