"""
Configuración específica para Evolution API de WhatsApp
Configuración para producción con notificaciones reales
"""

import os
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from core.config import settings

class EvolutionAPIConfig(BaseModel):
    """Configuración específica para Evolution API"""
    
    # Configuración básica de la API
    base_url: str = Field(default=settings.WHATSAPP_EVOLUTION_URL, description="URL base de Evolution API")
    api_key: str = Field(default=settings.WHATSAPP_EVOLUTION_API_KEY, description="API Key de Evolution API")
    instance_name: str = Field(default=settings.WHATSAPP_INSTANCE_NAME, description="Nombre de la instancia")
    
    # Configuración de la instancia
    webhook_url: str = Field(default=settings.WHATSAPP_WEBHOOK_URL, description="URL del webhook")
    webhook_enabled: bool = Field(default=True, description="Habilitar webhooks")
    webhook_events: List[str] = Field(
        default=["messages.upsert", "messages.update", "connection.update"],
        description="Eventos a escuchar"
    )
    
    # Configuración de mensajes
    message_delay: float = Field(default=1.0, description="Delay entre mensajes en segundos")
    max_retries: int = Field(default=3, description="Máximo de reintentos")
    retry_delay: float = Field(default=5.0, description="Delay entre reintentos")
    
    # Configuración de plantillas
    templates_enabled: bool = Field(default=True, description="Habilitar mensajes de plantilla")
    default_template: str = Field(default="clickup_notification", description="Plantilla por defecto")
    
    # Configuración de producción
    production_mode: bool = Field(default=True, description="Modo producción activado")
    fallback_to_simulator: bool = Field(default=False, description="Usar simulador como fallback")
    log_all_messages: bool = Field(default=True, description="Log de todos los mensajes")
    
    # Configuración de rate limiting
    rate_limit_enabled: bool = Field(default=True, description="Habilitar rate limiting")
    max_messages_per_minute: int = Field(default=30, description="Máximo mensajes por minuto")
    max_messages_per_hour: int = Field(default=1000, description="Máximo mensajes por hora")
    
    # Configuración de validación
    validate_phone_numbers: bool = Field(default=True, description="Validar números antes de enviar")
    require_country_code: bool = Field(default=True, description="Requerir código de país")
    default_country_code: str = Field(default="52", description="Código de país por defecto (México)")
    
    # Configuración de notificaciones específicas
    notification_types: Dict[str, bool] = Field(
        default={
            "task_created": True,
            "task_updated": True,
            "task_completed": True,
            "task_due_soon": True,
            "task_overdue": True,
            "task_assigned": True,
            "task_comment": False,  # Deshabilitado por defecto
            "task_attachment": False  # Deshabilitado por defecto
        },
        description="Tipos de notificación habilitados"
    )
    
    # Configuración de mensajes personalizados
    message_templates: Dict[str, str] = Field(
        default={
            "task_created": "🆕 Nueva tarea creada: {title}",
            "task_updated": "✏️ Tarea actualizada: {title}",
            "task_completed": "✅ Tarea completada: {title}",
            "task_due_soon": "⏰ Tarea vence pronto: {title} - Vence: {due_date}",
            "task_overdue": "🚨 Tarea vencida: {title} - Vencida desde: {due_date}",
            "task_assigned": "👤 Tarea asignada: {title} - Asignado a: {assignee}"
        },
        description="Plantillas de mensajes por tipo"
    )
    
    # Configuración de campos de ClickUp para extraer números
    phone_extraction_fields: List[str] = Field(
        default=["description", "custom_fields", "comments"],
        description="Campos de ClickUp para extraer números de teléfono"
    )
    
    # Configuración de fallback
    fallback_message: str = Field(
        default="📱 Notificación de ClickUp: {title}",
        description="Mensaje de fallback si la plantilla falla"
    )
    
    # Configuración de monitoreo
    health_check_interval: int = Field(default=300, description="Intervalo de health check en segundos")
    connection_timeout: int = Field(default=30, description="Timeout de conexión en segundos")
    request_timeout: int = Field(default=60, description="Timeout de peticiones en segundos")

# Instancia global de configuración
evolution_config = EvolutionAPIConfig()

def get_evolution_config() -> EvolutionAPIConfig:
    """Obtiene la configuración de Evolution API"""
    return evolution_config

def update_evolution_config(**kwargs) -> None:
    """Actualiza la configuración de Evolution API"""
    for key, value in kwargs.items():
        if hasattr(evolution_config, key):
            setattr(evolution_config, key, value)

def is_production_ready() -> bool:
    """Verifica si la configuración está lista para producción"""
    return (
        evolution_config.production_mode and
        evolution_config.api_key and
        evolution_config.base_url and
        evolution_config.instance_name
    )

def get_webhook_config() -> Dict:
    """Obtiene la configuración del webhook"""
    return {
        "url": evolution_config.webhook_url,
        "enabled": evolution_config.webhook_enabled,
        "events": evolution_config.webhook_events
    }
