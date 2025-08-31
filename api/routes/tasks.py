# ===== ARCHIVO COMPLETAMENTE NUEVO - VERSION FINAL =====
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
import asyncio

from core.database import get_db
from core.clickup_client import ClickUpClient, get_clickup_client
from models.task import Task
from user_mapping_config import get_clickup_user_id, CLICKUP_USER_MAPPING, CLICKUP_USER_ID_TO_NAME
from langgraph_tools.sync_workflow import run_sync_workflow
from api.schemas.task import TaskUpdate, TaskResponse

# ===== SISTEMA DE LOGGING AUTOMATICO CON LANGGRAPH =====
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from langgraph_tools.simple_error_logging import log_error_with_graph

# ===== CONFIGURACION DE CAMPOS PERSONALIZADOS =====
# Configuracion de campos personalizados por lista
CUSTOM_FIELD_IDS = {
    "901411770471": {  # PROYECTO 1
        "Email": "6464a671-73dd-4be5-b720-b5f0fe5adb04",  # Campo de referencia para usuario
        "Celular": "51fa0661-0995-4c37-ba8d-3307aef300ca"  # Campo de referencia para usuario
        # NOTA: "Nombre" no existe en ClickUp, "Asignar a" se sincroniza con "Persona asignada" (campo estándar)
    },
    "901411770470": {  # PROYECTO 2
        # Sin campos personalizados
    },
    "901412119767": {  # Tareas del Proyecto
        "Email": "6464a671-73dd-4be5-b720-b5f0fe5adb04",  # Campo de referencia para usuario
        "Celular": "51fa0661-0995-4c37-ba8d-3307aef300ca"  # Campo de referencia para usuario
    }
}

def get_custom_field_id(list_id: str, field_name: str) -> str:
    """Get el ID de un campo personalizado especifico"""
    list_fields = CUSTOM_FIELD_IDS.get(list_id, {})
    
    # Buscar coincidencia exacta primero
    if field_name in list_fields:
        return list_fields[field_name]
    
    # Buscar coincidencia case-insensitive
    for key, value in list_fields.items():
        if key.lower() == field_name.lower():
            return value
    
    return None

async def get_user_email_from_clickup(assignee_id: str, workspace_id: str) -> Optional[str]:
    """Obtener el email de un usuario desde ClickUp"""
    try:
        from core.clickup_client import ClickUpClient
        from core.config import settings
        
        if not settings.CLICKUP_API_TOKEN:
            print(f"❌ No hay token de ClickUp configurado")
            return None
        
        client = ClickUpClient()
        users = await client.get_users(workspace_id)
        
        if not users:
            return None
        
        # Buscar el usuario por ID
        for user in users:
            if isinstance(user, dict) and "user" in user:
                user_data = user["user"]
                if str(user_data.get("id")) == str(assignee_id):
                    email = user_data.get("email")
                    if email:
                        print(f"✅ Email del usuario {assignee_id} encontrado: {email}")
                        return email
        
        print(f"⚠️ Usuario {assignee_id} no encontrado o sin email")
        return None
        
    except Exception as e:
        print(f"❌ Error obteniendo email del usuario {assignee_id}: {e}")
        return None

def has_custom_fields(list_id: str) -> bool:
    """Verificar si una lista tiene campos personalizados"""
    return bool(CUSTOM_FIELD_IDS.get(list_id, {}))

async def update_custom_fields_direct(clickup_client: ClickUpClient, task_id: str, list_id: str, custom_fields: Dict[str, Any]):
    """Funcion de fallback para actualizar campos personalizados directamente"""
    print(f"   🔄 Actualizacion directa de campos personalizados...")
    
    updated_fields = {}
    errors = []
    plan_limit_warnings = []
    
    for field_name, field_value in custom_fields.items():
        field_id = get_custom_field_id(list_id, field_name)
        if field_id:
            try:
                print(f"      📝 Actualizando {field_name} (ID: {field_id}) con valor: {field_value}")
                result = await clickup_client.update_custom_field_value(task_id, field_id, field_value)
                updated_fields[field_name] = {
                    "status": "success",
                    "field_id": field_id,
                    "result": result
                }
                print(f"      ✅ Campo {field_name} actualizado exitosamente")
            except Exception as e:
                error_str = str(e)
                
                # Detectar error específico de límite del plan
                if "FIELD_033" in error_str or "Custom field usages exceeded for your plan" in error_str:
                    error_msg = f"LÍMITE DEL PLAN CLICKUP: {field_name} no se pudo actualizar (plan gratuito excedido)"
                    plan_limit_warnings.append(field_name)
                    print(f"      ⚠️ {error_msg}")
                    print(f"      💡 SOLUCIÓN: Actualizar a plan de pago o esperar reset mensual")
                else:
                    error_msg = f"Error updating {field_name}: {error_str}"
                    print(f"      ❌ {error_msg}")
                
                errors.append(error_msg)
                updated_fields[field_name] = {
                    "status": "error",
                    "field_id": field_id,
                    "error": error_msg
                }
        else:
            error_msg = f"No se encontro ID para el campo: {field_name}"
            errors.append(error_msg)
            updated_fields[field_name] = {
                "status": "error",
                "field_id": None,
                "error": error_msg
            }
            print(f"      ⚠️ {error_msg}")
    
    success_count = len([f for f in updated_fields.values() if f["status"] == "success"])
    error_count = len([f for f in updated_fields.values() if f["status"] == "error"])
    
    print(f"   📊 Resumen de actualizacion directa:")
    print(f"      ✅ Campos actualizados: {success_count}")
    print(f"      ❌ Errores: {error_count}")
    
    # Mostrar advertencias específicas del plan
    if plan_limit_warnings:
        print(f"   🚨 ADVERTENCIA DEL PLAN CLICKUP:")
        print(f"      📋 Campos afectados: {', '.join(plan_limit_warnings)}")
        print(f"      💡 Soluciones:")
        print(f"         • Actualizar a plan de pago")
        print(f"         • Esperar reset mensual del plan gratuito")
        print(f"         • Usar menos campos personalizados")
    
    return {
        "updated_fields": updated_fields,
        "success_count": success_count,
        "error_count": error_count,
        "errors": errors,
        "plan_limit_warnings": plan_limit_warnings
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
    assignee_id: Optional[str] = None
    due_date: Optional[str] = None
    custom_fields: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = {}

# Usar TaskResponse del schema en lugar de definición duplicada
from api.schemas.task import TaskResponse

router = APIRouter()

# ===== FUNCION AUXILIAR NECESARIA =====
def safe_timestamp_to_datetime(timestamp_value) -> Optional[datetime]:
    """HOTFIX: Convertir timestamp a datetime de forma segura"""
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
        
        # Si es int/float, ClickUp usa milisegundos, dividir por 1000
        if isinstance(timestamp_value, (int, float)):
            # ClickUp usa timestamps en milisegundos, convertir a segundos
            timestamp_seconds = timestamp_value / 1000
            return datetime.fromtimestamp(timestamp_seconds)
        
        return None
    except Exception as e:
        print(f"Error en safe_timestamp_to_datetime: {e}")
        return None

def safe_get_assignee_id(assignees_data) -> Optional[str]:
    """Obtener el ID del asignado de forma segura"""
    if not assignees_data:
        return None
    
    try:
        if isinstance(assignees_data, list) and len(assignees_data) > 0:
            assignee = assignees_data[0]
            if isinstance(assignee, dict):
                return assignee.get("id")
        elif isinstance(assignees_data, dict):
            return assignees_data.get("id")
        return None
    except Exception:
        return None

def safe_get_creator_id(creator_data) -> str:
    """Obtener el ID del creador de forma segura"""
    if not creator_data:
        return "system"
    
    try:
        if isinstance(creator_data, dict):
            return creator_data.get("id", "system")
        return str(creator_data)
    except Exception:
        return "system"

def safe_get_status(status_data) -> str:
    """Obtener el estado de forma segura"""
    if not status_data:
        return "to do"
    
    try:
        if isinstance(status_data, dict):
            return status_data.get("status", "to do")
        return str(status_data)
    except Exception:
        return "to do"

# ===== FUNCION COMPLETAMENTE NUEVA =====
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task_FINAL_VERSION(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    clickup_client: ClickUpClient = Depends(get_clickup_client)
):
    """Create una nueva tarea en ClickUp y sincronizar con BD local"""
    print(f"🔍 Creando tarea: {task_data.name}")
    print(f"📋 Datos recibidos: {task_data.dict()}")
    
    # Verificar configuracion
    if not clickup_client.api_token:
        print(f"❌ ERROR: No hay token de ClickUp configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No hay token de ClickUp configured"
        )
    
    try:
        # Procesar el usuario asignado
        clickup_assignee_id = None
        if task_data.assignee_id:
            # Verificar si es un ID de ClickUp o un nombre de usuario
            if task_data.assignee_id in CLICKUP_USER_ID_TO_NAME:
                # Es un ID de ClickUp válido
                clickup_assignee_id = task_data.assignee_id
                print(f"   👤 ID de ClickUp válido: {clickup_assignee_id} -> {CLICKUP_USER_ID_TO_NAME[clickup_assignee_id]}")
            elif task_data.assignee_id in CLICKUP_USER_MAPPING:
                # Es un nombre de usuario, convertirlo a ID
                clickup_assignee_id = CLICKUP_USER_MAPPING[task_data.assignee_id]
                print(f"   👤 Usuario '{task_data.assignee_id}' mapeado a ID ClickUp: {clickup_assignee_id}")
            else:
                print(f"   ⚠️ Usuario '{task_data.assignee_id}' no encontrado en el mapeo")
                print(f"   📋 IDs válidos: {list(CLICKUP_USER_ID_TO_NAME.keys())}")
                print(f"   📋 Nombres válidos: {list(CLICKUP_USER_MAPPING.keys())}")
        
        # Mapear el estado antes de enviarlo a ClickUp
        status_mapping = {
            "to do": "pendiente",
            "todo": "pendiente", 
            "pending": "pendiente",
            "pendiente": "pendiente",
            "in progress": "en curso",
            "in_progress": "en curso",
            "en curso": "en curso",
            "en progreso": "en progreso",
            "working": "en curso",
            "active": "en curso",
            "review": "en curso",
            "testing": "en curso",
            "complete": "completado",
            "completed": "completado",
            "completado": "completado",
            "done": "completado"
        }
        
        # Obtener el estado mapeado para ClickUp
        clickup_status = status_mapping.get(task_data.status.lower(), "pendiente")
        print(f"   🔄 Estado mapeado: {task_data.status} -> {clickup_status}")
        
        # Obtener automáticamente el email del usuario asignado
        user_email = None
        if clickup_assignee_id:
            user_email = await get_user_email_from_clickup(clickup_assignee_id, task_data.workspace_id)
            if user_email:
                print(f"✅ Email del usuario asignado obtenido automáticamente: {user_email}")
            else:
                print(f"⚠️ No se pudo obtener el email del usuario asignado")
        
        # Preparar campos personalizados incluyendo el email del usuario asignado
        custom_fields = task_data.custom_fields or {}
        if user_email:
            custom_fields["Email"] = user_email
            print(f"📧 Campo Email agregado automáticamente: {user_email}")
        
        # Preparar datos para ClickUp
        clickup_task_data = {
            "name": task_data.name,
            "description": task_data.description or "",
            "status": clickup_status,  # Estado ya mapeado para ClickUp
            "priority": task_data.priority or 3,
            "due_date": int(datetime.strptime(task_data.due_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59).timestamp() * 1000) if task_data.due_date else None,
            "assignees": [clickup_assignee_id] if clickup_assignee_id else [],  # Campo "Asignar a" → "Persona asignada"
            "custom_fields": custom_fields
        }
        
        print(f"🔍 Campo 'Asignar a' configurado para sincronizar con 'Persona asignada' en ClickUp")
        print(f"   📋 assignees: {clickup_task_data['assignees']}")
        
        print(f"🔍 Enviando datos a ClickUp: {clickup_task_data}")
        
        # Create tarea en ClickUp
        clickup_response = await clickup_client.create_task(task_data.list_id, clickup_task_data)
        
        if not clickup_response or "id" not in clickup_response:
            raise Exception("No se recibio ID de tarea de ClickUp")
        
        clickup_task_id = clickup_response["id"]
        print(f"✅ Tarea creada en ClickUp con ID: {clickup_task_id}")
        
        # ===== ACTUALIZACION AUTOMATICA DE CAMPOS PERSONALIZADOS =====
        print(f"🔍 DEBUG: Verificando actualización automática...")
        print(f"   📋 task_data.custom_fields: {task_data.custom_fields}")
        print(f"   🏷️ task_data.list_id: {task_data.list_id}")
        print(f"   🔍 has_custom_fields({task_data.list_id}): {has_custom_fields(task_data.list_id)}")
        print(f"   ✅ bool(task_data.custom_fields): {bool(task_data.custom_fields)}")
        print(f"   🔍 has_custom_fields({task_data.list_id}): {has_custom_fields(task_data.list_id)}")
        print(f"   ✅ Condicion completa: {bool(task_data.custom_fields) and has_custom_fields(task_data.list_id)}")
        
        # ===== ACTUALIZACION POST-CREACION COMPLETA =====
        # Update TODOS los campos despues de crear la tarea
        print(f"🔄 Iniciando actualización post-creación completa...")
        
        # 1. ACTUALIZAR ESTADO DE LA TAREA (solo si es diferente al enviado inicialmente)
        if task_data.status and task_data.status.lower() != "pendiente":
            try:
                # Mapear estados a los que ClickUp reconoce EXACTAMENTE
                status_mapping = {
                    "to do": "pendiente",
                    "todo": "pendiente", 
                    "pending": "pendiente",
                    "pendiente": "pendiente",
                    "in progress": "en curso",
                    "in_progress": "en curso",
                    "en curso": "en curso",
                    "en progreso": "en progreso",
                    "working": "en curso",
                    "active": "en curso",
                    "review": "en curso",
                    "testing": "en curso",
                    "complete": "completado",
                    "completed": "completado",
                    "completado": "completado",
                    "done": "completado"
                }
                
                clickup_status = status_mapping.get(task_data.status.lower(), "pendiente")
                print(f"   🔄 Actualizando estado a: {task_data.status} -> {clickup_status}")
                
                await clickup_client.update_task(clickup_task_id, {"status": clickup_status})
                print(f"   ✅ Estado actualizado exitosamente")
            except Exception as e:
                print(f"   ❌ Error updating estado: {e}")
                print(f"   ❌ Detalles del error: {type(e).__name__}: {str(e)}")
        else:
            print(f"   ℹ️ Estado ya correcto en ClickUp: {clickup_status}")
        
        # 2. ACTUALIZAR PRIORIDAD
        if task_data.priority and task_data.priority != 3:
            try:
                print(f"   🔄 Actualizando prioridad a: {task_data.priority}")
                await clickup_client.update_task(clickup_task_id, {"priority": task_data.priority})
                print(f"   ✅ Prioridad actualizada exitosamente")
            except Exception as e:
                print(f"   ❌ Error updating prioridad: {e}")
        
        # 3. ACTUALIZAR CAMPOS PERSONALIZADOS (solo los que existen en ClickUp)
        if task_data.custom_fields:
            print(f"   📝 Actualizando campos personalizados...")
            print(f"   📋 Campos a procesar: {task_data.custom_fields}")
            print(f"   🏷️ Lista: {task_data.list_id}")
            
            # Filtrar solo campos personalizados que existen en ClickUp
            available_custom_fields = {}
            for field_name, field_value in task_data.custom_fields.items():
                if get_custom_field_id(task_data.list_id, field_name):
                    available_custom_fields[field_name] = field_value
                    print(f"   ✅ Campo '{field_name}' disponible en ClickUp")
                else:
                    print(f"   ⚠️ Campo '{field_name}' NO existe en ClickUp - se omite")
            
            if available_custom_fields:
                print(f"   📋 Campos válidos para actualizar: {available_custom_fields}")
                
                # Verificar si la lista tiene campos personalizados configureds
                if has_custom_fields(task_data.list_id):
                    print(f"   ✅ Lista tiene campos personalizados configurados")
                    
                    # Usar directamente la funcion de actualizacion directa
                    try:
                        print(f"   🚀 Ejecutando actualización directa de campos personalizados...")
                        update_result = await update_custom_fields_direct(clickup_client, clickup_task_id, task_data.list_id, available_custom_fields)
                        
                        success_count = update_result.get('success_count', 0)
                        error_count = update_result.get('error_count', 0)
                        
                        print(f"   ✅ Actualización de campos personalizados completada!")
                        print(f"   ✅ Campos actualizados: {success_count}")
                        print(f"   ❌ Errores: {error_count}")
                        
                        if error_count > 0:
                            print(f"   ⚠️ Algunos campos no se pudieron actualizar")
                            print(f"   ❌ Errores: {update_result.get('errors', [])}")
                        
                    except Exception as update_error:
                        print(f"   ❌ Error en actualizacion de campos personalizados: {update_error}")
                        print(f"   🔍 Tipo de error: {type(update_error)}")
                        # No fallar la creacion por error en campos personalizados
                else:
                    print(f"   ⚠️ La lista {task_data.list_id} no tiene campos personalizados configurados")
                    print(f"   📋 Campos disponibles: {CUSTOM_FIELD_IDS.get(task_data.list_id, {})}")
            else:
                print(f"   ℹ️ No hay campos personalizados válidos para actualizar")
                print(f"   💡 Todos los campos enviados no existen en ClickUp")
        else:
            print(f"ℹ️ No hay campos personalizados para actualizar")
            print(f"   ℹ️ task_data.custom_fields esta vacio")
        
        print(f"✅ Actualización post-creación completada!")
        
        # Guardar en BD local
        new_task = Task(
            clickup_id=clickup_task_id,
            name=task_data.name,
            description=task_data.description or "",
            status=task_data.status or "to do",
            priority=task_data.priority or 3,
            due_date=datetime.strptime(task_data.due_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59) if task_data.due_date else None,
            workspace_id=task_data.workspace_id,
            list_id=task_data.list_id,
            assignee_id=task_data.assignee_id,
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
        
        # ===== ENVIO DE NOTIFICACIONES WHATSAPP =====
        print(f"📱 Verificando notificaciones WhatsApp...")
        try:
            # Importar el servicio de WhatsApp
            from core.whatsapp_client import WhatsAppNotificationService
            from core.phone_extractor import extract_whatsapp_numbers_from_task
            
            # Crear instancia del servicio
            whatsapp_service = WhatsAppNotificationService()
            
            if whatsapp_service.enabled:
                # Extraer números de teléfono desde los custom_fields y description
                task_info = {
                    "description": task_data.description or "",
                    "custom_fields": task_data.custom_fields or {}
                }
                
                whatsapp_numbers = extract_whatsapp_numbers_from_task(task_info)
                
                if whatsapp_numbers:
                    print(f"📱 Números WhatsApp encontrados: {whatsapp_numbers}")
                    
                    # Enviar notificación a cada número
                    for phone_number in whatsapp_numbers:
                        try:
                            result = await whatsapp_service.send_task_notification(
                                phone_number=phone_number,
                                task_name=task_data.name,
                                task_description=task_data.description or "",
                                due_date=task_data.due_date,
                                assignee_name=CLICKUP_USER_ID_TO_NAME.get(task_data.assignee_id, "Sin asignar")
                            )
                            
                            if result.success:
                                print(f"✅ WhatsApp enviado exitosamente a {phone_number}")
                            else:
                                print(f"❌ Error enviando WhatsApp a {phone_number}: {result.error}")
                                
                        except Exception as whatsapp_error:
                            print(f"❌ Error enviando WhatsApp a {phone_number}: {whatsapp_error}")
                else:
                    print(f"ℹ️ No se encontraron números de WhatsApp en la tarea")
            else:
                print(f"ℹ️ Notificaciones WhatsApp deshabilitadas")
                
        except Exception as e:
            print(f"⚠️ Error en el sistema de notificaciones WhatsApp: {e}")
            # No fallar la creación de tarea por error en WhatsApp
        
        return new_task
        
    except Exception as e:
        print(f"❌ Error al crear la tarea: {e}")
        
        # ===== LOGGING AUTOMATICO CON LANGGRAPH =====
        try:
            log_error_with_graph({
                "error_description": f"Error crear tarea: {str(e)}",
                "solution_description": "Verificar CLICKUP_API_TOKEN y datos de entrada",
                "context_info": f"Tarea: {task_data.name}, Lista: {task_data.list_id}, Workspace: {task_data.workspace_id}",
                "deployment_id": "railway-production",
                "environment": "production",
                "severity": "high",
                "status": "pending"
            })
        except Exception as logging_error:
            print(f"⚠️ Error en logging automatico: {logging_error}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error crear la tarea: {str(e)}"
        )

# ===== ENDPOINT PUT PARA ACTUALIZAR TAREAS =====
@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    clickup_client: ClickUpClient = Depends(get_clickup_client)
):
    """Actualizar tarea en ClickUp y sincronizar localmente"""
    print(f"🔄 Actualizando tarea: {task_id}")
    print(f"📋 Datos de actualización: {task_update.dict(exclude_unset=True)}")
    
    try:
        # Buscar la tarea en la base de datos local
        local_task = db.query(Task).filter(Task.clickup_id == task_id).first()
        if not local_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarea {task_id} no encontrada en la base de datos local"
            )
        
        # Preparar datos para actualización en ClickUp
        clickup_update_data = {}
        
        # Mapear campos básicos
        if task_update.name is not None:
            clickup_update_data["name"] = task_update.name
        if task_update.description is not None:
            clickup_update_data["description"] = task_update.description
        if task_update.priority is not None:
            clickup_update_data["priority"] = task_update.priority
        if task_update.due_date is not None:
            # Convertir due_date a timestamp de ClickUp
            if isinstance(task_update.due_date, str):
                try:
                    due_date_obj = datetime.strptime(task_update.due_date, "%Y-%m-%d")
                    clickup_update_data["due_date"] = int(due_date_obj.replace(hour=23, minute=59, second=59).timestamp() * 1000)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Formato de fecha inválido. Use YYYY-MM-DD"
                    )
            elif isinstance(task_update.due_date, datetime):
                clickup_update_data["due_date"] = int(task_update.due_date.timestamp() * 1000)
            elif isinstance(task_update.due_date, int):
                clickup_update_data["due_date"] = task_update.due_date
        
        # Mapear estado si se proporciona
        if task_update.status is not None:
            status_mapping = {
                "to do": "pendiente",
                "todo": "pendiente", 
                "pending": "pendiente",
                "pendiente": "pendiente",
                "in progress": "en curso",
                "in_progress": "en curso",
                "en curso": "en curso",
                "en progreso": "en progreso",
                "working": "en curso",
                "active": "en curso",
                "review": "en curso",
                "testing": "en curso",
                "complete": "completado",
                "completed": "completado",
                "completado": "completado",
                "done": "completado"
            }
            clickup_status = status_mapping.get(task_update.status.lower(), "pendiente")
            clickup_update_data["status"] = clickup_status
            print(f"   🔄 Estado mapeado: {task_update.status} -> {clickup_status}")
        
        # Mapear asignado si se proporciona
        if task_update.assignee_id is not None:
            clickup_assignee_id = None
            if task_update.assignee_id in CLICKUP_USER_ID_TO_NAME:
                clickup_assignee_id = task_update.assignee_id
            elif task_update.assignee_id in CLICKUP_USER_MAPPING:
                clickup_assignee_id = CLICKUP_USER_MAPPING[task_update.assignee_id]
            
            if clickup_assignee_id:
                clickup_update_data["assignees"] = [clickup_assignee_id]
                print(f"   👤 Asignado actualizado: {task_update.assignee_id} -> {clickup_assignee_id}")
            else:
                print(f"   ⚠️ Usuario '{task_update.assignee_id}' no encontrado en el mapeo")
        
        # Actualizar en ClickUp si hay cambios
        if clickup_update_data:
            print(f"🚀 Enviando actualización a ClickUp: {clickup_update_data}")
            try:
                clickup_response = await clickup_client.update_task(task_id, clickup_update_data)
                print(f"✅ Tarea actualizada exitosamente en ClickUp")
            except Exception as e:
                print(f"❌ Error actualizando en ClickUp: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error actualizando tarea en ClickUp: {str(e)}"
                )
        else:
            print(f"ℹ️ No hay cambios para enviar a ClickUp")
        
        # Actualizar campos personalizados si se proporcionan
        if task_update.custom_fields:
            print(f"📝 Actualizando campos personalizados...")
            try:
                # Verificar si la lista tiene campos personalizados configurados
                if has_custom_fields(local_task.list_id):
                    update_result = await update_custom_fields_direct(
                        clickup_client, 
                        task_id, 
                        local_task.list_id, 
                        task_update.custom_fields
                    )
                    
                    success_count = update_result.get('success_count', 0)
                    error_count = update_result.get('error_count', 0)
                    
                    print(f"✅ Campos personalizados actualizados: {success_count} exitosos, {error_count} errores")
                    
                    if error_count > 0:
                        print(f"⚠️ Errores en campos personalizados: {update_result.get('errors', [])}")
                else:
                    print(f"ℹ️ La lista no tiene campos personalizados configurados")
            except Exception as e:
                print(f"⚠️ Error actualizando campos personalizados: {e}")
                # No fallar la actualización por error en campos personalizados
        
        # Actualizar base de datos local
        if task_update.name is not None:
            local_task.name = task_update.name
        if task_update.description is not None:
            local_task.description = task_update.description
        if task_update.status is not None:
            local_task.status = task_update.status
        if task_update.priority is not None:
            local_task.priority = task_update.priority
        if task_update.due_date is not None:
            if isinstance(task_update.due_date, str):
                local_task.due_date = datetime.strptime(task_update.due_date, "%Y-%m-%d")
            elif isinstance(task_update.due_date, datetime):
                local_task.due_date = task_update.due_date
            elif isinstance(task_update.due_date, int):
                local_task.due_date = datetime.fromtimestamp(task_update.due_date / 1000)
        if task_update.assignee_id is not None:
            local_task.assignee_id = task_update.assignee_id
        if task_update.custom_fields is not None:
            local_task.custom_fields = task_update.custom_fields
        
        local_task.updated_at = datetime.now()
        local_task.is_synced = True
        local_task.last_sync = datetime.now()
        
        db.commit()
        db.refresh(local_task)
        
        print(f"✅ Tarea actualizada exitosamente en base de datos local")
        
        # ===== ENVIO DE NOTIFICACIONES WHATSAPP =====
        print(f"📱 Verificando notificaciones WhatsApp...")
        try:
            from core.whatsapp_client import WhatsAppNotificationService
            from core.phone_extractor import extract_whatsapp_numbers_from_task
            
            whatsapp_service = WhatsAppNotificationService()
            
            if whatsapp_service.enabled:
                # Extraer números de teléfono desde la descripción y campos personalizados
                task_info = {
                    "description": local_task.description or "",
                    "custom_fields": local_task.custom_fields or {}
                }
                
                whatsapp_numbers = extract_whatsapp_numbers_from_task(task_info)
                
                if whatsapp_numbers:
                    print(f"📱 Números WhatsApp encontrados: {whatsapp_numbers}")
                    
                    # Enviar notificación de actualización a cada número
                    for phone_number in whatsapp_numbers:
                        try:
                            result = await whatsapp_service.send_task_notification(
                                phone_number=phone_number,
                                task_name=local_task.name,
                                task_description=local_task.description or "",
                                due_date=local_task.due_date.isoformat() if local_task.due_date else None,
                                assignee_name=CLICKUP_USER_ID_TO_NAME.get(local_task.assignee_id, "Sin asignar"),
                                notification_type="updated"
                            )
                            
                            if result.success:
                                print(f"✅ WhatsApp de actualización enviado exitosamente a {phone_number}")
                            else:
                                print(f"❌ Error enviando WhatsApp de actualización a {phone_number}: {result.error}")
                                
                        except Exception as whatsapp_error:
                            print(f"❌ Error enviando WhatsApp de actualización a {phone_number}: {whatsapp_error}")
                else:
                    print(f"ℹ️ No se encontraron números de WhatsApp en la tarea")
            else:
                print(f"ℹ️ Notificaciones WhatsApp deshabilitadas")
                
        except Exception as e:
            print(f"⚠️ Error en el sistema de notificaciones WhatsApp: {e}")
            # No fallar la actualización por error en WhatsApp
        
        # Convertir a TaskResponse para la respuesta
        from api.schemas.task import TaskResponse
        
        response_data = {
            "id": local_task.id,
            "clickup_id": local_task.clickup_id,
            "name": local_task.name,
            "description": local_task.description,
            "status": local_task.status,
            "priority": local_task.priority,
            "due_date": local_task.due_date,
            "start_date": local_task.start_date,
            "assignee_id": local_task.assignee_id,
            "assignee_name": CLICKUP_USER_ID_TO_NAME.get(local_task.assignee_id, "Sin asignar"),
            "list_name": "Lista",  # TODO: Obtener nombre real de la lista
            "workspace_name": "Workspace",  # TODO: Obtener nombre real del workspace
            "tags": local_task.tags,
            "custom_fields": local_task.custom_fields,
            "workspace_id": local_task.workspace_id,
            "list_id": local_task.list_id,
            "creator_id": local_task.creator_id,
            "created_at": local_task.created_at,
            "updated_at": local_task.updated_at,
            "attachments": local_task.attachments,
            "comments": local_task.comments,
            "is_synced": local_task.is_synced,
            "last_sync": local_task.last_sync
        }
        
        return TaskResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error al actualizar la tarea: {e}")
        
        # ===== LOGGING AUTOMATICO CON LANGGRAPH =====
        try:
            log_error_with_graph({
                "error_description": f"Error actualizar tarea: {str(e)}",
                "solution_description": "Verificar CLICKUP_API_TOKEN y datos de entrada",
                "context_info": f"Tarea: {task_id}, Datos: {task_update.dict(exclude_unset=True)}",
                "deployment_id": "railway-production",
                "environment": "production",
                "severity": "high",
                "status": "pending"
            })
        except Exception as logging_error:
            print(f"⚠️ Error en logging automatico: {logging_error}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la tarea: {str(e)}"
        )

# ===== ENDPOINT PARA DIAGNOSTICAR PROBLEMAS DE CAMPOS PERSONALIZADOS =====
@router.get("/custom-fields/status", response_model=dict)
async def get_custom_fields_status(
    list_id: str = Query(..., description="ID de la lista para verificar"),
    clickup_client: ClickUpClient = Depends(get_clickup_client)
):
    """Verificar el estado de los campos personalizados de una lista"""
    try:
        print(f"🔍 Verificando estado de campos personalizados para lista: {list_id}")
        
        # Verificar si la lista tiene campos personalizados configurados
        if not has_custom_fields(list_id):
            return {
                "status": "error",
                "message": f"La lista {list_id} no tiene campos personalizados configurados",
                "available_fields": CUSTOM_FIELD_IDS.get(list_id, {}),
                "suggestions": [
                    "Verificar que la lista esté en CUSTOM_FIELD_IDS",
                    "Agregar campos personalizados a la configuración"
                ]
            }
        
        # Obtener campos disponibles
        available_fields = CUSTOM_FIELD_IDS.get(list_id, {})
        
        # Verificar cada campo
        field_status = {}
        for field_name, field_id in available_fields.items():
            try:
                # Intentar hacer una petición de prueba
                test_response = await clickup_client._make_request("GET", f"list/{list_id}/field/{field_id}")
                field_status[field_name] = {
                    "field_id": field_id,
                    "status": "available",
                    "details": "Campo disponible y accesible"
                }
            except Exception as e:
                error_str = str(e)
                if "FIELD_033" in error_str or "Custom field usages exceeded" in error_str:
                    field_status[field_name] = {
                        "field_id": field_id,
                        "status": "plan_limit_exceeded",
                        "details": "Límite del plan gratuito excedido",
                        "solution": "Actualizar a plan de pago o esperar reset mensual"
                    }
                elif "404" in error_str:
                    field_status[field_name] = {
                        "field_id": field_id,
                        "status": "not_found",
                        "details": "Campo no encontrado en ClickUp",
                        "solution": "Verificar que el campo existe en la lista"
                    }
                else:
                    field_status[field_name] = {
                        "field_id": field_id,
                        "status": "error",
                        "details": f"Error desconocido: {error_str}",
                        "solution": "Contactar soporte técnico"
                    }
        
        return {
            "status": "success",
            "list_id": list_id,
            "available_fields": available_fields,
            "field_status": field_status,
            "recommendations": [
                "Si hay campos con 'plan_limit_exceeded': actualizar a plan de pago",
                "Si hay campos con 'not_found': verificar configuración en ClickUp",
                "Los campos con 'available' funcionan correctamente"
            ]
        }
        
    except Exception as e:
        print(f"❌ Error verificando campos personalizados: {e}")
        return {
            "status": "error",
            "message": f"Error verificando campos personalizados: {str(e)}",
            "list_id": list_id
        }

# ===== ENDPOINT PARA ACTUALIZAR CAMPOS PERSONALIZADOS MANUALMENTE =====
@router.post("/{task_id}/update-custom-fields", response_model=dict)
async def update_task_custom_fields(
    task_id: str,
    custom_fields: Dict[str, Any],
    list_id: str,
    clickup_client: ClickUpClient = Depends(get_clickup_client)
):
    """Update campos personalizados de una tarea especifica"""
    print(f"🔄 Actualizando campos personalizados para tarea: {task_id}")
    print(f"📋 Campos: {custom_fields}")
    print(f"🏷️ Lista: {list_id}")
    
    try:
        if not has_custom_fields(list_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La lista {list_id} no tiene campos personalizados configureds"
            )
        
        updated_fields = {}
        errors = []
        
        for field_name, field_value in custom_fields.items():
            field_id = get_custom_field_id(list_id, field_name)
            if field_id:
                try:
                    print(f"   📝 Actualizando {field_name} (ID: {field_id}) con valor: {field_value}")
                    result = await clickup_client.update_custom_field_value(task_id, field_id, field_value)
                    updated_fields[field_name] = {
                        "status": "success",
                        "field_id": field_id,
                        "result": result
                    }
                    print(f"   ✅ Campo {field_name} actualizado exitosamente")
                except Exception as e:
                    error_msg = f"Error updating {field_name}: {str(e)}"
                    errors.append(error_msg)
                    updated_fields[field_name] = {
                        "status": "error",
                        "field_id": field_id,
                        "error": str(e)
                    }
                    print(f"   ❌ {error_msg}")
            else:
                error_msg = f"No se encontro ID para el campo: {field_name}"
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
        print(f"❌ Error updating campos personalizados: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating campos personalizados: {str(e)}"
        )

# ===== ENDPOINT DE SINCRONIZACION DE EMERGENCIA =====
@router.post("/sync-emergency")
async def sync_tasks_emergency(workspace_id: str = Query(None, description="ID del workspace de ClickUp")):
    """Sincronización de emergencia - más robusta y con mejor manejo de errores"""
    try:
        # Si no se proporciona workspace_id, usar el por defecto
        if not workspace_id or workspace_id.strip() == "":
            workspace_id = "9014943317"  # Workspace por defecto
            print(f"🆘 Usando workspace ID por defecto para sincronización de emergencia: {workspace_id}")
        
        print(f"🆘 INICIANDO SINCRONIZACIÓN DE EMERGENCIA para workspace: {workspace_id}")
        
        # Usar el sistema simplificado con manejo de errores mejorado
        try:
            from core.simple_sync import simple_sync_service
            
            # Configurar timeout más largo para emergencia
            result = await asyncio.wait_for(
                simple_sync_service.sync_workspace_tasks(workspace_id),
                timeout=300  # 5 minutos
            )
            
            print(f"✅ SINCRONIZACIÓN DE EMERGENCIA COMPLETADA: {result}")
            
            # Logging automático del resultado
            try:
                log_error_with_graph({
                    "error_description": f"Sincronización de emergencia completada: {result.get('total_tasks_synced', 0)} tareas",
                    "solution_description": "Sistema de sincronización funcionando correctamente",
                    "context_info": f"Endpoint: POST /sync-emergency, Workspace: {workspace_id}, Resultado: {result}",
                    "deployment_id": "railway-production",
                    "environment": "production",
                    "severity": "info",
                    "status": "resolved"
                })
            except Exception as logging_error:
                print(f"⚠️ Error en logging automático: {logging_error}")
            
            return {
                "status": "emergency_sync_completed",
                "message": "Sincronización de emergencia completada exitosamente",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except asyncio.TimeoutError:
            error_msg = "Sincronización de emergencia excedió el tiempo límite (5 minutos)"
            print(f"❌ {error_msg}")
            
            # Logging del timeout
            try:
                log_error_with_graph({
                    "error_description": error_msg,
                    "solution_description": "Verificar conexión a ClickUp y optimizar consultas",
                    "context_info": f"Endpoint: POST /sync-emergency, Workspace: {workspace_id}, Timeout: 300s",
                    "deployment_id": "railway-production",
                    "environment": "production",
                    "severity": "high",
                    "status": "pending"
                })
            except Exception as logging_error:
                print(f"⚠️ Error en logging automático: {logging_error}")
            
            raise HTTPException(status_code=408, detail=error_msg)
            
        except ImportError:
            error_msg = "Sistema de sincronización simplificado no disponible"
            print(f"❌ {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error crítico en sincronización de emergencia: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Logging del error crítico
        try:
            log_error_with_graph({
                "error_description": f"Error crítico en sincronización de emergencia: {str(e)}",
                "solution_description": "Revisar configuración completa del sistema",
                "context_info": f"Endpoint: POST /sync-emergency, Workspace: {workspace_id}, Error: {str(e)}",
                "deployment_id": "railway-production",
                "environment": "production",
                "severity": "critical",
                "status": "pending"
            })
        except Exception as logging_error:
            print(f"⚠️ Error en logging automático: {logging_error}")
        
        raise HTTPException(status_code=500, detail=error_msg)

# ===== ENDPOINT DE SINCRONIZACION CON PARAMETROS =====
@router.post("/sync")
async def sync_tasks(workspace_id: str = Query(None, description="ID del workspace de ClickUp")):
    """Sincronizar tareas desde ClickUp usando sistema simplificado"""
    try:
        # Si no se proporciona workspace_id, usar el por defecto
        if not workspace_id or workspace_id.strip() == "":
            # Obtener el primer workspace disponible
            try:
                clickup_client = ClickUpClient()
                workspaces = await clickup_client.get_workspaces()
                if workspaces and len(workspaces) > 0:
                    workspace_id = workspaces[0]["id"]
                    print(f"🔄 Usando workspace por defecto: {workspace_id}")
                else:
                    # Fallback al workspace ID hardcodeado
                    workspace_id = "9014943317"
                    print(f"🔄 Usando workspace ID hardcodeado: {workspace_id}")
            except Exception as e:
                print(f"⚠️ Error obteniendo workspace automáticamente: {e}")
                # Fallback al workspace ID hardcodeado
                workspace_id = "9014943317"
                print(f"🔄 Usando workspace ID hardcodeado como fallback: {workspace_id}")
        
        print(f"🔄 Iniciando sincronización de tareas para workspace: {workspace_id}")
        
        # Usar el nuevo sistema de sincronización simplificado
        try:
            from core.simple_sync import simple_sync_service
            result = await simple_sync_service.sync_workspace_tasks(workspace_id)
            print(f"✅ Sincronización completada: {result}")
            return result
        except ImportError:
            # Fallback al sistema anterior si no está disponible
            print("⚠️ Sistema simplificado no disponible, usando LangGraph workflow")
            result = await run_sync_workflow(workspace_id)
            print(f"✅ Sincronización completada: {result}")
            return result
        
    except HTTPException:
        # Re-lanzar HTTPExceptions sin modificar
        raise
    except Exception as e:
        error_msg = f"Error en sincronización: {str(e)}"
        print(f"❌ {error_msg}")
        
        # ===== LOGGING AUTOMATICO CON LANGGRAPH =====
        try:
            log_error_with_graph({
                "error_description": f"Error en sincronización: {str(e)}",
                "solution_description": "Verificar conexión a ClickUp y base de datos",
                "context_info": f"Endpoint: POST /sync, Workspace: {workspace_id}, Timestamp: {datetime.now()}",
                "deployment_id": "railway-production",
                "environment": "production",
                "severity": "high",
                "status": "pending"
            })
        except Exception as logging_error:
            print(f"⚠️ Error en logging automático: {logging_error}")
        
        raise HTTPException(status_code=500, detail=error_msg)

# ===== ENDPOINT GET PARA LISTAR TAREAS =====
@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    include_closed: bool = Query(True, description="Incluir tareas cerradas"),
    page: int = Query(0, description="Número de página"),
    limit: int = Query(100, description="Límite de tareas por página"),
    db: Session = Depends(get_db)
):
    """Obtener lista de tareas con paginación"""
    try:
        # Calcular offset para paginación
        offset = page * limit
        
        # Construir query base
        query = db.query(Task)
        
        # Aplicar filtros
        if not include_closed:
            query = query.filter(Task.status != "complete")
        
        # Aplicar paginación
        tasks = query.offset(offset).limit(limit).all()
        
        # Convertir a TaskResponse
        task_responses = []
        for task in tasks:
            task_response = TaskResponse(
                id=task.id,
                clickup_id=task.clickup_id,
                name=task.name,
                description=task.description,
                status=task.status,
                priority=task.priority,
                due_date=task.due_date,
                workspace_id=task.workspace_id,
                list_id=task.list_id,
                assignee_id=task.assignee_id,
                creator_id=task.creator_id,
                custom_fields=task.custom_fields,
                is_synced=task.is_synced,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            task_responses.append(task_response)
        
        return task_responses
        
    except Exception as e:
        # ===== LOGGING AUTOMATICO CON LANGGRAPH =====
        try:
            log_error_with_graph({
                "error_description": f"Error obteniendo tareas: {str(e)}",
                "solution_description": "Verificar conexión a base de datos y modelos",
                "context_info": f"Endpoint: GET /tasks, Timestamp: {datetime.now()}",
                "deployment_id": "railway-production",
                "environment": "production",
                "severity": "medium",
                "status": "pending"
            })
        except Exception as logging_error:
            print(f"⚠️ Error en logging automático: {logging_error}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo tareas: {str(e)}"
        )

# ===== ENDPOINTS ESPECIFICOS DEBEN IR ANTES DEL ENDPOINT GENERICO {task_id} =====
@router.get("/test")
async def test_endpoint():
    """Endpoint de prueba simple"""
    return {"message": "✅ Endpoint de tasks funcionando", "status": "ok"}

@router.get("/config")
async def show_config():
    """Mostrar configuracion actual para debugging"""
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
        
        # Verificar configuracion
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
        # ===== LOGGING AUTOMATICO CON LANGGRAPH =====
        try:
            log_error_with_graph({
                "error_description": f"Error en endpoint de debug: {str(e)}",
                "solution_description": "Verificar configuracion del sistema",
                "context_info": f"Endpoint: /debug, Timestamp: {datetime.now()}",
                "deployment_id": "railway-production",
                "environment": "production",
                "severity": "medium",
                "status": "pending"
            })
        except Exception as logging_error:
            print(f"⚠️ Error en logging automatico: {logging_error}")
        
        return {
            "status": "❌ Error en sistema",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/source-code")
async def get_source_code():
    """Get codigo fuente para debugging"""
    try:
        import os
        current_file = os.path.abspath(__file__)
        
        with open(current_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        return {
            "message": "✅ Codigo fuente obtenido",
            "file": current_file,
            "size": len(source_code),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "message": "❌ Error getting codigo fuente",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ===== ENDPOINT DE SINCRONIZACION SIMPLE (SIN PARAMETROS) - DEBE IR ANTES DE {task_id} =====
@router.post("/sync-simple", response_model=dict)
async def sync_tasks_simple(
    db: Session = Depends(get_db),
    clickup_client: ClickUpClient = Depends(get_clickup_client)
):
    """
    Sync todas las tareas de ClickUp a la base de datos local (sin parametros)
    """
    workspace_id = "9014943317"  # Workspace por defecto
    
    print(f"🔄 Iniciando sincronizacion simple para workspace: {workspace_id}")
    
    try:
        # Get espacios del workspace
        spaces = await clickup_client.get_spaces(workspace_id)
        print(f"📊 Encontrados {len(spaces)} espacios en el workspace")
        
        total_tasks_synced = 0
        total_tasks_created = 0
        total_tasks_updated = 0
        
        for space in spaces:
            space_id = space.get("id")
            space_name = space.get("name", "Sin nombre")
            print(f"🔄 Sincronizando espacio: {space_name} (ID: {space_id})")
            
            try:
                # Get listas de este espacio
                lists = await clickup_client.get_lists(space_id)
                print(f"   📋 Encontradas {len(lists)} listas en el espacio {space_name}")
                
                for list_info in lists:
                    list_id = list_info.get("id")
                    list_name = list_info.get("name", "Sin nombre")
                    print(f"   🔄 Sincronizando lista: {list_name} (ID: {list_id})")
                    
                    try:
                        # Get tareas de esta lista
                        tasks = await clickup_client.get_tasks(list_id)
                        print(f"      📊 Encontradas {len(tasks)} tareas en la lista {list_name}")
                        
                        for task_data in tasks:
                            task_id = task_data.get("id")
                            
                            # Verificar si la tarea ya existe en la BD local
                            existing_task = db.query(Task).filter(Task.clickup_id == task_id).first()
                            
                            if existing_task:
                                # Update tarea existente
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
                                # Create nueva tarea en BD local
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
                                print(f"      🆕 Nueva tarea creada: {task_data.get('name', 'Sin nombre')}")
                            
                            total_tasks_synced += 1
                        
                        # Commit despues de cada lista para evitar transacciones muy largas
                        try:
                            db.commit()
                            print(f"      ✅ Commit exitoso para lista: {list_name}")
                        except Exception as commit_error:
                            print(f"      ❌ Error en commit para lista {list_name}: {commit_error}")
                            db.rollback()
                            continue
                        
                    except Exception as e:
                        print(f"      ❌ Error syncing lista {list_name}: {e}")
                        continue
                        
            except Exception as e:
                print(f"   ❌ Error syncing espacio {space_name}: {e}")
                continue
        
        # ===== LIMPIAR TAREAS OBSOLETAS =====
        print(f"🧹 Iniciando limpieza de tareas obsoletas...")
        
        # Obtener todas las tareas de ClickUp en el workspace
        all_clickup_task_ids = set()
        for space in spaces:
            space_id = space.get("id")
            try:
                lists = await clickup_client.get_lists(space_id)
                for list_info in lists:
                    list_id = list_info.get("id")
                    try:
                        tasks = await clickup_client.get_tasks(list_id)
                        for task_data in tasks:
                            all_clickup_task_ids.add(task_data.get("id"))
                    except Exception as e:
                        print(f"   ⚠️ Error obteniendo tareas de lista {list_id}: {e}")
                        continue
            except Exception as e:
                print(f"   ⚠️ Error obteniendo listas de espacio {space_id}: {e}")
                continue
        
        print(f"   📊 Tareas encontradas en ClickUp: {len(all_clickup_task_ids)}")
        
        # Obtener todas las tareas de la BD local del workspace
        local_tasks = db.query(Task).filter(Task.workspace_id == workspace_id).all()
        print(f"   📊 Tareas en BD local: {len(local_tasks)}")
        
        # Identificar tareas obsoletas (que están en BD local pero no en ClickUp)
        obsolete_tasks = []
        for local_task in local_tasks:
            if local_task.clickup_id not in all_clickup_task_ids:
                obsolete_tasks.append(local_task)
        
        total_tasks_deleted = 0
        if obsolete_tasks:
            print(f"   🗑️ Encontradas {len(obsolete_tasks)} tareas obsoletas para eliminar:")
            for obsolete_task in obsolete_tasks:
                print(f"      🗑️ Eliminando: {obsolete_task.name} (ID: {obsolete_task.clickup_id})")
                db.delete(obsolete_task)
                total_tasks_deleted += 1
        else:
            print(f"   ✅ No hay tareas obsoletas para eliminar")
        
        # Commit final con limpieza
        db.commit()
        
        result = {
            "message": "Sincronizacion completa realizada",
            "total_tasks_synced": total_tasks_synced,
            "total_tasks_created": total_tasks_created,
            "total_tasks_updated": total_tasks_updated,
            "total_tasks_deleted": total_tasks_deleted,
            "workspace_id": workspace_id,
            "clickup_tasks_found": len(all_clickup_task_ids),
            "local_tasks_before": len(local_tasks),
            "local_tasks_after": len(local_tasks) - total_tasks_deleted
        }
        
        print(f"✅ Sincronizacion completa finalizada: {result}")
        print(f"📊 RESUMEN:")
        print(f"   • Tareas en ClickUp: {len(all_clickup_task_ids)}")
        print(f"   • Tareas creadas en BD: {total_tasks_created}")
        print(f"   • Tareas actualizadas en BD: {total_tasks_updated}")
        print(f"   • Tareas obsoletas eliminadas: {total_tasks_deleted}")
        print(f"   • Total procesadas: {total_tasks_synced}")
        return result
        
    except Exception as e:
        print(f"❌ Error en sincronizacion simple: {e}")
        
        # ===== LOGGING AUTOMATICO CON LANGGRAPH =====
        try:
            log_error_with_graph({
                "error_description": f"Error en sincronizacion simple: {str(e)}",
                "solution_description": "Verificar CLICKUP_API_TOKEN y conexion a ClickUp API",
                "context_info": f"Workspace: {workspace_id}, Timestamp: {datetime.now()}",
                "deployment_id": "railway-production",
                "environment": "production",
                "severity": "high",
                "status": "pending"
            })
        except Exception as logging_error:
            print(f"⚠️ Error en logging automatico: {logging_error}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en sincronizacion simple: {str(e)}"
        )

# ===== ENDPOINT DE PRUEBA SIMPLE PARA SINCRONIZACION =====
@router.post("/sync-simple", response_model=dict)
async def sync_tasks_simple():
    """Sincronización simple sin parámetros - usa workspace por defecto"""
    try:
        print("🔄 Iniciando sincronización simple...")
        
        # Usar workspace ID por defecto
        workspace_id = "9014943317"
        print(f"🔄 Usando workspace ID por defecto: {workspace_id}")
        
        # Ejecutar workflow de LangGraph
        result = await run_sync_workflow(workspace_id)
        
        print(f"✅ Sincronización simple completada: {result}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error en sincronización simple: {str(e)}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

# ===== ENDPOINT DELETE PARA ELIMINAR TAREAS =====
@router.delete("/{task_id}", response_model=dict)
async def delete_task(task_id: str, db: Session = Depends(get_db)):
    """Eliminar una tarea específica de ClickUp y de la base de datos local"""
    try:
        print(f"🗑️ Iniciando eliminación de tarea ID: {task_id}")
        
        # 1. Buscar la tarea por ID local o ID de ClickUp
        task = None
        
        # Intentar buscar por ID local (numérico)
        if task_id.isdigit():
            task = db.query(Task).filter(Task.id == int(task_id)).first()
        
        # Si no se encuentra, buscar por ID de ClickUp
        if not task:
            task = db.query(Task).filter(Task.clickup_id == task_id).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarea no encontrada con ID: {task_id}"
            )
        
        print(f"   📋 Tarea encontrada: {task.name} (ClickUp ID: {task.clickup_id})")
        
        # 2. Eliminar la tarea de ClickUp
        try:
            clickup_client = get_clickup_client()
            await clickup_client.delete_task(task.clickup_id)
            print(f"   ✅ Tarea eliminada de ClickUp exitosamente")
        except Exception as clickup_error:
            print(f"   ⚠️ Error eliminando de ClickUp: {clickup_error}")
            # Continuar con eliminación local incluso si falla ClickUp
        
        # 3. Eliminar de la base de datos local
        db.delete(task)
        db.commit()
        print(f"   ✅ Tarea eliminada de la base de datos local")
        
        return {
            "success": True,
            "message": f"Tarea '{task.name}' eliminada exitosamente",
            "task_id": task_id,
            "clickup_id": task.clickup_id,
            "deleted_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error eliminando tarea {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando tarea: {str(e)}"
        )

# ===== ENDPOINT GENERICO {task_id} - DEBE IR AL FINAL =====
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: Session = Depends(get_db)):
    """Get una tarea especifica por ID local o ID de ClickUp"""
    try:
        # Buscar tarea por ID local o ID de ClickUp
        task = None
        
        # Intentar buscar por ID local (numérico)
        if task_id.isdigit():
            task = db.query(Task).filter(Task.id == int(task_id)).first()
        
        # Si no se encuentra, buscar por ID de ClickUp
        if not task:
            task = db.query(Task).filter(Task.clickup_id == task_id).first()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarea no encontrada con ID: {task_id}"
            )
        return task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obtener tarea: {str(e)}"
        )
