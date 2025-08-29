#!/usr/bin/env python3
"""
Envío alternativo de mensajes de WhatsApp
"""

import requests
import json
import time

def enviar_mensaje_metodo_1():
    """Método 1: Envío estándar"""
    print("🔄 MÉTODO 1: Envío estándar")
    
    base_url = "http://localhost:8080"
    api_key = "clickup_whatsapp_key_2024"
    instance_name = "clickup_whatsapp"
    phone_number = "+525660576654"
    
    headers = {
        "Content-Type": "application/json",
        "apikey": api_key
    }
    
    data = {
        "number": phone_number,
        "text": "Mensaje de prueba - Método 1 🚀"
    }
    
    try:
        url = f"{base_url}/message/sendText/{instance_name}"
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Respuesta: {response.text}")
        
        if response.status_code == 200:
            print("✅ Método 1 exitoso")
            return True
        else:
            print("❌ Método 1 falló")
            return False
            
    except Exception as e:
        print(f"❌ Error método 1: {e}")
        return False

def enviar_mensaje_metodo_2():
    """Método 2: Con formato de número diferente"""
    print("\n🔄 MÉTODO 2: Formato de número alternativo")
    
    base_url = "http://localhost:8080"
    api_key = "clickup_whatsapp_key_2024"
    instance_name = "clickup_whatsapp"
    phone_number = "525660576654"  # Sin el +
    
    headers = {
        "Content-Type": "application/json",
        "apikey": api_key
    }
    
    data = {
        "number": phone_number,
        "text": "Mensaje de prueba - Método 2 🚀"
    }
    
    try:
        url = f"{base_url}/message/sendText/{instance_name}"
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Respuesta: {response.text}")
        
        if response.status_code == 200:
            print("✅ Método 2 exitoso")
            return True
        else:
            print("❌ Método 2 falló")
            return False
            
    except Exception as e:
        print(f"❌ Error método 2: {e}")
        return False

def enviar_mensaje_metodo_3():
    """Método 3: Con formato completo de WhatsApp"""
    print("\n🔄 MÉTODO 3: Formato completo de WhatsApp")
    
    base_url = "http://localhost:8080"
    api_key = "clickup_whatsapp_key_2024"
    instance_name = "clickup_whatsapp"
    phone_number = "5215660576654@s.whatsapp.net"  # Formato completo
    
    headers = {
        "Content-Type": "application/json",
        "apikey": api_key
    }
    
    data = {
        "number": phone_number,
        "text": "Mensaje de prueba - Método 3 🚀"
    }
    
    try:
        url = f"{base_url}/message/sendText/{instance_name}"
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Respuesta: {response.text}")
        
        if response.status_code == 200:
            print("✅ Método 3 exitoso")
            return True
        else:
            print("❌ Método 3 falló")
            return False
            
    except Exception as e:
        print(f"❌ Error método 3: {e}")
        return False

def verificar_mensajes_enviados():
    """Verificar si hay mensajes recientes"""
    print("\n🔍 Verificando mensajes recientes...")
    
    base_url = "http://localhost:8080"
    api_key = "clickup_whatsapp_key_2024"
    instance_name = "clickup_whatsapp"
    
    headers = {
        "apikey": api_key
    }
    
    try:
        # Intentar diferentes endpoints para mensajes
        endpoints = [
            f"/chat/findMessages/{instance_name}",
            f"/chat/findChats/{instance_name}",
            f"/message/findMessages/{instance_name}"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
                print(f"📡 Endpoint {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"📄 Datos: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except Exception as e:
                print(f"❌ Error en {endpoint}: {e}")
                
    except Exception as e:
        print(f"❌ Error verificando mensajes: {e}")

def main():
    """Función principal"""
    print("📱 ENVÍO ALTERNATIVO DE MENSAJES WHATSAPP")
    print("=" * 60)
    
    # Verificar que Evolution API esté funcionando
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        if response.status_code == 200:
            print("✅ Evolution API está ejecutándose")
        else:
            print(f"❌ Evolution API no está disponible: {response.status_code}")
            return
    except:
        print("❌ Evolution API no está disponible")
        return
    
    # Probar diferentes métodos
    print("\n🧪 Probando diferentes métodos de envío...")
    
    metodo1_ok = enviar_mensaje_metodo_1()
    time.sleep(2)  # Esperar entre envíos
    
    metodo2_ok = enviar_mensaje_metodo_2()
    time.sleep(2)
    
    metodo3_ok = enviar_mensaje_metodo_3()
    time.sleep(2)
    
    # Verificar mensajes
    verificar_mensajes_enviados()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE MÉTODOS:")
    print(f"Método 1: {'✅ Exitoso' if metodo1_ok else '❌ Falló'}")
    print(f"Método 2: {'✅ Exitoso' if metodo2_ok else '❌ Falló'}")
    print(f"Método 3: {'✅ Exitoso' if metodo3_ok else '❌ Falló'}")
    
    if any([metodo1_ok, metodo2_ok, metodo3_ok]):
        print("\n🎯 ¡Al menos un método funcionó!")
        print("📱 Verifica en tu WhatsApp si recibiste algún mensaje")
    else:
        print("\n❌ Ningún método funcionó")
        print("💡 Puede haber un problema con la configuración")

if __name__ == "__main__":
    main()
