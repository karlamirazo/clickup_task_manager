"""
Rutas de WhatsApp para integración con ClickUp
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import logging

from core.whatsapp_client import WhatsAppNotificationService, WhatsAppClient
from core.whatsapp_integrator import WhatsAppClickUpIntegrator
from core.phone_extractor import extract_whatsapp_numbers_from_task, get_primary_whatsapp_number
from core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Integration"])

# Modelos Pydantic
class WhatsAppMessageRequest(BaseModel):
    """Modelo para solicitudes de envío de mensajes"""
    phone_number: str = Field(..., description="Número de teléfono del destinatario")
    message: str = Field(..., description="Contenido del mensaje")
    message_type: str = Field(default="text", description="Tipo de mensaje")

class WhatsAppTaskNotificationRequest(BaseModel):
    """Modelo para notificaciones de tareas"""
    task_id: str = Field(..., description="ID de la tarea de ClickUp")
    phone_numbers: List[str] = Field(..., description="Lista de números de teléfono")
    custom_message: Optional[str] = Field(None, description="Mensaje personalizado")

class WhatsAppBulkNotificationRequest(BaseModel):
    """Modelo para notificaciones masivas"""
    notifications: List[Dict[str, Any]] = Field(..., description="Lista de notificaciones")

class WhatsAppWebhookRequest(BaseModel):
    """Modelo para webhooks de WhatsApp"""
    event: str = Field(..., description="Tipo de evento")
    data: Dict[str, Any] = Field(..., description="Datos del evento")

# Dependencias
async def get_clickup_client() -> WhatsAppClient:
    """Obtiene el cliente de ClickUp"""
    return WhatsAppClient()

async def get_whatsapp_integrator(
    clickup_client: WhatsAppClient = Depends(get_clickup_client)
) -> WhatsAppClickUpIntegrator:
    """Obtiene el integrador de WhatsApp"""
    return WhatsAppClickUpIntegrator(clickup_client)

# Rutas de estado y configuración
@router.get("/status")
async def get_whatsapp_status(
    integrator: WhatsAppClickUpIntegrator = Depends(get_whatsapp_integrator)
):
    """Obtiene el estado de la integración de WhatsApp"""
    try:
        status = await integrator.get_whatsapp_status()
        return JSONResponse(content=status, status_code=200)
    except Exception as e:
        logger.error(f"Error getting WhatsApp status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting WhatsApp status: {str(e)}")

@router.get("/instance/status")
async def get_instance_status():
    """Obtiene el estado de la instancia de WhatsApp Evolution"""
    try:
        async with WhatsAppClient.client:
            status = await WhatsAppClient.client.get_instance_status()
            return JSONResponse(content=status.dict(), status_code=200)
    except Exception as e:
        logger.error(f"Error getting instance status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting instance status: {str(e)}")

@router.get("/instance/qr")
async def get_qr_code():
    """Obtiene el código QR para conectar WhatsApp"""
    try:
        async with WhatsAppClient.client:
            qr_response = await WhatsAppClient.client.get_qr_code()
            return JSONResponse(content=qr_response.dict(), status_code=200)
    except Exception as e:
        logger.error(f"Error getting QR code: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting QR code: {str(e)}")

@router.delete("/instance/logout")
async def logout_instance():
    """Cierra sesión de la instancia de WhatsApp"""
    try:
        async with WhatsAppClient.client:
            logout_response = await WhatsAppClient.client.logout_instance()
            return JSONResponse(content=logout_response.dict(), status_code=200)
    except Exception as e:
        logger.error(f"Error logging out instance: {e}")
        raise HTTPException(status_code=500, detail=f"Error logging out instance: {str(e)}")

# Rutas de envío de mensajes
@router.post("/send/message")
async def send_whatsapp_message(
    request: WhatsAppMessageRequest,
    background_tasks: BackgroundTasks
):
    """Envía un mensaje de WhatsApp"""
    try:
        # Enviar mensaje en background para no bloquear la respuesta
        async def send_message():
            async with WhatsAppClient.client:
                result = await WhatsAppClient.client.send_text_message(
                    request.phone_number, 
                    request.message
                )
                logger.info(f"WhatsApp message sent: {result.dict()}")
        
        background_tasks.add_task(send_message)
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Mensaje enviado en background",
                "task_id": "background_send"
            },
            status_code=202
        )
        
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

@router.post("/send/media")
async def send_media_message(
    phone_number: str,
    media_url: str,
    caption: Optional[str] = None,
    message_type: str = "image",
    background_tasks: BackgroundTasks = None
):
    """Envía un mensaje multimedia por WhatsApp"""
    try:
        # Enviar mensaje en background
        async def send_media():
            async with WhatsAppClient.client:
                result = await WhatsAppClient.client.send_media_message(
                    phone_number, 
                    media_url, 
                    caption, 
                    message_type
                )
                logger.info(f"WhatsApp media message sent: {result.dict()}")
        
        if background_tasks:
            background_tasks.add_task(send_media)
            return JSONResponse(
                content={
                    "success": True,
                    "message": "Mensaje multimedia enviado en background",
                    "task_id": "background_media_send"
                },
                status_code=202
            )
        else:
            # Envío síncrono
            async with WhatsAppClient.client:
                result = await WhatsAppClient.client.send_media_message(
                    phone_number, 
                    media_url, 
                    caption, 
                    message_type
                )
                return JSONResponse(content=result.dict(), status_code=200)
                
    except Exception as e:
        logger.error(f"Error sending WhatsApp media message: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending media message: {str(e)}")

# Rutas de notificaciones de tareas
@router.post("/notify/task")
async def notify_task(
    request: WhatsAppTaskNotificationRequest,
    integrator: WhatsAppClickUpIntegrator = Depends(get_whatsapp_integrator),
    background_tasks: BackgroundTasks = None
):
    """Envía notificación de tarea por WhatsApp"""
    try:
        # Enviar notificación en background
        async def send_notification():
            result = await integrator.send_custom_notification(
                request.task_id,
                request.custom_message or "Tienes una nueva notificación de tarea",
                request.phone_numbers
            )
            logger.info(f"Task notification sent: {len(result)} results")
        
        if background_tasks:
            background_tasks.add_task(send_notification)
            return JSONResponse(
                content={
                    "success": True,
                    "message": "Notificación de tarea enviada en background",
                    "task_id": "background_task_notification"
                },
                status_code=202
            )
        else:
            # Envío síncrono
            result = await integrator.send_custom_notification(
                request.task_id,
                request.custom_message or "Tienes una nueva notificación de tarea",
                request.phone_numbers
            )
            return JSONResponse(
                content={
                    "success": True,
                    "message": f"Notificación enviada a {len(request.phone_numbers)} destinatarios",
                    "results": [r.dict() for r in result]
                },
                status_code=200
            )
            
    except Exception as e:
        logger.error(f"Error sending task notification: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending task notification: {str(e)}")

@router.post("/notify/bulk")
async def send_bulk_notifications(
    request: WhatsAppBulkNotificationRequest,
    background_tasks: BackgroundTasks = None
):
    """Envía múltiples notificaciones en lote"""
    try:
        # Enviar notificaciones en background
        async def send_bulk():
            result = await WhatsAppNotificationService.send_bulk_notifications(request.notifications)
            logger.info(f"Bulk notifications sent: {len(result)} results")
        
        if background_tasks:
            background_tasks.add_task(send_bulk)
            return JSONResponse(
                content={
                    "success": True,
                    "message": "Notificaciones masivas enviadas en background",
                    "task_id": "background_bulk_notification"
                },
                status_code=202
            )
        else:
            # Envío síncrono
            result = await WhatsAppNotificationService.send_bulk_notifications(request.notifications)
            return JSONResponse(
                content={
                    "success": True,
                    "message": f"Notificaciones masivas enviadas: {len(result)} resultados",
                    "results": [r.dict() for r in result]
                },
                status_code=200
            )
            
    except Exception as e:
        logger.error(f"Error sending bulk notifications: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending bulk notifications: {str(e)}")

# Rutas de automatización
@router.post("/automation/reminders")
async def send_task_reminders(
    hours_before: int = 24,
    integrator: WhatsAppClickUpIntegrator = Depends(get_whatsapp_integrator),
    background_tasks: BackgroundTasks = None
):
    """Envía recordatorios automáticos de tareas que vencen pronto"""
    try:
        # Enviar recordatorios en background
        async def send_reminders():
            result = await integrator.send_task_reminders(hours_before)
            logger.info(f"Task reminders sent: {len(result)} results")
        
        if background_tasks:
            background_tasks.add_task(send_reminders)
            return JSONResponse(
                content={
                    "success": True,
                    "message": "Recordatorios automáticos enviados en background",
                    "task_id": "background_reminders"
                },
                status_code=202
            )
        else:
            # Envío síncrono
            result = await integrator.send_task_reminders(hours_before)
            return JSONResponse(
                content={
                    "success": True,
                    "message": f"Recordatorios enviados: {len(result)} resultados",
                    "hours_before": hours_before,
                    "results": [r.dict() for r in result]
                },
                status_code=200
            )
            
    except Exception as e:
        logger.error(f"Error sending task reminders: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending reminders: {str(e)}")

@router.post("/automation/overdue")
async def send_overdue_notifications(
    integrator: WhatsAppClickUpIntegrator = Depends(get_whatsapp_integrator),
    background_tasks: BackgroundTasks = None
):
    """Envía notificaciones automáticas de tareas vencidas"""
    try:
        # Enviar notificaciones en background
        async def send_overdue():
            result = await integrator.send_overdue_notifications()
            logger.info(f"Overdue notifications sent: {len(result)} results")
        
        if background_tasks:
            background_tasks.add_task(send_overdue)
            return JSONResponse(
                content={
                    "success": True,
                    "message": "Notificaciones de tareas vencidas enviadas en background",
                    "task_id": "background_overdue"
                },
                status_code=202
            )
        else:
            # Envío síncrono
            result = await integrator.send_overdue_notifications()
            return JSONResponse(
                content={
                    "success": True,
                    "message": f"Notificaciones de tareas vencidas enviadas: {len(result)} resultados",
                    "results": [r.dict() for r in result]
                },
                status_code=200
            )
            
    except Exception as e:
        logger.error(f"Error sending overdue notifications: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending overdue notifications: {str(e)}")

# Rutas de webhooks
@router.post("/webhook/clickup")
async def clickup_webhook(
    webhook_data: Dict[str, Any],
    integrator: WhatsAppClickUpIntegrator = Depends(get_whatsapp_integrator)
):
    """Procesa webhooks de ClickUp y envía notificaciones por WhatsApp"""
    try:
        # Procesar webhook en background
        result = await integrator.process_task_webhook(webhook_data)
        
        return JSONResponse(
            content={
                "success": True,
                "message": f"Webhook procesado: {len(result)} notificaciones enviadas",
                "webhook_data": webhook_data,
                "results": [r.dict() for r in result]
            },
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error processing ClickUp webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")

# Rutas de utilidad
@router.get("/contacts")
async def get_contacts():
    """Obtiene la lista de contactos de WhatsApp"""
    try:
        async with WhatsAppClient.client:
            contacts = await WhatsAppClient.client.get_contacts()
            return JSONResponse(content=contacts.dict(), status_code=200)
    except Exception as e:
        logger.error(f"Error getting contacts: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting contacts: {str(e)}")

@router.get("/chat/history/{phone_number}")
async def get_chat_history(
    phone_number: str,
    limit: int = 50
):
    """Obtiene el historial de chat con un número específico"""
    try:
        async with WhatsAppClient.client:
            history = await WhatsAppClient.client.get_chat_history(phone_number, limit)
            return JSONResponse(content=history.dict(), status_code=200)
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting chat history: {str(e)}")

@router.post("/chat/mark-read")
async def mark_message_as_read(message_id: str):
    """Marca un mensaje como leído"""
    try:
        async with WhatsAppClient.client:
            result = await WhatsAppClient.client.mark_as_read(message_id)
            return JSONResponse(content=result.dict(), status_code=200)
    except Exception as e:
        logger.error(f"Error marking message as read: {e}")
        raise HTTPException(status_code=500, detail=f"Error marking message as read: {str(e)}")

@router.get("/health")
async def whatsapp_health_check():
    """Verificación de salud de la integración de WhatsApp"""
    try:
        health_status = {
            "service": "WhatsApp Integration",
            "status": "healthy" if settings.WHATSAPP_ENABLED else "disabled",
            "evolution_url": settings.WHATSAPP_EVOLUTION_URL,
            "instance_name": settings.WHATSAPP_INSTANCE_NAME,
            "notifications_enabled": settings.WHATSAPP_NOTIFICATIONS_ENABLED,
            "timestamp": "2024-01-01T00:00:00Z"  # Placeholder
        }
        
        return JSONResponse(content=health_status, status_code=200)
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return JSONResponse(
            content={
                "service": "WhatsApp Integration",
                "status": "unhealthy",
                "error": str(e)
            },
            status_code=500
        )
