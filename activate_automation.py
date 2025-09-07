#!/usr/bin/env python3
"""
Script para activar el sistema de automatización de notificaciones
"""

import requests
import json
import time

def activate_automation():
    """Activa el sistema de automatización"""
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    print("🚀 ACTIVANDO SISTEMA DE AUTOMATIZACIÓN DE NOTIFICACIONES")
    print("=" * 60)
    
    # Intentar diferentes endpoints
    endpoints = [
        "/api/v1/automation/control/start",
        "/api/v1/automation/start", 
        "/api/v1/notifications/start",
        "/api/v1/whatsapp/automation/start"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"🔍 Probando endpoint: {endpoint}")
            response = requests.post(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Éxito con {endpoint}")
                print(f"📊 Respuesta: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"❌ Error {response.status_code} con {endpoint}")
                print(f"📄 Respuesta: {response.text}")
                
        except Exception as e:
            print(f"❌ Error con {endpoint}: {e}")
    
    print("\n🔧 MÉTODO ALTERNATIVO: Verificar configuración")
    
    # Verificar configuración actual
    try:
        response = requests.get(f"{base_url}/debug", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("📊 Configuración actual:")
            print(f"   - WhatsApp habilitado: {data.get('configuration', {}).get('WHATSAPP_ENABLED', 'No configurado')}")
            print(f"   - Base de datos: {data.get('database', {}).get('database_status', 'No configurado')}")
            print(f"   - ClickUp: {data.get('clickup_client', {}).get('client_status', 'No configurado')}")
    except Exception as e:
        print(f"❌ Error verificando configuración: {e}")
    
    return False

if __name__ == "__main__":
    success = activate_automation()
    
    if success:
        print("\n🎉 ¡Sistema de automatización activado!")
        print("📱 Las notificaciones de WhatsApp deberían funcionar ahora")
    else:
        print("\n⚠️ No se pudo activar automáticamente")
        print("💡 El sistema puede necesitar configuración manual")


