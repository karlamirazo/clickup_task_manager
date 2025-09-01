#!/usr/bin/env python3
"""
Prueba directa de envío de WhatsApp
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_direct_whatsapp():
    """Prueba directa de envío de WhatsApp"""
    print("🧪 PRUEBA DIRECTA DE WHATSAPP")
    print("=" * 50)
    
    # Configuración de Evolution API
    EVOLUTION_URL = "https://evolution-api-production-9d5d.up.railway.app"
    API_KEY = "clickup-evolution-v223"
    INSTANCE = "clickup-v23"
    PHONE_NUMBER = "525660576654"
    
    print(f"📱 Evolution API: {EVOLUTION_URL}")
    print(f"🔑 API Key: {API_KEY}")
    print(f"📱 Instancia: {INSTANCE}")
    print(f"📞 Número de prueba: +{PHONE_NUMBER}")
    
    try:
        # 1. Verificar que la instancia existe y está conectada
        print(f"\n1️⃣ Verificando estado de la instancia '{INSTANCE}'...")
        async with aiohttp.ClientSession() as session:
            headers = {"apikey": API_KEY}
            
            # Usar el endpoint correcto
            connection_url = f"{EVOLUTION_URL}/instance/connectionState/{INSTANCE}"
            async with session.get(connection_url, headers=headers) as response:
                print(f"   📊 Status: {response.status}")
                if response.status == 200:
                    connection_data = await response.json()
                    print(f"   ✅ Estado de conexión: {connection_data}")
                    
                    # Verificar si está conectado
                    if isinstance(connection_data, dict):
                        instance_info = connection_data.get("instance", {})
                        if instance_info.get("state") == "open":
                            print(f"   🟢 WhatsApp conectado y listo")
                        else:
                            print(f"   🔴 WhatsApp NO está conectado")
                            print(f"   📋 Estado actual: {instance_info.get('state')}")
                            return
                    else:
                        print(f"   ❌ Formato de respuesta inesperado: {connection_data}")
                        return
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error verificando conexión: {error_text}")
                    return
                    
    except Exception as e:
        print(f"   ❌ Error verificando instancia: {e}")
        return
    
    try:
        # 2. Enviar mensaje de prueba
        print(f"\n2️⃣ Enviando mensaje de prueba...")
        async with aiohttp.ClientSession() as session:
            headers = {"apikey": API_KEY}
            
            message_url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE}"
            
            # Mensaje de prueba
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            test_message = {
                "number": PHONE_NUMBER,
                "text": f"🧪 **PRUEBA DIRECTA**\n\n¡Hola! Este es un mensaje de prueba directa desde la Evolution API.\n\n✅ Si ves este mensaje, la API está funcionando perfectamente\n📱 Número: +{PHONE_NUMBER}\n🕐 Timestamp: {timestamp}\n\n🔧 Sistema: ClickUp Project Manager\n📊 Estado: Prueba de notificaciones"
            }
            
            print(f"   📤 Enviando mensaje...")
            print(f"   📋 Contenido: {test_message['text'][:100]}...")
            
            async with session.post(message_url, headers=headers, json=test_message) as response:
                print(f"   📊 Status: {response.status}")
                
                if response.status == 200:
                    message_data = await response.json()
                    print(f"   ✅ Mensaje enviado exitosamente!")
                    print(f"   📋 Respuesta: {message_data}")
                    
                    # Verificar si el mensaje se envió correctamente
                    if isinstance(message_data, dict):
                        if message_data.get("status") == "success":
                            print(f"   🎉 ¡Mensaje enviado con éxito!")
                        elif message_data.get("status") == "pending":
                            print(f"   ⏳ Mensaje en cola de envío")
                        else:
                            print(f"   ⚠️ Estado del mensaje: {message_data.get('status')}")
                    else:
                        print(f"   ℹ️ Respuesta recibida: {message_data}")
                        
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error enviando mensaje: {error_text}")
                    
                    # Intentar parsear el error como JSON
                    try:
                        error_json = json.loads(error_text)
                        print(f"   📋 Detalles del error: {error_json}")
                    except:
                        print(f"   📋 Error en texto plano: {error_text}")
                    
    except Exception as e:
        print(f"   ❌ Error enviando mensaje: {e}")
    
    print(f"\n" + "=" * 50)
    print("✅ PRUEBA COMPLETADA")
    print(f"📱 Verifica si recibiste el mensaje en WhatsApp: +{PHONE_NUMBER}")

if __name__ == "__main__":
    print("🚀 Iniciando prueba directa de WhatsApp...")
    asyncio.run(test_direct_whatsapp())
