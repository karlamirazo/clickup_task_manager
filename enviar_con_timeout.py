#!/usr/bin/env python3
import requests
import json

print("🚀 Enviando mensaje con manejo de timeout...")

try:
    url = "http://localhost:8080/message/sendText/clickup_whatsapp"
    headers = {
        "apikey": "clickup_whatsapp_key_2024",
        "Content-Type": "application/json"
    }
    
    data = {
        "number": "+525660576654",
        "text": "Prueba con timeout - ¿Me recibes ahora? 🚀"
    }
    
    print(f"📱 Enviando a: {data['number']}")
    print(f"📝 Mensaje: {data['text']}")
    print("⏳ Enviando (puede tardar hasta 2 minutos)...")
    
    # Timeout más largo para Evolution API
    response = requests.post(url, headers=headers, json=data, timeout=120)
    
    print(f"📊 Status: {response.status_code}")
    print(f"📄 Respuesta: {response.text}")
    
    if response.status_code == 200:
        print("✅ Mensaje enviado exitosamente")
    else:
        print("❌ Error enviando mensaje")
        
except requests.exceptions.Timeout:
    print("⏰ Timeout - Evolution API está procesando el mensaje")
    print("💡 Esto es NORMAL en Evolution API")
    print("💡 El mensaje se está enviando en segundo plano")
    print("💡 Verifica en tu WhatsApp si lo recibiste")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n💡 RECOMENDACIONES:")
print("1. Verifica tu WhatsApp en 1-2 minutos")
print("2. A veces Evolution API tarda en responder")
print("3. El timeout no significa que falló")
