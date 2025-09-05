#!/usr/bin/env python3
"""
Script para crear y configurar la instancia de WhatsApp en Evolution API
"""

import asyncio
import aiohttp
import json
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings

async def create_whatsapp_instance():
    """Crear instancia de WhatsApp en Evolution API"""
    
    print("🚀 CONFIGURANDO INSTANCIA DE WHATSAPP")
    print("=" * 50)
    print(f"URL Evolution: {settings.WHATSAPP_EVOLUTION_URL}")
    print(f"Instancia: {settings.WHATSAPP_INSTANCE_NAME}")
    print()
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    if settings.WHATSAPP_EVOLUTION_API_KEY:
        headers['apikey'] = settings.WHATSAPP_EVOLUTION_API_KEY
        print(f"🔑 API Key configurado: {'*' * (len(settings.WHATSAPP_EVOLUTION_API_KEY) - 4) + settings.WHATSAPP_EVOLUTION_API_KEY[-4:]}")
    else:
        print("⚠️ API Key no configurado - usando sin autenticación")
    
    try:
        async with aiohttp.ClientSession() as session:
            
            # 1. Crear la instancia
            print("📱 Paso 1: Creando instancia...")
            create_url = f"{settings.WHATSAPP_EVOLUTION_URL}/instance/create"
            
            instance_data = {
                "instanceName": settings.WHATSAPP_INSTANCE_NAME,
                "token": settings.WHATSAPP_EVOLUTION_API_KEY or "default-token",
                "qrcode": True,
                "webhook": {
                    "url": settings.WHATSAPP_WEBHOOK_URL,
                    "enabled": True,
                    "events": [
                        "APPLICATION_STARTUP",
                        "QRCODE_UPDATED", 
                        "MESSAGES_UPSERT",
                        "MESSAGES_UPDATE",
                        "CONNECTION_UPDATE"
                    ]
                } if settings.WHATSAPP_WEBHOOK_URL else {}
            }
            
            async with session.post(create_url, headers=headers, json=instance_data) as resp:
                print(f"   Status: {resp.status}")
                
                if resp.status == 201:
                    data = await resp.json()
                    print("   ✅ Instancia creada exitosamente")
                    print(f"   📊 Respuesta: {json.dumps(data, indent=2)}")
                elif resp.status == 409:
                    print("   ⚠️ Instancia ya existe - continuando...")
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Error creando instancia: {error_text}")
                    return False
            
            # 2. Conectar WhatsApp
            print("\n📱 Paso 2: Iniciando conexión WhatsApp...")
            connect_url = f"{settings.WHATSAPP_EVOLUTION_URL}/instance/connect/{settings.WHATSAPP_INSTANCE_NAME}"
            
            async with session.get(connect_url, headers=headers) as resp:
                print(f"   Status: {resp.status}")
                
                if resp.status == 200:
                    data = await resp.json()
                    print("   ✅ Conexión iniciada")
                    
                    # Verificar si hay QR code
                    if 'qrcode' in data:
                        print("\n📱 QR CODE DISPONIBLE:")
                        print("   🔗 Escanea este QR con WhatsApp:")
                        print(f"   {data['qrcode']}")
                        
                        # Guardar QR en archivo
                        with open("whatsapp_qr.txt", "w") as f:
                            f.write(data['qrcode'])
                        print("   💾 QR guardado en: whatsapp_qr.txt")
                        
                        print("\n📱 INSTRUCCIONES:")
                        print("   1. Abre WhatsApp en tu teléfono")
                        print("   2. Ve a Configuración > Dispositivos vinculados")
                        print("   3. Toca 'Vincular un dispositivo'")
                        print("   4. Escanea el QR code arriba")
                        
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Error conectando: {error_text}")
                    return False
            
            # 3. Verificar estado
            print("\n📱 Paso 3: Verificando estado...")
            await asyncio.sleep(2)  # Esperar un poco
            
            status_url = f"{settings.WHATSAPP_EVOLUTION_URL}/instance/status/{settings.WHATSAPP_INSTANCE_NAME}"
            async with session.get(status_url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    state = data.get('instance', {}).get('state', 'unknown')
                    print(f"   📊 Estado actual: {state}")
                    
                    if state == 'open':
                        print("   ✅ WhatsApp CONECTADO - ¡Listo para enviar mensajes!")
                        return True
                    elif state == 'close':
                        print("   ⏳ WhatsApp esperando conexión - escanea el QR")
                        return True
                    else:
                        print(f"   ❓ Estado: {state}")
                        return True
                else:
                    print(f"   ❌ Error verificando estado: {resp.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def get_qr_code():
    """Obtener QR code si la instancia ya existe"""
    
    print("🔍 OBTENIENDO QR CODE...")
    print("-" * 30)
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    if settings.WHATSAPP_EVOLUTION_API_KEY:
        headers['apikey'] = settings.WHATSAPP_EVOLUTION_API_KEY
    
    try:
        async with aiohttp.ClientSession() as session:
            qr_url = f"{settings.WHATSAPP_EVOLUTION_URL}/instance/qrcode/{settings.WHATSAPP_INSTANCE_NAME}"
            
            async with session.get(qr_url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'qrcode' in data:
                        print("📱 QR CODE:")
                        print(data['qrcode'])
                        
                        with open("whatsapp_qr.txt", "w") as f:
                            f.write(data['qrcode'])
                        print("💾 QR guardado en: whatsapp_qr.txt")
                        return True
                    else:
                        print("⚠️ QR no disponible - posiblemente ya conectado")
                        return False
                else:
                    error_text = await resp.text()
                    print(f"❌ Error: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def check_connection_status():
    """Verificar estado de conexión actual"""
    
    print("📊 ESTADO ACTUAL DE LA CONEXIÓN")
    print("-" * 40)
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    if settings.WHATSAPP_EVOLUTION_API_KEY:
        headers['apikey'] = settings.WHATSAPP_EVOLUTION_API_KEY
    
    try:
        async with aiohttp.ClientSession() as session:
            status_url = f"{settings.WHATSAPP_EVOLUTION_URL}/instance/status/{settings.WHATSAPP_INSTANCE_NAME}"
            
            async with session.get(status_url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    state = data.get('instance', {}).get('state', 'unknown')
                    
                    print(f"Estado: {state}")
                    
                    if state == 'open':
                        print("✅ WhatsApp CONECTADO")
                        print("🚀 ¡Listo para enviar mensajes!")
                        
                        # Obtener info de la cuenta
                        phone = data.get('instance', {}).get('owner', 'No disponible')
                        print(f"📱 Cuenta conectada: {phone}")
                        
                    elif state == 'close':
                        print("❌ WhatsApp DESCONECTADO")
                        print("💡 Necesitas escanear el QR code")
                        
                    elif state == 'connecting':
                        print("⏳ WhatsApp CONECTANDO...")
                        print("💡 Espera unos segundos")
                        
                    else:
                        print(f"❓ Estado desconocido: {state}")
                    
                    return state
                    
                elif resp.status == 404:
                    print("❌ Instancia no encontrada")
                    print("💡 Ejecuta primero: python scripts/setup_whatsapp_instance.py --create")
                    return None
                    
                else:
                    error_text = await resp.text()
                    print(f"❌ Error: {error_text}")
                    return None
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

async def main():
    """Función principal"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--create":
            success = await create_whatsapp_instance()
            if success:
                print("\n🎉 ¡Configuración completada!")
                print("\n💡 Próximos pasos:")
                print("   1. Escanea el QR con WhatsApp")
                print("   2. Verifica estado: python scripts/setup_whatsapp_instance.py --status")
                print("   3. Prueba envío: python scripts/setup_whatsapp_instance.py --test")
            
        elif sys.argv[1] == "--qr":
            await get_qr_code()
            
        elif sys.argv[1] == "--status":
            await check_connection_status()
            
        elif sys.argv[1] == "--test":
            # Test básico de envío
            phone = input("📱 Ingresa número para test (ej: +5255123456): ")
            if phone:
                from integrations.whatsapp.client import WhatsAppNotificationService
                service = WhatsAppNotificationService()
                
                result = await service.send_task_notification(
                    phone_number=phone,
                    task_title="🧪 Test de Evolution API",
                    task_description="Si recibes este mensaje, ¡Evolution API funciona perfectamente!",
                    notification_type="created"
                )
                
                if result.success:
                    print(f"✅ Mensaje enviado: {result.message}")
                else:
                    print(f"❌ Error: {result.error}")
    else:
        print("🚀 SETUP DE WHATSAPP - EVOLUTION API")
        print("=" * 40)
        print("Comandos disponibles:")
        print("  --create    Crear y configurar instancia")
        print("  --qr        Obtener QR code")
        print("  --status    Ver estado actual")
        print("  --test      Enviar mensaje de prueba")
        print()
        print("Ejemplo: python scripts/setup_whatsapp_instance.py --create")

if __name__ == "__main__":
    asyncio.run(main())
