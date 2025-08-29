#!/usr/bin/env python3
"""
Script para configurar Evolution API sin autenticación estricta
"""

import requests
import json
import time

def test_evolution_api_no_auth():
    """Probar Evolution API sin autenticación"""
    
    base_url = "http://localhost:8080"
    
    print("🔍 Probando Evolution API sin autenticación...")
    
    # 1. Crear instancia sin autenticación
    print("\n📱 Paso 1: Creando instancia...")
    create_data = {
        "instanceName": "clickup-manager",
        "token": "test-token",
        "qrcode": True,
        "number": "",
        "webhook": "http://localhost:8000/api/webhooks/whatsapp",
        "webhookByEvents": True,
        "webhookBase64": False,
        "events": ["message", "presence.update", "connection.update"]
    }
    
    try:
        response = requests.post(f"{base_url}/instance/create", json=create_data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Instancia creada exitosamente!")
            instance_data = response.json()
            return instance_data
        else:
            print(f"❌ Error creando instancia: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_qr_code():
    """Obtener código QR para conectar WhatsApp"""
    
    base_url = "http://localhost:8080"
    instance_name = "clickup-manager"
    
    print(f"\n📱 Paso 2: Obteniendo código QR para {instance_name}...")
    
    try:
        response = requests.get(f"{base_url}/instance/connect/{instance_name}", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            qr_data = response.json()
            if "qrcode" in qr_data:
                print("✅ Código QR obtenido!")
                print("📱 Escanea este código QR con tu WhatsApp para conectar la instancia")
                return qr_data
            else:
                print("⚠️ No se encontró código QR en la respuesta")
                return None
        else:
            print(f"❌ Error obteniendo código QR: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_connection_status():
    """Verificar estado de conexión"""
    
    base_url = "http://localhost:8080"
    instance_name = "clickup-manager"
    
    print(f"\n🔍 Paso 3: Verificando estado de conexión...")
    
    try:
        response = requests.get(f"{base_url}/instance/connectionState/{instance_name}", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            status_data = response.json()
            state = status_data.get("state", "unknown")
            print(f"Estado de conexión: {state}")
            return status_data
        else:
            print(f"❌ Error verificando estado: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def send_test_message():
    """Enviar mensaje de prueba"""
    
    base_url = "http://localhost:8080"
    instance_name = "clickup-manager"
    phone_number = "+525660576654"
    
    print(f"\n📤 Paso 4: Enviando mensaje de prueba...")
    
    message_data = {
        "number": phone_number,
        "text": "¡Hola! Este es un mensaje de prueba desde Evolution API. 🚀\n\nSistema: ClickUp Project Manager\nAPI: Evolution API\nEstado: Funcionando correctamente"
    }
    
    try:
        response = requests.post(f"{base_url}/message/sendText/{instance_name}", json=message_data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Mensaje enviado exitosamente!")
            return True
        else:
            print(f"❌ Error enviando mensaje: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Configurando Evolution API sin autenticación")
    print("=" * 60)
    
    # Verificar si Evolution API está ejecutándose
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        print("✅ Evolution API está ejecutándose")
    except:
        print("❌ Evolution API no está ejecutándose")
        print("💡 Ejecuta: cd evolution-api && docker-compose up -d")
        return
    
    # Crear instancia
    instance = test_evolution_api_no_auth()
    if not instance:
        print("❌ No se pudo crear la instancia")
        return
    
    # Obtener código QR
    qr_data = get_qr_code()
    if not qr_data:
        print("❌ No se pudo obtener el código QR")
        return
    
    # Esperar a que se conecte
    print("\n⏳ Esperando a que se conecte WhatsApp...")
    print("📱 Escanea el código QR con tu WhatsApp")
    
    max_wait = 120  # 2 minutos
    wait_time = 0
    
    while wait_time < max_wait:
        time.sleep(10)
        wait_time += 10
        
        status = check_connection_status()
        if status and status.get("state") == "open":
            print("✅ WhatsApp conectado exitosamente!")
            break
        elif wait_time % 30 == 0:
            print(f"⏳ Esperando conexión... ({wait_time}s)")
    
    if wait_time >= max_wait:
        print("⏰ Tiempo de espera agotado")
        return
    
    # Enviar mensaje de prueba
    success = send_test_message()
    
    if success:
        print("\n🎯 ¡Prueba completada exitosamente!")
        print("📱 El mensaje fue enviado al número +525660576654")
    else:
        print("\n❌ Error enviando el mensaje")

if __name__ == "__main__":
    main()



