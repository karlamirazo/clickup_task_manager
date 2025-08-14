"""
Rutas para gestión de listas
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.clickup_client import ClickUpClient

router = APIRouter()
clickup_client = ClickUpClient()

@router.get("/")
async def get_lists(
    space_id: str = Query(..., description="ID del space"),
    db: Session = Depends(get_db)
):
    """Obtener todas las listas de un space"""
    try:
        lists = await clickup_client.get_lists(space_id)
        return {"lists": lists, "total": len(lists)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las listas: {str(e)}"
        )

@router.get("/{list_id}")
async def get_list(
    list_id: str,
    db: Session = Depends(get_db)
):
    """Obtener una lista específica"""
    try:
        list_data = await clickup_client.get_list(list_id)
        return list_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lista no encontrada: {str(e)}"
        )

@router.get("/{list_id}/tasks")
async def get_list_tasks(
    list_id: str,
    include_closed: bool = Query(False, description="Incluir tareas cerradas"),
    page: int = Query(0, ge=0, description="Número de página"),
    db: Session = Depends(get_db)
):
    """Obtener tareas de una lista"""
    try:
        tasks = await clickup_client.get_tasks(list_id, include_closed, page)
        return {"tasks": tasks, "total": len(tasks), "page": page}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las tareas: {str(e)}"
        )

@router.get("/{list_id}/fields")
async def get_list_custom_fields(
    list_id: str,
    db: Session = Depends(get_db)
):
    """Obtener campos personalizados de una lista"""
    try:
        fields = await clickup_client.get_list_custom_fields(list_id)
        return {"fields": fields, "total": len(fields)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los campos personalizados: {str(e)}"
        )
