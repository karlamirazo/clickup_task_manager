#!/usr/bin/env python3
"""
Script para probar WhatsApp real con Evolution API conectado
"""
import asyncio
import aiohttp
import json
from datetime import datetime

async def test_whatsapp_real():
    """Probar WhatsApp real con la instancia ya conectada"""
    
    print("🧪 PROBANDO WHATSAPP REAL CON EVOLUTION API")
    print("=" * 60)
    
    # Configuración
    app_base_url = 'https://clickuptaskmanager-production.up.railway.app'
    evolution_base_url = 'https://evolution-whatsapp-api-production.up.railway.app'
    api_key = 'clickup-whatsapp-2024'
    instance_name = 'clickup-manager'
    
    headers_app = {'Content-Type': 'application/json'}
    headers_evolution = {'apikey': api_key, 'Content-Type': 'application/json'}
    
    async with aiohttp.ClientSession() as session:
        
        # 1. Probar salud de WhatsApp en la app
        print("1️⃣ Verificando salud de WhatsApp en la aplicación...")
        try:
            async with session.get(f'{app_base_url}/api/v1/whatsapp/health', headers=headers_app) as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"   ✅ Salud: {health_data.get('status', 'unknown')}")
                    print(f"   📡 Evolution URL: {health_data.get('evolution_url', 'N/A')}")
                    print(f"   🔔 Notificaciones: {health_data.get('notifications_enabled', 'N/A')}")
                else:
                    print(f"   ❌ Error de salud: {response.status}")
        except Exception as e:
            print(f"   ❌ Error conectando a la app: {e}")
        
        print()
        
        # 2. Probar conexión directa con Evolution API
        print("2️⃣ Verificando Evolution API directamente...")
        try:
            async with session.get(f'{evolution_base_url}/instance/connectionState/{instance_name}', headers=headers_evolution) as response:
                if response.status == 200:
                    state_data = await response.json()
                    print(f"   ✅ Estado de conexión: {state_data}")
                else:
                    print(f"   ⚠️ Evolution API respuesta: {response.status}")
                    error_text = await response.text()
                    print(f"   📄 Respuesta: {error_text[:200]}...")
        except Exception as e:
            print(f"   ❌ Error conectando a Evolution API: {e}")
        
        print()
        
        # 3. Probar envío de mensaje directo por Evolution API
        print("3️⃣ Probando envío directo por Evolution API...")
        test_number = input("   📞 Ingresa tu número de WhatsApp (ej: +521234567890): ").strip()
        
        if test_number:
            message_data = {
                "number": test_number,
                "text": f"🧪 PRUEBA WHATSAPP REAL - {datetime.now().strftime('%H:%M:%S')}\n\n✅ Evolution API funcionando\n📱 Instancia: {instance_name}\n🔗 Desde ClickUp Task Manager"
            }
            
            try:
                async with session.post(
                    f'{evolution_base_url}/message/sendText/{instance_name}', 
                    headers=headers_evolution, 
                    json=message_data
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        print(f"   🎉 ¡MENSAJE ENVIADO POR EVOLUTION API!")
                        print(f"   📱 Resultado: {result}")
                    else:
                        print(f"   ❌ Error enviando por Evolution: {response.status}")
                        error_text = await response.text()
                        print(f"   📄 Error: {error_text}")
            except Exception as e:
                print(f"   ❌ Error en envío directo: {e}")
        
        print()
        
        # 4. Probar envío por la aplicación principal
        print("4️⃣ Probando envío por la aplicación principal...")
        if test_number:
            app_message_data = {
                "phone_number": test_number,
                "message": f"🚀 PRUEBA DESDE APP PRINCIPAL - {datetime.now().strftime('%H:%M:%S')}\n\n✅ Integración completa funcionando\n📋 ClickUp → Evolution API → WhatsApp"
            }
            
            try:
                async with session.post(
                    f'{app_base_url}/api/v1/whatsapp/send/message', 
                    headers=headers_app, 
                    json=app_message_data
                ) as response:
                    if response.status in [200, 202]:
                        result = await response.json()
                        print(f"   🎉 ¡MENSAJE ENVIADO POR LA APP!")
                        print(f"   📱 Resultado: {result}")
                    else:
                        print(f"   ❌ Error enviando por la app: {response.status}")
                        error_text = await response.text()
                        print(f"   📄 Error: {error_text}")
            except Exception as e:
                print(f"   ❌ Error en envío por app: {e}")
        
        print()
        print("=" * 60)
        print("🎯 PRUEBA COMPLETADA")
        print()
        print("📋 PRÓXIMO PASO: Si los mensajes llegaron, ¡WhatsApp real está funcionando!")
        print("📱 Puedes crear tareas en ClickUp con números de WhatsApp para recibir notificaciones automáticas")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBA DE WHATSAPP REAL...")
    print()
    asyncio.run(test_whatsapp_real())
