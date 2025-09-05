#!/usr/bin/env python3
"""
Diagnosticar notificaciones de WhatsApp
"""

import requests
import json
import sys
import os

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings

def diagnose_whatsapp_notifications():
    """Diagnosticar notificaciones de WhatsApp"""
    
    print("🔍 DIAGNÓSTICO DE NOTIFICACIONES WHATSAPP")
    print("=" * 60)
    
    # 1. Verificar configuración local
    print("📋 CONFIGURACIÓN LOCAL:")
    print(f"   ✅ WhatsApp habilitado: {settings.WHATSAPP_ENABLED}")
    print(f"   ✅ Notificaciones habilitadas: {settings.WHATSAPP_NOTIFICATIONS_ENABLED}")
    print(f"   ✅ Tarea creada habilitada: {settings.WHATSAPP_TASK_CREATED}")
    print(f"   ✅ Simulador habilitado: {settings.WHATSAPP_SIMULATOR_ENABLED}")
    print(f"   🌐 URL Evolution API: {settings.WHATSAPP_EVOLUTION_URL}")
    print(f"   🔑 API Key: {settings.WHATSAPP_EVOLUTION_API_KEY}")
    print(f"   📱 Nombre instancia: {settings.WHATSAPP_INSTANCE_NAME}")
    print(f"   🔗 Webhook URL: {settings.WHATSAPP_WEBHOOK_URL}")
    
    # 2. Verificar configuración de Railway
    print(f"\n🚂 CONFIGURACIÓN DE RAILWAY:")
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        response = requests.get(
            f"{base_url}/api/v1/config/whatsapp",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            railway_config = response.json()
            print(f"   ✅ Configuración obtenida de Railway")
            print(f"   📋 Datos: {json.dumps(railway_config, indent=2)}")
        else:
            print(f"   ❌ Error obteniendo configuración: {response.status_code}")
            print(f"   📋 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error conectando con Railway: {e}")
    
    # 3. Verificar estado de Evolution API
    print(f"\n📱 ESTADO DE EVOLUTION API:")
    evolution_url = settings.WHATSAPP_EVOLUTION_URL
    
    try:
        # Verificar si la API está activa
        response = requests.get(f"{evolution_url}/", timeout=10)
        print(f"   ✅ Evolution API responde: {response.status_code}")
        
        # Verificar instancia específica
        instance_url = f"{evolution_url}/instance/connectionState/{settings.WHATSAPP_INSTANCE_NAME}"
        response = requests.get(
            instance_url,
            headers={"apikey": settings.WHATSAPP_EVOLUTION_API_KEY},
            timeout=10
        )
        
        if response.status_code == 200:
            instance_state = response.json()
            print(f"   ✅ Estado de instancia obtenido")
            print(f"   📋 Estado: {json.dumps(instance_state, indent=2)}")
        else:
            print(f"   ❌ Error obteniendo estado de instancia: {response.status_code}")
            print(f"   📋 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error conectando con Evolution API: {e}")
    
    # 4. Verificar logs de Railway
    print(f"\n📊 LOGS DE RAILWAY:")
    try:
        # Intentar obtener logs recientes
        response = requests.get(
            f"{base_url}/api/v1/logs/whatsapp",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            logs = response.json()
            print(f"   ✅ Logs obtenidos de Railway")
            print(f"   📋 Logs: {json.dumps(logs, indent=2)}")
        else:
            print(f"   ❌ Error obteniendo logs: {response.status_code}")
            print(f"   📋 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error obteniendo logs: {e}")
    
    # 5. Verificar tareas recientes
    print(f"\n📝 TAREAS RECIENTES:")
    try:
        response = requests.get(
            f"{base_url}/api/v1/tasks/",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            tasks = response.json()
            recent_tasks = [t for t in tasks if t.get('created_at')]
            recent_tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            print(f"   ✅ Tareas obtenidas: {len(tasks)}")
            print(f"   📋 Últimas 3 tareas:")
            
            for i, task in enumerate(recent_tasks[:3]):
                print(f"      {i+1}. {task.get('name', 'Sin nombre')}")
                print(f"         📱 ClickUp ID: {task.get('clickup_id', 'N/A')}")
                print(f"         📅 Creada: {task.get('created_at', 'N/A')}")
                print(f"         📝 Descripción: {task.get('description', 'Sin descripción')[:100]}...")
                print()
                
        else:
            print(f"   ❌ Error obteniendo tareas: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error obteniendo tareas: {e}")
    
    print(f"\n🔍 DIAGNÓSTICO COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    diagnose_whatsapp_notifications()

