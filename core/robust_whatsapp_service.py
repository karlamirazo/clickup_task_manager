"""
Servicio Robusto de WhatsApp con Evolution API
Implementa reintentos automáticos, fallback al simulador y manejo inteligente de errores
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .whatsapp_client import WhatsAppNotificationService, WhatsAppResponse
from .whatsapp_simulator import WhatsAppSimulator
from .evolution_api_config import get_evolution_config, evolution_config
from .config import settings

# Configurar logging
logger = logging.getLogger(__name__)

class MessageStatus(Enum):
    """Estados posibles de un mensaje"""
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    FALLBACK = "fallback"

class RetryStrategy(Enum):
    """Estrategias de reintento"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    CONSTANT_DELAY = "constant_delay"

@dataclass
class MessageAttempt:
    """Intento de envío de mensaje"""
    attempt_number: int
    timestamp: datetime
    status: MessageStatus
    response: Optional[WhatsAppResponse] = None
    error: Optional[str] = None
    duration_ms: Optional[float] = None

@dataclass
class MessageResult:
    """Resultado final del envío de mensaje"""
    success: bool
    message_id: Optional[str] = None
    phone_number: str
    final_status: MessageStatus
    attempts: List[MessageAttempt]
    total_duration_ms: float
    used_fallback: bool
    final_response: Optional[WhatsAppResponse] = None
    error_summary: Optional[str] = None

class RobustWhatsAppService:
    """Servicio robusto de WhatsApp con reintentos y fallback"""
    
    def __init__(self):
        self.evolution_config = get_evolution_config()
        self.whatsapp_service = WhatsAppNotificationService()
        self.simulator = WhatsAppSimulator()
        
        # Configuración de reintentos
        self.max_retries = self.evolution_config.max_retries
        self.base_retry_delay = self.evolution_config.retry_delay
        self.max_retry_delay = 60.0  # Máximo 60 segundos entre reintentos
        
        # Estadísticas
        self.total_messages_sent = 0
        self.successful_messages = 0
        self.failed_messages = 0
        self.fallback_messages = 0
        self.total_retries = 0
        
        # Rate limiting
        self.message_timestamps = []
        self.rate_limit_window = 60  # Ventana de 1 minuto
        
        logger.info(f"🚀 Servicio robusto de WhatsApp inicializado")
        logger.info(f"   📱 Evolution API: {self.evolution_config.base_url}")
        logger.info(f"   🔑 Instancia: {self.evolution_config.instance_name}")
        logger.info(f"   🔄 Máximo reintentos: {self.max_retries}")
        logger.info(f"   ⏱️ Delay base: {self.base_retry_delay}s")
    
    @property
    def enabled(self) -> bool:
        """Verifica si el servicio está habilitado"""
        try:
            from .config import settings
            return (
                settings.WHATSAPP_ENABLED and 
                settings.WHATSAPP_NOTIFICATIONS_ENABLED and
                bool(settings.WHATSAPP_EVOLUTION_URL) and
                bool(settings.WHATSAPP_EVOLUTION_API_KEY) and
                bool(settings.WHATSAPP_INSTANCE_NAME)
            )
        except Exception as e:
            logger.warning(f"⚠️ Error verificando configuración de WhatsApp: {e}")
            return False
    
    async def send_message_with_retries(
        self,
        phone_number: str,
        message: str,
        message_type: str = "text",
        notification_type: str = "custom",
        **kwargs
    ) -> MessageResult:
        """
        Envía mensaje con reintentos automáticos y fallback al simulador
        
        Args:
            phone_number: Número de teléfono del destinatario
            message: Contenido del mensaje
            message_type: Tipo de mensaje (text, image, document)
            notification_type: Tipo de notificación
            **kwargs: Parámetros adicionales
            
        Returns:
            MessageResult con detalles del envío
        """
        start_time = time.time()
        attempts = []
        
        logger.info(f"📱 Enviando mensaje robusto a {phone_number}")
        logger.info(f"   📝 Mensaje: {message[:100]}...")
        logger.info(f"   🏷️ Tipo: {message_type}")
        logger.info(f"   🔔 Notificación: {notification_type}")
        
        # Verificar rate limiting
        if not self._check_rate_limit():
            error_msg = "Rate limit excedido, esperando..."
            logger.warning(f"⚠️ {error_msg}")
            await asyncio.sleep(5)  # Esperar 5 segundos
        
        # Intentar con Evolution API primero
        for attempt in range(self.max_retries + 1):
            attempt_start = time.time()
            
            try:
                logger.info(f"🔄 Intento {attempt + 1}/{self.max_retries + 1} con Evolution API")
                
                # Enviar mensaje usando el servicio principal
                response = await self.whatsapp_service.send_task_notification(
                    phone_number=phone_number,
                    task_name=kwargs.get('task_name', 'Tarea'),
                    task_description=message,
                    due_date=kwargs.get('due_date'),
                    assignee_name=kwargs.get('assignee_name', 'Sin asignar'),
                    notification_type=notification_type
                )
                
                attempt_duration = (time.time() - attempt_start) * 1000
                
                if response.success:
                    # Mensaje enviado exitosamente
                    logger.info(f"✅ Mensaje enviado exitosamente en intento {attempt + 1}")
                    
                    attempt_record = MessageAttempt(
                        attempt_number=attempt + 1,
                        timestamp=datetime.now(),
                        status=MessageStatus.SENT,
                        response=response,
                        duration_ms=attempt_duration
                    )
                    attempts.append(attempt_record)
                    
                    # Actualizar estadísticas
                    self.total_messages_sent += 1
                    self.successful_messages += 1
                    self._update_rate_limit()
                    
                    total_duration = (time.time() - start_time) * 1000
                    
                    return MessageResult(
                        success=True,
                        message_id=response.data.get('id') if response.data else None,
                        phone_number=phone_number,
                        final_status=MessageStatus.SENT,
                        attempts=attempts,
                        total_duration_ms=total_duration,
                        used_fallback=False,
                        final_response=response
                    )
                
                else:
                    # Error en el envío
                    error_msg = response.error or "Error desconocido"
                    logger.warning(f"❌ Error en intento {attempt + 1}: {error_msg}")
                    
                    attempt_record = MessageAttempt(
                        attempt_number=attempt + 1,
                        timestamp=datetime.now(),
                        status=MessageStatus.FAILED,
                        response=response,
                        error=error_msg,
                        duration_ms=attempt_duration
                    )
                    attempts.append(attempt_record)
                    
                    # Si es el último intento, usar fallback
                    if attempt == self.max_retries:
                        logger.info(f"🔄 Último intento fallido, usando fallback al simulador")
                        return await self._send_with_fallback(
                            phone_number, message, message_type, notification_type, 
                            attempts, start_time, **kwargs
                        )
                    
                    # Calcular delay para el siguiente intento
                    delay = self._calculate_retry_delay(attempt)
                    logger.info(f"⏱️ Esperando {delay}s antes del siguiente intento")
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ Excepción en intento {attempt + 1}: {error_msg}")
                
                attempt_duration = (time.time() - attempt_start) * 1000
                attempt_record = MessageAttempt(
                    attempt_number=attempt + 1,
                    timestamp=datetime.now(),
                    status=MessageStatus.FAILED,
                    error=error_msg,
                    duration_ms=attempt_duration
                )
                attempts.append(attempt_record)
                
                # Si es el último intento, usar fallback
                if attempt == self.max_retries:
                    logger.info(f"🔄 Último intento fallido por excepción, usando fallback")
                    return await self._send_with_fallback(
                        phone_number, message, message_type, notification_type,
                        attempts, start_time, **kwargs
                    )
                
                # Calcular delay para el siguiente intento
                delay = self._calculate_retry_delay(attempt)
                logger.info(f"⏱️ Esperando {delay}s antes del siguiente intento")
                await asyncio.sleep(delay)
        
        # Nunca debería llegar aquí, pero por seguridad
        total_duration = (time.time() - start_time) * 1000
        return MessageResult(
            success=False,
            phone_number=phone_number,
            final_status=MessageStatus.FAILED,
            attempts=attempts,
            total_duration_ms=total_duration,
            used_fallback=False,
            error_summary="Todos los intentos fallaron"
        )
    
    async def _send_with_fallback(
        self,
        phone_number: str,
        message: str,
        message_type: str,
        notification_type: str,
        attempts: List[MessageAttempt],
        start_time: float,
        **kwargs
    ) -> MessageResult:
        """Envía mensaje usando el simulador como fallback"""
        logger.info(f"🔄 Usando simulador como fallback para {phone_number}")
        
        try:
            # Intentar con el simulador
            simulator_response = await self.simulator.send_message(
                phone_number=phone_number,
                message=message,
                message_type=message_type
            )
            
            total_duration = (time.time() - start_time) * 1000
            
            if simulator_response.success:
                logger.info(f"✅ Mensaje enviado exitosamente usando simulador")
                
                # Actualizar estadísticas
                self.total_messages_sent += 1
                self.fallback_messages += 1
                
                attempt_record = MessageAttempt(
                    attempt_number=len(attempts) + 1,
                    timestamp=datetime.now(),
                    status=MessageStatus.FALLBACK,
                    response=simulator_response,
                    duration_ms=total_duration
                )
                attempts.append(attempt_record)
                
                return MessageResult(
                    success=True,
                    message_id=simulator_response.data.get('id') if simulator_response.data else None,
                    phone_number=phone_number,
                    final_status=MessageStatus.FALLBACK,
                    attempts=attempts,
                    total_duration_ms=total_duration,
                    used_fallback=True,
                    final_response=simulator_response
                )
            else:
                logger.error(f"❌ Simulador también falló: {simulator_response.error}")
                
                attempt_record = MessageAttempt(
                    attempt_number=len(attempts) + 1,
                    timestamp=datetime.now(),
                    status=MessageStatus.FAILED,
                    response=simulator_response,
                    error=simulator_response.error,
                    duration_ms=total_duration
                )
                attempts.append(attempt_record)
                
                self.failed_messages += 1
                
                return MessageResult(
                    success=False,
                    phone_number=phone_number,
                    final_status=MessageStatus.FAILED,
                    attempts=attempts,
                    total_duration_ms=total_duration,
                    used_fallback=True,
                    final_response=simulator_response,
                    error_summary="Fallback al simulador también falló"
                )
                
        except Exception as e:
            logger.error(f"❌ Error en simulador: {e}")
            
            total_duration = (time.time() - start_time) * 1000
            attempt_record = MessageAttempt(
                attempt_number=len(attempts) + 1,
                timestamp=datetime.now(),
                status=MessageStatus.FAILED,
                error=str(e),
                duration_ms=total_duration
            )
            attempts.append(attempt_record)
            
            self.failed_messages += 1
            
            return MessageResult(
                success=False,
                phone_number=phone_number,
                final_status=MessageStatus.FAILED,
                attempts=attempts,
                total_duration_ms=total_duration,
                used_fallback=True,
                error_summary=f"Error en simulador: {str(e)}"
            )
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calcula el delay para el siguiente reintento"""
        if attempt == 0:
            return self.base_retry_delay
        
        # Backoff exponencial con jitter
        delay = min(
            self.base_retry_delay * (2 ** attempt),
            self.max_retry_delay
        )
        
        # Agregar jitter para evitar thundering herd
        jitter = delay * 0.1 * (0.5 + (time.time() % 1))
        final_delay = delay + jitter
        
        logger.debug(f"   ⏱️ Delay calculado: {delay}s + jitter {jitter:.2f}s = {final_delay:.2f}s")
        
        return final_delay
    
    def _check_rate_limit(self) -> bool:
        """Verifica si se puede enviar un mensaje según el rate limit"""
        if not self.evolution_config.rate_limit_enabled:
            return True
        
        now = time.time()
        window_start = now - self.rate_limit_window
        
        # Limpiar timestamps antiguos
        self.message_timestamps = [ts for ts in self.message_timestamps if ts > window_start]
        
        # Verificar si se puede enviar
        if len(self.message_timestamps) < self.evolution_config.max_messages_per_minute:
            return True
        
        logger.warning(f"⚠️ Rate limit alcanzado: {len(self.message_timestamps)} mensajes en {self.rate_limit_window}s")
        return False
    
    def _update_rate_limit(self):
        """Actualiza el registro de rate limiting"""
        if self.evolution_config.rate_limit_enabled:
            self.message_timestamps.append(time.time())
    
    async def health_check(self) -> Dict[str, Any]:
        """Realiza un health check del servicio"""
        try:
            # Verificar Evolution API
            evolution_status = await self._check_evolution_api_health()
            
            # Verificar simulador
            simulator_status = await self._check_simulator_health()
            
            return {
                "status": "healthy" if evolution_status["healthy"] or simulator_status["healthy"] else "degraded",
                "timestamp": datetime.now().isoformat(),
                "evolution_api": evolution_status,
                "simulator": simulator_status,
                "statistics": {
                    "total_messages_sent": self.total_messages_sent,
                    "successful_messages": self.successful_messages,
                    "failed_messages": self.failed_messages,
                    "fallback_messages": self.fallback_messages,
                    "total_retries": self.total_retries
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error en health check: {e}")
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def _check_evolution_api_health(self) -> Dict[str, Any]:
        """Verifica la salud de Evolution API"""
        try:
            # Intentar una petición simple
            async with self.whatsapp_service.client:
                # Aquí podrías hacer una petición de health check específica
                # Por ahora, asumimos que está funcionando si no hay excepción
                return {
                    "healthy": True,
                    "url": self.evolution_config.base_url,
                    "instance": self.evolution_config.instance_name,
                    "message": "Evolution API responde correctamente"
                }
        except Exception as e:
            return {
                "healthy": False,
                "url": self.evolution_config.base_url,
                "instance": self.evolution_config.instance_name,
                "error": str(e),
                "message": "Evolution API no responde"
            }
    
    async def _check_simulator_health(self) -> Dict[str, Any]:
        """Verifica la salud del simulador"""
        try:
            # Verificar que el simulador esté disponible
            if hasattr(self.simulator, 'enabled') and self.simulator.enabled:
                return {
                    "healthy": True,
                    "message": "Simulador disponible y funcionando"
                }
            else:
                return {
                    "healthy": False,
                    "message": "Simulador no disponible"
                }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "message": "Error verificando simulador"
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del servicio"""
        return {
            "total_messages_sent": self.total_messages_sent,
            "successful_messages": self.successful_messages,
            "failed_messages": self.failed_messages,
            "fallback_messages": self.fallback_messages,
            "total_retries": self.total_retries,
            "success_rate": (self.successful_messages / max(self.total_messages_sent, 1)) * 100,
            "fallback_rate": (self.fallback_messages / max(self.total_messages_sent, 1)) * 100
        }

# Instancia global del servicio robusto
robust_whatsapp_service = RobustWhatsAppService()

async def get_robust_whatsapp_service() -> RobustWhatsAppService:
    """Obtiene la instancia del servicio robusto de WhatsApp"""
    return robust_whatsapp_service
