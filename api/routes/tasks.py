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

from core.database import get_db
from core.clickup_client import ClickUpClient, get_clickup_client
from models.task import Task

# ===== MODELOS PYDANTIC SIMPLES =====
class TaskCreate(BaseModel):
    """Modelo para crear tareas"""
    name: str
    description: Optional[str] = None
    priority: int = 3
    status: str = "to_do"
    assignees: List[str] = []
    due_date: Optional[Union[str, datetime]] = None
    workspace_id: str
    list_id: str
    custom_fields: Dict[str, Any] = {}
    
    @field_validator('due_date', mode='before')
    @classmethod
    def validate_due_date(cls, v):
        """Convertir string de fecha a datetime si es necesario"""
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                # Intentar parsear como ISO format (YYYY-MM-DD)
                return datetime.fromisoformat(v)
            except ValueError:
                try:
                    # Intentar parsear como formato común
                    return datetime.strptime(v, "%Y-%m-%d")
                except ValueError:
                    # Si no se puede parsear, devolver None en lugar de lanzar error
                    return None
        # Si es cualquier otro tipo, devolver None
        return None

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
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
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
            clickup_id=clickup_task_id,  # ✅ CORREGIDO: usar clickup_id, no id
            name=task_data.name,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            due_date=task_data.due_date,
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
        db.commit()  # ✅ CORREGIDO: remover await
        db.refresh(db_task)  # ✅ CORREGIDO: remover await
        
        print(f"✅ Tarea guardada exitosamente en BD local")
        
        # Construir respuesta
        response_data = {
            "id": db_task.id,  # ✅ Este es el ID de la BD local
            "clickup_id": db_task.clickup_id,  # ✅ Este es el ID de ClickUp
            "name": db_task.name,
            "description": db_task.description,
            "status": db_task.status,
            "priority": db_task.priority,
            "due_date": db_task.due_date,
            "start_date": db_task.start_date,
            "workspace_id": db_task.workspace_id,
            "list_id": db_task.list_id,
            "assignee_id": db_task.assignee_id,
            "creator_id": db_task.creator_id,  # ✅ AGREGADO: campo faltante
            "custom_fields": db_task.custom_fields,
            "is_synced": db_task.is_synced,  # ✅ AGREGADO: campo faltante
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la tarea: {str(e)}"
        )

# ===== NUEVO ENDPOINT DE SINCRONIZACIÓN =====
@router.post("/sync", response_model=dict)
async def sync_tasks_from_clickup(
    workspace_id: str = Query(..., description="ID del workspace de ClickUp"),
    db: Session = Depends(get_db),
    clickup_client: ClickUpClient = Depends(get_clickup_client)
):
    """
    Sincronizar todas las tareas de ClickUp a la base de datos local
    """
    print(f"🔄 Iniciando sincronización de tareas para workspace: {workspace_id}")
    
    try:
        # Obtener todas las listas del workspace
        lists = await clickup_client.get_workspace_lists(workspace_id)
        print(f"📋 Encontradas {len(lists)} listas en el workspace")
        
        total_tasks_synced = 0
        total_tasks_created = 0
        total_tasks_updated = 0
        
        for list_info in lists:
            list_id = list_info.get("id")
            list_name = list_info.get("name", "Sin nombre")
            print(f"🔄 Sincronizando lista: {list_name} (ID: {list_id})")
            
            try:
                # Obtener tareas de esta lista
                tasks = await clickup_client.get_list_tasks(list_id)
                print(f"   📝 Encontradas {len(tasks)} tareas en la lista {list_name}")
                
                for task_data in tasks:
                    task_id = task_data.get("id")
                    
                    # Verificar si la tarea ya existe en la BD local
                    existing_task = db.query(Task).filter(Task.id == task_id).first()
                    
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
                        print(f"   ✅ Tarea actualizada: {task_data.get('name', 'Sin nombre')}")
                    else:
                        # Crear nueva tarea en BD local
                        new_task = Task(
                            id=task_id,
                            name=task_data.get("name", "Sin nombre"),
                            description=task_data.get("description", ""),
                            status=task_data.get("status", {}).get("status", "to do"),
                            priority=task_data.get("priority", 3),
                            due_date=safe_timestamp_to_datetime(task_data.get("due_date")),
                            workspace_id=workspace_id,
                            list_id=list_id,
                            creator_id=task_data.get("creator", {}).get("id", "system"),
                            assignees=task_data.get("assignees", []),
                            custom_fields=task_data.get("custom_fields", {}),
                            created_at=safe_timestamp_to_datetime(task_data.get("date_created")),
                            updated_at=safe_timestamp_to_datetime(task_data.get("date_updated")),
                            is_synced=True
                        )
                        
                        db.add(new_task)
                        total_tasks_created += 1
                        print(f"   ➕ Nueva tarea creada: {task_data.get('name', 'Sin nombre')}")
                    
                    total_tasks_synced += 1
                
                # Commit después de cada lista para evitar transacciones muy largas
                await db.commit()
                
            except Exception as e:
                print(f"   ❌ Error sincronizando lista {list_name}: {e}")
                continue
        
        print(f"✅ Sincronización completada:")
        print(f"   📊 Total tareas procesadas: {total_tasks_synced}")
        print(f"   ➕ Nuevas tareas creadas: {total_tasks_created}")
        print(f"   🔄 Tareas actualizadas: {total_tasks_updated}")
        
        return {
            "message": "Sincronización completada exitosamente",
            "total_tasks_synced": total_tasks_synced,
            "new_tasks_created": total_tasks_created,
            "tasks_updated": total_tasks_updated,
            "workspace_id": workspace_id
        }
        
    except Exception as e:
        print(f"❌ Error en sincronización: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en sincronización: {str(e)}"
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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

@router.get("/debug-code")
async def debug_code_version():
    """Debug: Verificar qué versión del código se está ejecutando"""
    import inspect
    
    # Obtener el código fuente de la función create_task_FINAL_VERSION
    try:
        func_source = inspect.getsource(create_task_FINAL_VERSION)
        has_safe_timestamp = "safe_timestamp_to_datetime" in func_source
        has_import_status = "from fastapi import status" in func_source
        
        return {
            "message": "🔍 Debug del código ejecutándose",
            "timestamp": datetime.now().isoformat(),
            "commit_hash": "80f30be0",  # Último commit
            "function_exists": True,
            "has_safe_timestamp": has_safe_timestamp,
            "has_import_status": has_import_status,
            "code_length": len(func_source),
            "first_lines": func_source.split('\n')[:5]
        }
    except Exception as e:
        return {
            "message": "❌ Error obteniendo código fuente",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

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

# ===== ENDPOINT PARA VERIFICAR Y CREAR ESTRUCTURA DE BASE DE DATOS =====
@router.post("/fix-database-structure")
async def fix_database_structure(
    db: Session = Depends(get_db)
):
    """Verificar y crear la estructura correcta de la tabla tasks en PostgreSQL"""
    
    print("🔧 Iniciando verificación y corrección de estructura de base de datos...")
    
    try:
        # Verificar si la tabla tasks existe
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'tasks'
            );
        """))
        
        table_exists = result.scalar()
        print(f"📋 Tabla 'tasks' existe: {'✅ SÍ' if table_exists else '❌ NO'}")
        
        if table_exists:
            # Obtener estructura actual
            result = db.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'tasks' 
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            print(f"🏗️ Estructura actual de la tabla 'tasks':")
            print(f"{'Columna':<20} {'Tipo':<15} {'Nullable':<10} {'Default'}")
            print("-" * 60)
            
            for col in columns:
                col_name, data_type, nullable, default = col
                print(f"{col_name:<20} {data_type:<15} {nullable:<10} {default or 'N/A'}")
            
            # Verificar columnas específicas que necesitamos
            required_columns = [
                'id', 'clickup_id', 'name', 'description', 'status', 'priority',
                'due_date', 'start_date', 'created_at', 'updated_at',
                'workspace_id', 'list_id', 'assignee_id', 'creator_id',
                'tags', 'custom_fields', 'attachments', 'comments',
                'is_synced', 'last_sync'
            ]
            
            existing_columns = [col[0] for col in columns]
            missing_columns = [col for col in required_columns if col not in existing_columns]
            
            print(f"\n🔍 Análisis de columnas:")
            print(f"✅ Columnas existentes: {len(existing_columns)}")
            print(f"❌ Columnas faltantes: {len(missing_columns)}")
            
            if missing_columns:
                print(f"📝 Columnas que faltan: {', '.join(missing_columns)}")
                
                # Recrear la tabla con estructura correcta
                print(f"🔨 Recreando tabla con estructura correcta...")
                
                # Eliminar tabla existente
                db.execute(text("DROP TABLE IF EXISTS tasks CASCADE;"))
                db.commit()
                print(f"✅ Tabla eliminada")
                
                # Crear tabla con estructura correcta
                create_table_sql = """
                CREATE TABLE tasks (
                    id SERIAL PRIMARY KEY,
                    clickup_id VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(500) NOT NULL,
                    description TEXT,
                    status VARCHAR(100) NOT NULL DEFAULT 'to_do',
                    priority INTEGER DEFAULT 3,
                    due_date TIMESTAMP,
                    start_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    workspace_id VARCHAR(255) NOT NULL,
                    list_id VARCHAR(255) NOT NULL,
                    assignee_id VARCHAR(255),
                    creator_id VARCHAR(255) DEFAULT 'system',
                    tags JSONB,
                    custom_fields JSONB,
                    attachments JSONB,
                    comments JSONB,
                    is_synced BOOLEAN DEFAULT FALSE,
                    last_sync TIMESTAMP
                );
                """
                
                db.execute(text(create_table_sql))
                
                # Crear índices para mejor rendimiento
                print(f"📊 Creando índices...")
                db.execute(text("CREATE INDEX idx_tasks_clickup_id ON tasks(clickup_id);"))
                db.execute(text("CREATE INDEX idx_tasks_workspace_id ON tasks(workspace_id);"))
                db.execute(text("CREATE INDEX idx_tasks_list_id ON tasks(list_id);"))
                db.execute(text("CREATE INDEX idx_tasks_status ON tasks(status);"))
                db.execute(text("CREATE INDEX idx_tasks_priority ON tasks(priority);"))
                db.execute(text("CREATE INDEX idx_tasks_is_synced ON tasks(is_synced);"))
                
                db.commit()
                print(f"✅ Tabla 'tasks' recreada exitosamente!")
                print(f"✅ Índices creados para mejor rendimiento")
                
                return {
                    "message": "✅ Estructura de base de datos corregida exitosamente",
                    "action": "table_recreated",
                    "missing_columns": missing_columns,
                    "status": "fixed"
                }
            else:
                print(f"🎉 Todas las columnas necesarias están presentes!")
                return {
                    "message": "✅ Estructura de base de datos ya está correcta",
                    "action": "no_action_needed",
                    "status": "ok"
                }
        else:
            # Crear tabla desde cero
            print(f"🔨 Creando tabla tasks desde cero...")
            
            create_table_sql = """
            CREATE TABLE tasks (
                id SERIAL PRIMARY KEY,
                clickup_id VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(500) NOT NULL,
                description TEXT,
                status VARCHAR(100) NOT NULL DEFAULT 'to_do',
                priority INTEGER DEFAULT 3,
                due_date TIMESTAMP,
                start_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                workspace_id VARCHAR(255) NOT NULL,
                list_id VARCHAR(255) NOT NULL,
                assignee_id VARCHAR(255),
                creator_id VARCHAR(255) DEFAULT 'system',
                tags JSONB,
                custom_fields JSONB,
                attachments JSONB,
                comments JSONB,
                is_synced BOOLEAN DEFAULT FALSE,
                last_sync TIMESTAMP
            );
            """
            
            db.execute(text(create_table_sql))
            
            # Crear índices para mejor rendimiento
            print(f"📊 Creando índices...")
            db.execute(text("CREATE INDEX idx_tasks_clickup_id ON tasks(clickup_id);"))
            db.execute(text("CREATE INDEX idx_tasks_workspace_id ON tasks(workspace_id);"))
            db.execute(text("CREATE INDEX idx_tasks_list_id ON tasks(list_id);"))
            db.execute(text("CREATE INDEX idx_tasks_status ON tasks(status);"))
            db.execute(text("CREATE INDEX idx_tasks_priority ON tasks(priority);"))
            db.execute(text("CREATE INDEX idx_tasks_is_synced ON tasks(is_synced);"))
            
            db.commit()
            print(f"✅ Tabla 'tasks' creada exitosamente!")
            print(f"✅ Índices creados para mejor rendimiento")
            
            return {
                "message": "✅ Tabla tasks creada exitosamente",
                "action": "table_created",
                "status": "created"
            }
        
    except Exception as e:
        print(f"❌ Error corrigiendo estructura de base de datos: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error corrigiendo estructura de base de datos: {str(e)}"
        )
