# ===== SISTEMA DE NOTIFICACIONES POR EMAIL =====
# ===== ARCHIVO NUEVO - NOTIFICACIONES AUTOMÁTICAS =====

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from core.database import get_db
from utils.advanced_notifications import AdvancedNotificationService
from core.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
notification_logger = logging.getLogger("notifications")

router = APIRouter(prefix="/notifications", tags=["notifications"])

# Instancia del servicio de notificaciones
notification_service = AdvancedNotificationService()

@router.post("/send-task-notification", status_code=status.HTTP_200_OK)
async def send_task_notification(
    notification_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Enviar notificación por email cuando se crea una tarea
    """
    try:
        notification_logger.info(f"📧 Recibida solicitud de notificación para tarea: {notification_data.get('task_name', 'N/A')}")
        
        # Validar datos requeridos
        required_fields = ['task_id', 'task_name', 'contact_email', 'action']
        for field in required_fields:
            if not notification_data.get(field):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campo requerido faltante: {field}"
                )
        
        # Extraer datos de la notificación
        task_id = notification_data['task_id']
        task_name = notification_data['task_name']
        task_description = notification_data.get('task_description', 'Sin descripción')
        contact_email = notification_data['contact_email']
        contact_name = notification_data.get('contact_name', 'Usuario')
        due_date = notification_data.get('due_date')
        priority = notification_data.get('priority', 3)
        assignee = notification_data.get('assignee')
        action = notification_data['action']
        workspace_id = notification_data.get('workspace_id')
        list_id = notification_data.get('list_id')
        
        # Validar email
        if '@' not in contact_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email inválido"
            )
        
        # Preparar datos para el servicio de notificaciones
        recipient_emails = [contact_email]
        
        # Mapear prioridad a texto
        priority_text = {
            1: "Urgente",
            2: "Alta", 
            3: "Normal",
            4: "Baja"
        }.get(priority, "Normal")
        
        # Mapear acción a texto
        action_text = {
            'created': 'creada',
            'updated': 'actualizada',
            'deleted': 'eliminada',
            'completed': 'completada'
        }.get(action, action)
        
        notification_logger.info(f"📧 Enviando notificación de tarea {action_text}: {task_name}")
        notification_logger.info(f"📧 Destinatario: {contact_email}")
        notification_logger.info(f"📧 Prioridad: {priority_text}")
        notification_logger.info(f"📧 Fecha límite: {due_date}")
        
        # Enviar notificación usando el servicio avanzado
        result = await notification_service.send_task_notification(
            action=f"Tarea {action_text}",
            task_id=str(task_id),
            task_name=task_name,
            recipient_emails=recipient_emails,
            status="pendiente",
            priority=priority,
            assignee_name=assignee,
            due_date=due_date,
            description=task_description
        )
        
        # Obtener resumen de resultados
        summary = result.get_summary()
        
        if summary['successful']['emails'] > 0:
            notification_logger.info(f"✅ Notificación enviada exitosamente a {contact_email}")
            
            # Registrar en la base de datos (opcional)
            # await log_notification_sent(db, notification_data, summary)
            
            return {
                "success": True,
                "message": f"Notificación enviada exitosamente a {contact_email}",
                "task_name": task_name,
                "recipient": contact_email,
                "sent_at": datetime.now().isoformat(),
                "summary": summary
            }
        else:
            notification_logger.error(f"❌ No se pudo enviar la notificación a {contact_email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"No se pudo enviar la notificación: {summary.get('errors', ['Error desconocido'])}"
            )
            
    except HTTPException:
        # Re-lanzar excepciones HTTP
        raise
    except Exception as e:
        notification_logger.error(f"❌ Error inesperado enviando notificación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/test-email", status_code=status.HTTP_200_OK)
async def test_email_notification(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Endpoint de prueba para verificar el sistema de notificaciones por email
    """
    try:
        notification_logger.info(f"🧪 Enviando email de prueba a: {email}")
        
        # Validar email
        if '@' not in email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email inválido"
            )
        
        # Enviar notificación de prueba
        result = await notification_service.send_task_notification(
            action="Prueba del sistema",
            task_id="test-123",
            task_name="Tarea de Prueba del Sistema",
            recipient_emails=[email],
            status="pendiente",
            priority=3,
            assignee_name="Sistema",
            due_date=datetime.now().strftime("%Y-%m-%d"),
            description="Esta es una notificación de prueba para verificar que el sistema de emails funciona correctamente."
        )
        
        summary = result.get_summary()
        
        if summary['successful']['emails'] > 0:
            return {
                "success": True,
                "message": f"Email de prueba enviado exitosamente a {email}",
                "recipient": email,
                "sent_at": datetime.now().isoformat(),
                "summary": summary
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"No se pudo enviar el email de prueba: {summary.get('errors', ['Error desconocido'])}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        notification_logger.error(f"❌ Error en prueba de email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/status", status_code=status.HTTP_200_OK)
async def get_notification_status():
    """
    Obtener el estado del sistema de notificaciones
    """
    try:
        # Verificar configuración SMTP
        smtp_configured = bool(
            settings.SMTP_HOST and 
            settings.SMTP_USER and 
            settings.SMTP_PASSWORD
        )
        
        # Obtener estadísticas del servicio
        stats = notification_service.stats
        
        return {
            "service_status": "active" if smtp_configured else "inactive",
            "smtp_configured": smtp_configured,
            "smtp_host": settings.SMTP_HOST,
            "smtp_port": settings.SMTP_PORT,
            "smtp_user": settings.SMTP_USER,
            "smtp_use_tls": settings.SMTP_USE_TLS,
            "smtp_use_ssl": settings.SMTP_USE_SSL,
            "statistics": stats,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        notification_logger.error(f"❌ Error obteniendo estado de notificaciones: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
