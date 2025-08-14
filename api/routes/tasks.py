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

router = APIRouter()
clickup_client = ClickUpClient()


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
        # Crear tarea en ClickUp - solo campos esenciales
        clickup_task_data = {
            "name": task_data.name,
            "description": task_data.description or ""
        }
        
        # Agregar prioridad si existe (normalizada). ClickUp acepta 1-4
        if task_data.priority is not None:
            clickup_task_data["priority"] = _priority_to_int(task_data.priority)
        
        # Agregar estado si existe
        if task_data.status:
            clickup_task_data["status"] = task_data.status
        
        # Agregar asignatario si existe
        if task_data.assignee_id:
            # ClickUp espera IDs numéricos; convertir si es posible
            try:
                clickup_task_data["assignees"] = [int(str(task_data.assignee_id))]
            except ValueError:
                clickup_task_data["assignees"] = [str(task_data.assignee_id)]

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
        
        clickup_response = await clickup_client.create_task(
            task_data.list_id, 
            clickup_task_data
        )
        print(f"✅ Respuesta de ClickUp: {clickup_response}")
        
        # Verificar si la fecha límite se guardó correctamente en ClickUp
        if clickup_response.get("due_date"):
            print(f"✅ ClickUp recibió la fecha límite: {clickup_response['due_date']}")
            # Convertir el timestamp de ClickUp a datetime para comparar
            clickup_due_date = datetime.fromtimestamp(clickup_response['due_date'] / 1000)
            print(f"✅ ClickUp fecha límite convertida: {clickup_due_date}")
        else:
            print(f"⚠️ ClickUp NO recibió la fecha límite")
        
        # Agregar custom fields después de crear la tarea
        if task_data.custom_fields and clickup_response.get("id"):
            task_id = clickup_response["id"]
            print(f"📝 Agregando custom fields a tarea {task_id}")
            
            try:
                # Obtener los campos personalizados de la LISTA (no de la tarea recién creada)
                # porque la tarea nueva no tiene valores en los campos personalizados
                available_fields = await clickup_client.get_list_custom_fields(task_data.list_id)
                
                # Mapear nombres a IDs
                field_name_to_id = {}
                for field in available_fields:
                    field_name_to_id[field["name"]] = field["id"]
                
                print(f"🔍 Custom fields disponibles en la lista: {list(field_name_to_id.keys())}")
                
                # Actualizar custom fields uno por uno
                custom_fields_data = []
                print(f"🔍 Procesando custom fields: {task_data.custom_fields}")
                for field_name, field_value in task_data.custom_fields.items():
                    print(f"  📝 Campo: {field_name} = {field_value} (tipo: {type(field_value)})")
                    if field_value and field_name in field_name_to_id:
                        field_id = field_name_to_id[field_name]
                        custom_fields_data.append({
                            "id": field_id,
                            "value": str(field_value)
                        })
                        print(f"✅ Campo {field_name} preparado: {field_value} -> ID: {field_id}")
                    elif field_name not in field_name_to_id:
                        print(f"⚠️ Campo '{field_name}' no encontrado en la lista")
                    else:
                        print(f"⚠️ Campo '{field_name}' sin valor: {field_value}")
                
                # Actualizar la tarea con custom fields
                if custom_fields_data:
                    update_data = {"custom_fields": custom_fields_data}
                    print(f"🔄 Actualizando tarea {task_id} con custom fields: {update_data}")
                    
                    # Verificar formato de custom fields antes de enviar
                    for field in custom_fields_data:
                        print(f"  🔍 Campo a enviar: ID={field['id']}, valor={field['value']}")
                    
                    print(f"🔄 Enviando update_data a ClickUp: {update_data}")
                    await clickup_client.update_task(task_id, update_data)
                    print(f"✅ Custom fields actualizados en tarea {task_id}")
                    
                    # Verificar que se hayan guardado correctamente
                    try:
                        verification_task = await clickup_client.get_task(task_id)
                        if verification_task and "custom_fields" in verification_task:
                            print(f"🔍 Verificación: custom fields en ClickUp después de actualizar:")
                            for field in verification_task["custom_fields"]:
                                print(f"  📋 {field['name']}: {field.get('value', 'SIN VALOR')}")
                        else:
                            print(f"⚠️ No se pudieron verificar los custom fields en ClickUp")
                    except Exception as verify_error:
                        print(f"⚠️ Error verificando custom fields: {verify_error}")
                    
                    # Sincronización bidireccional: obtener los campos actualizados desde ClickUp
                    print("🔄 Iniciando sincronización bidireccional...")
                    try:
                        updated_task = await clickup_client.get_task(task_id)
                        if updated_task and "custom_fields" in updated_task:
                            print(f"📋 Tarea actualizada desde ClickUp: {updated_task['custom_fields']}")
                            # La sincronización se hará después de crear db_task
                    except Exception as sync_error:
                        print(f"⚠️ Error obteniendo tarea actualizada: {sync_error}")
                else:
                    print("⚠️ No se pudieron preparar campos personalizados válidos")
                
            except Exception as cf_error:
                print(f"⚠️ Error agregando custom fields: {cf_error}")
                # No fallar si los custom fields no se pueden agregar
        
        # Guardar en base de datos local; si ClickUp no devolvió priority, usar lo enviado
        print(f"💾 Guardando tarea en BD con due_date: {task_data.due_date}")
        print(f"💾 Tipo de due_date: {type(task_data.due_date)}")
        print(f"💾 Custom fields que se guardarán: {task_data.custom_fields}")
        
        # Convertir timestamp a datetime para la base de datos
        due_date_datetime = None
        # SOLUCIÓN TEMPORAL: Simplificar el manejo de due_date
        print(f"🔍 Debug due_date: valor={task_data.due_date}, tipo={type(task_data.due_date)}")
        
        # Convertir due_date a datetime de manera segura
        due_date_datetime = None
        if task_data.due_date:
            try:
                if isinstance(task_data.due_date, datetime):
                    due_date_datetime = task_data.due_date
                    print(f"📅 Due date ya es datetime: {due_date_datetime}")
                elif isinstance(task_data.due_date, (int, float)):
                    # Es timestamp en milisegundos
                    due_date_datetime = datetime.utcfromtimestamp(task_data.due_date / 1000)
                    print(f"📅 Timestamp convertido (UTC): {task_data.due_date} -> {due_date_datetime}")
                elif isinstance(task_data.due_date, str):
                    # Es string, intentar convertir a timestamp
                    timestamp = int(task_data.due_date)
                    due_date_datetime = datetime.utcfromtimestamp(timestamp / 1000)
                    print(f"📅 String convertido a timestamp (UTC): {task_data.due_date} -> {due_date_datetime}")
                else:
                    print(f"⚠️ Tipo de due_date no reconocido: {type(task_data.due_date)}")
            except Exception as e:
                print(f"❌ Error procesando due_date: {e}")
                due_date_datetime = None
        else:
            print(f"⚠️ No se proporcionó fecha límite")
        
        print(f"🔍 Debug antes de crear Task: due_date_datetime={due_date_datetime}, tipo={type(due_date_datetime)}")
        
        print(f"🔍 Debug antes de crear Task: due_date_datetime={due_date_datetime}, tipo={type(due_date_datetime)}")
        
        db_task = Task(
            clickup_id=clickup_response["id"],
            name=task_data.name,
            description=task_data.description,
            status=task_data.status,
            priority=_priority_to_int(clickup_task_data.get("priority", task_data.priority)) if task_data.priority is not None else 3,
            due_date=due_date_datetime,
            start_date=task_data.start_date,
            workspace_id=task_data.workspace_id,
            list_id=task_data.list_id,
            assignee_id=str(task_data.assignee_id) if task_data.assignee_id is not None else None,
            creator_id=str(clickup_response.get("creator", {}).get("id", "")),
            tags=task_data.tags,
            custom_fields=task_data.custom_fields,
            is_synced=True,
            last_sync=datetime.utcnow()
        )
        
        print(f"💾 Tarea creada en BD con ID: {db_task.id}")
        print(f"💾 Due date en BD: {db_task.due_date}")
        print(f"💾 Custom fields en BD: {db_task.custom_fields}")
        
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        print(f"💾 Tarea guardada en BD con ID: {db_task.id}")
        print(f"💾 Due date en BD después del commit: {db_task.due_date}")
        print(f"💾 Tipo de due_date en BD: {type(db_task.due_date)}")
        print(f"💾 Due date en BD (raw): {repr(db_task.due_date)}")
        print(f"💾 Due date en BD (timestamp): {int(db_task.due_date.timestamp() * 1000) if db_task.due_date else 'None'}")
        
        print(f"✅ TAREA CREADA EXITOSAMENTE EN BD: ID={db_task.id}, ClickUp ID={db_task.clickup_id}")
        print(f"✅ Due date guardado: {db_task.due_date}")
        print(f"✅ Custom fields guardados: {db_task.custom_fields}")
        
        # Sincronización bidireccional: actualizar custom_fields desde ClickUp
        print("🔄 Completando sincronización bidireccional...")
        try:
            updated_task = await clickup_client.get_task(clickup_response["id"])
            if updated_task and "custom_fields" in updated_task:
                # Actualizar la base de datos con los campos sincronizados
                db_task.custom_fields = updated_task["custom_fields"]
                db.commit()
                print(f"✅ Sincronización bidireccional completada: {updated_task['custom_fields']}")
        except Exception as sync_error:
            print(f"⚠️ Error en sincronización bidireccional: {sync_error}")
            # No fallar si la sincronización falla
        
        # Notificaciones (best-effort, no bloqueantes graves)
        try:
            print(f"🔔 Iniciando notificaciones para tarea: {db_task.name}")
            
            # OBTENER LOS CUSTOM FIELDS DESDE CLICKUP (después de crear la tarea)
            clickup_custom_fields = {}
            try:
                # Obtener la tarea desde ClickUp para leer sus custom fields reales
                clickup_task_details = await clickup_client.get_task(db_task.clickup_id)
                if clickup_task_details and "custom_fields" in clickup_task_details:
                    raw_custom_fields = clickup_task_details["custom_fields"]
                    print(f"🔍 Custom fields desde ClickUp: {raw_custom_fields}")
                    
                    # Convertir lista de custom fields a diccionario name:value
                    if isinstance(raw_custom_fields, list):
                        for field in raw_custom_fields:
                            if isinstance(field, dict) and "name" in field:
                                field_name = field["name"]
                                field_value = field.get("value")
                                # Incluir todos los campos, incluso si están vacíos, para logs
                                clickup_custom_fields[field_name] = field_value
                                if field_value:
                                    print(f"✅ Campo extraído con valor: {field_name} = {field_value}")
                                else:
                                    print(f"⚠️ Campo sin valor: {field_name} = {field_value}")
                    
                    # Si no hay custom fields con valores, usar los enviados desde el frontend
                    if not any(v for v in clickup_custom_fields.values()):
                        print("💡 Usando custom fields del frontend como fallback")
                        clickup_custom_fields = task_data.custom_fields or {}
                    
                    # Actualizar la base de datos con los custom fields reales
                    db_task.custom_fields = clickup_custom_fields
                    db.commit()
                    print(f"📝 Custom fields finales: {clickup_custom_fields}")
            except Exception as e:
                print(f"⚠️  Error obteniendo custom fields desde ClickUp: {e}")
                # Usar los custom fields locales como fallback
                clickup_custom_fields = task_data.custom_fields or {}
            
            # Obtener participantes del workspace (filtro básico)
            participants = (
                db.query(User).all()
                if not task_data.workspace_id
                else db.query(User).filter(User.workspaces.isnot(None)).all()
            )
            recipient_emails: List[str] = []
            recipient_telegrams: List[str] = []
            recipient_sms: List[str] = []
            
            print(f"👥 Participantes encontrados: {len(participants)}")
            
            for u in participants:
                if u and getattr(u, "email", None):
                    recipient_emails.append(u.email)
                    print(f"📧 Email agregado (usuario): {u.email}")
                try:
                    telegram = None
                    if u.preferences and isinstance(u.preferences, dict):
                        telegram = u.preferences.get("telegram") or u.preferences.get("telegram_chat_id")
                    if telegram:
                        recipient_telegrams.append(str(telegram))
                        print(f"🤖 Telegram agregado (usuario): {telegram}")
                        
                    # SMS desde preferencias de usuario
                    phone = None
                    if u.preferences and isinstance(u.preferences, dict):
                        phone = u.preferences.get("phone") or u.preferences.get("sms_number")
                    if phone:
                        recipient_sms.append(str(phone))
                        print(f"📱 SMS agregado (usuario): {phone}")
                except Exception:
                    pass

            # Agregar destinatarios desde campos personalizados de ClickUp
            try:
                from utils.notifications import (
                    send_email_async,
                    send_telegram_async,
                    send_sms_async,
                    build_task_email_content,
                    build_task_telegram_message,
                    build_task_sms_message,
                    extract_contacts_from_custom_fields,
                )
                
                print(f"🔍 Campos personalizados de ClickUp: {clickup_custom_fields}")
                extra_emails, extra_telegrams, extra_sms = extract_contacts_from_custom_fields(clickup_custom_fields)
                recipient_emails.extend(extra_emails)
                recipient_telegrams.extend(extra_telegrams)
                recipient_sms.extend(extra_sms)
                
                print(f"📧 Emails desde ClickUp: {extra_emails}")
                print(f"🤖 Telegrams desde ClickUp: {extra_telegrams}")
                print(f"📱 SMS desde ClickUp: {extra_sms}")
                
                print(f"📧 Emails totales: {recipient_emails}")
                print(f"🤖 Telegrams totales: {recipient_telegrams}")
                print(f"📱 SMS totales: {recipient_sms}")

                if recipient_emails or recipient_telegrams or recipient_sms:
                    subject, text_body, html_body = build_task_email_content(
                        action="created",
                        task_id=db_task.clickup_id,
                        name=db_task.name,
                        status=db_task.status,
                        priority=db_task.priority,
                        assignee_name=None,
                        due_date_iso=db_task.due_date.isoformat() if db_task.due_date else None,
                    )
                    telegram_msg = build_task_telegram_message(
                        action="created",
                        task_id=db_task.clickup_id,
                        name=db_task.name,
                        status=db_task.status,
                        priority=db_task.priority,
                        assignee_name=None,
                        due_date_iso=db_task.due_date.isoformat() if db_task.due_date else None,
                    )
                    sms_msg = build_task_sms_message(
                        action="created",
                        task_id=db_task.clickup_id,
                        name=db_task.name,
                        status=db_task.status,
                        priority=db_task.priority,
                        assignee_name=None,
                        due_date_iso=db_task.due_date.isoformat() if db_task.due_date else None,
                    )

                    print(f"📨 Enviando notificaciones...")

                    import asyncio

                    async def _notify():
                        await asyncio.gather(
                            send_email_async(list(dict.fromkeys(recipient_emails)), subject, text_body, html_body)
                            if recipient_emails
                            else asyncio.sleep(0),
                            send_telegram_async(list(dict.fromkeys(recipient_telegrams)), telegram_msg)
                            if recipient_telegrams
                            else asyncio.sleep(0),
                            send_sms_async(list(dict.fromkeys(recipient_sms)), sms_msg)
                            if recipient_sms
                            else asyncio.sleep(0),
                        )

                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            asyncio.create_task(_notify())
                        else:
                            loop.run_until_complete(_notify())
                        print(f"✅ Notificaciones enviadas correctamente")
                    except Exception as e:
                        print(f"❌ Error enviando notificaciones: {e}")
                else:
                    print(f"⚠️  No hay destinatarios para notificaciones")
            except Exception as e:
                print(f"⚠️ Error en sistema de notificaciones (no crítico): {e}")
                # No fallar si las notificaciones fallan
        except Exception as e:
            print(f"⚠️ Error en sistema de notificaciones (no crítico): {e}")
            # No fallar si las notificaciones fallan
        
        print(f"🚀 Retornando tarea creada exitosamente: {db_task.id}")
        
        # SOLUCIÓN TEMPORAL: Manejo robusto de errores
        try:
            response = TaskResponse.model_validate(db_task)
            print(f"✅ Respuesta validada exitosamente")
            return response
        except Exception as validation_error:
            print(f"⚠️ Error validando respuesta: {validation_error}")
            # Crear respuesta manual si falla la validación
            return TaskResponse(
                id=db_task.id,
                clickup_id=db_task.clickup_id,
                name=db_task.name,
                description=db_task.description,
                status=db_task.status,
                priority=db_task.priority,
                due_date=db_task.due_date,
                start_date=db_task.start_date,
                assignee_id=db_task.assignee_id,
                workspace_id=db_task.workspace_id,
                list_id=db_task.list_id,
                custom_fields=db_task.custom_fields,
                is_synced=db_task.is_synced,
                last_sync=db_task.last_sync
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la tarea: {str(e)}"
        )



@router.get("/", response_model=TaskList)
async def get_tasks(
    workspace_id: Optional[str] = Query(None, description="ID del workspace"),
    list_id: Optional[str] = Query(None, description="ID de la lista"),
    status: Optional[str] = Query(None, description="Estado de las tareas"),
    assignee_id: Optional[str] = Query(None, description="ID del usuario asignado"),
    priority: Optional[int] = Query(None, description="Prioridad"),
    search: Optional[str] = Query(None, description="Término de búsqueda"),
    include_closed: bool = Query(False, description="Incluir tareas cerradas"),
    page: int = Query(0, ge=0, description="Número de página"),
    limit: int = Query(50, ge=1, le=100, description="Límite de resultados"),
    db: Session = Depends(get_db)
):
    """Obtener lista de tareas con filtros"""
    try:
        query = db.query(Task)
        
        # Aplicar filtros
        if workspace_id:
            query = query.filter(Task.workspace_id == workspace_id)
        if list_id:
            query = query.filter(Task.list_id == list_id)
        if status:
            query = query.filter(Task.status == status)
        if assignee_id:
            query = query.filter(Task.assignee_id == assignee_id)
        if priority:
            query = query.filter(Task.priority == priority)
        if search:
            query = query.filter(Task.name.contains(search))
        if not include_closed:
            query = query.filter(Task.status != "complete")
        
        # Contar total
        total = query.count()
        
        # Paginar
        tasks = query.offset(page * limit).limit(limit).all()

        # Normalizar prioridad y construir respuesta de forma segura
        responses: List[TaskResponse] = []
        dirty = False
        for t in tasks:
            # Debug: verificar due_date antes de procesar
            print(f"🔍 Debug tarea {t.id}: due_date={t.due_date}, tipo={type(t.due_date)}")
            if t.due_date:
                print(f"  📅 Due date timestamp: {int(t.due_date.timestamp() * 1000)}")
                print(f"  📅 Due date raw: {repr(t.due_date)}")
            else:
                print(f"  ⚠️ Due date es None")
            
            # Asegurar que siempre haya una prioridad válida
            if t.priority is None or isinstance(t.priority, (str, dict)):
                t.priority = _priority_to_int(t.priority)
                dirty = True
            
            # Normalizar IDs a string si vinieron como enteros
            if getattr(t, "assignee_id", None) is not None and not isinstance(t.assignee_id, str):
                t.assignee_id = str(t.assignee_id)
                dirty = True
            if getattr(t, "creator_id", None) is not None and not isinstance(t.creator_id, str):
                t.creator_id = str(t.creator_id)
                dirty = True
            try:
                response = TaskResponse.model_validate(t)
                print(f"✅ Tarea {t.id} validada: due_date={response.due_date}, tipo={type(response.due_date)}")
                responses.append(response)
            except Exception as e:
                print(f"Error validando tarea {t.clickup_id}: {e}")
                # Intento adicional: forzar conversión y revalidar
                t.priority = _priority_to_int(getattr(t, "priority", 3))
                if getattr(t, "assignee_id", None) is not None and not isinstance(t.assignee_id, str):
                    t.assignee_id = str(t.assignee_id)
                    dirty = True
                if getattr(t, "creator_id", None) is not None and not isinstance(t.creator_id, str):
                    t.creator_id = str(t.creator_id)
                    dirty = True
                try:
                    response = TaskResponse.model_validate(t)
                    print(f"✅ Tarea {t.id} revalidada: due_date={response.due_date}, tipo={type(response.due_date)}")
                    responses.append(response)
                except Exception as e2:
                    print(f"Error persistente validando tarea {t.clickup_id}: {e2}")
        if dirty:
            db.commit()

        # Enriquecer con nombre de asignado, lista y workspace
        for r in responses:
            # Enriquecer nombre de asignado
            if getattr(r, "assignee_id", None) and not getattr(r, "assignee_name", None):
                try:
                    # Intentar obtener el nombre del usuario desde la base de datos local
                    from models.user import User
                    user = db.query(User).filter(User.clickup_id == str(r.assignee_id)).first()
                    if user:
                        # Usar el nombre completo si está disponible
                        if user.first_name and user.last_name:
                            assignee_name = f"{user.first_name} {user.last_name}"
                        elif user.first_name:
                            assignee_name = user.first_name
                        elif user.username:
                            assignee_name = user.username
                        else:
                            assignee_name = user.email
                        object.__setattr__(r, "assignee_name", assignee_name)
                    else:
                        # Si no se encuentra en la BD local, usar el ID como fallback
                        object.__setattr__(r, "assignee_name", f"Usuario {str(r.assignee_id)}")
                except Exception as e:
                    print(f"Error obteniendo nombre de usuario {r.assignee_id}: {e}")
                    # Fallback: usar el ID
                    object.__setattr__(r, "assignee_name", str(r.assignee_id))
            
            # Enriquecer nombre de lista (usar ID como fallback por ahora)
            if getattr(r, "list_id", None) and not getattr(r, "list_name", None):
                object.__setattr__(r, "list_name", f"Lista {str(r.list_id)}")
            
            # Enriquecer nombre de workspace
            if getattr(r, "workspace_id", None) and not getattr(r, "workspace_name", None):
                try:
                    from models.workspace import Workspace
                    workspace = db.query(Workspace).filter(Workspace.clickup_id == str(r.workspace_id)).first()
                    if workspace:
                        object.__setattr__(r, "workspace_name", workspace.name)
                    else:
                        object.__setattr__(r, "workspace_name", f"Workspace {str(r.workspace_id)}")
                except Exception as e:
                    print(f"Error obteniendo nombre de workspace {r.workspace_id}: {e}")
                    object.__setattr__(r, "workspace_name", str(r.workspace_id))

        return TaskList(
            tasks=responses,
            total=total,
            page=page,
            limit=limit,
            has_more=(page + 1) * limit < total
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener las tareas: {str(e)}"
        )

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Obtener una tarea específica"""
    try:
        # Buscar en base de datos local
        db_task = db.query(Task).filter(Task.clickup_id == task_id).first()
        
        if not db_task:
            # Si no existe localmente, obtener de ClickUp
            clickup_task = await clickup_client.get_task(task_id)
            
            # Crear registro local
            db_task = Task(
                clickup_id=clickup_task["id"],
                name=clickup_task["name"],
                description=clickup_task.get("description", ""),
                status=clickup_task["status"]["status"],
                priority=_priority_to_int(clickup_task.get("priority", 3)),
                due_date=datetime.fromtimestamp(clickup_task["due_date"] / 1000) if clickup_task.get("due_date") else None,
                start_date=datetime.fromtimestamp(clickup_task["start_date"] / 1000) if clickup_task.get("start_date") else None,
                workspace_id=clickup_task["team_id"],
                list_id=clickup_task["list"]["id"],
                assignee_id=str(clickup_task["assignees"][0]["id"]) if clickup_task.get("assignees") else None,
                creator_id=str(clickup_task["creator"]["id"]),
                tags=[tag["name"] for tag in clickup_task.get("tags", [])],
                custom_fields=clickup_task.get("custom_fields", {}),
                is_synced=True,
                last_sync=datetime.utcnow()
            )
            
            db.add(db_task)
            db.commit()
            db.refresh(db_task)
        else:
            # Asegurar que priority sea entero en respuestas
            db_task.priority = _priority_to_int(db_task.priority)
            db.commit()
        
        return TaskResponse.model_validate(db_task)
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Tarea no encontrada: {str(e)}"
        )

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una tarea existente"""
    try:
        # Buscar tarea en base de datos
        db_task = db.query(Task).filter(Task.clickup_id == task_id).first()
        
        if not db_task:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Tarea no encontrada"
            )
        
        # Preparar datos para ClickUp
        update_data = {}
        if task_data.name is not None:
            update_data["name"] = task_data.name
        if task_data.description is not None:
            update_data["description"] = task_data.description
        if task_data.status is not None and task_data.status.strip():
            # No enviar status en actualizaciones - puede causar error 400
            print(f"⚠️ Status '{task_data.status}' omitido en actualización para evitar errores")
        elif task_data.status == "":
            print("⚠️ Estado vacío recibido, no se actualizará en ClickUp")
        if task_data.priority is not None:
            update_data["priority"] = _priority_to_int(task_data.priority)
        if task_data.due_date is not None:
            update_data["due_date"] = int(task_data.due_date.timestamp() * 1000)
        if task_data.start_date is not None:
            update_data["start_date"] = int(task_data.start_date.timestamp() * 1000)
        if task_data.assignee_id is not None:
            try:
                update_data["assignees"] = [int(str(task_data.assignee_id))]
            except ValueError:
                update_data["assignees"] = [str(task_data.assignee_id)]
        if task_data.tags is not None:
            update_data["tags"] = task_data.tags
        if task_data.custom_fields is not None:
            print(f"📝 Custom fields recibidos del frontend: {task_data.custom_fields}")
            
            # Obtener la tarea actual para ver su estructura de custom_fields
            try:
                current_task = await clickup_client.get_task(task_id)
                current_custom_fields = current_task.get("custom_fields", [])
                print(f"🔍 Custom fields actuales en ClickUp: {current_custom_fields}")
                
                # Convertir custom_fields al formato que espera ClickUp usando IDs
                update_data["custom_fields"] = []
                for field_name, field_value in task_data.custom_fields.items():
                    if field_value:  # Solo agregar campos con valor
                        # Buscar el ID del campo por nombre
                        field_id = None
                        for cf in current_custom_fields:
                            if cf.get("name") == field_name:
                                field_id = cf.get("id")
                                break
                        
                        if field_id:
                            update_data["custom_fields"].append({
                                "id": field_id,
                                "value": str(field_value)
                            })
                            print(f"✅ Campo {field_name} mapeado a ID {field_id}")
                        else:
                            print(f"⚠️ No se encontró ID para campo {field_name}")
            except Exception as e:
                print(f"❌ Error obteniendo custom_fields actuales: {e}")
                # Fallback: usar nombres como antes
                update_data["custom_fields"] = []
                for field_name, field_value in task_data.custom_fields.items():
                    if field_value:
                        update_data["custom_fields"].append({
                            "name": field_name,
                            "value": str(field_value)
                        })
        
        # Verificar que tenemos datos para actualizar
        if not update_data:
            print("⚠️ No hay datos para actualizar en ClickUp")
            return TaskResponse.model_validate(db_task)
        
        # Actualizar en ClickUp
        print(f"🔧 Actualizando tarea {task_id} con datos: {update_data}")
        print(f"🔍 Tipo de task_id: {type(task_id)}, valor: {repr(task_id)}")
        
        try:
            await clickup_client.update_task(task_id, update_data)
            print(f"✅ Tarea {task_id} actualizada exitosamente en ClickUp")
        except Exception as clickup_error:
            print(f"❌ Error específico de ClickUp: {clickup_error}")
            print(f"🔍 Task ID: {task_id}")
            print(f"🔍 Update data: {update_data}")
            
            # Verificar si es problema de permisos o tarea inexistente
            if "400" in str(clickup_error):
                print("💡 Error 400 sugiere datos inválidos o permisos insuficientes")
            elif "404" in str(clickup_error):
                print("💡 Error 404 sugiere que la tarea no existe en ClickUp")
            elif "401" in str(clickup_error):
                print("💡 Error 401 sugiere problema de autenticación")
            
            # Si falla con custom_fields, intentar sin ellos
            if "custom_fields" in update_data and update_data["custom_fields"]:
                print("🔄 Reintentando sin custom_fields...")
                update_data_no_cf = {k: v for k, v in update_data.items() if k != "custom_fields"}
                print(f"🔧 Datos sin custom_fields: {update_data_no_cf}")
                try:
                    await clickup_client.update_task(task_id, update_data_no_cf)
                    print("✅ Actualización exitosa sin custom_fields")
                except Exception as retry_error:
                    print(f"❌ Error aún sin custom_fields: {retry_error}")
                    
                    # Último intento: actualizar solo nombre si es crítico
                    if "name" in update_data_no_cf:
                        try:
                            minimal_data = {"name": update_data_no_cf["name"]}
                            await clickup_client.update_task(task_id, minimal_data)
                            print("✅ Actualización mínima exitosa (solo nombre)")
                        except Exception as final_error:
                            print(f"❌ Error en actualización mínima: {final_error}")
                            raise clickup_error  # Lanzar el error original
                    else:
                        raise clickup_error
            else:
                raise clickup_error
        
        # Actualizar en base de datos local con normalización
        updates_dict = task_data.dict(exclude_unset=True)
        if "priority" in updates_dict:
            db_task.priority = _priority_to_int(updates_dict.pop("priority"))
        if "assignee_id" in updates_dict:
            db_task.assignee_id = str(updates_dict.pop("assignee_id")) if updates_dict.get("assignee_id") is not None else None
        # Asignar resto de campos directamente
        for field, value in updates_dict.items():
            setattr(db_task, field, value)
        
        db_task.is_synced = True
        db_task.last_sync = datetime.utcnow()
        
        db.commit()
        db.refresh(db_task)
        # Asegurar tipos correctos antes de responder
        db_task.priority = _priority_to_int(getattr(db_task, "priority", 3))
        if getattr(db_task, "assignee_id", None) is not None and not isinstance(db_task.assignee_id, str):
            db_task.assignee_id = str(db_task.assignee_id)
        if getattr(db_task, "creator_id", None) is not None and not isinstance(db_task.creator_id, str):
            db_task.creator_id = str(db_task.creator_id)
        response = TaskResponse.model_validate(db_task)

        # Notificaciones de actualización
        try:
            participants = db.query(User).all() if not db_task.workspace_id else db.query(User).filter(User.workspaces.isnot(None)).all()
            recipient_emails = []
            recipient_telegrams = []
            recipient_sms = []
            for u in participants:
                if u and u.email:
                    recipient_emails.append(u.email)
                try:
                    telegram = None
                    if u.preferences and isinstance(u.preferences, dict):
                        telegram = u.preferences.get("telegram") or u.preferences.get("telegram_chat_id")
                    if telegram:
                        recipient_telegrams.append(str(telegram))
                except Exception:
                    pass

            # Agregar destinatarios desde campos personalizados de la tarea
            from utils.notifications import (
                send_email_async,
                send_telegram_async,
                send_sms_async,
                build_task_email_content,
                build_task_telegram_message,
                build_task_sms_message,
                extract_contacts_from_custom_fields,
            )

            extra_emails, extra_telegrams, extra_sms = extract_contacts_from_custom_fields(db_task.custom_fields or {})
            recipient_emails.extend(extra_emails)
            recipient_telegrams.extend(extra_telegrams)
            recipient_sms.extend(extra_sms)

            if recipient_emails or recipient_telegrams or recipient_sms:
                subject, text_body, html_body = build_task_email_content(
                    action="updated",
                    task_id=db_task.clickup_id,
                    name=db_task.name,
                    status=db_task.status,
                    priority=db_task.priority,
                    assignee_name=None,
                    due_date_iso=db_task.due_date.isoformat() if db_task.due_date else None,
                )
                telegram_msg = build_task_telegram_message(
                    action="updated",
                    task_id=db_task.clickup_id,
                    name=db_task.name,
                    status=db_task.status,
                    priority=db_task.priority,
                    assignee_name=None,
                    due_date_iso=db_task.due_date.isoformat() if db_task.due_date else None,
                )
                sms_msg = build_task_sms_message(
                    action="updated",
                    task_id=db_task.clickup_id,
                    name=db_task.name,
                    status=db_task.status,
                    priority=db_task.priority,
                    assignee_name=None,
                    due_date_iso=db_task.due_date.isoformat() if db_task.due_date else None,
                )

                import asyncio

                async def _notify():
                    await asyncio.gather(
                        send_email_async(list(dict.fromkeys(recipient_emails)), subject, text_body, html_body)
                        if recipient_emails
                        else asyncio.sleep(0),
                        send_telegram_async(list(dict.fromkeys(recipient_telegrams)), telegram_msg)
                        if recipient_telegrams
                        else asyncio.sleep(0),
                        send_sms_async(list(dict.fromkeys(recipient_sms)), sms_msg)
                        if recipient_sms
                        else asyncio.sleep(0),
                    )

                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(_notify())
                    else:
                        loop.run_until_complete(_notify())
                except Exception:
                    pass
        except Exception:
            pass

        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la tarea: {str(e)}"
        )

@router.delete("/{task_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Eliminar una tarea"""
    try:
        # Eliminar de ClickUp
        await clickup_client.delete_task(task_id)
        
        # Eliminar de base de datos local
        db_task = db.query(Task).filter(Task.clickup_id == task_id).first()
        if db_task:
            # Notificaciones antes de eliminar
            try:
                participants = db.query(User).all() if not db_task.workspace_id else db.query(User).filter(User.workspaces.isnot(None)).all()
                recipient_emails = []
                recipient_telegrams = []
                recipient_sms = []
                for u in participants:
                    if u and u.email:
                        recipient_emails.append(u.email)
                    try:
                        telegram = None
                        if u.preferences and isinstance(u.preferences, dict):
                            telegram = u.preferences.get("telegram") or u.preferences.get("telegram_chat_id")
                        if telegram:
                            recipient_telegrams.append(str(telegram))
                    except Exception:
                        pass

                # Agregar destinatarios desde campos personalizados de la tarea
                from utils.notifications import (
                    send_email_async,
                    send_telegram_async,
                    build_task_email_content,
                    build_task_telegram_message,
                    extract_contacts_from_custom_fields,
                )

                extra_emails, extra_telegrams, extra_sms = extract_contacts_from_custom_fields(db_task.custom_fields or {})
                recipient_emails.extend(extra_emails)
                recipient_telegrams.extend(extra_telegrams)

                if recipient_emails or recipient_telegrams or recipient_sms:
                    subject, text_body, html_body = build_task_email_content(
                        action="deleted",
                        task_id=db_task.clickup_id,
                        name=db_task.name,
                        status=db_task.status,
                        priority=db_task.priority,
                        assignee_name=None,
                        due_date_iso=db_task.due_date.isoformat() if db_task.due_date else None,
                    )
                    telegram_msg = build_task_telegram_message(
                        action="deleted",
                        task_id=db_task.clickup_id,
                        name=db_task.name,
                        status=db_task.status,
                        priority=db_task.priority,
                        assignee_name=None,
                        due_date_iso=db_task.due_date.isoformat() if db_task.due_date else None,
                    )
                    sms_msg = build_task_sms_message(
                        action="deleted",
                        task_id=db_task.clickup_id,
                        name=db_task.name,
                        status=db_task.status,
                        priority=db_task.priority,
                        assignee_name=None,
                        due_date_iso=db_task.due_date.isoformat() if db_task.due_date else None,
                    )

                    import asyncio

                    async def _notify():
                        await asyncio.gather(
                            send_email_async(list(dict.fromkeys(recipient_emails)), subject, text_body, html_body)
                            if recipient_emails
                            else asyncio.sleep(0),
                            send_telegram_async(list(dict.fromkeys(recipient_telegrams)), telegram_msg)
                            if recipient_telegrams
                            else asyncio.sleep(0),
                        )

                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            asyncio.create_task(_notify())
                        else:
                            loop.run_until_complete(_notify())
                    except Exception:
                        pass
            except Exception:
                pass
            db.delete(db_task)
            db.commit()
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la tarea: {str(e)}"
        )

@router.post("/bulk-update", response_model=List[TaskResponse])
async def bulk_update_tasks(
    bulk_data: TaskBulkUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar múltiples tareas"""
    try:
        updated_tasks = []
        
        for task_id in bulk_data.task_ids:
            # Actualizar cada tarea
            await update_task(task_id, bulk_data.updates, db)
            
            # Obtener tarea actualizada
            db_task = db.query(Task).filter(Task.clickup_id == task_id).first()
            if db_task:
                updated_tasks.append(TaskResponse.model_validate(db_task))
        
        return updated_tasks
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en actualización masiva: {str(e)}"
        )

@router.delete("/bulk-delete", status_code=http_status.HTTP_204_NO_CONTENT)
async def bulk_delete_tasks(
    bulk_data: TaskBulkDelete,
    db: Session = Depends(get_db)
):
    """Eliminar múltiples tareas"""
    try:
        for task_id in bulk_data.task_ids:
            await delete_task(task_id, db)
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en eliminación masiva: {str(e)}"
        )

@router.post("/{task_id}/sync", response_model=TaskResponse)
async def sync_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Sincronizar una tarea con ClickUp"""
    try:
        # Obtener datos actualizados de ClickUp
        clickup_task = await clickup_client.get_task(task_id)
        
        # Buscar o crear tarea local
        db_task = db.query(Task).filter(Task.clickup_id == task_id).first()
        
        if not db_task:
            db_task = Task(clickup_id=task_id)
            db.add(db_task)
        
        # Actualizar datos
        db_task.name = clickup_task["name"]
        db_task.description = clickup_task.get("description", "")
        db_task.status = clickup_task["status"]["status"]
        db_task.priority = _priority_to_int(clickup_task.get("priority", 3))
        db_task.due_date = datetime.fromtimestamp(clickup_task["due_date"] / 1000) if clickup_task.get("due_date") else None
        db_task.start_date = datetime.fromtimestamp(clickup_task["start_date"] / 1000) if clickup_task.get("start_date") else None
        db_task.workspace_id = clickup_task["team_id"]
        db_task.list_id = clickup_task["list"]["id"]
        db_task.assignee_id = str(clickup_task["assignees"][0]["id"]) if clickup_task.get("assignees") else None
        db_task.creator_id = str(clickup_task["creator"]["id"])
        db_task.tags = [tag["name"] for tag in clickup_task.get("tags", [])]
        db_task.custom_fields = clickup_task.get("custom_fields", {})
        db_task.is_synced = True
        db_task.last_sync = datetime.utcnow()
        
        db.commit()
        db.refresh(db_task)
        
        return TaskResponse.model_validate(db_task)
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al sincronizar la tarea: {str(e)}"
        )

@router.post("/sync-all", response_model=List[TaskResponse])
async def sync_all_tasks(
    workspace_id: Optional[str] = Query(None, description="ID del workspace"),
    db: Session = Depends(get_db)
):
    """Sincronizar todas las tareas de ClickUp"""
    try:
        synced_tasks = []
        clickup_task_ids = set()  # Para rastrear tareas que existen en ClickUp
        
        # Obtener workspaces si no se especifica uno
        if not workspace_id:
            workspaces = await clickup_client.get_workspaces()
            workspace_id = workspaces[0]["id"] if workspaces else None
        
        if not workspace_id:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="No se encontró ningún workspace"
            )
        
        # Obtener spaces del workspace
        spaces = await clickup_client.get_spaces(workspace_id)
        
        for space in spaces:
            try:
                # Obtener listas del space
                lists = await clickup_client.get_lists(space["id"])
                
                for list_item in lists:
                    try:
                        # Obtener tareas de cada lista
                        tasks = await clickup_client.get_tasks(list_item["id"])
                        
                        for task in tasks:
                            clickup_task_ids.add(task["id"])  # Agregar a set de tareas existentes
                            
                            # Buscar o crear tarea local
                            db_task = db.query(Task).filter(Task.clickup_id == task["id"]).first()
                            
                            if not db_task:
                                db_task = Task(clickup_id=task["id"])
                                db.add(db_task)
                            
                            try:
                                # Actualizar datos con manejo de errores para cada campo
                                db_task.name = task["name"]
                                db_task.description = task.get("description", "")
                                
                                # Manejar status de forma segura
                                if task.get("status") and isinstance(task["status"], dict):
                                    db_task.status = task["status"].get("status", "pendiente")
                                else:
                                    db_task.status = "pendiente"
                                
                                # Manejar priority de forma segura
                                priority_value = task.get("priority", 3)
                                if isinstance(priority_value, dict):
                                    # Si priority es un dict, extraer el valor numérico del campo 'id'
                                    try:
                                        db_task.priority = int(priority_value.get("id", 3))
                                    except (ValueError, TypeError):
                                        db_task.priority = 3
                                elif isinstance(priority_value, str):
                                    # Si priority es string, convertir a int
                                    try:
                                        db_task.priority = int(priority_value)
                                    except (ValueError, TypeError):
                                        db_task.priority = 3
                                else:
                                    db_task.priority = priority_value
                                
                                # Manejar fechas de forma segura
                                if task.get("due_date"):
                                    try:
                                        db_task.due_date = datetime.fromtimestamp(task["due_date"] / 1000)
                                    except (ValueError, TypeError):
                                        db_task.due_date = None
                                else:
                                    db_task.due_date = None
                                
                                if task.get("start_date"):
                                    try:
                                        db_task.start_date = datetime.fromtimestamp(task["start_date"] / 1000)
                                    except (ValueError, TypeError):
                                        db_task.start_date = None
                                else:
                                    db_task.start_date = None
                                
                                db_task.workspace_id = task.get("team_id", workspace_id)
                                
                                # Manejar list_id de forma segura
                                if task.get("list") and isinstance(task["list"], dict):
                                    db_task.list_id = task["list"].get("id", list_item["id"])
                                else:
                                    db_task.list_id = list_item["id"]
                                
                                # Manejar assignee de forma segura
                                if task.get("assignees") and isinstance(task["assignees"], list) and len(task["assignees"]) > 0:
                                    assignee_id = task["assignees"][0].get("id")
                                    db_task.assignee_id = str(assignee_id) if assignee_id is not None else None
                                else:
                                    db_task.assignee_id = None
                                
                                # Manejar creator de forma segura
                                if task.get("creator") and isinstance(task["creator"], dict):
                                    creator_id = task["creator"].get("id", "")
                                    db_task.creator_id = str(creator_id) if creator_id else ""
                                else:
                                    db_task.creator_id = ""
                                
                                # Manejar tags de forma segura
                                if task.get("tags") and isinstance(task["tags"], list):
                                    tag_names = [tag.get("name", "") for tag in task["tags"] if isinstance(tag, dict) and tag.get("name")]
                                    db_task.tags = tag_names  # SQLAlchemy JSON column maneja listas automáticamente
                                else:
                                    db_task.tags = []
                                
                                # Manejar custom_fields de forma segura
                                if task.get("custom_fields") and isinstance(task["custom_fields"], dict):
                                    # Filtrar valores booleanos que podrían causar problemas
                                    safe_custom_fields = {}
                                    for key, value in task["custom_fields"].items():
                                        if isinstance(value, bool):
                                            safe_custom_fields[key] = str(value).lower()
                                        else:
                                            safe_custom_fields[key] = value
                                    db_task.custom_fields = safe_custom_fields
                                else:
                                    db_task.custom_fields = {}
                                
                                db_task.is_synced = True
                                db_task.last_sync = datetime.utcnow()
                                
                                synced_tasks.append(TaskResponse.model_validate(db_task))
                                
                            except Exception as task_error:
                                print(f"Error procesando tarea {task['id']}: {task_error}")
                                continue
                            
                    except Exception as e:
                        print(f"Error sincronizando lista {list_item['id']}: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error sincronizando space {space['id']}: {e}")
                continue
        
        # Eliminar tareas que ya no existen en ClickUp
        if clickup_task_ids:
            tasks_to_delete = db.query(Task).filter(
                Task.workspace_id == workspace_id,
                ~Task.clickup_id.in_(clickup_task_ids)
            ).all()
            
            for task_to_delete in tasks_to_delete:
                print(f"🗑️ Eliminando tarea local que ya no existe en ClickUp: {task_to_delete.clickup_id}")
                db.delete(task_to_delete)
        
        db.commit()
        
        return synced_tasks
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al sincronizar las tareas: {str(e)}"
        )
