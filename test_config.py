#!/usr/bin/env python3
"""
Script simple para verificar la configuración de WhatsApp
"""

from core.config import settings

print("🔧 Configuración de WhatsApp:")
print(f"   🌐 URL: {settings.WHATSAPP_EVOLUTION_URL}")
print(f"   🔑 API Key: {settings.WHATSAPP_EVOLUTION_API_KEY}")
print(f"   📱 Instancia: {settings.WHATSAPP_INSTANCE_NAME}")
print(f"   📱 Habilitado: {settings.WHATSAPP_ENABLED}")
print(f"   🔔 Notificaciones: {settings.WHATSAPP_NOTIFICATIONS_ENABLED}")
print(f"   🎮 Simulador: {settings.WHATSAPP_SIMULATOR_ENABLED}")
