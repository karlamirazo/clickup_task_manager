#!/usr/bin/env python3
"""
Prueba simple del servicio de WhatsApp
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_whatsapp_simple():
    """Prueba simple del servicio de WhatsApp"""
    print("🧪 PRUEBA SIMPLE DEL SERVICIO DE WHATSAPP")
    print("=" * 50)
    
    try:
        # 1. Verificar configuración
        from core.config import settings
        print(f"✅ Configuración cargada:")
        print(f"   🌐 Evolution API URL: {settings.WHATSAPP_EVOLUTION_URL}")
        print(f"   🔑 API Key: {settings.WHATSAPP_EVOLUTION_API_KEY}")
        print(f"   📱 Instancia: {settings.WHATSAPP_INSTANCE_NAME}")
        
        # 2. Verificar servicio robusto
        from core.robust_whatsapp_service import get_robust_whatsapp_service
        print(f"\n🛡️ Obteniendo servicio robusto...")
        
        whatsapp_service = await get_robust_whatsapp_service()
        print(f"✅ Servicio robusto obtenido: {whatsapp_service.enabled}")
        
        # 3. Health check
        print(f"\n🏥 Health check...")
        health = await whatsapp_service.health_check()
        print(f"✅ Health check: {health}")
        
        # 4. Probar envío de mensaje
        print(f"\n📤 Probando envío de mensaje...")
        result = await whatsapp_service.send_message_with_retries(
            phone_number="525660576654",
            message="🧪 **PRUEBA LOCAL**\n\nVerificando que el servicio funcione localmente.\n\n✅ Si ves este mensaje, el servicio está funcionando\n📱 Número: +525660576654",
            message_type="text",
            notification_type="task_created",
            task_name="Prueba Local",
            due_date=None,
            assignee_name="Usuario de Prueba"
        )
        
        print(f"✅ Resultado del envío: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_whatsapp_simple())
