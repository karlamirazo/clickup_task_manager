"""
Programador de notificaciones automáticas para ClickUp
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .clickup_webhook_manager import webhook_manager
from .whatsapp_integrator import WhatsAppClickUpIntegrator
from .whatsapp_simulator import whatsapp_simulator
from .config import settings

logger = logging.getLogger(__name__)

@dataclass
class ScheduledNotification:
    """Notificación programada"""
    id: str
    task_id: str
    task_name: str
    phone_numbers: List[str]
    notification_type: str
    scheduled_time: datetime
    message: str
    status: str = "pending"  # pending, sent, failed, cancelled

class NotificationScheduler:
    """Programador de notificaciones automáticas"""
    
    def __init__(self, whatsapp_integrator: WhatsAppClickUpIntegrator):
        self.whatsapp_integrator = whatsapp_integrator
        self.scheduled_notifications: List[ScheduledNotification] = []
        self.is_running = False
        self.check_interval = 60  # segundos
        self.last_check = None
        
    async def start_scheduler(self) -> None:
        """Inicia el programador de notificaciones"""
        if self.is_running:
            logger.info("⚠️ El programador ya está ejecutándose")
            return
        
        logger.info("🚀 Iniciando programador de notificaciones...")
        self.is_running = True
        
        # Conectar WhatsApp (simulador o real)
        if settings.WHATSAPP_SIMULATOR_ENABLED:
            await whatsapp_simulator.connect()
            logger.info("✅ WhatsApp Simulator conectado")
        
        # Iniciar bucle principal
        while self.is_running:
            try:
                await self._check_and_send_notifications()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error en el programador: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def stop_scheduler(self) -> None:
        """Detiene el programador de notificaciones"""
        logger.info("🛑 Deteniendo programador de notificaciones...")
        self.is_running = False
        
        if settings.WHATSAPP_SIMULATOR_ENABLED:
            await whatsapp_simulator.disconnect()
            logger.info("✅ WhatsApp Simulator desconectado")
    
    async def _check_and_send_notifications(self) -> None:
        """Verifica y envía notificaciones programadas"""
        now = datetime.now()
        
        # Filtrar notificaciones pendientes que deben enviarse
        pending_notifications = [
            notif for notif in self.scheduled_notifications
            if notif.status == "pending" and notif.scheduled_time <= now
        ]
        
        if pending_notifications:
            logger.info(f"📨 Enviando {len(pending_notifications)} notificaciones programadas...")
            
            for notification in pending_notifications:
                try:
                    await self._send_scheduled_notification(notification)
                except Exception as e:
                    logger.error(f"Error enviando notificación {notification.id}: {e}")
                    notification.status = "failed"
        
        self.last_check = now
    
    async def _send_scheduled_notification(self, notification: ScheduledNotification) -> None:
        """Envía una notificación programada"""
        logger.info(f"📱 Enviando notificación {notification.notification_type} para tarea: {notification.task_name}")
        
        # Enviar a cada número de teléfono
        for phone_number in notification.phone_numbers:
            try:
                if settings.WHATSAPP_SIMULATOR_ENABLED:
                    # Usar simulador
                    result = await whatsapp_simulator.send_text_message(
                        phone_number, 
                        notification.message
                    )
                else:
                    # Usar WhatsApp real (Evolution API)
                    result = await self.whatsapp_integrator.whatsapp_service.send_text_message(
                        phone_number, 
                        notification.message
                    )
                
                if result.get("status") == "success":
                    logger.info(f"✅ Notificación enviada a {phone_number}")
                else:
                    logger.warning(f"⚠️ Error enviando a {phone_number}: {result.get('message', 'Error desconocido')}")
                    
            except Exception as e:
                logger.error(f"💥 Error enviando notificación a {phone_number}: {e}")
        
        # Marcar como enviada
        notification.status = "sent"
        logger.info(f"✅ Notificación {notification.id} marcada como enviada")
    
    async def schedule_task_reminder(self, task_data: Dict[str, Any], reminder_type: str = "due_soon") -> str:
        """Programa un recordatorio para una tarea"""
        task_id = task_data.get("id")
        task_name = task_data.get("name", "Tarea sin nombre")
        task_description = task_data.get("description", "")
        
        # Extraer números de WhatsApp
        from .phone_extractor import extract_whatsapp_numbers_from_task
        phone_numbers = extract_whatsapp_numbers_from_task(task_description, task_name)
        
        if not phone_numbers:
            logger.warning(f"No se encontraron números de WhatsApp para la tarea: {task_name}")
            return None
        
        # Determinar tiempo de recordatorio
        scheduled_time = self._calculate_reminder_time(task_data, reminder_type)
        
        # Crear mensaje personalizado
        message = self._create_reminder_message(task_data, reminder_type)
        
        # Crear notificación programada
        notification = ScheduledNotification(
            id=f"reminder_{task_id}_{int(datetime.now().timestamp())}",
            task_id=task_id,
            task_name=task_name,
            phone_numbers=phone_numbers,
            notification_type=reminder_type,
            scheduled_time=scheduled_time,
            message=message
        )
        
        self.scheduled_notifications.append(notification)
        
        logger.info(f"📅 Recordatorio programado para {task_name} a las {scheduled_time.strftime('%H:%M')}")
        
        return notification.id
    
    def _calculate_reminder_time(self, task_data: Dict[str, Any], reminder_type: str) -> datetime:
        """Calcula el tiempo para el recordatorio"""
        now = datetime.now()
        
        if reminder_type == "due_soon":
            # Recordatorio 1 hora antes
            return now + timedelta(hours=1)
        elif reminder_type == "overdue":
            # Recordatorio inmediato para tareas vencidas
            return now
        elif reminder_type == "daily":
            # Recordatorio diario a las 9:00 AM
            tomorrow = now + timedelta(days=1)
            return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        else:
            # Recordatorio por defecto en 30 minutos
            return now + timedelta(minutes=30)
    
    def _create_reminder_message(self, task_data: Dict[str, Any], reminder_type: str) -> str:
        """Crea el mensaje de recordatorio"""
        task_name = task_data.get("name", "Tarea")
        due_date = task_data.get("due_date")
        
        if reminder_type == "due_soon":
            return f"⏰ RECORDATORIO: La tarea '{task_name}' vence pronto. ¡Revisa ClickUp!"
        elif reminder_type == "overdue":
            return f"🚨 URGENTE: La tarea '{task_name}' está vencida. ¡Actúa ahora!"
        elif reminder_type == "daily":
            return f"📋 RESUMEN DIARIO: Revisa tus tareas pendientes en ClickUp, incluyendo '{task_name}'"
        else:
            return f"📱 Notificación de ClickUp: {task_name}"
    
    async def schedule_custom_notification(self, task_data: Dict[str, Any], custom_message: str, delay_minutes: int = 0) -> str:
        """Programa una notificación personalizada"""
        task_id = task_data.get("id")
        task_name = task_data.get("name", "Tarea sin nombre")
        task_description = task_data.get("description", "")
        
        # Extraer números de WhatsApp
        from .phone_extractor import extract_whatsapp_numbers_from_task
        phone_numbers = extract_whatsapp_numbers_from_task(task_description, task_name)
        
        if not phone_numbers:
            logger.warning(f"No se encontraron números de WhatsApp para la tarea: {task_name}")
            return None
        
        # Calcular tiempo de envío
        scheduled_time = datetime.now() + timedelta(minutes=delay_minutes)
        
        # Crear notificación programada
        notification = ScheduledNotification(
            id=f"custom_{task_id}_{int(datetime.now().timestamp())}",
            task_id=task_id,
            task_name=task_name,
            phone_numbers=phone_numbers,
            notification_type="custom",
            scheduled_time=scheduled_time,
            message=custom_message
        )
        
        self.scheduled_notifications.append(notification)
        
        logger.info(f"📅 Notificación personalizada programada para {task_name} a las {scheduled_time.strftime('%H:%M')}")
        
        return notification.id
    
    def get_scheduled_notifications(self, status: str = None) -> List[ScheduledNotification]:
        """Obtiene las notificaciones programadas"""
        if status:
            return [notif for notif in self.scheduled_notifications if notif.status == status]
        return self.scheduled_notifications
    
    def cancel_notification(self, notification_id: str) -> bool:
        """Cancela una notificación programada"""
        for notification in self.scheduled_notifications:
            if notification.id == notification_id and notification.status == "pending":
                notification.status = "cancelled"
                logger.info(f"❌ Notificación {notification_id} cancelada")
                return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del programador"""
        total = len(self.scheduled_notifications)
        pending = len([n for n in self.scheduled_notifications if n.status == "pending"])
        sent = len([n for n in self.scheduled_notifications if n.status == "sent"])
        failed = len([n for n in self.scheduled_notifications if n.status == "failed"])
        cancelled = len([n for n in self.scheduled_notifications if n.status == "cancelled"])
        
        return {
            "total_notifications": total,
            "pending": pending,
            "sent": sent,
            "failed": failed,
            "cancelled": cancelled,
            "is_running": self.is_running,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "check_interval": self.check_interval
        }

# Función de conveniencia para crear el programador
def create_notification_scheduler(whatsapp_integrator: WhatsAppClickUpIntegrator) -> NotificationScheduler:
    """Crea una instancia del programador de notificaciones"""
    return NotificationScheduler(whatsapp_integrator)

