"""
Cliente de WhatsApp Evolution API para integración con ClickUp
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import aiohttp
from pydantic import BaseModel, Field

from core.config import settings
from .simulator import WhatsAppSimulator

# Configurar logging
logger = logging.getLogger(__name__)

class WhatsAppMessage(BaseModel):
    """Modelo para mensajes de WhatsApp"""
    to: str = Field(..., description="Número de teléfono del destinatario")
    message: str = Field(..., description="Contenido del mensaje")
    type: str = Field(default="text", description="Tipo de mensaje")
    media_url: Optional[str] = Field(None, description="URL del archivo multimedia")
    caption: Optional[str] = Field(None, description="Pie de foto para archivos multimedia")

class WhatsAppResponse(BaseModel):
    """Modelo para respuestas de la API de WhatsApp"""
    success: bool
    message: str
    data: Optional[Dict] = None
    error: Optional[str] = None

class WhatsAppClient:
    """Cliente para interactuar con la API de Evolution para WhatsApp"""
    
    def __init__(self):
        self.base_url = settings.WHATSAPP_EVOLUTION_URL
        self.api_key = settings.WHATSAPP_EVOLUTION_API_KEY
        self.instance_name = settings.WHATSAPP_INSTANCE_NAME
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                "Content-Type": "application/json",
                "apikey": self.api_key
            } if self.api_key else {"Content-Type": "application/json"}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None
    ) -> WhatsAppResponse:
        """Realiza una petición HTTP a la API de WhatsApp"""
        if not self.session:
            raise RuntimeError("Cliente no inicializado. Use 'async with' o llame a start()")
            
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, json=data) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        response_data = json.loads(response_text)
                        return WhatsAppResponse(
                            success=True,
                            message="Operación exitosa",
                            data=response_data
                        )
                    except json.JSONDecodeError:
                        return WhatsAppResponse(
                            success=True,
                            message="Operación exitosa",
                            data={"raw_response": response_text}
                        )
                else:
                    return WhatsAppResponse(
                        success=False,
                        message=f"Error HTTP {response.status}",
                        error=response_text
                    )
                    
        except Exception as e:
            logger.error(f"Error en petición a WhatsApp API: {e}")
            return WhatsAppResponse(
                success=False,
                message="Error de conexión",
                error=str(e)
            )
    
    async def start(self):
        """Inicia la sesión del cliente"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    "Content-Type": "application/json",
                    "apikey": self.api_key
                } if self.api_key else {"Content-Type": "application/json"}
            )
    
    async def stop(self):
        """Detiene la sesión del cliente"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_instance_info(self) -> WhatsAppResponse:
        """Obtiene información de la instancia de WhatsApp"""
        return await self._make_request("GET", f"/instance/info/{self.instance_name}")
    
    async def get_instance_status(self) -> WhatsAppResponse:
        """Obtiene el estado de la instancia de WhatsApp"""
        return await self._make_request("GET", f"/instance/status/{self.instance_name}")
    
    async def get_qr_code(self) -> WhatsAppResponse:
        """Obtiene el código QR para conectar WhatsApp"""
        return await self._make_request("GET", f"/instance/qrcode/{self.instance_name}")
    
    async def logout_instance(self) -> WhatsAppResponse:
        """Cierra sesión de la instancia de WhatsApp"""
        return await self._make_request("DELETE", f"/instance/logout/{self.instance_name}")
    
    async def send_text_message(self, to: str, message: str) -> WhatsAppResponse:
        """Envía un mensaje de texto"""
        data = {
            "number": to,
            "text": message
        }
        return await self._make_request(
            "POST", 
            f"/message/sendText/{self.instance_name}", 
            data
        )
    
    async def send_media_message(
        self, 
        to: str, 
        media_url: str, 
        caption: Optional[str] = None,
        message_type: str = "image"
    ) -> WhatsAppResponse:
        """Envía un mensaje multimedia"""
        data = {
            "number": to,
            "url": media_url,
            "type": message_type
        }
        
        if caption:
            data["caption"] = caption
            
        endpoint_map = {
            "image": f"/message/sendImage/{self.instance_name}",
            "video": f"/message/sendVideo/{self.instance_name}",
            "audio": f"/message/sendAudio/{self.instance_name}",
            "document": f"/message/sendDocument/{self.instance_name}"
        }
        
        endpoint = endpoint_map.get(message_type, endpoint_map["image"])
        return await self._make_request("POST", endpoint, data)
    
    async def send_template_message(
        self, 
        to: str, 
        template_name: str, 
        variables: Optional[Dict[str, str]] = None
    ) -> WhatsAppResponse:
        """Envía un mensaje de plantilla"""
        data = {
            "number": to,
            "template": template_name
        }
        
        if variables:
            data["variables"] = variables
            
        return await self._make_request(
            "POST", 
            f"/message/sendTemplate/{self.instance_name}", 
            data
        )
    
    async def get_chat_history(self, number: str, limit: int = 50) -> WhatsAppResponse:
        """Obtiene el historial de chat con un número"""
        return await self._make_request(
            "GET", 
            f"/chat/history/{self.instance_name}/{number}?limit={limit}"
        )
    
    async def mark_as_read(self, message_id: str) -> WhatsAppResponse:
        """Marca un mensaje como leído"""
        data = {"messageId": message_id}
        return await self._make_request(
            "POST", 
            f"/chat/markRead/{self.instance_name}", 
            data
        )
    
    async def get_contacts(self) -> WhatsAppResponse:
        """Obtiene la lista de contactos"""
        return await self._make_request("GET", f"/contact/{self.instance_name}")
    
    async def check_number_status(self, number: str) -> WhatsAppResponse:
        """Verifica el estado de un número de WhatsApp"""
        return await self._make_request(
            "GET", 
            f"/contact/status/{self.instance_name}/{number}"
        )

class WhatsAppNotificationService:
    """Servicio de notificaciones de WhatsApp para ClickUp"""
    
    def __init__(self):
        self.client = WhatsAppClient()
        self.simulator = WhatsAppSimulator() if settings.WHATSAPP_SIMULATOR_ENABLED else None
        self.enabled = settings.WHATSAPP_ENABLED and settings.WHATSAPP_NOTIFICATIONS_ENABLED
        
    async def send_task_notification(
        self, 
        phone_number: str, 
        task_title: str, 
        task_description: str,
        notification_type: str,
        due_date: Optional[datetime] = None,
        assignee: Optional[str] = None
    ) -> WhatsAppResponse:
        """Envía una notificación de tarea por WhatsApp"""
        if not self.enabled:
            return WhatsAppResponse(
                success=False,
                message="WhatsApp notifications disabled",
                error="WhatsApp notifications are not enabled"
            )
        
        # Usar simulador si está habilitado
        if self.simulator and settings.WHATSAPP_SIMULATOR_ENABLED:
            # Formatear el mensaje según el tipo de notificación
            message = self._format_task_message(
                task_title, task_description, notification_type, due_date, assignee
            )
            
            clean_phone = self._clean_phone_number(phone_number)
            result = await self.simulator.send_text_message(clean_phone, message)
            
            return WhatsAppResponse(
                success=result.get("success", True),
                message=f"📱 SIMULADOR: {result.get('message', 'Mensaje enviado')}",
                data=result
            )
        
        # Formatear el mensaje según el tipo de notificación
        message = self._format_task_message(
            task_title, task_description, notification_type, due_date, assignee
        )
        
        # Limpiar y formatear el número de teléfono
        clean_phone = self._clean_phone_number(phone_number)
        
        try:
            async with self.client:
                return await self.client.send_text_message(clean_phone, message)
        except Exception as e:
            logger.error(f"Error enviando notificación WhatsApp: {e}")
            return WhatsAppResponse(
                success=False,
                message="Error sending WhatsApp notification",
                error=str(e)
            )
    
    def _format_task_message(
        self, 
        title: str, 
        description: str, 
        notification_type: str,
        due_date: Optional[datetime] = None,
        assignee: Optional[str] = None
    ) -> str:
        """Formatea el mensaje según el tipo de notificación"""
        
        emoji_map = {
            "created": "🆕",
            "updated": "✏️",
            "completed": "✅",
            "due_soon": "⏰",
            "overdue": "🚨"
        }
        
        emoji = emoji_map.get(notification_type, "📋")
        
        message = f"{emoji} *ClickUp Task Notification*\n\n"
        message += f"*{title}*\n\n"
        
        if description:
            message += f"📝 {description[:200]}{'...' if len(description) > 200 else ''}\n\n"
        
        if assignee:
            message += f"👤 Asignado a: {assignee}\n"
        
        if due_date:
            # Convertir due_date a datetime si es string
            try:
                if isinstance(due_date, str):
                    # Intentar parsear la fecha si es string
                    if due_date:
                        due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    else:
                        due_date = None
                
                if due_date and hasattr(due_date, 'strftime'):
                    if notification_type == "due_soon":
                        message += f"⏰ Vence pronto: {due_date.strftime('%d/%m/%Y %H:%M')}\n"
                    elif notification_type == "overdue":
                        message += f"🚨 Vencida desde: {due_date.strftime('%d/%m/%Y %H:%M')}\n"
                    else:
                        message += f"📅 Fecha límite: {due_date.strftime('%d/%m/%Y %H:%M')}\n"
            except Exception as e:
                logger.warning(f"Error formateando fecha: {e}, omitiendo fecha del mensaje")
        
        message += f"\n🔗 Ver en ClickUp: https://app.clickup.com"
        
        return message
    
    def _clean_phone_number(self, phone: str) -> str:
        """Limpia y formatea un número de teléfono para WhatsApp"""
        # Remover espacios, guiones, paréntesis y otros caracteres
        clean = ''.join(filter(str.isdigit, phone))
        
        # Si empieza con 0, removerlo
        if clean.startswith('0'):
            clean = clean[1:]
        
        # Si no tiene código de país, agregar +52 (México) por defecto
        if not clean.startswith('52'):
            clean = f"52{clean}"
        
        # Agregar el + al inicio
        return f"+{clean}"
    
    async def send_bulk_notifications(
        self, 
        notifications: List[Dict]
    ) -> List[WhatsAppResponse]:
        """Envía múltiples notificaciones en lote"""
        if not self.enabled:
            return [
                WhatsAppResponse(
                    success=False,
                    message="WhatsApp notifications disabled",
                    error="WhatsApp notifications are not enabled"
                ) for _ in notifications
            ]
        
        results = []
        
        try:
            async with self.client:
                for notification in notifications:
                    result = await self.send_task_notification(
                        phone_number=notification["phone"],
                        task_title=notification["title"],
                        task_description=notification.get("description", ""),
                        notification_type=notification["type"],
                        due_date=notification.get("due_date"),
                        assignee=notification.get("assignee")
                    )
                    results.append(result)
                    
                    # Pequeña pausa entre mensajes para evitar spam
                    await asyncio.sleep(1)
                    
        except Exception as e:
            logger.error(f"Error en envío masivo de WhatsApp: {e}")
            # Agregar errores para las notificaciones restantes
            remaining = len(notifications) - len(results)
            for _ in range(remaining):
                results.append(WhatsAppResponse(
                    success=False,
                    message="Bulk notification error",
                    error=str(e)
                ))
        
        return results
    
    async def get_status(self) -> Dict[str, any]:
        """Obtiene el estado del servicio de WhatsApp"""
        try:
            return {
                "enabled": self.enabled,
                "simulator_enabled": self.simulator is not None,
                "client_configured": bool(self.client.api_key),
                "base_url": self.client.base_url,
                "instance_name": self.client.instance_name,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error obteniendo estado del servicio: {e}")
            return {
                "enabled": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Instancia global del servicio de notificaciones
whatsapp_service = WhatsAppNotificationService()
