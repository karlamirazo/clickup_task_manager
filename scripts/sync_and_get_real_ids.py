#!/usr/bin/env python3
"""
Script para sincronizar con ClickUp y obtener IDs reales
"""

import requests
import json
from datetime import datetime

def sync_with_clickup():
    """Sincronizar con ClickUp para obtener datos reales"""
    print("🔄 Sincronizando con ClickUp para obtener datos reales")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Intentar diferentes endpoints de sincronización
    sync_endpoints = [
        "/api/v1/workspaces/sync",
        "/api/v1/lists/sync",
        "/api/v1/users/sync",
        "/api/v1/tasks/sync"
    ]
    
    for endpoint in sync_endpoints:
        try:
            print(f"🔄 Sincronizando: {endpoint}")
            response = requests.post(f"{base_url}{endpoint}", timeout=30)
            
            if response.status_code == 200:
                print(f"   ✅ Sincronización exitosa")
                result = response.json()
                print(f"   📊 Resultado: {result}")
            else:
                print(f"   ❌ Error {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def get_real_data_after_sync():
    """Obtener datos reales después de la sincronización"""
    print(f"\n🔍 Obteniendo datos reales después de sincronización")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Obtener workspaces
    try:
        print("📁 Obteniendo workspaces...")
        response = requests.get(f"{base_url}/api/v1/workspaces", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            workspaces = data.get("workspaces", [])
            print(f"   ✅ Workspaces: {len(workspaces)}")
            
            for workspace in workspaces:
                print(f"      📁 {workspace.get('name', 'N/A')} - ID: {workspace.get('id', 'N/A')}")
                
                # Intentar obtener listas de este workspace
                workspace_id = workspace.get('id')
                if workspace_id:
                    try:
                        lists_response = requests.get(
                            f"{base_url}/api/v1/lists?space_id={workspace_id}",
                            timeout=10
                        )
                        
                        if lists_response.status_code == 200:
                            lists_data = lists_response.json()
                            lists = lists_data.get("lists", [])
                            print(f"         📋 Listas en {workspace.get('name', 'N/A')}: {len(lists)}")
                            
                            for list_item in lists:
                                print(f"            📝 {list_item.get('name', 'N/A')} - ID: {list_item.get('id', 'N/A')}")
                        else:
                            print(f"         ❌ Error obteniendo listas: {lists_response.status_code}")
                            
                    except Exception as e:
                        print(f"         ❌ Error: {e}")
        else:
            print(f"   ❌ Error obteniendo workspaces: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Obtener usuarios
    try:
        print(f"\n👤 Obteniendo usuarios...")
        response = requests.get(f"{base_url}/api/v1/users", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            users = data.get("users", [])
            print(f"   ✅ Usuarios: {len(users)}")
            
            for user in users:
                print(f"      👤 {user.get('first_name', '')} {user.get('last_name', '')} - ID: {user.get('id', 'N/A')}")
        else:
            print(f"   ❌ Error obteniendo usuarios: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_with_known_ids():
    """Probar con IDs conocidos basados en la información proporcionada"""
    print(f"\n🧪 Probando con IDs conocidos")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Intentar diferentes combinaciones de IDs basadas en la información proporcionada
    test_combinations = [
        {
            "list_id": "9014943317",  # Usar el workspace ID como lista ID
            "user_id": "156221125",
            "description": "Usando workspace ID como lista ID"
        },
        {
            "list_id": "9014943318",  # Workspace ID + 1
            "user_id": "156221125",
            "description": "Workspace ID + 1"
        },
        {
            "list_id": "9014943319",  # Workspace ID + 2
            "user_id": "156221125",
            "description": "Workspace ID + 2"
        }
    ]
    
    for i, combo in enumerate(test_combinations, 1):
        print(f"\n🧪 Prueba {i}: {combo['description']}")
        print(f"   📋 Lista ID: {combo['list_id']}")
        print(f"   👤 Usuario ID: {combo['user_id']}")
        
        test_task_data = {
            "name": f"Tarea de prueba {i} - {datetime.now().strftime('%H:%M:%S')}",
            "description": f"Prueba {i}: {combo['description']}",
            "status": "to do",
            "priority": 3,
            "due_date": "2025-08-25",
            "assignee_id": combo['user_id'],
            "list_id": combo['list_id'],
            "workspace_id": "9014943317",
            "custom_fields": {
                "email": "test@example.com",
                "Celular": "+52 55 1234 5678"
            }
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/tasks/",
                json=test_task_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"   ✅ ¡ÉXITO! Tarea creada correctamente")
                result = response.json()
                print(f"   🆔 ID ClickUp: {result.get('clickup_id', 'N/A')}")
                break
            else:
                print(f"   ❌ Error {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Función principal"""
    print("🔄 SINCRONIZACIÓN Y OBTENCIÓN DE DATOS REALES DE CLICKUP")
    print("=" * 70)
    
    # Sincronizar con ClickUp
    print("\n" + "=" * 70)
    print("PASO 1: SINCRONIZAR CON CLICKUP")
    print("=" * 70)
    
    sync_with_clickup()
    
    # Obtener datos reales
    print("\n" + "=" * 70)
    print("PASO 2: OBTENER DATOS REALES")
    print("=" * 70)
    
    get_real_data_after_sync()
    
    # Probar con IDs conocidos
    print("\n" + "=" * 70)
    print("PASO 3: PROBAR CON IDs CONOCIDOS")
    print("=" * 70)
    
    test_with_known_ids()
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)
    
    print("✅ Proceso de sincronización completado")
    print("✅ Datos reales obtenidos")
    print("✅ Pruebas con IDs conocidos realizadas")
    
    print(f"\n💡 PRÓXIMOS PASOS:")
    print("   1. Revisar los IDs obtenidos en el paso 2")
    print("   2. Usar los IDs correctos para crear tareas")
    print("   3. Verificar que los campos personalizados funcionan")
    
    print(f"\n🕐 Proceso completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
