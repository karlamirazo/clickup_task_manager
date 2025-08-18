# ===== ARCHIVO COMPLETAMENTE NUEVO - VERSIÓN FINAL =====
# ===== ACTUALIZADO EL 17 DE AGOSTO DE 2025 A LAS 2:58 AM =====
# ===== ESTE ARCHIVO DEBE EJECUTARSE COMPLETAMENTE =====
# ===== PROBLEMA DE DEPLOY RESUELTO DEFINITIVAMENTE =====

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from fastapi import status
from pydantic import BaseModel, field_validator
from sqlalchemy import text
import json

from core.database import get_db
from core.clickup_client import ClickUpClient, get_clickup_client
from models.task import Task

# ===== SISTEMA DE LOGGING AUTOMÁTICO CON LANGGRAPH =====
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from langgraph_tools.simple_error_logging import log_error_with_graph

# ===== CONFIGURACIÓN DE CAMPOS PERSONALIZADOS =====
# Configuración de campos personalizados por lista
CUSTOM_FIELD_IDS = {
    "901411770471": {  # PROYECTO 1
        "Email": "6464a671-73dd-4be5-b720-b5f0fe5adb04",
        "Celular": "51fa0661-0995-4c37-ba8d-3307aef300ca"
    },
    "901411770470": {  # PROYECTO 2
        # Sin campos personalizados
    },
    "901412119767": {  # Tareas del Proyecto
        "email": "621ed627-a960-4d3a-8ac7-7d0946fe17c2",  # Nota: minúscula
        "Celular": "51fa0661-0995-4c37-ba8d-3307aef300ca"
    }
}

def get_custom_field_id(list_id: str, field_name: str) -> str:
    """Obtener el ID de un campo personalizado específico"""
    list_fields = CUSTOM_FIELD_IDS.get(list_id, {})
    
    # Buscar coincidencia exacta primero
    if field_name in list_fields:
        return list_fields[field_name]
    
    # Buscar coincidencia case-insensitive
    for key, value in list_fields.items():
        if key.lower() == field_name.lower():
            return value
    
    return None

def has_custom_fields(list_id: str) -> bool:
    """Verificar si una lista tiene campos personalizados"""
    return bool(CUSTOM_FIELD_IDS.get(list_id, {}))

async def update_custom_fields_direct(clickup_client: ClickUpClient, task_id: str, list_id: str, custom_fields: Dict[str, Any]):
    """Función de fallback para actualizar campos personalizados directamente"""
    print(f"   🔧 Actualización directa de campos personalizados...")
    
    updated_fields = {}
    errors = []
    
    for field_name, field_value in custom_fields.items():
        field_id = get_custom_field_id(list_id, field_name)
        if field_id:
            try:
                print(f"      📧 Actualizando {field_name} (ID: {field_id}) con valor: {field_value}")
                result = await clickup_client.update_custom_field_value(task_id, field_id, field_value)
                updated_fields[field_name] = {
                    "status": "success",
                    "field_id": field_id,
                    "result": result
                }
                print(f"      ✅ Campo {field_name} actualizado exitosamente")
            except Exception as e:
                error_msg = f"Error actualizando {field_name}: {str(e)}"
                errors.append(error_msg)
                updated_fields[field_name] = {
                    "status": "error",
                    "field_id": field_id,
                    "error": str(e)
                }
                print(f"      ❌ {error_msg}")
        else:
            error_msg = f"No se encontró ID para el campo: {field_name}"
            errors.append(error_msg)
            updated_fields[field_name] = {
                "status": "error",
                "field_id": None,
                "error": error_msg
            }
            print(f"      ⚠️ {error_msg}")
    
    success_count = len([f for f in updated_fields.values() if f["status"] == "success"])
    error_count = len([f for f in updated_fields.values() if f["status"] == "error"])
    
    print(f"   📊 Resumen de actualización directa:")
    print(f"      ✅ Campos actualizados: {success_count}")
    print(f"      ❌ Errores: {error_count}")
    
    return {
        "updated_fields": updated_fields,
        "success_count": success_count,
        "error_count": error_count,
        "errors": errors
    }

# ===== MODELOS PYDANTIC SIMPLES =====
class TaskCreate(BaseModel):
    """Modelo para crear tareas"""
    name: str
    workspace_id: str
    list_id: str
    description: Optional[str] = None
    priority: Optional[int] = 3
    status: Optional[str] = "to_do"
    assignees: Optional[str] = None
    due_date: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = {}

class TaskResponse(BaseModel):
    """Modelo para respuestas de tareas"""
    id: int
    clickup_id: str
    name: str
    description: Optional[str]
    status: str
    priority: int
    due_date: Optional[datetime]
    workspace_id: str
    list_id: str
    assignee_id: Optional[str]
    creator_id: Optional[str]
    custom_fields: Optional[Dict[str, Any]]
    is_synced: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

router = APIRouter()

# ===== FUNCIÓN AUXILIAR NECESARIA =====
def safe_timestamp_to_datetime(timestamp_value) -> Optional[datetime]:
    """HOTFIX: Convertir timestamp a datetime de forma segura sin divisiones por 1000"""
    if timestamp_value is None:
        return None
    
    try:
        # Si ya es datetime, devolverlo
        if isinstance(timestamp_value, datetime):
            return timestamp_value
        
        # Si es string, intentar convertir a int
        if isinstance(timestamp_value, str):
            if timestamp_value.isdigit():
                timestamp_value = int(timestamp_value)
            else:
                return None
        
        # Si es int/float, asumir que ya está en segundos (no milisegundos)
        if isinstance(timestamp_value, (int, float)):
            return datetime.fromtimestamp(timestamp_value)
        
        return None
    except Exception:
        return None

# ===== FUNCIÓN COMPLETAMENTE NUEVA =====
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task_FINAL_VERSION(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    clickup_client: ClickUpClient = Depends(get_clickup_client)
):
    """Crear una nueva tarea en ClickUp y sincronizar con BD local"""
    print(f"🚀 Creando tarea: {task_data.name}")
    print(f"📋 Datos recibidos: {task_data.dict()}")
    
    # Verificar configuración
    if not clickup_client.api_token:
        print(f"❌ ERROR: No hay token de ClickUp configurado")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No hay token de ClickUp configurado"
        )
    
    try:
        # Preparar datos para ClickUp
        clickup_task_data = {
            "name": task_data.name,
            "description": task_data.description or "",
            "status": task_data.status or "to do",
            "priority": task_data.priority or 3,
            "due_date": int(datetime.strptime(task_data.due_date, "%Y-%m-%d").timestamp() * 1000) if task_data.due_date else None,
            "assignees": [int(task_data.assignees)] if task_data.assignees else [],
            "custom_fields": task_data.custom_fields or {}
        }
        
        print(f"📤 Enviando datos a ClickUp: {clickup_task_data}")
        
        # Crear tarea en ClickUp
        clickup_response = await clickup_client.create_task(task_data.list_id, clickup_task_data)
        
        if not clickup_response or "id" not in clickup_response:
            raise Exception("No se recibió ID de tarea de ClickUp")
        
        clickup_task_id = clickup_response["id"]
        print(f"✅ Tarea creada en ClickUp con ID: {clickup_task_id}")
        
        # ===== ACTUALIZACIÓN AUTOMÁTICA DE CAMPOS PERSONALIZADOS =====
        print(f"🔍 DEBUG: Verificando actualización automática...")
        print(f"   📧 task_data.custom_fields: {task_data.custom_fields}")
        print(f"   📋 task_data.list_id: {task_data.list_id}")
        print(f"   🔍 has_custom_fields({task_data.list_id}): {has_custom_fields(task_data.list_id)}")
        
        if task_data.custom_fields and has_custom_fields(task_data.list_id):
            print(f"🔧 Actualizando campos personalizados automáticamente...")
            print(f"   📧 Campos a procesar: {task_data.custom_fields}")
            
            # Usar directamente la función de actualización directa
            try:
                print(f"   🔄 Ejecutando actualización directa de campos personalizados...")
                update_result = await update_custom_fields_direct(clickup_client, clickup_task_id, task_data.list_id, task_data.custom_fields)
                
                success_count = update_result.get('success_count', 0)
                error_count = update_result.get('error_count', 0)
                
                print(f"   ✅ Actualización automática completada!")
                print(f"   📊 Campos actualizados: {success_count}")
                print(f"   ❌ Errores: {error_count}")
                
                if error_count > 0:
                    print(f"   ⚠️ Algunos campos no se pudieron actualizar")
                    print(f"   📋 Errores: {update_result.get('errors', [])}")
                
            except Exception as update_error:
                print(f"   ❌ Error en actualización automática: {update_error}")
                print(f"   📋 Tipo de error: {type(update_error)}")
                # No fallar la creación por error en campos personalizados
        else:
            print(f"ℹ️ No hay campos personalizados para actualizar")
            if not task_data.custom_fields:
                print(f"   ❌ task_data.custom_fields está vacío")
            if not has_custom_fields(task_data.list_id):
                print(f"   ❌ La lista {task_data.list_id} no tiene campos personalizados configurados")
        
        # Guardar en BD local
        new_task = Task(
            clickup_id=clickup_task_id,
            name=task_data.name,
            description=task_data.description or "",
            status=task_data.status or "to do",
            priority=task_data.priority or 3,
            due_date=datetime.strptime(task_data.due_date, "%Y-%m-%d") if task_data.due_date else None,
            workspace_id=task_data.workspace_id,
            list_id=task_data.list_id,
            assignee_id=task_data.assignees,
            creator_id="system",
            custom_fields=task_data.custom_fields or {},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_synced=True
        )
        
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        
        print(f"✅ Tarea guardada en BD local con ID: {new_task.id}")
        
        return new_task
        
    except Exception as e:
        print(f"❌ Error al crear la tarea: {e}")
        
        # ===== LOGGING AUTOMÁTICO CON LANGGRAPH =====
        try:
            log_error_with_graph({
                "error_description": f"Error al crear tarea: {str(e)}",
                "solution_description": "Verificar CLICKUP_API_TOKEN y datos de entrada",
                "context_info": f"Tarea: {task_data.name}, Lista: {task_data.list_id}, Workspace: {task_data.workspace_id}",
                "deployment_id": "railway-production",
                "environment": "production",
                "severity": "high",
                "status": "pending"
            })
        except Exception as logging_error:
            print(f"⚠️ Error en logging automático: {logging_error}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la tarea: {str(e)}"
        )

# ===== ENDPOINT PARA ACTUALIZAR CAMPOS PERSONALIZADOS MANUALMENTE =====
@router.post("/{task_id}/update-custom-fields", response_model=dict)
async def update_task_custom_fields(
    task_id: str,
    custom_fields: Dict[str, Any],
    list_id: str,
    clickup_client: ClickUpClient = Depends(get_clickup_client)
):
    """Actualizar campos personalizados de una tarea específica"""
    print(f"🔧 Actualizando campos personalizados para tarea: {task_id}")
    print(f"📧 Campos: {custom_fields}")
    print(f"📋 Lista: {list_id}")
    
    try:
        if not has_custom_fields(list_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La lista {list_id} no tiene campos personalizados configurados"
            )
        
        updated_fields = {}
        errors = []
        
        for field_name, field_value in custom_fields.items():
            field_id = get_custom_field_id(list_id, field_name)
            if field_id:
                try:
                    print(f"   📧 Actualizando {field_name} (ID: {field_id}) con valor: {field_value}")
                    result = await clickup_client.update_custom_field_value(task_id, field_id, field_value)
                    updated_fields[field_name] = {
                        "status": "success",
                        "field_id": field_id,
                        "result": result
                    }
                    print(f"   ✅ Campo {field_name} actualizado exitosamente")
                except Exception as e:
                    error_msg = f"Error actualizando {field_name}: {str(e)}"
                    errors.append(error_msg)
                    updated_fields[field_name] = {
                        "status": "error",
                        "field_id": field_id,
                        "error": str(e)
                    }
                    print(f"   ❌ {error_msg}")
            else:
                error_msg = f"No se encontró ID para el campo: {field_name}"
                errors.append(error_msg)
                updated_fields[field_name] = {
                    "status": "error",
                    "field_id": None,
                    "error": error_msg
                }
                print(f"   ⚠️ {error_msg}")
        
        return {
            "task_id": task_id,
            "list_id": list_id,
            "updated_fields": updated_fields,
            "success_count": len([f for f in updated_fields.values() if f["status"] == "success"]),
            "error_count": len([f for f in updated_fields.values() if f["status"] == "error"]),
            "errors": errors
        }
        
    except Exception as e:
        print(f"❌ Error actualizando campos personalizados: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando campos personalizados: {str(e)}"
        )

# ===== ENDPOINT DE SINCRONIZACIÓN CON PARÁMETROS =====
@router.post("/sync", response_model=dict)
async def sync_tasks_from_clickup(
    workspace_id: Optional[str] = Query(default=None, description="ID del workspace de ClickUp (opcional)"),
    db: Session = Depends(get_db),
    clickup_client: ClickUpClient = Depends(get_clickup_client)
):
    """
    Sincronizar todas las tareas de ClickUp a la base de datos local
    """
    # Si no se proporciona workspace_id, usar el workspace por defecto
    if not workspace_id:
        workspace_id = "9014943317"  # Workspace por defecto
    
    print(f"🔄 Iniciando sincronización de tareas para workspace: {workspace_id}")
    
    try:
        # Obtener espacios del workspace
        spaces = await clickup_client.get_spaces(workspace_id)
        print(f"📁 Encontrados {len(spaces)} espacios en el workspace")
        
        total_tasks_synced = 0
        total_tasks_created = 0
        total_tasks_updated = 0
        
        for space in spaces:
            space_id = space.get("id")
            space_name = space.get("name", "Sin nombre")
            print(f"🔄 Sincronizando espacio: {space_name} (ID: {space_id})")
            
            try:
                # Obtener listas de este espacio
                lists = await clickup_client.get_lists(space_id)
                print(f"   📋 Encontradas {len(lists)} listas en el espacio {space_name}")
                
                for list_info in lists:
                    list_id = list_info.get("id")
                    list_name = list_info.get("name", "Sin nombre")
                    print(f"   🔄 Sincronizando lista: {list_name} (ID: {list_id})")
                    
                    try:
                        # Obtener tareas de esta lista
                        tasks = await clickup_client.get_tasks(list_id)
                        print(f"      📝 Encontradas {len(tasks)} tareas en la lista {list_name}")
                        
                        for task_data in tasks:
                            task_id = task_data.get("id")
                            
                            # Verificar si la tarea ya existe en la BD local
                            existing_task = db.query(Task).filter(Task.clickup_id == task_id).first()
                            
                            if existing_task:
                                # Actualizar tarea existente
                                existing_task.name = task_data.get("name", existing_task.name)
                                existing_task.description = task_data.get("description", existing_task.description)
                                existing_task.status = task_data.get("status", {}).get("status", existing_task.status)
                                existing_task.priority = task_data.get("priority", existing_task.priority)
                                existing_task.due_date = safe_timestamp_to_datetime(task_data.get("due_date"))
                                existing_task.updated_at = datetime.now()
                                existing_task.is_synced = True
                                
                                total_tasks_updated += 1
                                print(f"      ✅ Tarea actualizada: {task_data.get('name', 'Sin nombre')}")
                            else:
                                # Crear nueva tarea en BD local
                                new_task = Task(
                                    clickup_id=task_id,
                                    name=task_data.get("name", "Sin nombre"),
                                    description=task_data.get("description", ""),
                                    status=task_data.get("status", {}).get("status", "to_do"),
                                    priority=task_data.get("priority", 3),
                                    due_date=safe_timestamp_to_datetime(task_data.get("due_date")),
                                    workspace_id=workspace_id,
                                    list_id=list_id,
                                    creator_id=task_data.get("creator", {}).get("id", "system"),
                                    assignee_id=task_data.get("assignees", [{}])[0].get("id") if task_data.get("assignees") else None,
                                    custom_fields=task_data.get("custom_fields", {}),
                                    created_at=safe_timestamp_to_datetime(task_data.get("date_created")),
                                    updated_at=safe_timestamp_to_datetime(task_data.get("date_updated")),
                                    is_synced=True
                                )
                                
                                db.add(new_task)
                                total_tasks_created += 1
                                print(f"      ➕ Nueva tarea creada: {task_data.get('name', 'Sin nombre')}")
                            
                            total_tasks_synced += 1
                        
                        # Commit después de cada lista para evitar transacciones muy largas
                        db.commit()
                        
                    except Exception as e:
                        print(f"      ❌ Error sincronizando lista {list_name}: {e}")
                        
                        # ===== LOGGING AUTOMÁTICO CON LANGGRAPH =====
                        try:
                            log_error_with_graph({
                                "error_description": f"Error sincronizando lista {list_name}: {str(e)}",
                                "solution_description": "Verificar permisos de lista y conexión a ClickUp API",
                                "context_info": f"Lista: {list_name} (ID: {list_id}), Espacio: {space_name} (ID: {space_id}), Workspace: {workspace_id}",
                                "deployment_id": "railway-production",
                                "environment": "production",
                                "severity": "medium",
                                "status": "pending"
                            })
                        except Exception as logging_error:
                            print(f"⚠️ Error en logging automático: {logging_error}")
                        
                        continue
                        
            except Exception as e:
                print(f"   ❌ Error sincronizando espacio {space_name}: {e}")
                
                # ===== LOGGING AUTOMÁTICO CON LANGGRAPH =====
                try:
                    log_error_with_graph({
                        "error_description": f"Error sincronizando espacio {space_name}: {str(e)}",
                        "solution_description": "Verificar permisos de espacio y conexión a ClickUp API",
                        "context_info": f"Espacio: {space_name} (ID: {space_id}), Workspace: {workspace_id}",
                        "deployment_id": "railway-production",
                        "environment": "production",
                        "severity": "medium",
                        "status": "pending"
                    })
                except Exception as logging_error:
                    print(f"⚠️ Error en logging automático: {logging_error}")
                
                continue
        
        # Commit final
        db.commit()
        
        result = {
            "message": "Sincronización completada",
            "total_tasks_synced": total_tasks_synced,
            "total_tasks_created": total_tasks_created,
            "total_tasks_updated": total_tasks_updated,
            "workspace_id": workspace_id
        }
        
        print(f"✅ Sincronización completada: {result}")
        return result
        
    except Exception as e:
        print(f"❌ Error en sincronización: {e}")
        
        # ===== LOGGING AUTOMÁTICO CON LANGGRAPH =====
        try:
            log_error_with_graph({
                "error_description": f"Error en sincronización de tareas: {str(e)}",
                "solution_description": "Verificar CLICKUP_API_TOKEN y conexión a ClickUp API",
                "context_info": f"Workspace: {workspace_id}, Timestamp: {datetime.now()}",
                "deployment_id": "railway-production",
                "environment": "production",
                "severity": "high",
                "status": "pending"
            })
        except Exception as logging_error:
            print(f"⚠️ Error en logging automático: {logging_error}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en sincronización: {str(e)}"
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
        "clickup_token_configured": bool(settings.CLICKUP_API_TOKEN),
        "database_url_configured": bool(settings.DATABASE_URL),
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/debug")
async def debug_endpoint():
    """Endpoint de debugging para verificar estado del sistema"""
    try:
        from core.config import settings
        from core.database import get_db
        from sqlalchemy.orm import Session
        
        # Verificar configuración
        config_status = {
            "clickup_token": bool(settings.CLICKUP_API_TOKEN),
            "database_url": bool(settings.DATABASE_URL),
            "environment": settings.ENVIRONMENT
        }
        
        # Verificar base de datos
        db = next(get_db())
        try:
            result = db.execute(text("SELECT COUNT(*) FROM tasks"))
            task_count = result.scalar()
            db_status = "✅ Conectado"
        except Exception as e:
            db_status = f"❌ Error: {str(e)}"
            task_count = 0
        
        # Verificar ClickUp API
        try:
            from core.clickup_client import ClickUpClient
            client = ClickUpClient(settings.CLICKUP_API_TOKEN)
            workspaces = await client.get_workspaces()
            clickup_status = f"✅ Conectado ({len(workspaces)} workspaces)"
        except Exception as e:
            clickup_status = f"❌ Error: {str(e)}"
        
        return {
            "status": "✅ Sistema funcionando",
            "config": config_status,
            "database": db_status,
            "clickup": clickup_status,
            "task_count": task_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        # ===== LOGGING AUTOMÁTICO CON LANGGRAPH =====
        try:
            log_error_with_graph({
                "error_description": f"Error en endpoint de debug: {str(e)}",
                "solution_description": "Verificar configuración del sistema",
                "context_info": f"Endpoint: /debug, Timestamp: {datetime.now()}",
                "deployment_id": "railway-production",
                "environment": "production",
                "severity": "medium",
                "status": "pending"
            })
        except Exception as logging_error:
            print(f"⚠️ Error en logging automático: {logging_error}")
        
        return {
            "status": "❌ Error en sistema",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/source-code")
async def get_source_code():
    """Obtener código fuente para debugging"""
    try:
        import os
        current_file = os.path.abspath(__file__)
        
        with open(current_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        return {
            "message": "✅ Código fuente obtenido",
            "file": current_file,
            "size": len(source_code),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "message": "❌ Error obteniendo código fuente",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ===== ENDPOINT DE SINCRONIZACIÓN SIMPLE (SIN PARÁMETROS) - DEBE IR ANTES DE {task_id} =====
@router.post("/sync-simple", response_model=dict)
async def sync_tasks_simple(
    db: Session = Depends(get_db),
    clickup_client: ClickUpClient = Depends(get_clickup_client)
):
    """
    Sincronizar todas las tareas de ClickUp a la base de datos local (sin parámetros)
    """
    workspace_id = "9014943317"  # Workspace por defecto
    
    print(f"🔄 Iniciando sincronización simple para workspace: {workspace_id}")
    
    try:
        # Obtener espacios del workspace
        spaces = await clickup_client.get_spaces(workspace_id)
        print(f"📁 Encontrados {len(spaces)} espacios en el workspace")
        
        total_tasks_synced = 0
        total_tasks_created = 0
        total_tasks_updated = 0
        
        for space in spaces:
            space_id = space.get("id")
            space_name = space.get("name", "Sin nombre")
            print(f"🔄 Sincronizando espacio: {space_name} (ID: {space_id})")
            
            try:
                # Obtener listas de este espacio
                lists = await clickup_client.get_lists(space_id)
                print(f"   📋 Encontradas {len(lists)} listas en el espacio {space_name}")
                
                for list_info in lists:
                    list_id = list_info.get("id")
                    list_name = list_info.get("name", "Sin nombre")
                    print(f"   🔄 Sincronizando lista: {list_name} (ID: {list_id})")
                    
                    try:
                        # Obtener tareas de esta lista
                        tasks = await clickup_client.get_tasks(list_id)
                        print(f"      📝 Encontradas {len(tasks)} tareas en la lista {list_name}")
                        
                        for task_data in tasks:
                            task_id = task_data.get("id")
                            
                            # Verificar si la tarea ya existe en la BD local
                            existing_task = db.query(Task).filter(Task.clickup_id == task_id).first()
                            
                            if existing_task:
                                # Actualizar tarea existente
                                existing_task.name = task_data.get("name", existing_task.name)
                                existing_task.description = task_data.get("description", existing_task.description)
                                existing_task.status = task_data.get("status", {}).get("status", existing_task.status)
                                existing_task.priority = task_data.get("priority", existing_task.priority)
                                existing_task.due_date = safe_timestamp_to_datetime(task_data.get("due_date"))
                                existing_task.updated_at = datetime.now()
                                existing_task.is_synced = True
                                
                                total_tasks_updated += 1
                                print(f"      ✅ Tarea actualizada: {task_data.get('name', 'Sin nombre')}")
                            else:
                                # Crear nueva tarea en BD local
                                new_task = Task(
                                    clickup_id=task_id,
                                    name=task_data.get("name", "Sin nombre"),
                                    description=task_data.get("description", ""),
                                    status=task_data.get("status", {}).get("status", "to_do"),
                                    priority=task_data.get("priority", 3),
                                    due_date=safe_timestamp_to_datetime(task_data.get("due_date")),
                                    workspace_id=workspace_id,
                                    list_id=list_id,
                                    creator_id=task_data.get("creator", {}).get("id", "system"),
                                    assignee_id=task_data.get("assignees", [{}])[0].get("id") if task_data.get("assignees") else None,
                                    custom_fields=task_data.get("custom_fields", {}),
                                    created_at=safe_timestamp_to_datetime(task_data.get("date_created")),
                                    updated_at=safe_timestamp_to_datetime(task_data.get("date_updated")),
                                    is_synced=True
                                )
                                
                                db.add(new_task)
                                total_tasks_created += 1
                                print(f"      ➕ Nueva tarea creada: {task_data.get('name', 'Sin nombre')}")
                            
                            total_tasks_synced += 1
                        
                        # Commit después de cada lista para evitar transacciones muy largas
                        db.commit()
                        
                    except Exception as e:
                        print(f"      ❌ Error sincronizando lista {list_name}: {e}")
                        continue
                        
            except Exception as e:
                print(f"   ❌ Error sincronizando espacio {space_name}: {e}")
                continue
        
        # Commit final
        db.commit()
        
        result = {
            "message": "Sincronización simple completada",
            "total_tasks_synced": total_tasks_synced,
            "total_tasks_created": total_tasks_created,
            "total_tasks_updated": total_tasks_updated,
            "workspace_id": workspace_id
        }
        
        print(f"✅ Sincronización simple completada: {result}")
        return result
        
    except Exception as e:
        print(f"❌ Error en sincronización simple: {e}")
        
        # ===== LOGGING AUTOMÁTICO CON LANGGRAPH =====
        try:
            log_error_with_graph({
                "error_description": f"Error en sincronización simple: {str(e)}",
                "solution_description": "Verificar CLICKUP_API_TOKEN y conexión a ClickUp API",
                "context_info": f"Workspace: {workspace_id}, Timestamp: {datetime.now()}",
                "deployment_id": "railway-production",
                "environment": "production",
                "severity": "high",
                "status": "pending"
            })
        except Exception as logging_error:
            print(f"⚠️ Error en logging automático: {logging_error}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en sincronización simple: {str(e)}"
        )

# ===== ENDPOINT GENÉRICO {task_id} - DEBE IR AL FINAL =====
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Obtener una tarea específica"""
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        return task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tarea: {str(e)}"
        )
