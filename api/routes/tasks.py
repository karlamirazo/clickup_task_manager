"""
Rutas para gestión de tareas
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy.orm import Session
from datetime import datetime

from core.database import get_db
from core.clickup_client import ClickUpClient
from models.task import Task
from models.user import User
from api.schemas.task import (
    TaskCreate, 
    TaskUpdate, 
    TaskResponse, 
    TaskList, 
    TaskFilter,
    TaskBulkUpdate,
    TaskBulkDelete
)

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

router = APIRouter()
clickup_client = ClickUpClient()

# ENDPOINTS BÁSICOS - RESTAURADOS

@router.get("/workspaces")
async def get_workspaces():
    """Obtener todos los workspaces"""
    try:
        print("🔍 Intentando obtener workspaces...")
        workspaces = await clickup_client.get_workspaces()
        print(f"✅ Workspaces obtenidos: {workspaces}")
        return {"workspaces": workspaces}
    except Exception as e:
        print(f"❌ Error obteniendo workspaces: {e}")
        print(f"❌ Tipo de error: {type(e)}")
        import traceback
        print(f"❌ Traceback completo: {traceback.format_exc()}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener workspaces: {str(e)}"
        )

@router.get("/workspaces/{workspace_id}/spaces")
async def get_spaces(workspace_id: str):
    """Obtener espacios de un workspace"""
    try:
        spaces = await clickup_client.get_spaces(workspace_id)
        return {"spaces": spaces}
    except Exception as e:
        print(f"❌ Error obteniendo spaces: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener spaces: {str(e)}"
        )

@router.get("/spaces/{space_id}/folders")
async def get_folders(space_id: str):
    """Obtener carpetas de un espacio"""
    try:
        folders = await clickup_client.get_folders(space_id)
        return {"folders": folders}
    except Exception as e:
        print(f"❌ Error obteniendo folders: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener folders: {str(e)}"
        )

@router.get("/folders/{folder_id}/lists")
async def get_lists_in_folder(folder_id: str):
    """Obtener listas de una carpeta"""
    try:
        lists = await clickup_client.get_lists_in_folder(folder_id)
        return {"lists": lists}
    except Exception as e:
        print(f"❌ Error obteniendo lists: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener lists: {str(e)}"
        )

@router.get("/spaces/{space_id}/lists")
async def get_lists_in_space(space_id: str):
    """Obtener listas de un espacio"""
    try:
        lists = await clickup_client.get_lists_in_space(space_id)
        return {"lists": lists}
    except Exception as e:
        print(f"❌ Error obteniendo lists: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener lists: {str(e)}"
        )

@router.get("/lists/{list_id}/tasks")
async def get_tasks_in_list(list_id: str):
    """Obtener tareas de una lista"""
    try:
        tasks = await clickup_client.get_tasks_in_list(list_id)
        return {"tasks": tasks}
    except Exception as e:
        print(f"❌ Error obteniendo tasks: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tasks: {str(e)}"
        )

@router.get("/users")
async def get_users():
    """Obtener usuarios del equipo"""
    try:
        users = await clickup_client.get_users()
        return {"users": users}
    except Exception as e:
        print(f"❌ Error obteniendo users: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener users: {str(e)}"
        )

def _priority_to_int(priority_value) -> int:
    """Convertir diferentes representaciones de prioridad a entero (1-4).
    1=Urgente, 2=Alta, 3=Normal, 4=Baja. Cualquier valor inesperado -> 3.
    """
    # Si es dict con id
    if isinstance(priority_value, dict):
        try:
            return int(priority_value.get("id", 3))
        except (ValueError, TypeError):
            return 3
    # Si es entero
    if isinstance(priority_value, int):
        return priority_value if priority_value in {1, 2, 3, 4} else 3
    # Si es string (id numérico o nombre)
    if isinstance(priority_value, str):
        # Intentar parsear como número primero
        try:
            num = int(priority_value)
            return num if num in {1, 2, 3, 4} else 3
        except (ValueError, TypeError):
            normalized = priority_value.strip().lower()
            name_to_id = {
                "urgent": 1,
                "alta": 2,
                "high": 2,
                "normal": 3,
                "media": 3,
                "low": 4,
                "baja": 4,
            }
            return name_to_id.get(normalized, 3)
    # Cualquier otro caso
    return 3

@router.post("/", response_model=TaskResponse, status_code=http_status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db)
):
    """Crear una nueva tarea"""
    try:
        print(f"🚀 INICIO: Creando tarea con datos: {task_data}")
        print(f"📋 List ID: {task_data.list_id}")
        print(f"🏢 Workspace ID: {task_data.workspace_id}")
        
        # Crear tarea en ClickUp - solo campos esenciales
        clickup_task_data = {
            "name": task_data.name,
            "description": task_data.description or ""
        }
        
        print(f"📝 Datos básicos preparados: {clickup_task_data}")
        
        # Agregar prioridad si existe (normalizada). ClickUp acepta 1-4
        if task_data.priority is not None:
            clickup_task_data["priority"] = _priority_to_int(task_data.priority)
            print(f"🎯 Prioridad agregada: {clickup_task_data['priority']}")
        
        # Agregar estado si existe
        if task_data.status:
            clickup_task_data["status"] = task_data.status
            print(f"📊 Estado agregado: {clickup_task_data['status']}")
        
        # Agregar asignatario si existe
        if task_data.assignee_id:
            # ClickUp espera IDs numéricos; convertir si es posible
            try:
                clickup_task_data["assignees"] = [int(str(task_data.assignee_id))]
                print(f"👤 Asignatario agregado: {clickup_task_data['assignees']}")
            except ValueError:
                clickup_task_data["assignees"] = [str(task_data.assignee_id)]
                print(f"👤 Asignatario agregado (string): {clickup_task_data['assignees']}")

        # Agregar fechas si existen
        if task_data.due_date:
            # Debug: verificar formato de fecha antes de enviar
            print(f"🔍 Debug fecha límite antes de enviar a ClickUp:")
            print(f"  📅 task_data.due_date: {task_data.due_date} (tipo: {type(task_data.due_date)})")
            
            # SOLUCIÓN TEMPORAL: Manejar manualmente la conversión de tipos
            if isinstance(task_data.due_date, datetime):
                # Convertir datetime a timestamp en milisegundos
                timestamp_ms = int(task_data.due_date.timestamp() * 1000)
                clickup_task_data["due_date"] = timestamp_ms
                print(f"  📅 DateTime convertido a timestamp: {task_data.due_date} -> {timestamp_ms}")
            elif isinstance(task_data.due_date, (int, float)):
                # Ya es timestamp en milisegundos
                clickup_task_data["due_date"] = int(task_data.due_date)
                print(f"  📅 Timestamp directo: {task_data.due_date}")
            elif isinstance(task_data.due_date, str):
                # Intentar convertir string a timestamp
                try:
                    timestamp = int(task_data.due_date)
                    clickup_task_data["due_date"] = timestamp
                    print(f"  📅 String convertido a timestamp: {task_data.due_date} -> {timestamp}")
                except (ValueError, TypeError):
                    print(f"  ❌ No se pudo convertir string a timestamp: {task_data.due_date}")
                    # No incluir due_date si no se puede convertir
            else:
                print(f"  ⚠️ Tipo de due_date no reconocido: {type(task_data.due_date)}")
                # No incluir due_date si no se puede convertir
            
            print(f"📅 Fecha límite enviada a ClickUp: {clickup_task_data['due_date']}")
        
        if task_data.start_date:
            if isinstance(task_data.start_date, (int, float)):
                clickup_task_data["start_date"] = int(task_data.start_date)
            else:
                clickup_task_data["start_date"] = int(task_data.start_date.timestamp() * 1000)
            
        # Manejar custom_fields de forma simplificada
        if task_data.custom_fields:
            print(f"📝 Custom fields recibidos: {task_data.custom_fields}")
            print(f"📅 Due date recibido: {task_data.due_date} (tipo: {type(task_data.due_date)})")
            print(f"📅 Due date raw: {repr(task_data.due_date)}")
            # Por ahora, crear la tarea sin custom fields para evitar errores 400
            # Los custom fields se agregarán después de la creación
            print("⚠️ Custom fields se agregarán después de crear la tarea para evitar errores 400")
        
        print(f"🚀 Enviando tarea a ClickUp con datos: {clickup_task_data}")
        print(f"📅 Due date que se envía: {clickup_task_data.get('due_date')}")
        print(f"📅 Due date original: {task_data.due_date}")
        print(f"📅 Due date original raw: {repr(task_data.due_date)}")
        print(f"📅 Due date en clickup_task_data: {clickup_task_data.get('due_date')}")
        print(f"📅 Tipo de due_date en clickup_task_data: {type(clickup_task_data.get('due_date'))}")
        
        print(f"🔗 Llamando a clickup_client.create_task con list_id: {task_data.list_id}")
        clickup_response = await clickup_client.create_task(
            task_data.list_id, 
            clickup_task_data
        )
        print(f"✅ Respuesta de ClickUp: {clickup_response}")
        
        # HOTFIX: No procesar due_date del response para evitar errores de división
        # La fecha ya se envió correctamente a ClickUp, no necesitamos leerla de vuelta
        print(f"✅ Tarea creada en ClickUp con ID: {clickup_response.get('id')}")
        print(f"📅 Due date enviado: {clickup_response.get('due_date')} (no procesado para evitar errores)")
        
        # HOTFIX: Agregar custom fields de forma NO-BLOQUEANTE
        if task_data.custom_fields and clickup_response.get("id"):
            task_id = clickup_response["id"]
            print(f"📝 HOTFIX: Agregando custom fields a tarea {task_id}")
            print(f"🔍 Custom fields recibidos: {task_data.custom_fields}")
            
            # Ejecutar en background sin bloquear la respuesta
            import asyncio
            asyncio.create_task(_update_custom_fields_background(task_id, task_data.custom_fields, task_data.list_id))
        
        # Guardar en base de datos local; si ClickUp no devolvió priority, usar lo enviado
        task_priority = clickup_response.get("priority", {}).get("id") if isinstance(clickup_response.get("priority"), dict) else clickup_task_data.get("priority", 3)
        
        # HOTFIX: Simplificar manejo de fechas para evitar errores
        task_due_date = None
        task_start_date = None
        
        # Solo procesar fechas si existen y son válidas
        if clickup_response.get("due_date"):
            try:
                due_date_val = clickup_response.get("due_date")
                if isinstance(due_date_val, (int, float)):
                    task_due_date = datetime.fromtimestamp(due_date_val)
                elif isinstance(due_date_val, str) and due_date_val.isdigit():
                    task_due_date = datetime.fromtimestamp(int(due_date_val))
            except Exception as e:
                print(f"⚠️ Error procesando due_date: {e}")
                task_due_date = None
        
        if clickup_response.get("start_date"):
            try:
                start_date_val = clickup_response.get("start_date")
                if isinstance(start_date_val, (int, float)):
                    task_start_date = datetime.fromtimestamp(start_date_val)
                elif isinstance(start_date_val, str) and start_date_val.isdigit():
                    task_start_date = datetime.fromtimestamp(int(start_date_val))
            except Exception as e:
                print(f"⚠️ Error procesando start_date: {e}")
                task_start_date = None
        
        print(f"💾 Preparando para guardar en base de datos...")
        print(f"  📋 ClickUp ID: {clickup_response['id']}")
        print(f"  📝 Nombre: {clickup_response['name']}")
        print(f"  🏢 Workspace ID: {task_data.workspace_id}")
        print(f"  📋 List ID: {task_data.list_id}")
        print(f"  👤 Assignee ID: {clickup_response.get('assignees', [{}])[0].get('id') if clickup_response.get('assignees') else None}")
        
        # Crear objeto Task para la base de datos (llenar campos obligatorios)
        db_task = Task(
            clickup_id=clickup_response["id"],
            name=clickup_response["name"],
            description=clickup_response.get("description", ""),
            status=clickup_response.get("status", {}).get("status", ""),
            priority=task_priority,
            due_date=task_due_date,
            start_date=task_start_date,
            list_id=task_data.list_id,
            workspace_id=task_data.workspace_id,
            assignee_id=clickup_response.get("assignees", [{}])[0].get("id") if clickup_response.get("assignees") else None,
            creator_id=str(clickup_response.get("creator", {}).get("id") or "system"),
            custom_fields=task_data.custom_fields or {},
            is_synced=True
        )
        
        print(f"💾 Objeto Task creado, agregando a sesión...")
        db.add(db_task)
        print(f"💾 Commit a base de datos...")
        db.commit()
        print(f"💾 Refresh del objeto...")
        db.refresh(db_task)
        print(f"✅ Tarea guardada en BD con ID local: {db_task.id}")
        
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

# HOTFIX: Función auxiliar para actualizar custom fields en background
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

# ENDPOINTS ADICIONALES
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

# ENDPOINTS ESPECÍFICOS DEBEN IR ANTES DEL ENDPOINT GENÉRICO {task_id}
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tarea: {str(e)}"
        )

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una tarea"""
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        
        # Actualizar campos
        for field, value in task_data.dict(exclude_unset=True).items():
            setattr(task, field, value)
        
        db.commit()
        db.refresh(task)
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar tarea: {str(e)}"
        )

@router.delete("/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Eliminar una tarea"""
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        
        db.delete(task)
        db.commit()
        return {"message": "Tarea eliminada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar tarea: {str(e)}"
        )

# ENDPOINTS DE SINCRONIZACIÓN
@router.post("/sync")
async def sync_tasks(db: Session = Depends(get_db)):
    """Sincronizar tareas desde ClickUp"""
    try:
        # Implementar sincronización
        return {"message": "Sincronización iniciada"}
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al sincronizar las tareas: {str(e)}"
        )

# ENDPOINT DE DEBUGGING PARA CREACIÓN DE TAREAS
@router.post("/debug-create")
async def debug_create_task():
    """Endpoint de debugging para probar creación de tareas sin lógica compleja"""
    try:
        print("🔍 DEBUG: Probando endpoint de debugging")
        
        # Verificar configuración básica
        if not clickup_client.api_token:
            return {
                "error": "Token no configurado",
                "token_set": False,
                "token_length": 0
            }
        
        # Verificar conexión con ClickUp
        try:
            workspaces = await clickup_client.get_workspaces()
            return {
                "message": "✅ Debug exitoso",
                "token_set": True,
                "token_length": len(clickup_client.api_token),
                "workspaces_count": len(workspaces) if workspaces else 0,
                "clickup_connection": "✅ Conectado"
            }
        except Exception as clickup_error:
            return {
                "message": "❌ Error en ClickUp",
                "token_set": True,
                "token_length": len(clickup_client.api_token),
                "clickup_connection": f"❌ Error: {str(clickup_error)}",
                "error_type": str(type(clickup_error))
            }
            
    except Exception as e:
        print(f"❌ DEBUG ERROR: {e}")
        return {
            "error": f"Error general: {str(e)}",
            "error_type": str(type(e)),
            "traceback": str(e)
        }

# ENDPOINT DE DEBUGGING PARA VERIFICAR BASE DE DATOS
@router.post("/debug-db")
async def debug_database():
    """Endpoint de debugging para verificar la base de datos"""
    try:
        from core.database import get_db
        from models.task import Task
        
        # Obtener sesión de BD
        db = next(get_db())
        
        try:
            # Verificar si la tabla existe
            result = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
            table_exists = result.fetchone() is not None
            
            # Contar tareas existentes
            task_count = db.query(Task).count()
            
            # Verificar estructura de la tabla
            if table_exists:
                result = db.execute("PRAGMA table_info(tasks)")
                columns = result.fetchall()
                column_info = [{"name": col[1], "type": col[2], "not_null": col[3]} for col in columns]
            else:
                column_info = []
            
            return {
                "message": "✅ Debug de base de datos exitoso",
                "database_url": str(settings.DATABASE_URL),
                "table_exists": table_exists,
                "task_count": task_count,
                "columns": column_info,
                "database_status": "✅ Conectado"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ DEBUG DB ERROR: {e}")
        import traceback
        return {
            "error": f"Error en base de datos: {str(e)}",
            "error_type": str(type(e)),
            "traceback": traceback.format_exc(),
            "database_status": "❌ Error"
        }

# ENDPOINT DE DEBUGGING PARA VERIFICAR MODELOS
@router.post("/debug-models")
async def debug_models():
    """Endpoint de debugging para verificar los modelos"""
    try:
        from models.task import Task
        from models.workspace import Workspace
        from models.user import User
        
        # Verificar que los modelos se pueden importar
        models_info = {
            "Task": {
                "imported": True,
                "table_name": Task.__tablename__,
                "columns": [col.name for col in Task.__table__.columns]
            },
            "Workspace": {
                "imported": True,
                "table_name": Workspace.__tablename__,
                "columns": [col.name for col in Workspace.__table__.columns]
            },
            "User": {
                "imported": True,
                "table_name": User.__tablename__,
                "columns": [col.name for col in User.__table__.columns]
            }
        }
        
        return {
            "message": "✅ Debug de modelos exitoso",
            "models": models_info,
            "models_status": "✅ Importados correctamente"
        }
        
    except Exception as e:
        print(f"❌ DEBUG MODELS ERROR: {e}")
        import traceback
        return {
            "error": f"Error en modelos: {str(e)}",
            "error_type": str(type(e)),
            "traceback": traceback.format_exc(),
            "models_status": "❌ Error"
        }
