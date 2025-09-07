#!/usr/bin/env python3
"""
Script para probar las notificaciones de WhatsApp después de la corrección
"""

import asyncio
import sys
from datetime import datetime

async def test_whatsapp_notification():
    """Prueba el envío de notificación de WhatsApp"""
    
    print("🧪 PROBANDO NOTIFICACIONES DE WHATSAPP")
    print("=" * 60)
    
    try:
        # Importar el servicio robusto de WhatsApp
        from core.robust_whatsapp_service import get_robust_whatsapp_service
        
        # Obtener el servicio
        whatsapp_service = await get_robust_whatsapp_service()
        
        print("✅ Servicio de WhatsApp cargado correctamente")
        
        # Verificar si está habilitado
        if not whatsapp_service.enabled:
            print("❌ WhatsApp está deshabilitado en la configuración")
            return False
        
        print("✅ WhatsApp está habilitado")
        
        # Realizar health check
        print("\n🔍 Realizando health check...")
        health_status = await whatsapp_service.health_check()
        
        print(f"📊 Estado del servicio: {health_status['status']}")
        
        if 'evolution_api' in health_status:
            evolution_status = health_status['evolution_api']
            print(f"🌐 Evolution API: {'✅ Saludable' if evolution_status['healthy'] else '❌ No responde'}")
            print(f"   URL: {evolution_status.get('url', 'N/A')}")
            print(f"   Instancia: {evolution_status.get('instance', 'N/A')}")
        
        if 'simulator' in health_status:
            simulator_status = health_status['simulator']
            print(f"🎭 Simulador: {'✅ Disponible' if simulator_status['healthy'] else '❌ No disponible'}")
        
        # Probar envío de mensaje (usar un número de prueba)
        print("\n📱 Probando envío de mensaje...")
        
        # Número de prueba (reemplazar con un número real para probar)
        test_phone = "525512345678"  # Número de prueba mexicano
        test_message = f"🧪 Prueba de notificación WhatsApp - {datetime.now().strftime('%H:%M:%S')}"
        
        print(f"📞 Enviando a: +{test_phone}")
        print(f"📝 Mensaje: {test_message}")
        
        result = await whatsapp_service.send_message_with_retries(
            phone_number=test_phone,
            message=test_message,
            message_type="text",
            notification_type="test",
            task_name="Prueba de WhatsApp",
            assignee_name="Sistema"
        )
        
        print(f"\n📊 RESULTADO DEL ENVÍO:")
        print(f"   ✅ Éxito: {result.success}")
        print(f"   📱 Teléfono: {result.phone_number}")
        print(f"   🏷️ Estado final: {result.final_status.value}")
        print(f"   🔄 Usó fallback: {result.used_fallback}")
        print(f"   ⏱️ Duración total: {result.total_duration_ms:.0f}ms")
        print(f"   🔢 Intentos: {len(result.attempts)}")
        
        if result.error_summary:
            print(f"   ❌ Error: {result.error_summary}")
        
        # Mostrar detalles de cada intento
        print(f"\n📋 DETALLES DE INTENTOS:")
        for i, attempt in enumerate(result.attempts, 1):
            print(f"   {i}. {attempt.timestamp.strftime('%H:%M:%S')} - {attempt.status.value}")
            if attempt.error:
                print(f"      ❌ Error: {attempt.error}")
            if attempt.duration_ms:
                print(f"      ⏱️ Duración: {attempt.duration_ms:.0f}ms")
        
        # Mostrar estadísticas del servicio
        stats = whatsapp_service.get_statistics()
        print(f"\n📈 ESTADÍSTICAS DEL SERVICIO:")
        print(f"   📤 Total enviados: {stats['total_messages_sent']}")
        print(f"   ✅ Exitosos: {stats['successful_messages']}")
        print(f"   ❌ Fallidos: {stats['failed_messages']}")
        print(f"   🔄 Fallback: {stats['fallback_messages']}")
        print(f"   📊 Tasa de éxito: {stats['success_rate']:.1f}%")
        
        return result.success
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Función principal"""
    success = await test_whatsapp_notification()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 ¡PRUEBA EXITOSA! Las notificaciones de WhatsApp están funcionando")
        print("✅ El problema ha sido resuelto")
    else:
        print("❌ La prueba falló. Revisar configuraciones y logs")
        print("🔍 Verificar que Evolution API esté funcionando correctamente")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)

