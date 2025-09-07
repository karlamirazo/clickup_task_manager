#!/usr/bin/env python3
"""
Script para probar la creación de tarea con número de teléfono
"""

import requests
import json
from datetime import datetime, timedelta

def test_task_creation_with_phone():
    """Probar creación de tarea con número de teléfono"""
    
    print("🧪 PROBANDO CREACIÓN DE TAREA CON NÚMERO DE TELÉFONO")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Datos de la tarea de prueba
    task_data = {
        "name": f"🧪 Prueba WhatsApp - {datetime.now().strftime('%H:%M:%S')}",
        "description": f"""
        Esta es una tarea de prueba para verificar las notificaciones de WhatsApp.
        
        📱 Número de contacto: +525660576654
        📞 Teléfono: 525660576654
        WhatsApp: +525660576654
        
        Si recibes esta notificación, significa que el sistema está funcionando correctamente.
        """,
        "priority": 2,  # 1=low, 2=medium, 3=high
        "status": "pending",
        "due_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "assignee_id": "156221125",  # Tu ID de usuario
        "list_id": "901",  # Lista de prueba
        "workspace_id": "156221125",  # Tu workspace
        "custom_fields": {
            "Número de Celular": "+525660576654",
            "WhatsApp": "525660576654",
            "Teléfono": "+525660576654"
        }
    }
    
    print("📋 Datos de la tarea:")
    print(f"   📝 Nombre: {task_data['name']}")
    print(f"   📱 Números incluidos: +525660576654")
    print(f"   👤 Asignado a: {task_data['assignee_id']}")
    print(f"   📅 Fecha límite: {task_data['due_date']}")
    
    print(f"\n🚀 Enviando tarea a la API...")
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/tasks/",
            json=task_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Tarea creada exitosamente")
            print(f"   🆔 ID: {result.get('id', 'N/A')}")
            print(f"   📋 ClickUp ID: {result.get('clickup_id', 'N/A')}")
            print(f"   📝 Nombre: {result.get('name', 'N/A')}")
            
            print(f"\n📱 NOTIFICACIÓN WHATSAPP:")
            print(f"   Si el sistema está funcionando correctamente,")
            print(f"   deberías recibir una notificación en WhatsApp")
            print(f"   al número +525660576654")
            
            return True
            
        else:
            print(f"❌ Error creando tarea: {response.status_code}")
            print(f"📋 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 PRUEBA DE CREACIÓN DE TAREA CON WHATSAPP")
    print("=" * 60)
    
    success = test_task_creation_with_phone()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 ¡Prueba completada!")
        print("📱 Revisa tu WhatsApp para ver si llegó la notificación")
        print("🔧 Si llegó, el sistema está funcionando correctamente")
    else:
        print("❌ La prueba falló")
        print("🔍 Revisar logs y configuraciones")
    
    return success

if __name__ == "__main__":
    result = main()
    exit(0 if result else 1)
