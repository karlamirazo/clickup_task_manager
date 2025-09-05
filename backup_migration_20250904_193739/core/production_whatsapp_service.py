"""
Servicio de WhatsApp de producción usando Evolution API
Sistema completo para notificaciones reales en producción
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
import aiohttp
from pydantic import BaseModel, Field

from .evolution_api_config import get_evolution_config, is_production_ready
from .phone_extractor import PhoneNumberExtractor
from .config import settings

logger = logging.getLogger(__name__)

@dataclass
class ProductionNotification:
    """Notificación de producción"""
    id: str
    task_id: str
    task_title: str
    task_description: str
    phone_numbers: List[str]
    notification_type: str
    due_date: Optional[datetime] = None
    assignee: Optional[str] = None
    priority: str = "normal"  # low, normal, high, urgent
    retry_count: int = 0
    status: str = "pending"  # pending, sent, failed, retrying

class ProductionWhatsAppService:
    """Servicio de WhatsApp de producción con Evolution API"""
    
    def __init__(self):
        self.config = get_evolution_config()
        self.phone_extractor = PhoneNumberExtractor()
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_connected = False
        self.connection_status = "disconnected"
        self.rate_limiter = RateLimiter(
            max_per_minute=self.config.max_messages_per_minute,
            max_per_hour=self.config.max_messages_per_hour
        )
        self.health_check_task: Optional[asyncio.Task] = None
        
    async def __aenter__(self):
        """Context manager entry"""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.disconnect()
    
    async def connect(self) -> bool:
        """Conecta al servicio de Evolution API"""
        if not is_production_ready():
            logger.error("❌ Configuración de producción no está lista")
            return False
        
        try:
            self.session = aiohttp.ClientSession(
                headers={
                    "Content-Type": "application/json",
                    "apikey": self.config.api_key
                },
                timeout=aiohttp.ClientTimeout(
                    total=self.config.request_timeout,
                    connect=self.config.connection_timeout
                )
            )
            
            # Verificar conexión
            status = await self.get_instance_status()
            if status.get("success"):
                self.is_connected = True
                self.connection_status = "connected"
                logger.info("✅ Conectado a Evolution API")
                
                # Iniciar health check
                self.health_check_task = asyncio.create_task(self._health_check_loop())
                
                return True
            else:
                logger.error(f"❌ Error conectando a Evolution API: {status.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Desconecta del servicio"""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        if self.session:
            await self.session.close()
            self.session = None
        
        self.is_connected = False
        self.connection_status = "disconnected"
        logger.info("🔌 Desconectado de Evolution API")
    
    async def get_instance_status(self) -> Dict[str, Any]:
        """Obtiene el estado de la instancia"""
        try:
            url = f"{self.config.base_url}/instance/connectionState/{self.config.instance_name}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"success": True, "data": data}
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def send_task_notification(
        self, 
        notification: ProductionNotification
    ) -> Dict[str, Any]:
        """Envía una notificación de tarea"""
        if not self.is_connected:
            return {"success": False, "error": "Servicio no conectado"}
        
        # Verificar rate limiting
        if not self.rate_limiter.can_send():
            return {"success": False, "error": "Rate limit excedido"}
        
        # Validar números de teléfono
        valid_phones = []
        for phone in notification.phone_numbers:
            if self._validate_phone_number(phone):
                valid_phones.append(phone)
            else:
                logger.warning(f"⚠️ Número inválido: {phone}")
        
        if not valid_phones:
            return {"success": False, "error": "No hay números válidos"}
        
        # Enviar notificaciones
        results = []
        for phone in valid_phones:
            try:
                message = self._format_notification_message(notification, phone)
                result = await self._send_message(phone, message)
                results.append(result)
                
                # Delay entre mensajes
                if self.config.message_delay > 0:
                    await asyncio.sleep(self.config.message_delay)
                    
            except Exception as e:
                logger.error(f"Error enviando a {phone}: {e}")
                results.append({"success": False, "phone": phone, "error": str(e)})
        
        # Actualizar rate limiter
        self.rate_limiter.record_send(len(valid_phones))
        
        return {
            "success": True,
            "results": results,
            "total_sent": len([r for r in results if r.get("success")]),
            "total_failed": len([r for r in results if not r.get("success")])
        }
    
    async def _send_message(self, phone: str, message: str) -> Dict[str, Any]:
        """Envía un mensaje individual"""
        try:
            url = f"{self.config.base_url}/message/sendText/{self.config.instance_name}"
            data = {
                "number": phone,
                "text": message
            }
            
            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return {
                        "success": True,
                        "phone": phone,
                        "message_id": response_data.get("id"),
                        "data": response_data
                    }
                else:
                    return {
                        "success": False,
                        "phone": phone,
                        "error": f"HTTP {response.status}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "phone": phone,
                "error": str(e)
            }
    
    def _format_notification_message(
        self, 
        notification: ProductionNotification, 
        phone: str
    ) -> str:
        """Formatea el mensaje de notificación"""
        template = self.config.message_templates.get(
            notification.notification_type, 
            self.config.fallback_message
        )
        
        # Variables disponibles para el template
        variables = {
            "title": notification.task_title,
            "description": notification.task_description[:200] + "..." if len(notification.task_description) > 200 else notification.task_description,
            "due_date": notification.due_date.strftime("%d/%m/%Y %H:%M") if notification.due_date else "No especificada",
            "assignee": notification.assignee or "No asignado",
            "priority": notification.priority.upper(),
            "task_id": notification.task_id
        }
        
        try:
            message = template.format(**variables)
        except KeyError:
            # Fallback si el template falla
            message = self.config.fallback_message.format(**variables)
        
        # Agregar información adicional
        message += f"\n\n📋 ID: {notification.task_id}"
        message += f"\n🔗 Ver en ClickUp: https://app.clickup.com"
        
        return message
    
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
    
    async def extract_phones_from_task(self, task_data: Dict[str, Any]) -> List[str]:
        """Extrae números de teléfono de una tarea de ClickUp"""
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
        
        # Buscar en comentarios si están disponibles
        if "comments" in task_data:
            for comment in task_data["comments"]:
                if "comment" in comment:
                    extracted = self.phone_extractor.extract_phones_from_text(comment["comment"])
                    phones.extend([phone.number for phone in extracted])
        
        # Eliminar duplicados y validar
        unique_phones = list(set(phones))
        valid_phones = [phone for phone in unique_phones if self._validate_phone_number(phone)]
        
        return valid_phones
    
    async def _health_check_loop(self) -> None:
        """Bucle de verificación de salud"""
        while self.is_connected:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                status = await self.get_instance_status()
                
                if not status.get("success"):
                    logger.warning("⚠️ Problema de conectividad detectado")
                    self.connection_status = "unstable"
                else:
                    self.connection_status = "connected"
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en health check: {e}")
                self.connection_status = "error"

class RateLimiter:
    """Controlador de rate limiting para mensajes"""
    
    def __init__(self, max_per_minute: int = 30, max_per_hour: int = 1000):
        self.max_per_minute = max_per_minute
        self.max_per_hour = max_per_hour
        self.minute_messages = []
        self.hour_messages = []
    
    def can_send(self) -> bool:
        """Verifica si se puede enviar un mensaje"""
        now = datetime.now()
        
        # Limpiar mensajes antiguos
        self.minute_messages = [t for t in self.minute_messages if now - t < timedelta(minutes=1)]
        self.hour_messages = [t for t in self.hour_messages if now - t < timedelta(hours=1)]
        
        # Verificar límites
        if len(self.minute_messages) >= self.max_per_minute:
            return False
        
        if len(self.hour_messages) >= self.max_per_hour:
            return False
        
        return True
    
    def record_send(self, count: int = 1) -> None:
        """Registra el envío de mensajes"""
        now = datetime.now()
        for _ in range(count):
            self.minute_messages.append(now)
            self.hour_messages.append(now)

# Instancia global del servicio
production_service = ProductionWhatsAppService()

async def get_production_service() -> ProductionWhatsAppService:
    """Obtiene la instancia del servicio de producción"""
    if not production_service.is_connected:
        await production_service.connect()
    return production_service
