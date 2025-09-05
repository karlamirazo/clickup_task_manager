#!/usr/bin/env python3
"""
Script para probar directamente si el token de ClickUp funciona
"""

import requests
import json

# Configuración
BASE_URL = "https://clickuptaskmanager-production.up.railway.app"

def test_clickup_token_directly():
    """Probar el token de ClickUp directamente"""
    print("🔍 Probando token de ClickUp directamente...")
    
    try:
        # Obtener información del usuario desde ClickUp
        print("📤 Probando endpoint /api/v1/users/...")
        response = requests.get(f"{BASE_URL}/api/v1/users/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Usuarios obtenidos: {response.status_code}")
            print(f"   📋 Respuesta: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error obteniendo usuarios: {response.status_code}")
            print(f"   📋 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_clickup_workspace_access():
    """Probar acceso a workspaces de ClickUp"""
    print("\n🔍 Probando acceso a workspaces de ClickUp...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/workspaces/")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Workspaces obtenidos: {response.status_code}")
            
            if isinstance(data, dict) and 'workspaces' in data:
                workspaces = data['workspaces']
                print(f"   📋 Número de workspaces: {len(workspaces)}")
                
                for ws in workspaces:
                    print(f"      - {ws.get('name', 'N/A')} (ID: {ws.get('id', 'N/A')})")
                    
                    # Probar acceso a listas del workspace
                    workspace_id = ws.get('id')
                    if workspace_id:
                        print(f"         🔍 Probando acceso a listas del workspace {workspace_id}...")
                        
                        list_response = requests.get(f"{BASE_URL}/api/v1/lists/?workspace_id={workspace_id}")
                        if list_response.status_code == 200:
                            list_data = list_response.json()
                            lists = list_data.get('lists', [])
                            print(f"         ✅ Listas obtenidas: {len(lists)}")
                            
                            for lst in lists[:3]:  # Solo las primeras 3
                                print(f"            - {lst.get('name', 'N/A')} (ID: {lst.get('id', 'N/A')})")
                        else:
                            print(f"         ❌ Error obteniendo listas: {list_response.status_code}")
                            print(f"            📋 Respuesta: {list_response.text}")
            else:
                print(f"   📋 Formato de respuesta inesperado: {type(data)}")
                print(f"   📋 Contenido: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error obteniendo workspaces: {response.status_code}")
            print(f"   📋 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_clickup_task_creation_error():
    """Probar si hay errores en la creación de tareas"""
    print("\n🔍 Probando creación de tarea para detectar errores...")
    
    try:
        # Obtener workspace y lista
        ws_response = requests.get(f"{BASE_URL}/api/v1/workspaces/")
        if ws_response.status_code == 200:
            ws_data = ws_response.json()
            if isinstance(ws_data, dict) and 'workspaces' in ws_data:
                workspace_id = ws_data['workspaces'][0]['id']
                
                list_response = requests.get(f"{BASE_URL}/api/v1/lists/?workspace_id={workspace_id}")
                if list_response.status_code == 200:
                    list_data = list_response.json()
                    if isinstance(list_data, dict) and 'lists' in list_data:
                        list_id = list_data['lists'][0]['id']
                        
                        # Intentar crear una tarea de prueba
                        task_data = {
                            "name": "Tarea de prueba de token",
                            "description": "Verificar si el token funciona",
                            "status": "to do",
                            "priority": 3,
                            "list_id": list_id,
                            "workspace_id": workspace_id
                        }
                        
                        print(f"📤 Enviando tarea de prueba...")
                        print(f"   📋 Datos: {json.dumps(task_data, indent=2)}")
                        
                        response = requests.post(
                            f"{BASE_URL}/api/v1/tasks/",
                            headers={"Content-Type": "application/json"},
                            json=task_data
                        )
                        
                        print(f"📊 Respuesta: {response.status_code}")
                        
                        if response.status_code == 201:
                            result = response.json()
                            print(f"✅ Tarea creada:")
                            print(f"   📋 ID local: {result.get('id')}")
                            print(f"   📋 ClickUp ID: {result.get('clickup_id')}")
                            print(f"   📋 Sincronizada: {result.get('is_synced')}")
                            
                            # Verificar si realmente se sincronizó
                            if result.get('clickup_id'):
                                print(f"   🔍 Verificando si aparece en ClickUp...")
                                print(f"   💡 Ve a ClickUp y busca la tarea: {result.get('name')}")
                                print(f"   💡 Con ID: {result.get('clickup_id')}")
                        else:
                            print(f"❌ Error creando tarea:")
                            try:
                                error_data = response.json()
                                print(f"   📋 Detalles: {json.dumps(error_data, indent=2)}")
                            except:
                                print(f"   📋 Respuesta: {response.text}")
                    else:
                        print("❌ No se pudieron obtener listas")
                else:
                    print(f"❌ Error obteniendo listas: {list_response.status_code}")
            else:
                print("❌ No se pudieron obtener workspaces")
        else:
            print(f"❌ Error obteniendo workspaces: {ws_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando prueba directa del token de ClickUp")
    print(f"📍 URL base: {BASE_URL}")
    print("=" * 70)
    
    # 1. Probar token directamente
    test_clickup_token_directly()
    
    # 2. Probar acceso a workspaces
    test_clickup_workspace_access()
    
    # 3. Probar creación de tarea para detectar errores
    test_clickup_task_creation_error()
    
    print("\n" + "=" * 70)
    print("🏁 Prueba completada")
    
    print("\n💡 INSTRUCCIONES:")
    print("   1. Ve a ClickUp y busca la tarea 'Tarea de prueba de token'")
    print("   2. Si NO la encuentras, el token tiene problemas")
    print("   3. Si la encuentras, el problema está en otro lugar")

if __name__ == "__main__":
    main()
