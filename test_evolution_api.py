#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la conectividad con la Evolution API real
"""

import asyncio
import sys
import os
import aiohttp
import json

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_evolution_api():
    """Prueba la conectividad con la Evolution API real"""
    print("🧪 Probando conectividad con Evolution API real...")
    
    try:
        from core.config import settings
        
        # Mostrar configuración
        print(f"🌐 Evolution API URL: {settings.WHATSAPP_EVOLUTION_URL}")
        print(f"🔑 API Key: {settings.WHATSAPP_EVOLUTION_API_KEY}")
        print(f"📱 Instancia: {settings.WHATSAPP_INSTANCE_NAME}")
        print(f"📱 WhatsApp habilitado: {settings.WHATSAPP_ENABLED}")
        print(f"🔔 Notificaciones habilitadas: {settings.WHATSAPP_NOTIFICATIONS_ENABLED}")
        
        # Crear sesión HTTP
        async with aiohttp.ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "apikey": settings.WHATSAPP_EVOLUTION_API_KEY
            }
            
            # 1. Probar health check de la instancia
            print("\n🏥 Probando health check de la instancia...")
            try:
                health_url = f"{settings.WHATSAPP_EVOLUTION_URL}/instance/health"
                async with session.get(health_url, headers=headers) as response:
                    print(f"   📊 Status: {response.status}")
                    if response.status == 200:
                        health_data = await response.json()
                        print(f"   ✅ Health check exitoso: {health_data}")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Error en health check: {error_text}")
            except Exception as e:
                print(f"   ❌ Error conectando a health check: {e}")
            
            # 2. Probar obtener información de la instancia
            print("\n📱 Probando obtener información de la instancia...")
            try:
                instance_url = f"{settings.WHATSAPP_EVOLUTION_URL}/instance/info"
                async with session.get(instance_url, headers=headers) as response:
                    print(f"   📊 Status: {response.status}")
                    if response.status == 200:
                        instance_data = await response.json()
                        print(f"   ✅ Información de instancia: {instance_data}")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Error obteniendo información: {error_text}")
            except Exception as e:
                print(f"   ❌ Error obteniendo información de instancia: {e}")
            
            # 3. Probar obtener conexiones
            print("\n🔗 Probando obtener conexiones...")
            try:
                connections_url = f"{settings.WHATSAPP_EVOLUTION_URL}/instance/connections"
                async with session.get(connections_url, headers=headers) as response:
                    print(f"   📊 Status: {response.status}")
                    if response.status == 200:
                        connections_data = await response.json()
                        print(f"   ✅ Conexiones: {connections_data}")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Error obteniendo conexiones: {error_text}")
            except Exception as e:
                print(f"   ❌ Error obteniendo conexiones: {e}")
            
            # 4. Probar enviar mensaje de prueba
            print("\n📤 Probando envío de mensaje de prueba...")
            try:
                message_url = f"{settings.WHATSAPP_EVOLUTION_URL}/message/sendText/{settings.WHATSAPP_INSTANCE_NAME}"
                test_message = {
                    "number": "525660576654",
                    "text": "🧪 **PRUEBA DE EVOLUTION API**\n\nEste es un mensaje de prueba para verificar que la Evolution API esté funcionando correctamente.\n\n✅ Si ves este mensaje, la API está funcionando\n📱 Número: +525660576654\n🕐 Timestamp: Prueba del sistema real"
                }
                
                async with session.post(message_url, headers=headers, json=test_message) as response:
                    print(f"   📊 Status: {response.status}")
                    if response.status == 200:
                        message_data = await response.json()
                        print(f"   ✅ Mensaje enviado exitosamente: {message_data}")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Error enviando mensaje: {error_text}")
            except Exception as e:
                print(f"   ❌ Error enviando mensaje: {e}")
            
            # 5. Probar obtener webhooks
            print("\n🔗 Probando obtener webhooks...")
            try:
                webhooks_url = f"{settings.WHATSAPP_EVOLUTION_URL}/webhook/find/{settings.WHATSAPP_INSTANCE_NAME}"
                async with session.get(webhooks_url, headers=headers) as response:
                    print(f"   📊 Status: {response.status}")
                    if response.status == 200:
                        webhooks_data = await response.json()
                        print(f"   ✅ Webhooks: {webhooks_data}")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Error obteniendo webhooks: {error_text}")
            except Exception as e:
                print(f"   ❌ Error obteniendo webhooks: {e}")
        
        print("\n✅ Diagnóstico de Evolution API completado!")
        
    except Exception as e:
        print(f"❌ Error en el diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_evolution_api())
