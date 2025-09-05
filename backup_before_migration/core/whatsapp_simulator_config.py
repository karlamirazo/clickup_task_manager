"""
Configuración del simulador de WhatsApp para pruebas
"""

import os
from typing import Dict, Any

# Configuración del simulador
SIMULATOR_ENABLED = os.getenv("WHATSAPP_SIMULATOR_ENABLED", "True").lower() == "true"
SIMULATOR_INSTANCE_NAME = "clickup-manager-simulator"

# Configuración de mensajes simulados
SIMULATOR_MESSAGE_DELAY = float(os.getenv("WHATSAPP_SIMULATOR_DELAY", "0.1"))  # segundos
SIMULATOR_SAVE_MESSAGES = os.getenv("WHATSAPP_SIMULATOR_SAVE_MESSAGES", "True").lower() == "true"
SIMULATOR_LOG_FILE = os.getenv("WHATSAPP_SIMULATOR_LOG_FILE", "whatsapp_simulator.log")

# Configuración de respuestas simuladas
SIMULATOR_RESPONSES = {
    "success_rate": float(os.getenv("WHATSAPP_SIMULATOR_SUCCESS_RATE", "0.95")),  # 95% éxito
    "response_delay": float(os.getenv("WHATSAPP_SIMULATOR_RESPONSE_DELAY", "0.5")),  # 0.5 segundos
    "error_probability": float(os.getenv("WHATSAPP_SIMULATOR_ERROR_PROBABILITY", "0.05"))  # 5% errores
}

# Configuración de notificaciones simuladas
SIMULATOR_NOTIFICATIONS = {
    "max_length": int(os.getenv("WHATSAPP_SIMULATOR_MAX_LENGTH", "1000")),
    "include_emoji": os.getenv("WHATSAPP_SIMULATOR_INCLUDE_EMOJI", "True").lower() == "true",
    "include_timestamp": os.getenv("WHATSAPP_SIMULATOR_INCLUDE_TIMESTAMP", "True").lower() == "true",
    "simulate_delivery": os.getenv("WHATSAPP_SIMULATOR_DELIVERY", "True").lower() == "true"
}

# Configuración de validación
SIMULATOR_VALIDATION = {
    "phone_format": os.getenv("WHATSAPP_SIMULATOR_PHONE_FORMAT", "international"),  # international, local
    "min_phone_length": int(os.getenv("WHATSAPP_SIMULATOR_MIN_PHONE_LENGTH", "10")),
    "max_phone_length": int(os.getenv("WHATSAPP_SIMULATOR_MAX_PHONE_LENGTH", "15")),
    "validate_phone": os.getenv("WHATSAPP_SIMULATOR_VALIDATE_PHONE", "True").lower() == "true"
}

def get_simulator_config() -> Dict[str, Any]:
    """Obtiene la configuración completa del simulador"""
    return {
        "enabled": SIMULATOR_ENABLED,
        "instance_name": SIMULATOR_INSTANCE_NAME,
        "message_delay": SIMULATOR_MESSAGE_DELAY,
        "save_messages": SIMULATOR_SAVE_MESSAGES,
        "log_file": SIMULATOR_LOG_FILE,
        "responses": SIMULATOR_RESPONSES,
        "notifications": SIMULATOR_NOTIFICATIONS,
        "validation": SIMULATOR_VALIDATION
    }

def is_simulator_enabled() -> bool:
    """Verifica si el simulador está habilitado"""
    return SIMULATOR_ENABLED

def get_simulator_instance_name() -> str:
    """Obtiene el nombre de la instancia del simulador"""
    return SIMULATOR_INSTANCE_NAME
