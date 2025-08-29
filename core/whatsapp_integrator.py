"""
Integrador de WhatsApp con ClickUp
Maneja la integración entre eventos de ClickUp y notificaciones de WhatsApp
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .whatsapp_client import WhatsAppNotificationService
from .phone_extractor import extract_whatsapp_numbers_from_task, get_primary_whatsapp_number

logger = logging.getLogger(__name__)

@dataclass
class TaskNotification:
    """Datos de notificación de tarea"""
    task_id: str
    task_title: str
    task_description: str
    task_url: str
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    notification_type: str = "custom"

class WhatsAppClickUpIntegrator:
    """Integrador principal entre ClickUp y WhatsApp"""
    
    def __init__(self, whatsapp_service: WhatsAppNotificationService):
        self.whatsapp_service = whatsapp_service
        self.notifications_sent = 0
        self.last_notification = None
        
    async def process_task_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un webhook de ClickUp y envía notificaciones de WhatsApp
        
        Args:
            webhook_data: Datos del webhook de ClickUp
            
        Returns:
            Resultado del procesamiento
        """
        try:
            # Mapear el evento del webhook
            event_type = self._map_webhook_event(webhook_data)
            if not event_type:
                logger.warning(f"Evento de webhook no reconocido: {webhook_data.get('event')}")
                return {"success": False, "error": "Evento no reconocido"}
            
            # Verificar si las notificaciones están habilitadas para este tipo
            if not self._is_notification_enabled(event_type):
                logger.info(f"Notificaciones deshabilitadas para evento: {event_type}")
                return {"success": True, "message": "Notificaciones deshabilitadas"}
            
            # Extraer información de la tarea
            task_info = self._extract_task_info(webhook_data)
            if not task_info:
                logger.warning("No se pudo extraer información de la tarea")
                return {"success": False, "error": "Información de tarea no válida"}
            
            # Extraer números de WhatsApp desde la descripción
            whatsapp_numbers = extract_whatsapp_numbers_from_task(
                task_info.task_description, 
                task_info.task_title
            )
            
            if not whatsapp_numbers:
                logger.info(f"No se encontraron números de WhatsApp en la tarea: {task_info.task_id}")
                return {"success": True, "message": "No hay números de WhatsApp"}
            
            # Enviar notificaciones a todos los números encontrados
            results = []
            for phone_number in whatsapp_numbers:
                try:
                    result = await self._send_task_notification(task_info, phone_number, event_type)
                    results.append({
                        "phone": phone_number,
                        "success": result.get("success", False),
                        "message": result.get("message", "Error desconocido")
                    })
                except Exception as e:
                    logger.error(f"Error enviando notificación a {phone_number}: {e}")
                    results.append({
                        "phone": phone_number,
                        "success": False,
                        "message": str(e)
                    })
            
            # Actualizar estadísticas
            successful_notifications = sum(1 for r in results if r["success"])
            self.notifications_sent += successful_notifications
            self.last_notification = datetime.now()
            
            return {
                "success": True,
                "message": f"Procesado evento {event_type}",
                "notifications_sent": successful_notifications,
                "total_numbers": len(whatsapp_numbers),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error procesando webhook: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_task_reminders(self, tasks_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Envía recordatorios para tareas que vencen pronto
        
        Args:
            tasks_data: Lista de tareas con información
            
        Returns:
            Resultado del envío de recordatorios
        """
        if not self._is_notification_enabled("due_soon"):
            return {"success": False, "error": "Notificaciones de recordatorios deshabilitadas"}
        
        results = []
        for task_data in tasks_data:
            try:
                # Extraer números de WhatsApp desde la descripción
                whatsapp_numbers = extract_whatsapp_numbers_from_task(
                    task_data.get("description", ""),
                    task_data.get("title", "")
                )
                
                if not whatsapp_numbers:
                    continue
                
                # Crear objeto de tarea
                task_info = TaskNotification(
                    task_id=task_data.get("id", ""),
                    task_title=task_data.get("title", ""),
                    task_description=task_data.get("description", ""),
                    task_url=task_data.get("url", ""),
                    assignee=task_data.get("assignee"),
                    due_date=self._parse_clickup_date(task_data.get("due_date")),
                    notification_type="due_soon"
                )
                
                # Enviar notificaciones
                for phone_number in whatsapp_numbers:
                    result = await self._send_task_notification(task_info, phone_number, "due_soon")
                    results.append({
                        "task_id": task_info.task_id,
                        "phone": phone_number,
                        "success": result.get("success", False),
                        "message": result.get("message", "Error desconocido")
                    })
                    
            except Exception as e:
                logger.error(f"Error procesando recordatorio para tarea {task_data.get('id')}: {e}")
                results.append({
                    "task_id": task_data.get("id", ""),
                    "phone": "unknown",
                    "success": False,
                    "message": str(e)
                })
        
        return {
            "success": True,
            "message": "Recordatorios procesados",
            "total_tasks": len(tasks_data),
            "results": results
        }
    
    async def send_overdue_notifications(self, tasks_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Envía notificaciones para tareas vencidas
        
        Args:
            tasks_data: Lista de tareas vencidas
            
        Returns:
            Resultado del envío de notificaciones
        """
        if not self._is_notification_enabled("overdue"):
            return {"success": False, "error": "Notificaciones de tareas vencidas deshabilitadas"}
        
        results = []
        for task_data in tasks_data:
            try:
                # Extraer números de WhatsApp desde la descripción
                whatsapp_numbers = extract_whatsapp_numbers_from_task(
                    task_data.get("description", ""),
                    task_data.get("title", "")
                )
                
                if not whatsapp_numbers:
                    continue
                
                # Crear objeto de tarea
                task_info = TaskNotification(
                    task_id=task_data.get("id", ""),
                    task_title=task_data.get("title", ""),
                    task_description=task_data.get("description", ""),
                    task_url=task_data.get("url", ""),
                    assignee=task_data.get("assignee"),
                    due_date=self._parse_clickup_date(task_data.get("due_date")),
                    notification_type="overdue"
                )
                
                # Enviar notificaciones
                for phone_number in whatsapp_numbers:
                    result = await self._send_task_notification(task_info, phone_number, "overdue")
                    results.append({
                        "task_id": task_info.task_id,
                        "phone": phone_number,
                        "success": result.get("success", False),
                        "message": result.get("message", "Error desconocido")
                    })
                    
            except Exception as e:
                logger.error(f"Error procesando notificación vencida para tarea {task_data.get('id')}: {e}")
                results.append({
                    "task_id": task_data.get("id", ""),
                    "phone": "unknown",
                    "success": False,
                    "message": str(e)
                })
        
        return {
            "success": True,
            "message": "Notificaciones de tareas vencidas procesadas",
            "total_tasks": len(tasks_data),
            "results": results
        }
    
    async def send_custom_notification(
        self, 
        task_data: Dict[str, Any], 
        notification_type: str = "custom",
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envía una notificación personalizada para una tarea
        
        Args:
            task_data: Datos de la tarea
            notification_type: Tipo de notificación
            custom_message: Mensaje personalizado (opcional)
            
        Returns:
            Resultado del envío
        """
        try:
            # Extraer números de WhatsApp desde la descripción
            whatsapp_numbers = extract_whatsapp_numbers_from_task(
                task_data.get("description", ""),
                task_data.get("title", "")
            )
            
            if not whatsapp_numbers:
                return {"success": False, "error": "No se encontraron números de WhatsApp"}
            
            # Crear objeto de tarea
            task_info = TaskNotification(
                task_id=task_data.get("id", ""),
                task_title=task_data.get("title", ""),
                task_description=task_data.get("description", ""),
                task_url=task_data.get("url", ""),
                assignee=task_data.get("assignee"),
                due_date=self._parse_clickup_date(task_data.get("due_date")),
                notification_type=notification_type
            )
            
            # Enviar notificaciones
            results = []
            for phone_number in whatsapp_numbers:
                result = await self._send_task_notification(
                    task_info, 
                    phone_number, 
                    notification_type,
                    custom_message
                )
                results.append({
                    "phone": phone_number,
                    "success": result.get("success", False),
                    "message": result.get("message", "Error desconocido")
                })
            
            return {
                "success": True,
                "message": "Notificación personalizada enviada",
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error enviando notificación personalizada: {e}")
            return {"success": False, "error": str(e)}
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Obtiene el estado de la integración"""
        return {
            "status": "active",
            "notifications_sent": self.notifications_sent,
            "last_notification": self.last_notification.isoformat() if self.last_notification else None,
            "whatsapp_service_status": self.whatsapp_service.get_status(),
            "phone_extraction_enabled": True,
            "extraction_method": "description_based"
        }
    
    def _map_webhook_event(self, webhook_data: Dict[str, Any]) -> Optional[str]:
        """Mapea eventos de webhook a tipos de notificación"""
        event = webhook_data.get("event", "").lower()
        
        event_mapping = {
            "taskcreated": "created",
            "taskupdated": "updated",
            "taskcompleted": "completed",
            "taskdeleted": "deleted",
            "taskassigned": "assigned",
            "taskunassigned": "unassigned",
            "taskduesoon": "due_soon",
            "taskoverdue": "overdue"
        }
        
        return event_mapping.get(event)
    
    def _is_notification_enabled(self, notification_type: str) -> bool:
        """Verifica si las notificaciones están habilitadas para un tipo específico"""
        # Esta función debería verificar la configuración
        # Por ahora, asumimos que todas están habilitadas
        return True
    
    def _extract_task_info(self, webhook_data: Dict[str, Any]) -> Optional[TaskNotification]:
        """Extrae información de la tarea del webhook"""
        try:
            task_data = webhook_data.get("task", {})
            
            return TaskNotification(
                task_id=task_data.get("id", ""),
                task_title=task_data.get("name", ""),
                task_description=task_data.get("description", ""),
                task_url=task_data.get("url", ""),
                assignee=task_data.get("assignee", {}).get("username") if task_data.get("assignee") else None,
                due_date=self._parse_clickup_date(task_data.get("due_date")),
                notification_type=self._map_webhook_event(webhook_data) or "custom"
            )
        except Exception as e:
            logger.error(f"Error extrayendo información de tarea: {e}")
            return None
    
    def _parse_clickup_date(self, date_string: Optional[str]) -> Optional[datetime]:
        """Parsea fechas de ClickUp"""
        if not date_string:
            return None
        
        try:
            # ClickUp usa timestamps en milisegundos
            if date_string.isdigit():
                timestamp = int(date_string) / 1000  # Convertir a segundos
                return datetime.fromtimestamp(timestamp)
            else:
                # Intentar parsear como string ISO
                return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except Exception as e:
            logger.warning(f"No se pudo parsear fecha: {date_string}, error: {e}")
            return None
    
    async def _send_task_notification(
        self, 
        task_info: TaskNotification, 
        phone_number: str, 
        notification_type: str,
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Envía una notificación de tarea específica"""
        try:
            result = await self.whatsapp_service.send_task_notification(
                phone_number=phone_number,
                task_title=task_info.task_title,
                task_description=task_info.task_description,
                notification_type=notification_type,
                due_date=task_info.due_date,
                assignee=task_info.assignee,
                custom_message=custom_message
            )
            
            return {
                "success": result.success,
                "message": result.message,
                "data": result.data
            }
            
        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")
            return {
                "success": False,
                "message": str(e),
                "data": None
            }
