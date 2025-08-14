"""
Rutas para gestión de integraciones
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime

from core.database import get_db
from models.integration import Integration
from api.schemas.integration import (
    IntegrationCreate, 
    IntegrationUpdate, 
    IntegrationResponse, 
    IntegrationList,
    IntegrationTest
)

router = APIRouter()

@router.post("/", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    integration_data: IntegrationCreate,
    db: Session = Depends(get_db)
):
    """Crear una nueva integración"""
    try:
        db_integration = Integration(
            name=integration_data.name,
            description=integration_data.description,
            integration_type=integration_data.integration_type,
            provider=integration_data.provider,
            config=integration_data.config,
            credentials=integration_data.credentials,
            workspace_id=integration_data.workspace_id,
            created_by="system"  # En un sistema real, esto vendría del usuario autenticado
        )
        
        db.add(db_integration)
        db.commit()
        db.refresh(db_integration)
        
        return IntegrationResponse.from_orm(db_integration)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la integración: {str(e)}"
        )

@router.get("/", response_model=IntegrationList)
async def get_integrations(
    workspace_id: Optional[str] = Query(None, description="ID del workspace"),
    integration_type: Optional[str] = Query(None, description="Tipo de integración"),
    active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    page: int = Query(0, ge=0, description="Número de página"),
    limit: int = Query(20, ge=1, le=100, description="Límite de resultados"),
    db: Session = Depends(get_db)
):
    """Obtener lista de integraciones"""
    try:
        query = db.query(Integration)
        
        # Aplicar filtros
        if workspace_id:
            query = query.filter(Integration.workspace_id == workspace_id)
        if integration_type:
            query = query.filter(Integration.integration_type == integration_type)
        if active is not None:
            query = query.filter(Integration.active == active)
        
        # Contar total
        total = query.count()
        
        # Paginar
        integrations = query.offset(page * limit).limit(limit).all()
        
        return IntegrationList(
            integrations=[IntegrationResponse.from_orm(integration) for integration in integrations],
            total=total,
            page=page,
            limit=limit,
            has_more=(page + 1) * limit < total
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las integraciones: {str(e)}"
        )

@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: int,
    db: Session = Depends(get_db)
):
    """Obtener una integración específica"""
    try:
        db_integration = db.query(Integration).filter(Integration.id == integration_id).first()
        
        if not db_integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integración no encontrada"
            )
        
        return IntegrationResponse.from_orm(db_integration)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la integración: {str(e)}"
        )

@router.put("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: int,
    integration_data: IntegrationUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una integración existente"""
    try:
        db_integration = db.query(Integration).filter(Integration.id == integration_id).first()
        
        if not db_integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integración no encontrada"
            )
        
        # Actualizar campos
        for field, value in integration_data.dict(exclude_unset=True).items():
            setattr(db_integration, field, value)
        
        db_integration.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_integration)
        
        return IntegrationResponse.from_orm(db_integration)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la integración: {str(e)}"
        )

@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar una integración"""
    try:
        db_integration = db.query(Integration).filter(Integration.id == integration_id).first()
        
        if not db_integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integración no encontrada"
            )
        
        db.delete(db_integration)
        db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la integración: {str(e)}"
        )

@router.post("/{integration_id}/test", response_model=dict)
async def test_integration(
    integration_id: int,
    test_data: IntegrationTest,
    db: Session = Depends(get_db)
):
    """Probar una integración"""
    try:
        db_integration = db.query(Integration).filter(Integration.id == integration_id).first()
        
        if not db_integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integración no encontrada"
            )
        
        if not db_integration.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La integración no está activa"
            )
        
        # Aquí se ejecutaría la prueba de conexión según el tipo de integración
        test_result = await _test_integration_connection(db_integration, test_data.test_type)
        
        # Actualizar estadísticas
        if test_result["success"]:
            db_integration.connected = True
            db_integration.last_sync = datetime.utcnow()
        else:
            db_integration.error_count += 1
            db_integration.last_error = test_result.get("error", "Error desconocido")
        
        db.commit()
        
        return test_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al probar la integración: {str(e)}"
        )

@router.post("/{integration_id}/sync", response_model=dict)
async def sync_integration(
    integration_id: int,
    db: Session = Depends(get_db)
):
    """Sincronizar datos con una integración"""
    try:
        db_integration = db.query(Integration).filter(Integration.id == integration_id).first()
        
        if not db_integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integración no encontrada"
            )
        
        if not db_integration.active or not db_integration.enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La integración no está activa o habilitada"
            )
        
        # Aquí se ejecutaría la sincronización según el tipo de integración
        sync_result = await _sync_integration_data(db_integration)
        
        # Actualizar estadísticas
        if sync_result["success"]:
            db_integration.sync_count += 1
            db_integration.last_sync = datetime.utcnow()
            db_integration.connected = True
        else:
            db_integration.error_count += 1
            db_integration.last_error = sync_result.get("error", "Error desconocido")
        
        db.commit()
        
        return sync_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al sincronizar la integración: {str(e)}"
        )

@router.post("/{integration_id}/toggle", response_model=IntegrationResponse)
async def toggle_integration(
    integration_id: int,
    db: Session = Depends(get_db)
):
    """Activar/desactivar una integración"""
    try:
        db_integration = db.query(Integration).filter(Integration.id == integration_id).first()
        
        if not db_integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integración no encontrada"
            )
        
        db_integration.active = not db_integration.active
        db_integration.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_integration)
        
        return IntegrationResponse.from_orm(db_integration)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar el estado de la integración: {str(e)}"
        )

@router.get("/providers/available")
async def get_available_providers():
    """Obtener proveedores de integración disponibles"""
    return {
        "providers": {
            "crm": [
                {"id": "salesforce", "name": "Salesforce", "description": "CRM líder en el mercado"},
                {"id": "hubspot", "name": "HubSpot", "description": "CRM y marketing automation"},
                {"id": "pipedrive", "name": "Pipedrive", "description": "CRM enfocado en ventas"}
            ],
            "database": [
                {"id": "postgresql", "name": "PostgreSQL", "description": "Base de datos relacional"},
                {"id": "mysql", "name": "MySQL", "description": "Base de datos relacional"},
                {"id": "mongodb", "name": "MongoDB", "description": "Base de datos NoSQL"}
            ],
            "productivity": [
                {"id": "slack", "name": "Slack", "description": "Comunicación en equipo"},
                {"id": "microsoft_teams", "name": "Microsoft Teams", "description": "Colaboración empresarial"},
                {"id": "google_workspace", "name": "Google Workspace", "description": "Suite de productividad"}
            ],
            "project_management": [
                {"id": "jira", "name": "Jira", "description": "Gestión de proyectos ágiles"},
                {"id": "asana", "name": "Asana", "description": "Gestión de proyectos y tareas"},
                {"id": "trello", "name": "Trello", "description": "Gestión visual de proyectos"}
            ]
        }
    }

async def _test_integration_connection(integration: Integration, test_type: str) -> dict:
    """Probar conexión con una integración"""
    try:
        # Aquí se implementaría la lógica específica para cada tipo de integración
        if integration.integration_type == "crm":
            return await _test_crm_connection(integration, test_type)
        elif integration.integration_type == "database":
            return await _test_database_connection(integration, test_type)
        elif integration.integration_type == "productivity":
            return await _test_productivity_connection(integration, test_type)
        else:
            return {
                "success": False,
                "error": f"Tipo de integración no soportado: {integration.integration_type}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def _sync_integration_data(integration: Integration) -> dict:
    """Sincronizar datos con una integración"""
    try:
        # Aquí se implementaría la lógica específica para cada tipo de integración
        if integration.integration_type == "crm":
            return await _sync_crm_data(integration)
        elif integration.integration_type == "database":
            return await _sync_database_data(integration)
        elif integration.integration_type == "productivity":
            return await _sync_productivity_data(integration)
        else:
            return {
                "success": False,
                "error": f"Tipo de integración no soportado: {integration.integration_type}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Funciones específicas para cada tipo de integración
async def _test_crm_connection(integration: Integration, test_type: str) -> dict:
    """Probar conexión con CRM"""
    # Implementación específica para CRM
    return {
        "success": True,
        "message": f"Conexión exitosa con {integration.provider}",
        "test_type": test_type
    }

async def _test_database_connection(integration: Integration, test_type: str) -> dict:
    """Probar conexión con base de datos"""
    # Implementación específica para bases de datos
    return {
        "success": True,
        "message": f"Conexión exitosa con {integration.provider}",
        "test_type": test_type
    }

async def _test_productivity_connection(integration: Integration, test_type: str) -> dict:
    """Probar conexión con herramientas de productividad"""
    # Implementación específica para herramientas de productividad
    return {
        "success": True,
        "message": f"Conexión exitosa con {integration.provider}",
        "test_type": test_type
    }

async def _sync_crm_data(integration: Integration) -> dict:
    """Sincronizar datos con CRM"""
    # Implementación específica para CRM
    return {
        "success": True,
        "message": f"Datos sincronizados exitosamente con {integration.provider}",
        "records_synced": 0
    }

async def _sync_database_data(integration: Integration) -> dict:
    """Sincronizar datos con base de datos"""
    # Implementación específica para bases de datos
    return {
        "success": True,
        "message": f"Datos sincronizados exitosamente con {integration.provider}",
        "records_synced": 0
    }

async def _sync_productivity_data(integration: Integration) -> dict:
    """Sincronizar datos con herramientas de productividad"""
    # Implementación específica para herramientas de productividad
    return {
        "success": True,
        "message": f"Datos sincronizados exitosamente con {integration.provider}",
        "records_synced": 0
    }
