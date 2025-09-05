"""
Gestor de webhooks para Evolution API
Maneja eventos y respuestas de WhatsApp
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from .evolution_api_config import get_webhook_config
from .production_whatsapp_service import ProductionWhatsAppService

logger = logging.getLogger(__name__)

class WebhookEventType(Enum):
    """Tipos de eventos de webhook"""
    MESSAGE_UPSERT = "messages.upsert"
    MESSAGE_UPDATE = "messages.update"
    CONNECTION_UPDATE = "connection.update"
    PRESENCE_UPDATE = "presence.update"
    CHAT_UPDATE = "chat.update"
    CONTACT_UPDATE = "contact.update"
    GROUP_UPDATE = "group.update"
    CALL_UPDATE = "call.update"

@dataclass
class WebhookEvent:
    """Evento de webhook procesado"""
    event_type: WebhookEventType
    timestamp: datetime
    data: Dict[str, Any]
    instance_name: str
    processed: bool = False

class EvolutionWebhookManager:
    """Gestor de webhooks para Evolution API"""
    
    def __init__(self):
        self.config = get_webhook_config()
        self.event_handlers: Dict[WebhookEventType, List[Callable]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.is_processing = False
        self.processing_task: Optional[asyncio.Task] = None
        self.whatsapp_service: Optional[ProductionWhatsAppService] = None
        
    async def start(self) -> None:
        """Inicia el gestor de webhooks"""
        if self.is_processing:
            logger.info("⚠️ El gestor de webhooks ya está ejecutándose")
            return
        
        logger.info("🚀 Iniciando gestor de webhooks de Evolution API...")
        self.is_processing = True
        
        # Inicializar servicio de WhatsApp
        try:
            self.whatsapp_service = await ProductionWhatsAppService().connect()
            logger.info("✅ Servicio de WhatsApp inicializado")
        except Exception as e:
            logger.error(f"❌ Error inicializando servicio de WhatsApp: {e}")
        
        # Iniciar procesamiento de eventos
        self.processing_task = asyncio.create_task(self._process_event_queue())
        logger.info("✅ Gestor de webhooks iniciado")
    
    async def stop(self) -> None:
        """Detiene el gestor de webhooks"""
        logger.info("🛑 Deteniendo gestor de webhooks...")
        self.is_processing = False
        
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        if self.whatsapp_service:
            await self.whatsapp_service.disconnect()
        
        logger.info("✅ Gestor de webhooks detenido")
    
    def register_handler(
        self, 
        event_type: WebhookEventType, 
        handler: Callable[[WebhookEvent], None]
    ) -> None:
        """Registra un manejador para un tipo de evento"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.info(f"📝 Manejador registrado para {event_type.value}")
    
    async def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa un webhook recibido"""
        try:
            # Validar datos del webhook
            if not self._validate_webhook_data(webhook_data):
                return {"success": False, "error": "Datos de webhook inválidos"}
            
            # Crear evento
            event = self._create_webhook_event(webhook_data)
            
            # Agregar a la cola de procesamiento
            await self.event_queue.put(event)
            
            logger.info(f"📥 Webhook recibido: {event.event_type.value}")
            
            return {"success": True, "message": "Webhook procesado"}
            
        except Exception as e:
            logger.error(f"Error procesando webhook: {e}")
            return {"success": False, "error": str(e)}
    
    def _validate_webhook_data(self, data: Dict[str, Any]) -> bool:
        """Valida los datos del webhook"""
        required_fields = ["event", "instance", "timestamp"]
        
        for field in required_fields:
            if field not in data:
                logger.warning(f"Campo requerido faltante: {field}")
                return False
        
        return True
    
    def _create_webhook_event(self, data: Dict[str, Any]) -> WebhookEvent:
        """Crea un evento de webhook"""
        try:
            event_type = WebhookEventType(data["event"])
        except ValueError:
            # Evento desconocido, usar MESSAGE_UPSERT como fallback
            event_type = WebhookEventType.MESSAGE_UPSERT
            logger.warning(f"Evento desconocido: {data['event']}, usando fallback")
        
        timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        
        return WebhookEvent(
            event_type=event_type,
            timestamp=timestamp,
            data=data,
            instance_name=data.get("instance", "unknown")
        )
    
    async def _process_event_queue(self) -> None:
        """Procesa la cola de eventos"""
        while self.is_processing:
            try:
                # Esperar evento con timeout
                try:
                    event = await asyncio.wait_for(
                        self.event_queue.get(), 
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Procesar evento
                await self._handle_event(event)
                
                # Marcar como procesado
                event.processed = True
                self.event_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error procesando evento: {e}")
    
    async def _handle_event(self, event: WebhookEvent) -> None:
        """Maneja un evento específico"""
        try:
            # Llamar manejadores registrados
            if event.event_type in self.event_handlers:
                for handler in self.event_handlers[event.event_type]:
                    try:
                        await self._call_handler(handler, event)
                    except Exception as e:
                        logger.error(f"Error en manejador {handler.__name__}: {e}")
            
            # Procesar evento según su tipo
            await self._process_event_by_type(event)
            
        except Exception as e:
            logger.error(f"Error manejando evento {event.event_type.value}: {e}")
    
    async def _call_handler(self, handler: Callable, event: WebhookEvent) -> None:
        """Llama a un manejador de evento"""
        if asyncio.iscoroutinefunction(handler):
            await handler(event)
        else:
            handler(event)
    
    async def _process_event_by_type(self, event: WebhookEvent) -> None:
        """Procesa un evento según su tipo"""
        if event.event_type == WebhookEventType.MESSAGE_UPSERT:
            await self._handle_message_upsert(event)
        elif event.event_type == WebhookEventType.CONNECTION_UPDATE:
            await self._handle_connection_update(event)
        elif event.event_type == WebhookEventType.PRESENCE_UPDATE:
            await self._handle_presence_update(event)
        else:
            logger.debug(f"Evento no procesado: {event.event_type.value}")
    
    async def _handle_message_upsert(self, event: WebhookEvent) -> None:
        """Maneja eventos de mensajes nuevos/actualizados"""
        try:
            message_data = event.data.get("data", {})
            
            # Verificar si es un mensaje entrante
            if message_data.get("key", {}).get("fromMe", False):
                logger.debug("Mensaje saliente, ignorando")
                return
            
            # Extraer información del mensaje
            from_number = message_data.get("key", {}).get("remoteJid", "")
            message_text = message_data.get("message", {}).get("conversation", "")
            timestamp = message_data.get("messageTimestamp", 0)
            
            if from_number and message_text:
                logger.info(f"📱 Mensaje recibido de {from_number}: {message_text[:50]}...")
                
                # Aquí puedes implementar lógica de respuesta automática
                await self._handle_incoming_message(from_number, message_text, timestamp)
                
        except Exception as e:
            logger.error(f"Error manejando mensaje: {e}")
    
    async def _handle_connection_update(self, event: WebhookEvent) -> None:
        """Maneja actualizaciones de conexión"""
        try:
            connection_data = event.data.get("data", {})
            state = connection_data.get("state", "unknown")
            
            logger.info(f"🔌 Estado de conexión: {state}")
            
            if state == "open":
                logger.info("✅ WhatsApp conectado y listo")
            elif state == "close":
                logger.warning("⚠️ WhatsApp desconectado")
            elif state == "connecting":
                logger.info("🔄 Conectando WhatsApp...")
                
        except Exception as e:
            logger.error(f"Error manejando actualización de conexión: {e}")
    
    async def _handle_presence_update(self, event: WebhookEvent) -> None:
        """Maneja actualizaciones de presencia"""
        try:
            presence_data = event.data.get("data", {})
            user_id = presence_data.get("id", "")
            presence = presence_data.get("presence", "unknown")
            
            logger.debug(f"👤 Presencia actualizada: {user_id} -> {presence}")
            
        except Exception as e:
            logger.error(f"Error manejando actualización de presencia: {e}")
    
    async def _handle_incoming_message(
        self, 
        from_number: str, 
        message_text: str, 
        timestamp: int
    ) -> None:
        """Maneja mensajes entrantes"""
        try:
            # Aquí puedes implementar lógica de respuesta automática
            # Por ejemplo, responder a comandos específicos
            
            if message_text.lower() in ["hola", "hello", "hi"]:
                response = "¡Hola! Soy el bot de notificaciones de ClickUp. ¿En qué puedo ayudarte?"
                await self._send_response(from_number, response)
                
            elif message_text.lower() in ["estado", "status"]:
                if self.whatsapp_service and self.whatsapp_service.is_connected:
                    response = "✅ Sistema funcionando correctamente. WhatsApp conectado."
                else:
                    response = "⚠️ Sistema con problemas. WhatsApp desconectado."
                await self._send_response(from_number, response)
                
            elif message_text.lower() in ["ayuda", "help"]:
                response = """📋 Comandos disponibles:
• hola - Saludo
• estado - Estado del sistema
• ayuda - Esta lista
• info - Información del sistema"""
                await self._send_response(from_number, response)
                
        except Exception as e:
            logger.error(f"Error manejando mensaje entrante: {e}")
    
    async def _send_response(self, to_number: str, message: str) -> None:
        """Envía una respuesta automática"""
        if not self.whatsapp_service or not self.whatsapp_service.is_connected:
            logger.warning("No se puede enviar respuesta: servicio no disponible")
            return
        
        try:
            # Crear notificación de respuesta
            from .production_whatsapp_service import ProductionNotification
            
            response_notification = ProductionNotification(
                id=f"response_{datetime.now().timestamp()}",
                task_id="auto_response",
                task_title="Respuesta automática",
                task_description=message,
                phone_numbers=[to_number],
                notification_type="auto_response"
            )
            
            result = await self.whatsapp_service.send_task_notification(response_notification)
            
            if result.get("success"):
                logger.info(f"✅ Respuesta automática enviada a {to_number}")
            else:
                logger.warning(f"⚠️ Error enviando respuesta automática: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error enviando respuesta automática: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado del gestor de webhooks"""
        return {
            "is_processing": self.is_processing,
            "queue_size": self.event_queue.qsize(),
            "event_handlers": {
                event_type.value: len(handlers)
                for event_type, handlers in self.event_handlers.items()
            },
            "whatsapp_service_connected": (
                self.whatsapp_service.is_connected 
                if self.whatsapp_service else False
            ),
            "webhook_config": self.config
        }

# Instancia global del gestor
webhook_manager = EvolutionWebhookManager()

async def get_webhook_manager() -> EvolutionWebhookManager:
    """Obtiene la instancia del gestor de webhooks"""
    if not webhook_manager.is_processing:
        await webhook_manager.start()
    return webhook_manager
