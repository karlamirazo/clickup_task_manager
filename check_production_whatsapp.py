#!/usr/bin/env python3
"""
Script para verificar el estado de WhatsApp en producción
"""

import requests
import json
from datetime import datetime

def check_production_whatsapp():
    """Verificar estado de WhatsApp en producción"""
    
    print("🔍 VERIFICANDO ESTADO DE WHATSAPP EN PRODUCCIÓN")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # 1. Verificar que la aplicación esté funcionando
    print("🌐 Verificando aplicación...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Aplicación funcionando correctamente")
        else:
            print(f"❌ Aplicación con problemas: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando a la aplicación: {e}")
        return False
    
    # 2. Verificar endpoint de configuración (si existe)
    print(f"\n📋 Verificando configuración...")
    try:
        response = requests.get(f"{base_url}/api/v1/config/", timeout=10)
        if response.status_code == 200:
            config = response.json()
            print("✅ Endpoint de configuración disponible")
            print(f"📋 Configuración: {json.dumps(config, indent=2)}")
        else:
            print(f"⚠️ Endpoint de configuración no disponible: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error accediendo configuración: {e}")
    
    # 3. Verificar endpoint de WhatsApp (si existe)
    print(f"\n📱 Verificando endpoint de WhatsApp...")
    try:
        response = requests.get(f"{base_url}/api/v1/whatsapp/status", timeout=10)
        if response.status_code == 200:
            whatsapp_status = response.json()
            print("✅ Endpoint de WhatsApp disponible")
            print(f"📱 Estado: {json.dumps(whatsapp_status, indent=2)}")
        else:
            print(f"⚠️ Endpoint de WhatsApp no disponible: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error accediendo estado de WhatsApp: {e}")
    
    # 4. Probar envío de mensaje de prueba
    print(f"\n🧪 Probando envío de mensaje...")
    try:
        test_data = {
            "phone_number": "525660576654",
            "message": f"🧪 Prueba desde producción - {datetime.now().strftime('%H:%M:%S')}",
            "message_type": "text",
            "notification_type": "test"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/whatsapp/send",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Mensaje enviado exitosamente")
            print(f"📊 Resultado: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error enviando mensaje: {response.status_code}")
            print(f"📋 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en prueba de envío: {e}")
    
    # 5. Verificar logs recientes (si hay endpoint)
    print(f"\n📋 Verificando logs...")
    try:
        response = requests.get(f"{base_url}/api/v1/logs", timeout=10)
        if response.status_code == 200:
            logs = response.json()
            print("✅ Logs disponibles")
            print(f"📋 Logs: {json.dumps(logs, indent=2)}")
        else:
            print(f"⚠️ Endpoint de logs no disponible: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error accediendo logs: {e}")
    
    print(f"\n🎯 DIAGNÓSTICO:")
    print(f"Si no recibiste notificación al crear la tarea, puede ser por:")
    print(f"1. Variables de entorno no configuradas en Railway")
    print(f"2. Evolution API no conectada o instancia desconectada")
    print(f"3. Número de teléfono no encontrado en la tarea")
    print(f"4. Webhook de ClickUp no configurado correctamente")
    
    return True

def main():
    """Función principal"""
    print("🔍 DIAGNÓSTICO DE WHATSAPP EN PRODUCCIÓN")
    print("=" * 60)
    
    success = check_production_whatsapp()
    
    print(f"\n{'='*60}")
    if success:
        print("✅ Diagnóstico completado")
    else:
        print("❌ Error en el diagnóstico")
    
    return success

if __name__ == "__main__":
    result = main()
    exit(0 if result else 1)
