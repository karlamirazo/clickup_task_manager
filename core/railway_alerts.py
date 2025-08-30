#!/usr/bin/env python3
"""
Sistema de alertas automáticas para Railway
Integra con WhatsApp, Email y sistema de logging
"""

import os
import sys
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Configurar path para importar módulos del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from utils.notifications import send_email_notification
from core.whatsapp_client import WhatsAppClient
from langgraph_tools.simple_error_logging import log_error_with_graph

class AlertLevel(Enum):
    """Niveles de alerta"""
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    CRITICAL = "critical"

class AlertType(Enum):
    """Tipos de alerta"""
    SYSTEM_DOWN = "system_down"
    HIGH_ERROR_RATE = "high_error_rate"
    SLOW_RESPONSE = "slow_response"
    DATABASE_ERROR = "database_error"
    MEMORY_HIGH = "memory_high"
    CPU_HIGH = "cpu_high"
    DEPLOYMENT_FAILED = "deployment_failed"

@dataclass
class Alert:
    """Estructura de alerta"""
    id: str
    level: AlertLevel
    type: AlertType
    title: str
    message: str
    timestamp: datetime
    details: Dict[str, Any]
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "level": self.level.value,
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "resolved": self.resolved,
            "resolution_time": self.resolution_time.isoformat() if self.resolution_time else None
        }

class RailwayAlertsManager:
    """Gestor de alertas para Railway"""
    
    def __init__(self):
        self.active_alerts: List[Alert] = []
        self.alert_history: List[Alert] = []
        self.notification_cooldown = timedelta(minutes=15)
        self.last_notifications = {}
        
        # Configurar clientes de notificación
        self.whatsapp_client = WhatsAppClient() if settings.WHATSAPP_ENABLED else None
        
        # Thresholds de alertas
        self.thresholds = {
            "error_rate_per_hour": 10,
            "response_time_seconds": 5.0,
            "cpu_percent": 85.0,
            "memory_percent": 90.0,
            "consecutive_failures": 3
        }
    
    async def process_health_check_result(self, status: str, details: Dict[str, Any], response_time: float):
        """Procesar resultado de health check"""
        current_time = datetime.now()
        
        # Verificar sistema caído
        if status in ["error", "timeout"]:
            await self._create_alert(
                level=AlertLevel.CRITICAL,
                alert_type=AlertType.SYSTEM_DOWN,
                title="🚨 Sistema Railway No Responde",
                message=f"El sistema no responde. Status: {status}",
                details={
                    "status": status,
                    "response_time": response_time,
                    "timestamp": current_time.isoformat(),
                    **details
                }
            )
        
        # Verificar respuesta lenta
        elif response_time > self.thresholds["response_time_seconds"]:
            await self._create_alert(
                level=AlertLevel.WARNING,
                alert_type=AlertType.SLOW_RESPONSE,
                title="⚠️ Respuesta Lenta del Sistema",
                message=f"Tiempo de respuesta alto: {response_time:.2f}s",
                details={
                    "response_time": response_time,
                    "threshold": self.thresholds["response_time_seconds"],
                    "timestamp": current_time.isoformat()
                }
            )
        
        # Resolver alertas de sistema si está funcionando
        elif status == "healthy":
            await self._resolve_alerts_by_type([AlertType.SYSTEM_DOWN, AlertType.SLOW_RESPONSE])
    
    async def process_database_status(self, status: str, errors: List[str]):
        """Procesar estado de la base de datos"""
        if status == "error" and errors:
            await self._create_alert(
                level=AlertLevel.ERROR,
                alert_type=AlertType.DATABASE_ERROR,
                title="❌ Error en Base de Datos",
                message=f"Errores detectados en {len(errors)} endpoints",
                details={
                    "status": status,
                    "errors": errors,
                    "timestamp": datetime.now().isoformat()
                }
            )
        elif status == "healthy":
            await self._resolve_alerts_by_type([AlertType.DATABASE_ERROR])
    
    async def process_error_spike(self, error_count: int, recent_errors: List[Dict[str, Any]]):
        """Procesar pico de errores"""
        if error_count >= self.thresholds["error_rate_per_hour"]:
            error_types = {}
            for error in recent_errors:
                error_type = error.get("error_type", "unknown")
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            await self._create_alert(
                level=AlertLevel.ERROR,
                alert_type=AlertType.HIGH_ERROR_RATE,
                title="🔥 Pico de Errores Detectado",
                message=f"{error_count} errores en la última hora",
                details={
                    "error_count": error_count,
                    "threshold": self.thresholds["error_rate_per_hour"],
                    "error_types": error_types,
                    "sample_errors": recent_errors[:5],
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    async def process_system_metrics(self, cpu_percent: float, memory_percent: float):
        """Procesar métricas del sistema"""
        current_time = datetime.now()
        
        # Verificar CPU alto
        if cpu_percent > self.thresholds["cpu_percent"]:
            await self._create_alert(
                level=AlertLevel.WARNING,
                alert_type=AlertType.CPU_HIGH,
                title="⚡ CPU Alto Detectado",
                message=f"Uso de CPU: {cpu_percent:.1f}%",
                details={
                    "cpu_percent": cpu_percent,
                    "threshold": self.thresholds["cpu_percent"],
                    "timestamp": current_time.isoformat()
                }
            )
        
        # Verificar memoria alta
        if memory_percent > self.thresholds["memory_percent"]:
            await self._create_alert(
                level=AlertLevel.WARNING,
                alert_type=AlertType.MEMORY_HIGH,
                title="💾 Memoria Alta Detectada",
                message=f"Uso de memoria: {memory_percent:.1f}%",
                details={
                    "memory_percent": memory_percent,
                    "threshold": self.thresholds["memory_percent"],
                    "timestamp": current_time.isoformat()
                }
            )
    
    async def _create_alert(self, level: AlertLevel, alert_type: AlertType, title: str, message: str, details: Dict[str, Any]):
        """Crear nueva alerta"""
        # Verificar si ya existe una alerta activa del mismo tipo
        existing_alert = self._find_active_alert_by_type(alert_type)
        if existing_alert:
            # Actualizar alerta existente
            existing_alert.details.update(details)
            existing_alert.timestamp = datetime.now()
            return
        
        # Crear nueva alerta
        alert = Alert(
            id=f"{alert_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            level=level,
            type=alert_type,
            title=title,
            message=message,
            timestamp=datetime.now(),
            details=details
        )
        
        self.active_alerts.append(alert)
        
        # Enviar notificaciones
        await self._send_alert_notifications(alert)
        
        # Registrar en sistema de logging
        await self._log_alert_to_system(alert)
    
    async def _resolve_alerts_by_type(self, alert_types: List[AlertType]):
        """Resolver alertas por tipo"""
        current_time = datetime.now()
        
        for alert in self.active_alerts[:]:  # Crear copia para modificar durante iteración
            if alert.type in alert_types and not alert.resolved:
                alert.resolved = True
                alert.resolution_time = current_time
                
                # Mover a historial
                self.alert_history.append(alert)
                self.active_alerts.remove(alert)
                
                # Enviar notificación de resolución
                await self._send_resolution_notification(alert)
    
    def _find_active_alert_by_type(self, alert_type: AlertType) -> Optional[Alert]:
        """Encontrar alerta activa por tipo"""
        for alert in self.active_alerts:
            if alert.type == alert_type and not alert.resolved:
                return alert
        return None
    
    async def _send_alert_notifications(self, alert: Alert):
        """Enviar notificaciones de alerta"""
        # Verificar cooldown
        cooldown_key = f"{alert.type.value}_{alert.level.value}"
        last_notification = self.last_notifications.get(cooldown_key)
        
        if last_notification and datetime.now() - last_notification < self.notification_cooldown:
            return  # Dentro del período de cooldown
        
        self.last_notifications[cooldown_key] = datetime.now()
        
        # Formatear mensaje
        formatted_message = self._format_alert_message(alert)
        
        # Enviar por email
        if settings.SMTP_HOST:
            try:
                await self._send_email_alert(alert, formatted_message)
            except Exception as e:
                print(f"❌ Error enviando email: {e}")
        
        # Enviar por WhatsApp
        if self.whatsapp_client and settings.WHATSAPP_NOTIFICATIONS_ENABLED:
            try:
                await self._send_whatsapp_alert(alert, formatted_message)
            except Exception as e:
                print(f"❌ Error enviando WhatsApp: {e}")
    
    async def _send_resolution_notification(self, alert: Alert):
        """Enviar notificación de resolución"""
        if alert.level in [AlertLevel.CRITICAL, AlertLevel.ERROR]:
            duration = alert.resolution_time - alert.timestamp
            
            message = f"✅ RESUELTO: {alert.title}\n"
            message += f"Duración: {self._format_duration(duration)}\n"
            message += f"Resuelto: {alert.resolution_time.strftime('%H:%M:%S')}"
            
            # Enviar notificación de resolución solo para alertas críticas
            if settings.WHATSAPP_NOTIFICATIONS_ENABLED and self.whatsapp_client:
                try:
                    await self.whatsapp_client.send_message(
                        phone_number="1234567890",  # Número de admin
                        message=message
                    )
                except Exception as e:
                    print(f"❌ Error enviando resolución por WhatsApp: {e}")
    
    async def _send_email_alert(self, alert: Alert, formatted_message: str):
        """Enviar alerta por email"""
        subject = f"[Railway Alert] {alert.title}"
        
        # Email HTML más detallado
        html_content = f"""
        <html>
        <body>
            <h2 style="color: {'red' if alert.level == AlertLevel.CRITICAL else 'orange' if alert.level == AlertLevel.ERROR else 'blue'};">
                {alert.title}
            </h2>
            <p><strong>Nivel:</strong> {alert.level.value.upper()}</p>
            <p><strong>Tipo:</strong> {alert.type.value}</p>
            <p><strong>Mensaje:</strong> {alert.message}</p>
            <p><strong>Timestamp:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h3>Detalles:</h3>
            <pre>{json.dumps(alert.details, indent=2)}</pre>
            
            <p><em>Sistema de Monitoreo de Railway - ClickUp Project Manager</em></p>
        </body>
        </html>
        """
        
        await send_email_notification(
            to_email=settings.SMTP_FROM,  # Enviar a admin
            subject=subject,
            body=formatted_message,
            html_body=html_content
        )
    
    async def _send_whatsapp_alert(self, alert: Alert, formatted_message: str):
        """Enviar alerta por WhatsApp"""
        # Límite de caracteres para WhatsApp
        if len(formatted_message) > 1000:
            formatted_message = formatted_message[:950] + "\n... (mensaje truncado)"
        
        await self.whatsapp_client.send_message(
            phone_number="1234567890",  # Número de admin - configurar en settings
            message=formatted_message
        )
    
    def _format_alert_message(self, alert: Alert) -> str:
        """Formatear mensaje de alerta"""
        emoji_map = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.ERROR: "❌",
            AlertLevel.CRITICAL: "🚨"
        }
        
        emoji = emoji_map.get(alert.level, "🔔")
        
        message = f"{emoji} {alert.title}\n\n"
        message += f"📅 {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += f"📊 Nivel: {alert.level.value.upper()}\n"
        message += f"🏷️ Tipo: {alert.type.value}\n\n"
        message += f"💬 {alert.message}\n\n"
        
        # Agregar detalles relevantes
        if alert.details:
            message += "📋 Detalles:\n"
            for key, value in alert.details.items():
                if key not in ["timestamp"]:  # Omitir timestamp duplicado
                    if isinstance(value, (int, float)):
                        message += f"   • {key}: {value}\n"
                    elif isinstance(value, list) and len(value) <= 3:
                        message += f"   • {key}: {', '.join(map(str, value))}\n"
                    elif isinstance(value, str) and len(value) <= 50:
                        message += f"   • {key}: {value}\n"
        
        message += f"\n🔗 Sistema: Railway ClickUp Manager"
        
        return message
    
    def _format_duration(self, duration: timedelta) -> str:
        """Formatear duración"""
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    async def _log_alert_to_system(self, alert: Alert):
        """Registrar alerta en sistema de logging"""
        try:
            # Usar workflow de LangGraph para logging
            error_data = {
                "error_description": f"[{alert.level.value.upper()}] {alert.title}: {alert.message}",
                "solution_description": "Verificar sistema y resolver causa raíz del problema",
                "context_info": f"Alerta automática - Tipo: {alert.type.value}, Detalles: {json.dumps(alert.details)}",
                "deployment_id": f"railway-alert-{alert.id}",
                "environment": "production",
                "severity": alert.level.value,
                "status": "active"
            }
            
            result = log_error_with_graph(error_data)
            
            if result["status"] == "success":
                print(f"✅ Alerta registrada en sistema de logging: {alert.id}")
            else:
                print(f"❌ Error registrando alerta: {result.get('message', 'Unknown')}")
                
        except Exception as e:
            print(f"❌ Error logging alerta {alert.id}: {e}")
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Obtener alertas activas"""
        return [alert.to_dict() for alert in self.active_alerts]
    
    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Obtener historial de alertas"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_alerts = [
            alert for alert in self.alert_history
            if alert.timestamp >= cutoff_time
        ]
        
        return [alert.to_dict() for alert in recent_alerts]
    
    async def test_notifications(self):
        """Probar sistema de notificaciones"""
        test_alert = Alert(
            id="test_alert",
            level=AlertLevel.INFO,
            type=AlertType.SYSTEM_DOWN,
            title="🧪 Prueba de Notificaciones",
            message="Este es un mensaje de prueba del sistema de alertas",
            timestamp=datetime.now(),
            details={"test": True, "source": "railway_alerts_test"}
        )
        
        await self._send_alert_notifications(test_alert)
        print("✅ Prueba de notificaciones enviada")

# Instancia global del gestor de alertas
alerts_manager = RailwayAlertsManager()

# Funciones de conveniencia
async def create_custom_alert(level: str, title: str, message: str, details: Dict[str, Any] = None):
    """Crear alerta personalizada"""
    alert_level = AlertLevel(level.lower())
    alert_type = AlertType.SYSTEM_DOWN  # Por defecto
    
    await alerts_manager._create_alert(
        level=alert_level,
        alert_type=alert_type,
        title=title,
        message=message,
        details=details or {}
    )

async def test_alert_system():
    """Probar sistema de alertas"""
    await alerts_manager.test_notifications()

# Script principal
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sistema de alertas de Railway")
    parser.add_argument("--test", action="store_true", help="Probar sistema de notificaciones")
    
    args = parser.parse_args()
    
    if args.test:
        asyncio.run(test_alert_system())
    else:
        print("Sistema de alertas iniciado. Use --test para probar notificaciones.")
