#!/usr/bin/env python3
"""
Verificar configuración real de WhatsApp en Railway
"""

import requests
import json

def check_railway_whatsapp_config():
    """Verificar configuración real de WhatsApp en Railway"""
    
    print("🔍 VERIFICANDO CONFIGURACIÓN REAL DE WHATSAPP EN RAILWAY")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # 1. Verificar endpoint de configuración
    print("📋 ENDPOINT DE CONFIGURACIÓN:")
    try:
        response = requests.get(
            f"{base_url}/api/v1/config/",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            config = response.json()
            print(f"   ✅ Configuración obtenida")
            print(f"   📋 Datos: {json.dumps(config, indent=2)}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📋 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Verificar variables de entorno
    print(f"\n🔧 VARIABLES DE ENTORNO:")
    try:
        response = requests.get(
            f"{base_url}/api/v1/env/whatsapp",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            env_vars = response.json()
            print(f"   ✅ Variables obtenidas")
            print(f"   📋 Datos: {json.dumps(env_vars, indent=2)}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📋 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Verificar estado de WhatsApp
    print(f"\n📱 ESTADO DE WHATSAPP:")
    try:
        response = requests.get(
            f"{base_url}/api/v1/whatsapp/status",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ Estado obtenido")
            print(f"   📋 Datos: {json.dumps(status, indent=2)}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📋 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Verificar logs de WhatsApp
    print(f"\n📊 LOGS DE WHATSAPP:")
    try:
        response = requests.get(
            f"{base_url}/api/v1/whatsapp/logs",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            logs = response.json()
            print(f"   ✅ Logs obtenidos")
            print(f"   📋 Datos: {json.dumps(logs, indent=2)}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📋 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 5. Verificar endpoints disponibles
    print(f"\n🔗 ENDPOINTS DISPONIBLES:")
    try:
        response = requests.get(
            f"{base_url}/docs",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"   ✅ Documentación disponible")
            print(f"   📋 URL: {base_url}/docs")
        else:
            print(f"   ❌ Documentación no disponible: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n🔍 VERIFICACIÓN COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    check_railway_whatsapp_config()

