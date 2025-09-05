"""
Routes for gestion de spaces y lists
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from integrations.clickup.client import ClickUpClient

router = APIRouter()
clickup_client = ClickUpClient()

@router.get("/{space_id}/lists")
async def get_space_lists(
    space_id: str,
    db: Session = Depends(get_db)
):
    """Get todas las listas de un space"""
    try:
        lists = await clickup_client.get_lists(space_id)
        return {"lists": lists, "total": len(lists)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obtener las listas: {str(e)}"
        )

@router.get("/{space_id}")
async def get_space(
    space_id: str,
    db: Session = Depends(get_db)
):
    """Get un space especifico"""
    try:
        space = await clickup_client.get_space(space_id)
        return space
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Space no encontrado: {str(e)}"
        )
