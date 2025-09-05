#!/usr/bin/env python3
"""
Script para probar la creación de tareas en la API
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración
BASE_URL = "https://clickuptaskmanager-production.up.railway.app"
# BASE_URL = "http://localhost:8000"  # Para pruebas locales

def test_api_endpoints():
    """Probar endpoints básicos de la API"""
    print("🔍 Probando endpoints de la API...")
    
    # Probar endpoint de debug
    try:
        response = requests.get(f"{BASE_URL}/debug")
        print(f"✅ /debug: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📋 Configuración: {data.get('config_status', {})}")
            print(f"   🗄️ Base de datos: {data.get('db_status', 'N/A')}")
    except Exception as e:
        print(f"❌ /debug: Error - {e}")
    
    # Probar endpoint de workspaces
    try:
        response = requests.get(f"{BASE_URL}/api/v1/workspaces/")
        print(f"✅ /api/v1/workspaces/: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            workspaces = data.get('workspaces', [])
            print(f"   📋 Workspaces disponibles: {len(workspaces)}")
            for ws in workspaces[:3]:  # Mostrar solo los primeros 3
                print(f"      - {ws.get('name', 'N/A')} (ID: {ws.get('id', 'N/A')})")
    except Exception as e:
        print(f"❌ /api/v1/workspaces/: Error - {e}")
    
    # Probar endpoint de listas
    try:
        response = requests.get(f"{BASE_URL}/api/v1/lists/")
        print(f"✅ /api/v1/lists/: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            lists = data.get('lists', [])
            print(f"   📋 Listas disponibles: {len(lists)}")
            for lst in lists[:3]:  # Mostrar solo las primeras 3
                print(f"      - {lst.get('name', 'N/A')} (ID: {lst.get('id', 'N/A')})")
    except Exception as e:
        print(f"❌ /api/v1/lists/: Error - {e}")

def test_task_creation():
    """Probar la creación de una tarea"""
    print("\n🔄 Probando creación de tarea...")
    
    # Primero obtener workspaces y listas
    try:
        # Obtener primer workspace
        ws_response = requests.get(f"{BASE_URL}/api/v1/workspaces/")
        if ws_response.status_code != 200:
            print("❌ No se pudieron obtener workspaces")
            return
        
        workspaces = ws_response.json().get('workspaces', [])
        if not workspaces:
            print("❌ No hay workspaces disponibles")
            return
        
        workspace_id = workspaces[0]['id']
        print(f"✅ Usando workspace: {workspaces[0]['name']} (ID: {workspace_id})")
        
        # Obtener primera lista
        list_response = requests.get(f"{BASE_URL}/api/v1/lists/")
        if list_response.status_code != 200:
            print("❌ No se pudieron obtener listas")
            return
        
        lists = list_response.json().get('lists', [])
        if not lists:
            print("❌ No hay listas disponibles")
            return
        
        list_id = lists[0]['id']
        print(f"✅ Usando lista: {lists[0]['name']} (ID: {list_id})")
        
        # Crear tarea de prueba
        tomorrow = datetime.now() + timedelta(days=1)
        task_data = {
            "name": f"Tarea de prueba - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "description": "Esta es una tarea de prueba creada desde el script",
            "status": "to do",
            "priority": 3,
            "due_date": tomorrow.strftime("%Y-%m-%d"),
            "list_id": list_id,
            "workspace_id": workspace_id
        }
        
        print(f"📋 Datos de la tarea: {json.dumps(task_data, indent=2)}")
        
        # Enviar solicitud de creación
        response = requests.post(
            f"{BASE_URL}/api/v1/tasks/",
            headers={"Content-Type": "application/json"},
            json=task_data
        )
        
        print(f"📤 Respuesta del servidor: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ ¡Tarea creada exitosamente!")
            print(f"   📋 ID de la tarea: {result.get('id', 'N/A')}")
            print(f"   📋 ClickUp ID: {result.get('clickup_id', 'N/A')}")
            print(f"   📋 Nombre: {result.get('name', 'N/A')}")
        else:
            print(f"❌ Error creando tarea: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📋 Detalles del error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   📋 Respuesta del servidor: {response.text}")
                
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de la API de creación de tareas")
    print(f"📍 URL base: {BASE_URL}")
    print("=" * 60)
    
    # Probar endpoints básicos
    test_api_endpoints()
    
    # Probar creación de tareas
    test_task_creation()
    
    print("\n" + "=" * 60)
    print("🏁 Pruebas completadas")

if __name__ == "__main__":
    main()
