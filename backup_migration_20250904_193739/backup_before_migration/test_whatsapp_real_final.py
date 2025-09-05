#!/usr/bin/env python3
"""
Test final de WhatsApp real con Evolution API v2.3.0
"""

import asyncio
import sys
import os

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.whatsapp_client import WhatsAppNotificationService

async def test_whatsapp_real():
    """Probar notificación WhatsApp real"""
    
    print("📱 PROBANDO WHATSAPP REAL - Evolution API v2.3.0")
    print("=" * 60)
    
    service = WhatsAppNotificationService()
    
    print(f"✅ Simulador desactivado: {not service.simulator}")
    print(f"✅ WhatsApp habilitado: {service.enabled}")
    
    print(f"\n🚀 Enviando notificación REAL a +525560576654...")
    
    try:
        result = await service.send_task_notification(
            phone_number="+525560576654",
            task_title="¡WhatsApp Real Funcionando!",
            task_description="Sistema ClickUp conectado exitosamente con WhatsApp real usando Evolution API v2.3.0",
            notification_type="created",
            assignee="Karla"
        )
        
        if result.success:
            print("🎉 ¡NOTIFICACIÓN ENVIADA A WHATSAPP REAL!")
            print(f"📋 Respuesta: {result.message}")
            print("📱 ¡REVISA TU WHATSAPP!")
        else:
            print(f"❌ Error: {result.error}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_whatsapp_real())
