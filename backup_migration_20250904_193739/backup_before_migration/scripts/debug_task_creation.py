#!/usr/bin/env python3
"""
Script para diagnosticar la creación de tareas en ClickUp
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración
BASE_URL = "https://clickuptaskmanager-production.up.railway.app"

def test_clickup_connection():
    """Probar la conexión con ClickUp"""
    print("🔍 Probando conexión con ClickUp...")
    
    try:
        # Probar endpoint de debug para ver el token
        response = requests.get(f"{BASE_URL}/debug")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Debug endpoint: {response.status_code}")
            print(f"   📋 Configuración: {data.get('configuration', {})}")
            
            # Verificar si hay token de ClickUp (manejar codificación de caracteres)
            config = data.get('configuration', {})
            clickup_token_status = config.get('CLICKUP_API_TOKEN', '')
            
            # Verificar si contiene "Configured" (ignorar caracteres extraños)
            if 'Configured' in clickup_token_status:
                print("   ✅ Token de ClickUp configurado")
                return True
            else:
                print(f"   ❌ Token de ClickUp NO configurado: {clickup_token_status}")
                return False
        else:
            print(f"❌ Debug endpoint: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en debug endpoint: {e}")
        return False
    
    return True

def test_workspace_and_lists():
    """Probar obtención de workspaces y listas"""
    print("\n🔍 Probando obtención de workspaces y listas...")
    
    try:
        # Obtener workspaces
        response = requests.get(f"{BASE_URL}/api/v1/workspaces/")
        if response.status_code == 200:
            data = response.json()
            workspaces = data.get('workspaces', [])
            print(f"✅ Workspaces: {len(workspaces)} encontrados")
            
            if workspaces:
                workspace = workspaces[0]
                workspace_id = workspace['id']
                print(f"   📋 Usando workspace: {workspace['name']} (ID: {workspace_id})")
                
                # Obtener listas del workspace
                list_response = requests.get(f"{BASE_URL}/api/v1/lists/?workspace_id={workspace_id}")
                if list_response.status_code == 200:
                    list_data = list_response.json()
                    lists = list_data.get('lists', [])
                    print(f"✅ Listas: {len(lists)} encontradas")
                    
                    if lists:
                        list_item = lists[0]
                        print(f"   📋 Usando lista: {list_item['name']} (ID: {list_item['id']})")
                        return workspace_id, list_item['id']
                    else:
                        print("   ❌ No hay listas disponibles")
                        return None, None
                else:
                    print(f"   ❌ Error obteniendo listas: {list_response.status_code}")
                    return None, None
            else:
                print("   ❌ No hay workspaces disponibles")
                return None, None
        else:
            print(f"❌ Error obteniendo workspaces: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def test_task_creation_with_debug(workspace_id, list_id):
    """Probar creación de tarea con logging detallado"""
    print(f"\n🔄 Probando creación de tarea...")
    print(f"   📋 Workspace ID: {workspace_id}")
    print(f"   📋 List ID: {list_id}")
    
    if not workspace_id or not list_id:
        print("❌ No se pueden crear tareas sin workspace_id y list_id")
        return
    
    try:
        # Crear tarea de prueba
        tomorrow = datetime.now() + timedelta(days=1)
        task_data = {
            "name": f"Tarea de prueba - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "description": "Esta es una tarea de prueba para diagnosticar la sincronización",
            "status": "to do",
            "priority": 3,
            "due_date": tomorrow.strftime("%Y-%m-%d"),
            "list_id": list_id,
            "workspace_id": workspace_id
        }
        
        print(f"📋 Datos de la tarea:")
        print(f"   {json.dumps(task_data, indent=2)}")
        
        # Enviar solicitud de creación
        print(f"\n📤 Enviando solicitud POST a /api/v1/tasks/...")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/tasks/",
            headers={"Content-Type": "application/json"},
            json=task_data
        )
        
        print(f"📊 Respuesta del servidor:")
        print(f"   📋 Status Code: {response.status_code}")
        print(f"   📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ ¡Tarea creada exitosamente!")
            print(f"   📋 Respuesta completa: {json.dumps(result, indent=2)}")
            
            # Verificar si tiene clickup_id
            if result.get('clickup_id'):
                print(f"   ✅ ClickUp ID: {result['clickup_id']} - Sincronización exitosa!")
            else:
                print(f"   ⚠️ No hay ClickUp ID - Solo se creó localmente")
                
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
    print("🚀 Iniciando diagnóstico de creación de tareas")
    print(f"📍 URL base: {BASE_URL}")
    print("=" * 70)
    
    # 1. Probar conexión con ClickUp
    if not test_clickup_connection():
        print("❌ No se puede continuar sin conexión a ClickUp")
        return
    
    # 2. Probar obtención de workspaces y listas
    workspace_id, list_id = test_workspace_and_lists()
    
    # 3. Probar creación de tarea
    test_task_creation_with_debug(workspace_id, list_id)
    
    print("\n" + "=" * 70)
    print("🏁 Diagnóstico completado")

if __name__ == "__main__":
    main()
