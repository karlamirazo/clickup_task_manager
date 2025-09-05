"""
Gestor de notificaciones automáticas para ClickUp
Integra Evolution API con sistema de tareas para envío automático
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import uuid

from core.robust_whatsapp_service import RobustWhatsAppService
from integrations.clickup.client import ClickUpClient
from core.phone_extractor import extract_whatsapp_numbers_from_task, PhoneNumberExtractor
from integrations.evolution_api.config import get_evolution_config, is_production_ready
from core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class AutomatedNotification:
    """Notificación automática programada"""
    id: str
    task_id: str
    task_title: str
    task_description: str
    notification_type: str
    scheduled_time: datetime
    due_date: Optional[datetime] = None
    assignee: Optional[str] = None
    priority: str = "normal"
    status: str = "pending"  # pending, sent, failed, cancelled
    retry_count: int = 0
    max_retries: int = 3
    phone_numbers: List[str] = None

class AutomatedNotificationManager:
    """Gestor de notificaciones automáticas para ClickUp"""
    
    def __init__(self):
        self.config = get_evolution_config()
        self.whatsapp_service: Optional[ProductionWhatsAppService] = None
        self.clickup_client: Optional[ClickUpClient] = None
        self.phone_extractor = PhoneNumberExtractor()
        
        # Cola de notificaciones
        self.notification_queue: asyncio.Queue = asyncio.Queue()
        self.scheduled_notifications: List[AutomatedNotification] = []
        
        # Estado del sistema
        self.is_running = False
        self.processing_task: Optional[asyncio.Task] = None
        self.scheduler_task: Optional[asyncio.Task] = None
        
        # Configuración de intervalos
        self.check_interval = 60  # segundos
        self.last_check = None
        
    async def start(self) -> bool:
        """Inicia el gestor de notificaciones automáticas"""
        if self.is_running:
            logger.info("⚠️ El gestor ya está ejecutándose")
            return True
        
        logger.info("🚀 Iniciando gestor de notificaciones automáticas...")
        
        # Verificar configuración
        if not is_production_ready():
            logger.error("❌ Configuración de producción no está lista")
            return False
        
        try:
            # Inicializar servicios
            await self._initialize_services()
            
            # Iniciar tareas de procesamiento
            self.is_running = True
            self.processing_task = asyncio.create_task(self._process_notification_queue())
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
            
            logger.info("✅ Gestor de notificaciones automáticas iniciado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error iniciando gestor: {e}")
            return False
    
    async def stop(self) -> None:
        """Detiene el gestor de notificaciones"""
        logger.info("🛑 Deteniendo gestor de notificaciones...")
        self.is_running = False
        
        # Cancelar tareas
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        # Desconectar servicios
        if self.whatsapp_service:
            await self.whatsapp_service.disconnect()
        
        logger.info("✅ Gestor de notificaciones detenido")
    
    async def _initialize_services(self) -> None:
        """Inicializa los servicios necesarios"""
        # Inicializar servicio de WhatsApp
        self.whatsapp_service = ProductionWhatsAppService()
        await self.whatsapp_service.connect()
        logger.info("✅ Servicio de WhatsApp inicializado")
        
        # Inicializar cliente de ClickUp
        self.clickup_client = ClickUpClient()
        logger.info("✅ Cliente de ClickUp inicializado")
    
    async def schedule_task_notification(
        self, 
        task_data: Dict[str, Any],
        notification_type: str,
        delay_minutes: int = 0
    ) -> str:
        """Programa una notificación para una tarea"""
        try:
            # Extraer números de teléfono
            phone_numbers = await self._extract_phones_from_task(task_data)
            
            if not phone_numbers:
                logger.warning(f"⚠️ No se encontraron números de teléfono para la tarea {task_data.get('id')}")
                return None
            
            # Crear notificación
            notification = AutomatedNotification(
                id=str(uuid.uuid4()),
                task_id=task_data.get('id', ''),
                task_title=task_data.get('name', 'Sin título'),
                task_description=task_data.get('description', ''),
                notification_type=notification_type,
                scheduled_time=datetime.now() + timedelta(minutes=delay_minutes),
                due_date=self._parse_due_date(task_data.get('due_date')),
                assignee=self._get_assignee_name(task_data),
                priority=task_data.get('priority', 'normal'),
                phone_numbers=phone_numbers
            )
            
            # Agregar a la cola
            await self.notification_queue.put(notification)
            self.scheduled_notifications.append(notification)
            
            logger.info(f"📅 Notificación programada: {notification_type} para tarea {notification.task_id}")
            return notification.id
            
        except Exception as e:
            logger.error(f"Error programando notificación: {e}")
            return None
    
    async def _extract_phones_from_task(self, task_data: Dict[str, Any]) -> List[str]:
        """Extrae números de teléfono de una tarea"""
        phones = []
        
        # Buscar en campos específicos
        for field_name in self.config.phone_extraction_fields:
            if field_name in task_data:
                field_value = task_data[field_name]
                if isinstance(field_value, str):
                    extracted = self.phone_extractor.extract_phones_from_text(field_value)
                    phones.extend([phone.number for phone in extracted])
                elif isinstance(field_value, dict):
                    # Buscar en campos personalizados
                    for key, value in field_value.items():
                        if isinstance(value, str):
                            extracted = self.phone_extractor.extract_phones_from_text(value)
                            phones.extend([phone.number for phone in extracted])
        
        # Buscar en comentarios
        if "comments" in task_data:
            for comment in task_data["comments"]:
                if "comment" in comment:
                    extracted = self.phone_extractor.extract_phones_from_text(comment["comment"])
                    phones.extend([phone.number for phone in extracted])
        
        # Eliminar duplicados y validar
        unique_phones = list(set(phones))
        valid_phones = [phone for phone in unique_phones if self._validate_phone_number(phone)]
        
        return valid_phones
    
    def _validate_phone_number(self, phone: str) -> bool:
        """Valida un número de teléfono"""
        if not phone:
            return False
        
        # Limpiar el número
        clean = ''.join(filter(str.isdigit, phone))
        
        # Verificar longitud mínima
        if len(clean) < 10:
            return False
        
        # Verificar código de país si es requerido
        if self.config.require_country_code:
            if not clean.startswith(self.config.default_country_code):
                return False
        
        return True
    
    def _parse_due_date(self, due_date_str: Optional[str]) -> Optional[datetime]:
        """Parsea la fecha de vencimiento"""
        if not due_date_str:
            return None
        
        try:
            # Formato ISO de ClickUp
            return datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
        except Exception:
            try:
                # Formato timestamp
                return datetime.fromtimestamp(int(due_date_str) / 1000)
            except Exception:
                return None
    
    def _get_assignee_name(self, task_data: Dict[str, Any]) -> Optional[str]:
        """Obtiene el nombre del asignado"""
        assignee = task_data.get('assignees', [])
        if assignee and len(assignee) > 0:
            return assignee[0].get('username', 'Usuario')
        return None
    
    async def _process_notification_queue(self) -> None:
        """Procesa la cola de notificaciones"""
        while self.is_running:
            try:
                # Esperar notificación con timeout
                try:
                    notification = await asyncio.wait_for(
                        self.notification_queue.get(), 
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Procesar notificación
                await self._process_notification(notification)
                
                # Marcar como procesada
                self.notification_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error procesando cola de notificaciones: {e}")
    
    async def _process_notification(self, notification: AutomatedNotification) -> None:
        """Procesa una notificación individual"""
        try:
            logger.info(f"📱 Procesando notificación: {notification.notification_type} para tarea {notification.task_id}")
            
            # Verificar si es hora de enviar
            if notification.scheduled_time > datetime.now():
                # Re-agregar a la cola para más tarde
                await self.notification_queue.put(notification)
                return
            
            # Enviar notificación
            result = await self._send_notification(notification)
            
            if result.get("success"):
                notification.status = "sent"
                logger.info(f"✅ Notificación enviada: {notification.id}")
            else:
                notification.status = "failed"
                logger.error(f"❌ Error enviando notificación: {result.get('error')}")
                
                # Reintentar si es posible
                if notification.retry_count < notification.max_retries:
                    notification.retry_count += 1
                    notification.status = "retrying"
                    notification.scheduled_time = datetime.now() + timedelta(minutes=5 * notification.retry_count)
                    await self.notification_queue.put(notification)
                    logger.info(f"🔄 Reintentando notificación {notification.id} (intento {notification.retry_count})")
                
        except Exception as e:
            logger.error(f"Error procesando notificación {notification.id}: {e}")
            notification.status = "failed"
    
    async def _send_notification(self, notification: AutomatedNotification) -> Dict[str, Any]:
        """Envía una notificación"""
        if not self.whatsapp_service or not self.whatsapp_service.is_connected:
            return {"success": False, "error": "Servicio de WhatsApp no disponible"}
        
        try:
            # Crear notificación de producción
            prod_notification = ProductionNotification(
                id=notification.id,
                task_id=notification.task_id,
                task_title=notification.task_title,
                task_description=notification.task_description,
                phone_numbers=notification.phone_numbers or [],
                notification_type=notification.notification_type,
                due_date=notification.due_date,
                assignee=notification.assignee,
                priority=notification.priority
            )
            
            # Enviar
            result = await self.whatsapp_service.send_task_notification(prod_notification)
            return result
            
        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")
            return {"success": False, "error": str(e)}
    
    async def _scheduler_loop(self) -> None:
        """Bucle principal del programador"""
        while self.is_running:
            try:
                await self._check_scheduled_notifications()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error en el programador: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_scheduled_notifications(self) -> None:
        """Verifica notificaciones programadas"""
        now = datetime.now()
        
        # Filtrar notificaciones que deben enviarse
        due_notifications = [
            notif for notif in self.scheduled_notifications
            if notif.status == "pending" and notif.scheduled_time <= now
        ]
        
        if due_notifications:
            logger.info(f"📨 Enviando {len(due_notifications)} notificaciones programadas...")
            
            for notification in due_notifications:
                try:
                    await self._process_notification(notification)
                except Exception as e:
                    logger.error(f"Error procesando notificación programada {notification.id}: {e}")
        
        self.last_check = now
    
    async def process_clickup_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa webhooks de ClickUp para notificaciones automáticas"""
        try:
            event_type = webhook_data.get('type', '')
            task_data = webhook_data.get('task', {})
            
            if not task_data:
                return {"success": False, "error": "No hay datos de tarea en el webhook"}
            
            # Mapear tipos de evento a tipos de notificación
            notification_mapping = {
                'taskCreated': 'task_created',
                'taskUpdated': 'task_updated',
                'taskCompleted': 'task_completed',
                'taskDeleted': 'task_deleted',
                'taskAssigned': 'task_assigned',
                'taskDueDateChanged': 'task_due_soon'
            }
            
            notification_type = notification_mapping.get(event_type)
            if not notification_type:
                logger.debug(f"Evento no mapeado: {event_type}")
                return {"success": False, "error": f"Tipo de evento no soportado: {event_type}"}
            
            # Verificar si este tipo de notificación está habilitado
            if not self.config.notification_types.get(notification_type, False):
                logger.debug(f"Notificación {notification_type} deshabilitada")
                return {"success": False, "error": f"Tipo de notificación deshabilitado: {notification_type}"}
            
            # Programar notificación
            notification_id = await self.schedule_task_notification(
                task_data, 
                notification_type
            )
            
            if notification_id:
                return {
                    "success": True, 
                    "message": f"Notificación programada: {notification_type}",
                    "notification_id": notification_id
                }
            else:
                return {"success": False, "error": "No se pudo programar la notificación"}
                
        except Exception as e:
            logger.error(f"Error procesando webhook de ClickUp: {e}")
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado del gestor"""
        return {
            "is_running": self.is_running,
            "queue_size": self.notification_queue.qsize(),
            "scheduled_notifications": len(self.scheduled_notifications),
            "whatsapp_service_connected": (
                self.whatsapp_service.is_connected 
                if self.whatsapp_service else False
            ),
            "clickup_client_available": self.clickup_client is not None,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "config": {
                "production_ready": is_production_ready(),
                "notification_types": self.config.notification_types,
                "phone_extraction_fields": self.config.phone_extraction_fields
            }
        }

# Instancia global del gestor
automated_manager = AutomatedNotificationManager()

async def get_automated_manager() -> AutomatedNotificationManager:
    """Obtiene la instancia del gestor automático"""
    if not automated_manager.is_running:
        await automated_manager.start()
    return automated_manager
