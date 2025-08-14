"""
Webhooks de ClickUp para recibir notificaciones automáticas de cambios
"""

import hashlib
import hmac
import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Depends
from fastapi import status as http_status
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from models.task import Task
from utils.advanced_notifications import notification_service
from utils.notifications import extract_contacts_from_custom_fields

# Configurar logging
webhook_logger = logging.getLogger("webhooks")

router = APIRouter()


class WebhookProcessor:
    """Procesador de webhooks de ClickUp"""
    
    @staticmethod
    def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
        """Verificar firma del webhook para seguridad"""
        if not secret:
            webhook_logger.warning("⚠️ No hay secreto configurado para webhooks")
            return True  # Permitir si no hay secreto configurado
        
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # ClickUp puede enviar la firma con prefijo 'sha256='
        if signature.startswith('sha256='):
            signature = signature[7:]
        
        return hmac.compare_digest(expected_signature, signature)
    
    @staticmethod
    async def process_task_event(
        event_type: str,
        task_data: Dict[str, Any],
        db: Session,
        background_tasks: BackgroundTasks
    ):
        """Procesar evento de tarea"""
        task_id = task_data.get("id")
        if not task_id:
            webhook_logger.error("❌ Evento de tarea sin ID")
            return
        
        webhook_logger.info(f"🔔 Procesando evento '{event_type}' para tarea {task_id}")
        
        try:
            # Buscar o crear tarea en la base de datos
            local_task = db.query(Task).filter(Task.clickup_id == task_id).first()
            
            if event_type == "taskCreated":
                if not local_task:
                    local_task = await WebhookProcessor._create_task_from_webhook(task_data, db)
                    webhook_logger.info(f"✅ Tarea {task_id} creada desde webhook")
                
                # Programar notificaciones en background
                background_tasks.add_task(
                    WebhookProcessor._send_task_notifications,
                    "created", local_task, task_data
                )
                
            elif event_type == "taskUpdated":
                if local_task:
                    await WebhookProcessor._update_task_from_webhook(local_task, task_data, db)
                    webhook_logger.info(f"✅ Tarea {task_id} actualizada desde webhook")
                else:
                    # Crear tarea si no existe localmente
                    local_task = await WebhookProcessor._create_task_from_webhook(task_data, db)
                    webhook_logger.info(f"✅ Tarea {task_id} creada desde webhook de actualización")
                
                # Programar notificaciones en background
                background_tasks.add_task(
                    WebhookProcessor._send_task_notifications,
                    "updated", local_task, task_data
                )
                
            elif event_type == "taskDeleted":
                if local_task:
                    # Programar notificaciones antes de eliminar
                    background_tasks.add_task(
                        WebhookProcessor._send_task_notifications,
                        "deleted", local_task, task_data
                    )
                    
                    db.delete(local_task)
                    db.commit()
                    webhook_logger.info(f"✅ Tarea {task_id} eliminada desde webhook")
            
            elif event_type in ["taskStatusUpdated", "taskPriorityUpdated", "taskAssigneeUpdated"]:
                if local_task:
                    await WebhookProcessor._update_task_from_webhook(local_task, task_data, db)
                    
                    # Enviar notificación específica del cambio
                    change_type = event_type.replace("task", "").replace("Updated", "").lower()
                    background_tasks.add_task(
                        WebhookProcessor._send_task_notifications,
                        f"updated_{change_type}", local_task, task_data
                    )
                    
                    webhook_logger.info(f"✅ {change_type} actualizado para tarea {task_id}")
        
        except Exception as e:
            webhook_logger.error(f"❌ Error procesando evento {event_type} para tarea {task_id}: {e}")
            raise
    
    @staticmethod
    async def _create_task_from_webhook(task_data: Dict[str, Any], db: Session) -> Task:
        """Crear tarea desde datos del webhook"""
        from api.routes.tasks import _priority_to_int
        
        # Extraer datos del webhook
        task = Task(
            clickup_id=task_data["id"],
            name=task_data.get("name", ""),
            description=task_data.get("description", ""),
            status=task_data.get("status", {}).get("status", "open"),
            priority=_priority_to_int(task_data.get("priority", 3)),
            due_date=datetime.fromtimestamp(task_data["due_date"] / 1000) if task_data.get("due_date") else None,
            start_date=datetime.fromtimestamp(task_data["start_date"] / 1000) if task_data.get("start_date") else None,
            workspace_id=task_data.get("team_id", ""),
            list_id=task_data.get("list", {}).get("id", ""),
            assignee_id=str(task_data["assignees"][0]["id"]) if task_data.get("assignees") else None,
            creator_id=str(task_data.get("creator", {}).get("id", "")),
            tags=[tag["name"] for tag in task_data.get("tags", [])],
            custom_fields=task_data.get("custom_fields", []),
            is_synced=True,
            last_sync=datetime.now()
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        return task
    
    @staticmethod
    async def _update_task_from_webhook(local_task: Task, task_data: Dict[str, Any], db: Session):
        """Actualizar tarea desde datos del webhook"""
        from api.routes.tasks import _priority_to_int
        
        # Actualizar campos
        local_task.name = task_data.get("name", local_task.name)
        local_task.description = task_data.get("description", local_task.description)
        
        # Status
        if task_data.get("status"):
            local_task.status = task_data["status"].get("status", local_task.status)
        
        # Priority
        if "priority" in task_data:
            local_task.priority = _priority_to_int(task_data["priority"])
        
        # Dates
        if task_data.get("due_date"):
            local_task.due_date = datetime.fromtimestamp(task_data["due_date"] / 1000)
        elif "due_date" in task_data:  # null/None value
            local_task.due_date = None
            
        if task_data.get("start_date"):
            local_task.start_date = datetime.fromtimestamp(task_data["start_date"] / 1000)
        elif "start_date" in task_data:  # null/None value
            local_task.start_date = None
        
        # Assignees
        if task_data.get("assignees"):
            local_task.assignee_id = str(task_data["assignees"][0]["id"])
        elif "assignees" in task_data:  # empty list
            local_task.assignee_id = None
        
        # Custom fields
        if "custom_fields" in task_data:
            local_task.custom_fields = task_data["custom_fields"]
        
        # Tags
        if "tags" in task_data:
            local_task.tags = [tag["name"] for tag in task_data["tags"]]
        
        # Metadata
        local_task.is_synced = True
        local_task.last_sync = datetime.now()
        
        db.commit()
    
    @staticmethod
    async def _send_task_notifications(action: str, task: Task, task_data: Dict[str, Any]):
        """Enviar notificaciones de tarea en background"""
        try:
            webhook_logger.info(f"📤 Enviando notificaciones para acción '{action}' en tarea {task.clickup_id}")
            
            # Obtener participantes del workspace
            from core.database import get_db
            from models.user import User
            
            db = next(get_db())
            try:
                participants = db.query(User).filter(User.workspaces.isnot(None)).all()
                
                # Recopilar destinatarios
                recipient_emails = []
                recipient_telegrams = []
                
                for user in participants:
                    if user.email:
                        recipient_emails.append(user.email)
                    if user.telegram_id:
                        recipient_telegrams.append(user.telegram_id)
                    
                
                # Extraer contactos adicionales desde custom fields
                if task.custom_fields:
                    extra_emails, extra_telegrams, _ = extract_contacts_from_custom_fields(task.custom_fields)
                    recipient_emails.extend(extra_emails)
                    recipient_telegrams.extend(extra_telegrams)
                
                # Obtener nombre del asignado
                assignee_name = None
                if task_data.get("assignees"):
                    assignee_name = task_data["assignees"][0].get("username", "Usuario")
                
                # Formatear fecha de vencimiento
                due_date_str = None
                if task.due_date:
                    due_date_str = task.due_date.strftime("%Y-%m-%d %H:%M")
                
                # Enviar notificaciones usando el servicio avanzado
                    result = await notification_service.send_task_notification(
                    action=action,
                    task_id=task.clickup_id,
                    task_name=task.name,
                    recipient_emails=recipient_emails,
                    recipient_telegrams=recipient_telegrams,
                    status=task.status,
                    priority=task.priority,
                    assignee_name=assignee_name,
                    due_date=due_date_str,
                    description=task.description
                )
                
                summary = result.get_summary()
                webhook_logger.info(f"📊 Notificaciones enviadas: {summary['successful']['total']} exitosas, {summary['failed']} fallidas")
                
            finally:
                db.close()
                
        except Exception as e:
            webhook_logger.error(f"❌ Error enviando notificaciones para tarea {task.clickup_id}: {e}")


@router.post("/clickup", status_code=http_status.HTTP_200_OK)
async def clickup_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Endpoint para recibir webhooks de ClickUp
    
    ClickUp enviará eventos cuando ocurran cambios en tareas, espacios, etc.
    """
    try:
        # Obtener el payload
        payload = await request.body()
        
        # Verificar firma si está configurada
        signature = request.headers.get("X-Signature", "")
        if settings.CLICKUP_WEBHOOK_SECRET:
            if not WebhookProcessor.verify_signature(payload, signature, settings.CLICKUP_WEBHOOK_SECRET):
                webhook_logger.warning(f"⚠️ Firma de webhook inválida: {signature}")
                raise HTTPException(
                    status_code=http_status.HTTP_401_UNAUTHORIZED,
                    detail="Firma de webhook inválida"
                )
        
        # Parsear JSON
        try:
            data = json.loads(payload.decode('utf-8'))
        except json.JSONDecodeError as e:
            webhook_logger.error(f"❌ Error parseando JSON del webhook: {e}")
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="JSON inválido"
            )
        
        # Log del evento recibido
        event_type = data.get("event")
        webhook_logger.info(f"📥 Webhook recibido: {event_type}")
        webhook_logger.debug(f"Datos del webhook: {json.dumps(data, indent=2)}")
        
        # Procesar según el tipo de evento
        if event_type and event_type.startswith("task"):
            task_data = data.get("task_id") or data.get("task")
            if task_data:
                await WebhookProcessor.process_task_event(event_type, task_data, db, background_tasks)
            else:
                webhook_logger.warning(f"⚠️ Evento de tarea sin datos: {event_type}")
        
        elif event_type in ["spaceCreated", "spaceUpdated", "spaceDeleted"]:
            webhook_logger.info(f"📁 Evento de espacio: {event_type}")
            # Aquí podrías procesar eventos de espacios si es necesario
        
        elif event_type in ["listCreated", "listUpdated", "listDeleted"]:
            webhook_logger.info(f"📋 Evento de lista: {event_type}")
            # Aquí podrías procesar eventos de listas si es necesario
        
        elif event_type == "ping":
            webhook_logger.info("🏓 Ping recibido de ClickUp")
        
        else:
            webhook_logger.info(f"❓ Evento no manejado: {event_type}")
        
        return {"status": "success", "message": "Webhook procesado"}
    
    except HTTPException:
        raise
    except Exception as e:
        webhook_logger.error(f"❌ Error procesando webhook: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/test", status_code=http_status.HTTP_200_OK)
async def test_webhook():
    """
    Endpoint de prueba para verificar que los webhooks funcionan
    """
    return {
        "status": "success",
        "message": "Endpoint de webhooks funcionando",
        "timestamp": datetime.now().isoformat(),
        "webhook_secret_configured": bool(settings.CLICKUP_WEBHOOK_SECRET)
    }


@router.post("/test-notification", status_code=http_status.HTTP_200_OK)
async def test_notification(background_tasks: BackgroundTasks):
    """
    Endpoint para probar el sistema de notificaciones
    """
    # Crear una notificación de prueba
    background_tasks.add_task(
        notification_service.send_task_notification,
        action="created",
        task_id="test-123",
        task_name="Tarea de Prueba del Sistema de Webhooks",
        recipient_emails=["karlamirazo@gmail.com"],
        recipient_telegrams=["6888123233"],
        status="in progress",
        priority=2,
        assignee_name="Usuario de Prueba",
        description="Esta es una notificación de prueba para verificar que el sistema funciona correctamente."
    )
    
    return {
        "status": "success",
        "message": "Notificación de prueba programada",
        "timestamp": datetime.now().isoformat()
    }


# Configurar logging para webhooks
logging.basicConfig(level=logging.INFO)
webhook_logger.setLevel(logging.INFO)
