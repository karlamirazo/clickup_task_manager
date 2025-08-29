#!/usr/bin/env python3
import requests
import json

print("🚀 Enviando mensaje simple...")

try:
    url = "http://localhost:8080/message/sendText/clickup_whatsapp"
    headers = {
        "apikey": "clickup_whatsapp_key_2024",
        "Content-Type": "application/json"
    }
    
    data = {
        "number": "+525660576654",
        "text": "Prueba simple - ¿Me recibes? 🚀"
    }
    
    print(f"📱 Enviando a: {data['number']}")
    print(f"📝 Mensaje: {data['text']}")
    
    response = requests.post(url, headers=headers, json=data, timeout=30)
    
    print(f"📊 Status: {response.status_code}")
    print(f"📄 Respuesta: {response.text}")
    
    if response.status_code == 200:
        print("✅ Mensaje enviado exitosamente")
    else:
        print("❌ Error enviando mensaje")
        
except Exception as e:
    print(f"❌ Error: {e}")
