#!/usr/bin/env python3
"""
Diagnóstico completo del sistema de WhatsApp
"""

import asyncio
import sys
import os
import aiohttp
import json

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def diagnose_whatsapp_complete():
    """Diagnóstico completo del sistema de WhatsApp"""
    print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA DE WHATSAPP")
    print("=" * 60)
    
    try:
        from core.config import settings
        
        # 1. VERIFICAR CONFIGURACIÓN
        print("\n📋 1. CONFIGURACIÓN ACTUAL:")
        print(f"   🌐 Evolution API URL: {settings.WHATSAPP_EVOLUTION_URL}")
        print(f"   🔑 API Key: {settings.WHATSAPP_EVOLUTION_API_KEY}")
        print(f"   📱 Instancia: {settings.WHATSAPP_INSTANCE_NAME}")
        print(f"   📱 WhatsApp habilitado: {settings.WHATSAPP_ENABLED}")
        print(f"   🔔 Notificaciones habilitadas: {settings.WHATSAPP_NOTIFICATIONS_ENABLED}")
        print(f"   🎮 Simulador habilitado: {settings.WHATSAPP_SIMULATOR_ENABLED}")
        
        # 2. VERIFICAR CONECTIVIDAD CON EVOLUTION API
        print("\n🌐 2. VERIFICANDO CONECTIVIDAD CON EVOLUTION API:")
        try:
            async with aiohttp.ClientSession() as session:
                # Health check básico
                async with session.get(settings.WHATSAPP_EVOLUTION_URL) as response:
                    print(f"   📊 Status: {response.status}")
                    if response.status == 200:
                        health_data = await response.text()
                        print(f"   ✅ API responde: {health_data[:100]}...")
                    else:
                        print(f"   ❌ Error: {response.status}")
        except Exception as e:
            print(f"   ❌ Error de conectividad: {e}")
        
        # 3. VERIFICAR INSTANCIA ESPECÍFICA
        print(f"\n📱 3. VERIFICANDO INSTANCIA '{settings.WHATSAPP_INSTANCE_NAME}':")
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"apikey": settings.WHATSAPP_EVOLUTION_API_KEY}
                
                # Verificar si la instancia existe
                instance_url = f"{settings.WHATSAPP_EVOLUTION_URL}/instance/find/{settings.WHATSAPP_INSTANCE_NAME}"
                async with session.get(instance_url, headers=headers) as response:
                    print(f"   📊 Status: {response.status}")
                    if response.status == 200:
                        instance_data = await response.json()
                        print(f"   ✅ Instancia encontrada: {instance_data}")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Instancia no encontrada: {error_text}")
        except Exception as e:
            print(f"   ❌ Error verificando instancia: {e}")
        
        # 4. VERIFICAR ESTADO DE CONEXIÓN
        print(f"\n🔗 4. VERIFICANDO ESTADO DE CONEXIÓN:")
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"apikey": settings.WHATSAPP_EVOLUTION_API_KEY}
                
                # Verificar conexiones
                connections_url = f"{settings.WHATSAPP_EVOLUTION_URL}/instance/connections/{settings.WHATSAPP_INSTANCE_NAME}"
                async with session.get(connections_url, headers=headers) as response:
                    print(f"   📊 Status: {response.status}")
                    if response.status == 200:
                        connections_data = await response.json()
                        print(f"   ✅ Estado de conexión: {connections_data}")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Error obteniendo conexiones: {error_text}")
        except Exception as e:
            print(f"   ❌ Error verificando conexiones: {e}")
        
        # 5. PROBAR ENVÍO DE MENSAJE
        print(f"\n📤 5. PROBANDO ENVÍO DE MENSAJE:")
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"apikey": settings.WHATSAPP_EVOLUTION_API_KEY}
                
                # Enviar mensaje de prueba
                message_url = f"{settings.WHATSAPP_EVOLUTION_URL}/message/sendText/{settings.WHATSAPP_INSTANCE_NAME}"
                test_message = {
                    "number": "525660576654",
                    "text": "🧪 **PRUEBA DE DIAGNÓSTICO**\n\nVerificando que la Evolution API esté funcionando correctamente.\n\n✅ Si ves este mensaje, la API está funcionando\n📱 Número: +525660576654\n🕐 Timestamp: Diagnóstico del sistema"
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
        
        # 6. VERIFICAR SERVICIO ROBUSTO
        print(f"\n🛡️ 6. VERIFICANDO SERVICIO ROBUSTO:")
        try:
            from integrations.whatsapp.service import get_robust_whatsapp_service
            
            whatsapp_service = await get_robust_whatsapp_service()
            print(f"   📱 Servicio habilitado: {whatsapp_service.enabled}")
            
            # Health check del servicio
            health = await whatsapp_service.health_check()
            print(f"   🏥 Health check: {health}")
            
        except Exception as e:
            print(f"   ❌ Error en servicio robusto: {e}")
        
        # 7. VERIFICAR EXTRACCIÓN DE NÚMEROS
        print(f"\n📞 7. VERIFICANDO EXTRACCIÓN DE NÚMEROS:")
        try:
            from core.phone_extractor import extract_whatsapp_numbers_from_task
            
            # Probar con texto de ejemplo
            test_text = "📱 **Número de Celular para WhatsApp:** +525660576654"
            numbers = extract_whatsapp_numbers_from_task(
                task_description=test_text,
                task_title="Tarea de prueba"
            )
            print(f"   📱 Números extraídos: {numbers}")
            
        except Exception as e:
            print(f"   ❌ Error en extracción: {e}")
        
        print("\n" + "=" * 60)
        print("✅ DIAGNÓSTICO COMPLETADO")
        
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(diagnose_whatsapp_complete())
