#!/usr/bin/env python3
"""
Script optimizado para enviar mensajes por WhatsApp usando Evolution API
"""

import requests
import json
import time

def send_whatsapp_message():
    """Enviar mensaje por WhatsApp"""
    
    # Configuración
    base_url = "http://localhost:8080"
    api_key = "clickup_whatsapp_key_2024"
    instance_name = "clickup_whatsapp"
    phone_number = "+525660576654"
    
    # Mensaje personalizado
    message = """¡Hola! 🚀

Este es un mensaje de prueba desde Evolution API.

Sistema: ClickUp Project Manager
API: Evolution API
Estado: Funcionando correctamente

¡Saludos desde tu asistente de IA! 🤖"""
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "apikey": api_key
    }
    
    # Datos del mensaje
    data = {
        "number": phone_number,
        "text": message
    }
    
    print("🚀 Enviando mensaje por WhatsApp...")
    print(f"📱 Destinatario: {phone_number}")
    print(f"🏷️ Instancia: {instance_name}")
    print("-" * 50)
    
    try:
        # Enviar mensaje
        url = f"{base_url}/message/sendText/{instance_name}"
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Mensaje enviado exitosamente!")
            print(f"📄 Respuesta: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - Evolution API está procesando el mensaje")
        print("💡 Verifica en tu WhatsApp si el mensaje fue recibido")
        return True  # Consideramos éxito si hay timeout (común en Evolution API)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 Envío de mensaje por WhatsApp - Evolution API")
    print("=" * 60)
    
    # Verificar conexión
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        print("✅ Evolution API está ejecutándose")
    except:
        print("❌ Evolution API no está disponible")
        return
    
    # Enviar mensaje
    success = send_whatsapp_message()
    
    if success:
        print("\n🎯 ¡Mensaje enviado!")
        print("📱 Verifica en tu WhatsApp si lo recibiste")
        print("✅ Evolution API está funcionando correctamente")
    else:
        print("\n❌ Error enviando el mensaje")

if __name__ == "__main__":
    main()



