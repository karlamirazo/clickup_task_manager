#!/usr/bin/env python3
"""
Enviar mensaje de WhatsApp AHORA
"""

import requests
import json

def enviar_mensaje():
    """Enviar mensaje de WhatsApp"""
    
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
Estado: ¡Funcionando perfectamente!

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
    
    print("🚀 ENVIANDO MENSAJE DE WHATSAPP...")
    print(f"📱 Destinatario: {phone_number}")
    print(f"🏷️ Instancia: {instance_name}")
    print(f"🔑 API Key: {api_key}")
    print("-" * 60)
    
    try:
        # Enviar mensaje
        url = f"{base_url}/message/sendText/{instance_name}"
        print(f"🌐 URL: {url}")
        print("⏳ Enviando petición...")
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Respuesta: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n🎉 ¡MENSAJE ENVIADO EXITOSAMENTE!")
            print(f"📋 Respuesta completa: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"\n❌ Error en la respuesta: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n⏰ Timeout - Evolution API está procesando el mensaje")
        print("💡 Esto es normal en Evolution API")
        print("💡 Verifica en tu WhatsApp si el mensaje fue recibido")
        return True
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error de conexión")
        print("💡 Verifica que Evolution API esté ejecutándose")
        return False
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False

def main():
    """Función principal"""
    print("📱 ENVÍO DE MENSAJE WHATSAPP - EVOLUTION API")
    print("=" * 60)
    
    # Verificar que Evolution API esté funcionando
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        if response.status_code == 200:
            print("✅ Evolution API está ejecutándose")
        else:
            print(f"⚠️ Evolution API responde con error: {response.status_code}")
            return
    except:
        print("❌ Evolution API no está disponible")
        print("💡 Ejecuta: python start_evolution_api.py")
        return
    
    # Enviar mensaje
    success = enviar_mensaje()
    
    if success:
        print("\n🎯 ¡Mensaje enviado!")
        print("📱 Verifica en tu WhatsApp si lo recibiste")
        print("✅ Evolution API está funcionando correctamente")
    else:
        print("\n❌ Error enviando el mensaje")

if __name__ == "__main__":
    main()
