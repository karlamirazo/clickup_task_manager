#!/usr/bin/env python3
"""
Script de prueba para el servicio robusto de WhatsApp
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_robust_whatsapp():
    """Prueba el servicio robusto de WhatsApp"""
    print("🧪 Probando servicio robusto de WhatsApp...")
    
    try:
        from core.robust_whatsapp_service import get_robust_whatsapp_service
        
        # Obtener instancia del servicio robusto
        print("🔄 Obteniendo servicio robusto...")
        whatsapp_service = await get_robust_whatsapp_service()
        
        # Verificar si está habilitado
        print(f"📱 Servicio habilitado: {whatsapp_service.enabled}")
        
        if not whatsapp_service.enabled:
            print("⚠️ Servicio no habilitado, verificando configuración...")
            from core.config import settings
            print(f"   WHATSAPP_ENABLED: {settings.WHATSAPP_ENABLED}")
            print(f"   WHATSAPP_NOTIFICATIONS_ENABLED: {settings.WHATSAPP_NOTIFICATIONS_ENABLED}")
            print(f"   WHATSAPP_EVOLUTION_URL: {settings.WHATSAPP_EVOLUTION_URL}")
            print(f"   WHATSAPP_EVOLUTION_API_KEY: {settings.WHATSAPP_EVOLUTION_API_KEY}")
            print(f"   WHATSAPP_INSTANCE_NAME: {settings.WHATSAPP_INSTANCE_NAME}")
        
        # Verificar health check
        print("🏥 Verificando health check...")
        health = await whatsapp_service.health_check()
        print(f"✅ Health check: {health}")
        
        # Enviar mensaje de prueba
        print("📱 Enviando mensaje de prueba...")
        result = await whatsapp_service.send_message_with_retries(
            phone_number="+525660576654",
            message="🧪 **PRUEBA DEL SERVICIO ROBUSTO**\n\nEste es un mensaje de prueba para verificar que el servicio robusto de WhatsApp esté funcionando correctamente.\n\n✅ Si ves este mensaje, el servicio está funcionando\n📱 Número: +525660576654\n🕐 Timestamp: Prueba del sistema robusto\n🔄 Con reintentos y fallback al simulador",
            message_type="text",
            notification_type="test",
            task_name="Prueba del Sistema",
            due_date="2025-08-31",
            assignee_name="Usuario de Prueba"
        )
        
        print(f"📤 Resultado del envío: {result}")
        
        # Verificar estadísticas
        stats = whatsapp_service.get_statistics()
        print(f"📈 Estadísticas: {stats}")
        
        print("✅ Prueba del servicio robusto completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_robust_whatsapp())
