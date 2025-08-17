# ===== ARCHIVO COMPLETAMENTE NUEVO - VERSIÓN FINAL =====
# ===== ACTUALIZADO EL 17 DE AGOSTO DE 2025 A LAS 2:52 AM =====
# ===== ESTE ARCHIVO DEBE EJECUTARSE COMPLETAMENTE =====
# ===== PROBLEMA DE DEPLOY RESUELTO =====

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import http_status

from core.database import get_db
from core.clickup_client import ClickUpClient, get_clickup_client
from models.task import Task
from schemas.task import TaskCreate, TaskResponse

router = APIRouter()

# ===== FUNCIÓN COMPLETAMENTE NUEVA =====
@router.post("/", response_model=TaskResponse, status_code=http_status.HTTP_201_CREATED)
async def create_task_FINAL_VERSION(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    clickup_client: ClickUpClient = Depends(get_clickup_client)
):
    """
    Crear una nueva tarea en ClickUp y en la base de datos local - VERSIÓN FINAL
    """
    print("🚀 ===== CÓDIGO COMPLETAMENTE NUEVO - VERSIÓN FINAL =====")
    print(f"📝 Creando tarea: {task_data.name}")
    print(f"🔍 Timestamp de ejecución: {datetime.now()}")
    print(f"🔑 Token configurado: {'✅ SÍ' if clickup_client.api_token else '❌ NO'}")
    
    # Verificar configuración
    if not clickup_client.api_token:
        print(f"❌ ERROR: No hay token de ClickUp configurado")
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CLICKUP_API_TOKEN no está configurado en el servidor"
        )
    
    print(f"✅ Configuración verificada, procediendo con creación...")
    
    try:
        # Crear tarea en ClickUp
        clickup_task_data = {
            "name": task_data.name,
            "description": task_data.description,
            "priority": task_data.priority,
            "status": task_data.status,
            "assignees": task_data.assignees,
            "due_date": task_data.due_date
        }
        
        print(f"🚀 Enviando tarea a ClickUp con datos: {clickup_task_data}")
        
        clickup_response = await clickup_client.create_task(
            list_id=task_data.list_id,
            task_data=clickup_task_data
        )
        
        print(f"✅ Respuesta de ClickUp: {clickup_response}")
        
        # Extraer información esencial de la respuesta de ClickUp
        clickup_task_id = clickup_response.get("id")
        
        # Extraer workspace_id y list_id de la respuesta de ClickUp
        workspace_id = clickup_response.get("team_id") or task_data.workspace_id
        list_id = clickup_response.get("list", {}).get("id") or task_data.list_id
                
        print(f"🔍 Valores extraídos para BD local:")
        print(f"   📁 workspace_id: {workspace_id}")
        print(f"   📋 list_id: {list_id}")
        print(f"   🆔 clickup_task_id: {clickup_task_id}")
        
        # Guardar en base de datos local
        db_task = Task(
            id=clickup_task_id,
            name=task_data.name,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            due_date=task_data.due_date,
            assignees=task_data.assignees,
            custom_fields=task_data.custom_fields,
            workspace_id=workspace_id,
            list_id=list_id,
            creator_id=clickup_response.get("creator", {}).get("id", "system"),
            is_synced=True
        )
        
        print(f"💾 Guardando tarea en BD local con datos:")
        print(f"   🆔 id: {db_task.id}")
        print(f"   📁 workspace_id: {db_task.workspace_id}")
        print(f"   📋 list_id: {db_task.list_id}")
        print(f"   👤 creator_id: {db_task.creator_id}")
        
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        
        print(f"✅ Tarea guardada exitosamente en BD local")
        
        # Construir respuesta
        response_data = {
            "id": db_task.id,
            "clickup_id": db_task.clickup_id,
            "name": db_task.name,
            "description": db_task.description,
            "status": db_task.status,
            "priority": db_task.priority,
            "due_date": db_task.due_date,
            "start_date": db_task.start_date,
            "workspace_id": db_task.workspace_id,
            "list_id": db_task.list_id,
            "assignee_id": db_task.assignee_id,
            "custom_fields": db_task.custom_fields,
            "created_at": db_task.created_at,
            "updated_at": db_task.updated_at
        }
        
        print(f"✅ Tarea creada exitosamente en BD local: {response_data}")
        return response_data
        
    except Exception as e:
        print(f"❌ Error creando tarea: {e}")
        print(f"❌ Tipo de error: {type(e)}")
        import traceback
        print(f"❌ Traceback completo: {traceback.format_exc()}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la tarea: {str(e)}"
        )

# ===== FUNCIÓN COMPLETAMENTE NUEVA =====
async def _update_custom_fields_background(task_id: str, custom_fields: dict, list_id: str):
    """Actualizar custom fields en background sin bloquear la respuesta principal"""
    try:
        print(f"🔄 Background: Actualizando custom fields para tarea {task_id}")
        
        # Obtener campos disponibles
        available_fields = await clickup_client.get_list_custom_fields(list_id)
        field_name_to_id = {str(f.get("name", "")).strip().lower(): f["id"] for f in available_fields if f.get("name")}
        
        # Preparar datos
        custom_fields_data = []
        for field_name, field_value in custom_fields.items():
            if not field_value or str(field_value).strip() == "":
                continue
            
            key = str(field_name).strip().lower()
            if key in field_name_to_id:
                custom_fields_data.append({
                    "id": field_name_to_id[key],
                    "value": field_value
                })
                print(f"✅ Campo '{field_name}' mapeado a ID {field_name_to_id[key]}")
            else:
                print(f"⚠️ Campo '{field_name}' no encontrado en la lista")
        
        if custom_fields_data:
            # Actualizar custom fields en ClickUp
            await clickup_client.update_task_custom_fields(task_id, custom_fields_data)
            print(f"✅ Custom fields actualizados en background para tarea {task_id}")
        else:
            print(f"⚠️ No hay custom fields válidos para actualizar")
            
    except Exception as e:
        print(f"❌ Error en background actualizando custom fields: {e}")
        # NO lanzar excepción - esto es background

# ===== ENDPOINTS ADICIONALES =====
@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Obtener todas las tareas"""
    try:
        tasks = db.query(Task).offset(skip).limit(limit).all()
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tareas: {str(e)}"
        )

# ===== ENDPOINTS ESPECÍFICOS DEBEN IR ANTES DEL ENDPOINT GENÉRICO {task_id} =====
@router.get("/test")
async def test_endpoint():
    """Endpoint de prueba simple"""
    return {"message": "✅ Endpoint de tasks funcionando", "status": "ok"}

@router.get("/config")
async def show_config():
    """Mostrar configuración actual para debugging"""
    from core.config import settings
    return {
        "message": "🔧 Configuración actual",
        "clickup_token_set": bool(settings.CLICKUP_API_TOKEN),
        "clickup_token_length": len(settings.CLICKUP_API_TOKEN) if settings.CLICKUP_API_TOKEN else 0,
        "clickup_base_url": settings.CLICKUP_API_BASE_URL,
        "debug": settings.DEBUG
    }

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Obtener una tarea específica"""
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        return task
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tarea: {str(e)}"
        )

# ===== FIN DEL ARCHIVO COMPLETAMENTE NUEVO =====
