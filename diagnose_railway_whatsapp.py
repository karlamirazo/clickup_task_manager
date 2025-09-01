#!/usr/bin/env python3
"""
Diagnóstico específico para Railway - WhatsApp
"""

import asyncio
import sys
import os
import aiohttp
import json

async def diagnose_railway_whatsapp():
    """Diagnóstico específico para Railway"""
    print("🔍 DIAGNÓSTICO RAILWAY - WHATSAPP")
    print("=" * 50)
    
    # Configuración de Railway (hardcodeada para diagnóstico)
    RAILWAY_URL = "https://tu-app.railway.app"  # Cambia esto por tu URL real
    EVOLUTION_URL = "https://evolution-api-production-9d5d.up.railway.app"
    API_KEY = "clickup-evolution-v223"
    INSTANCE = "clickup-v23"
    
    print(f"🌐 Railway App: {RAILWAY_URL}")
    print(f"📱 Evolution API: {EVOLUTION_URL}")
    print(f"🔑 API Key: {API_KEY}")
    print(f"📱 Instancia: {INSTANCE}")
    
    try:
        # 1. Verificar que la app de Railway responda
        print(f"\n1️⃣ Verificando app de Railway...")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{RAILWAY_URL}/health") as response:
                print(f"   📊 Status: {response.status}")
                if response.status == 200:
                    health_data = await response.text()
                    print(f"   ✅ App responde: {health_data[:100]}...")
                else:
                    print(f"   ❌ Error: {response.status}")
                    
    except Exception as e:
        print(f"   ❌ Error conectando a Railway: {e}")
    
    try:
        # 2. Verificar Evolution API
        print(f"\n2️⃣ Verificando Evolution API...")
        async with aiohttp.ClientSession() as session:
            # Health check básico
            async with session.get(EVOLUTION_URL) as response:
                print(f"   📊 Status: {response.status}")
                if response.status == 200:
                    health_data = await response.text()
                    print(f"   ✅ Evolution API responde: {health_data[:100]}...")
                else:
                    print(f"   ❌ Error: {response.status}")
                    
    except Exception as e:
        print(f"   ❌ Error conectando a Evolution API: {e}")
    
    try:
        # 3. Verificar instancia específica
        print(f"\n3️⃣ Verificando instancia '{INSTANCE}'...")
        async with aiohttp.ClientSession() as session:
            headers = {"apikey": API_KEY}
            
            # Verificar si la instancia existe
            instance_url = f"{EVOLUTION_URL}/instance/find/{INSTANCE}"
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
    
    try:
        # 4. Verificar conexiones
        print(f"\n4️⃣ Verificando conexiones...")
        async with aiohttp.ClientSession() as session:
            headers = {"apikey": API_KEY}
            
            connections_url = f"{EVOLUTION_URL}/instance/connections/{INSTANCE}"
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
    
    try:
        # 5. Probar envío de mensaje
        print(f"\n5️⃣ Probando envío de mensaje...")
        async with aiohttp.ClientSession() as session:
            headers = {"apikey": API_KEY}
            
            message_url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE}"
            test_message = {
                "number": "525660576654",
                "text": "🧪 **PRUEBA RAILWAY**\n\nVerificando que la Evolution API funcione desde Railway.\n\n✅ Si ves este mensaje, la API está funcionando\n📱 Número: +525660576654\n🕐 Timestamp: Diagnóstico Railway"
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
    
    print(f"\n" + "=" * 50)
    print("✅ DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    print("⚠️ IMPORTANTE: Cambia 'tu-app.railway.app' por tu URL real de Railway")
    print("⚠️ Ejecuta este script DESPUÉS de cambiar la URL")
    print()
    
    # Preguntar si quiere continuar
    response = input("¿Quieres continuar con el diagnóstico? (s/n): ")
    if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        asyncio.run(diagnose_railway_whatsapp())
    else:
        print("Diagnóstico cancelado")

