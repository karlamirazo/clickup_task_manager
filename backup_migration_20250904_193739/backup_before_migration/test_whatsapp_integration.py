#!/usr/bin/env python3
"""
Test de integración de WhatsApp
"""

import requests
import json

def test_whatsapp_integration():
    """Probar integración de WhatsApp"""
    
    print("🔍 TEST DE INTEGRACIÓN WHATSAPP")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # 1. Probar envío directo de notificación
    print("📱 TEST ENVÍO DIRECTO DE NOTIFICACIÓN:")
    try:
        notification_data = {
            "phone_numbers": ["+525660576654"],
            "task_title": "Test de WhatsApp",
            "task_description": "Esta es una prueba de notificación WhatsApp",
            "notification_type": "created"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/whatsapp/notify/task",
            json=notification_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Notificación enviada exitosamente")
            result = response.json()
            print(f"   📋 Respuesta: {json.dumps(result, indent=2)}")
        else:
            print(f"   ❌ Error enviando notificación")
            print(f"   📋 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error en la petición: {e}")
    
    # 2. Probar envío de mensaje de texto
    print(f"\n💬 TEST ENVÍO DE MENSAJE DE TEXTO:")
    try:
        message_data = {
            "phone_number": "+525660576654",
            "message": "🧪 Test de integración WhatsApp desde Railway"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/whatsapp/send/text",
            json=message_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Mensaje enviado exitosamente")
            result = response.json()
            print(f"   📋 Respuesta: {json.dumps(result, indent=2)}")
        else:
            print(f"   ❌ Error enviando mensaje")
            print(f"   📋 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error en la petición: {e}")
    
    # 3. Verificar estado de la instancia
    print(f"\n🔍 TEST ESTADO DE INSTANCIA:")
    try:
        response = requests.get(
            f"{base_url}/api/v1/whatsapp/instance/status",
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Estado de instancia obtenido")
            result = response.json()
            print(f"   📋 Respuesta: {json.dumps(result, indent=2)}")
        else:
            print(f"   ❌ Error obteniendo estado")
            print(f"   📋 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error en la petición: {e}")
    
    # 4. Verificar configuración de WhatsApp
    print(f"\n⚙️ TEST CONFIGURACIÓN WHATSAPP:")
    try:
        response = requests.get(
            f"{base_url}/api/v1/whatsapp/config",
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Configuración obtenida")
            result = response.json()
            print(f"   📋 Respuesta: {json.dumps(result, indent=2)}")
        else:
            print(f"   ❌ Error obteniendo configuración")
            print(f"   📋 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error en la petición: {e}")
    
    print(f"\n🔍 TEST COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    test_whatsapp_integration()

