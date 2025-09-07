#!/usr/bin/env python3
"""
Script para probar WhatsApp con número específico: +525660576654
"""

import asyncio
import sys
from datetime import datetime

async def test_whatsapp_specific_number():
    """Prueba el envío de notificación de WhatsApp con número específico"""
    
    print("📱 PROBANDO WHATSAPP CON NÚMERO ESPECÍFICO")
    print("=" * 60)
    
    # Número específico proporcionado
    phone_number = "525660576654"
    
    print(f"📱 Número a probar: +{phone_number}")
    
    try:
        # Importar el servicio robusto de WhatsApp
        from core.robust_whatsapp_service import get_robust_whatsapp_service
        
        # Obtener el servicio
        whatsapp_service = await get_robust_whatsapp_service()
        
        print("✅ Servicio de WhatsApp cargado correctamente")
        
        # Verificar configuraciones
        print(f"\n🔧 CONFIGURACIONES ACTUALES:")
        print(f"   🌐 URL: {whatsapp_service.evolution_config.base_url}")
        print(f"   🔑 API Key: {whatsapp_service.evolution_config.api_key}")
        print(f"   📱 Instancia: {whatsapp_service.evolution_config.instance_name}")
        print(f"   🚫 Simulador: {'Deshabilitado' if not whatsapp_service.evolution_config.fallback_to_simulator else 'Habilitado'}")
        
        # Verificar que el simulador esté deshabilitado
        if whatsapp_service.evolution_config.fallback_to_simulator:
            print("⚠️ ADVERTENCIA: El simulador está habilitado como fallback")
        
        # Realizar health check
        print(f"\n🔍 Realizando health check...")
        health_status = await whatsapp_service.health_check()
        
        print(f"📊 Estado del servicio: {health_status['status']}")
        
        if 'evolution_api' in health_status:
            evolution_status = health_status['evolution_api']
            if evolution_status['healthy']:
                print("✅ Evolution API: Conectado y funcionando")
                print(f"   URL: {evolution_status.get('url', 'N/A')}")
                print(f"   Instancia: {evolution_status.get('instance', 'N/A')}")
            else:
                print("❌ Evolution API: No responde")
                print(f"   Error: {evolution_status.get('error', 'Desconocido')}")
                return False
        
        # Preparar mensaje de prueba
        test_message = f"""🧪 *PRUEBA DE NOTIFICACIÓN WHATSAPP*

✅ *Sistema funcionando correctamente*
📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
🔧 Configuración: Producción
📱 Instancia: {whatsapp_service.evolution_config.instance_name}

*Esta es una prueba del sistema de notificaciones de ClickUp.*

Si recibes este mensaje, significa que las notificaciones de WhatsApp están funcionando correctamente. 🎉

---
*Mensaje enviado desde el sistema de gestión de proyectos ClickUp*"""
        
        print(f"\n📝 Mensaje de prueba preparado")
        print(f"📏 Longitud: {len(test_message)} caracteres")
        
        # Enviar mensaje
        print(f"\n📤 Enviando mensaje a +{phone_number}...")
        start_time = datetime.now()
        
        result = await whatsapp_service.send_message_with_retries(
            phone_number=phone_number,
            message=test_message,
            message_type="text",
            notification_type="test",
            task_name="Prueba de WhatsApp Real",
            assignee_name="Sistema de Pruebas"
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n📊 RESULTADO DEL ENVÍO:")
        print(f"   ✅ Éxito: {result.success}")
        print(f"   📱 Teléfono: +{result.phone_number}")
        print(f"   🏷️ Estado final: {result.final_status.value}")
        print(f"   🔄 Usó fallback: {result.used_fallback}")
        print(f"   ⏱️ Duración total: {duration:.1f}s")
        print(f"   🔢 Intentos: {len(result.attempts)}")
        
        if result.message_id:
            print(f"   🆔 ID del mensaje: {result.message_id}")
        
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
    print("🧪 PRUEBA DE WHATSAPP CON NÚMERO ESPECÍFICO")
    print("📱 Número: +525660576654")
    print("=" * 60)
    
    success = await test_whatsapp_specific_number()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 ¡PRUEBA EXITOSA!")
        print("✅ El mensaje se envió correctamente a WhatsApp")
        print("📱 Revisa el WhatsApp del número +525660576654 para confirmar la recepción")
        print("🔧 Las notificaciones están funcionando correctamente")
    else:
        print("❌ La prueba falló")
        print("🔍 Revisar configuraciones y logs")
        print("📞 Verificar que el número +525660576654 sea válido en WhatsApp")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
