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
    space_id: Optional[str] = Query(None, description="ID del space (opcional)"),
    workspace_id: Optional[str] = Query(None, description="ID del workspace (opcional)"),
    db: Session = Depends(get_db)
):
    """Obtener todas las listas"""
    try:
        if space_id:
            # Si se proporciona space_id, obtener listas de ese space
            lists = await clickup_client.get_lists(space_id)
            return {"lists": lists, "total": len(lists)}
        elif workspace_id:
            # Si se proporciona workspace_id, obtener todas las listas del workspace
            spaces = await clickup_client.get_spaces(workspace_id)
            all_lists = []
            for space in spaces:
                try:
                    space_lists = await clickup_client.get_lists(space.get("id"))
                    all_lists.extend(space_lists)
                except Exception as e:
                    print(f"Error obteniendo listas del space {space.get('id')}: {e}")
            return {"lists": all_lists, "total": len(all_lists)}
        else:
            # Si no se proporciona ningún ID, devolver lista vacía
            return {"lists": [], "total": 0, "message": "Se requiere space_id o workspace_id"}
        
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
