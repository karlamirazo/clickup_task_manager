"""
Rutas para gestión de automatizaciones
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime

from core.database import get_db
from models.automation import Automation
from api.schemas.automation import (
    AutomationCreate, 
    AutomationUpdate, 
    AutomationResponse, 
    AutomationList
)

router = APIRouter()

@router.post("/", response_model=AutomationResponse, status_code=status.HTTP_201_CREATED)
async def create_automation(
    automation_data: AutomationCreate,
    db: Session = Depends(get_db)
):
    """Crear una nueva automatización"""
    try:
        db_automation = Automation(
            name=automation_data.name,
            description=automation_data.description,
            trigger_type=automation_data.trigger_type,
            trigger_conditions=automation_data.trigger_conditions,
            actions=automation_data.actions,
            workspace_id=automation_data.workspace_id,
            task_id=automation_data.task_id if hasattr(automation_data, 'task_id') else None
        )
        
        db.add(db_automation)
        db.commit()
        db.refresh(db_automation)
        
        return AutomationResponse.from_orm(db_automation)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la automatización: {str(e)}"
        )

@router.get("/", response_model=AutomationList)
async def get_automations(
    workspace_id: Optional[str] = Query(None, description="ID del workspace"),
    active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    page: int = Query(0, ge=0, description="Número de página"),
    limit: int = Query(20, ge=1, le=100, description="Límite de resultados"),
    db: Session = Depends(get_db)
):
    """Obtener lista de automatizaciones"""
    try:
        query = db.query(Automation)
        
        # Aplicar filtros
        if workspace_id:
            query = query.filter(Automation.workspace_id == workspace_id)
        if active is not None:
            query = query.filter(Automation.active == active)
        
        # Contar total
        total = query.count()
        
        # Paginar
        automations = query.offset(page * limit).limit(limit).all()
        
        return AutomationList(
            automations=[AutomationResponse.from_orm(automation) for automation in automations],
            total=total,
            page=page,
            limit=limit,
            has_more=(page + 1) * limit < total
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las automatizaciones: {str(e)}"
        )

@router.get("/{automation_id}", response_model=AutomationResponse)
async def get_automation(
    automation_id: int,
    db: Session = Depends(get_db)
):
    """Obtener una automatización específica"""
    try:
        db_automation = db.query(Automation).filter(Automation.id == automation_id).first()
        
        if not db_automation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automatización no encontrada"
            )
        
        return AutomationResponse.from_orm(db_automation)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la automatización: {str(e)}"
        )

@router.put("/{automation_id}", response_model=AutomationResponse)
async def update_automation(
    automation_id: int,
    automation_data: AutomationUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una automatización existente"""
    try:
        db_automation = db.query(Automation).filter(Automation.id == automation_id).first()
        
        if not db_automation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automatización no encontrada"
            )
        
        # Actualizar campos
        for field, value in automation_data.dict(exclude_unset=True).items():
            setattr(db_automation, field, value)
        
        db_automation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_automation)
        
        return AutomationResponse.from_orm(db_automation)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la automatización: {str(e)}"
        )

@router.delete("/{automation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_automation(
    automation_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar una automatización"""
    try:
        db_automation = db.query(Automation).filter(Automation.id == automation_id).first()
        
        if not db_automation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automatización no encontrada"
            )
        
        db.delete(db_automation)
        db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la automatización: {str(e)}"
        )

@router.post("/{automation_id}/execute", response_model=dict)
async def execute_automation(
    automation_id: int,
    db: Session = Depends(get_db)
):
    """Ejecutar una automatización manualmente"""
    try:
        db_automation = db.query(Automation).filter(Automation.id == automation_id).first()
        
        if not db_automation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automatización no encontrada"
            )
        
        if not db_automation.active or not db_automation.enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La automatización no está activa o habilitada"
            )
        
        # Aquí se ejecutaría la lógica de la automatización
        # Por ahora solo actualizamos las estadísticas
        db_automation.execution_count += 1
        db_automation.last_executed = datetime.utcnow()
        
        db.commit()
        
        return {
            "message": "Automatización ejecutada exitosamente",
            "automation_id": automation_id,
            "execution_count": db_automation.execution_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Incrementar contador de errores
        db_automation = db.query(Automation).filter(Automation.id == automation_id).first()
        if db_automation:
            db_automation.error_count += 1
            db_automation.last_error = str(e)
            db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al ejecutar la automatización: {str(e)}"
        )

@router.post("/{automation_id}/toggle", response_model=AutomationResponse)
async def toggle_automation(
    automation_id: int,
    db: Session = Depends(get_db)
):
    """Activar/desactivar una automatización"""
    try:
        db_automation = db.query(Automation).filter(Automation.id == automation_id).first()
        
        if not db_automation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automatización no encontrada"
            )
        
        db_automation.active = not db_automation.active
        db_automation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_automation)
        
        return AutomationResponse.from_orm(db_automation)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar el estado de la automatización: {str(e)}"
        )
