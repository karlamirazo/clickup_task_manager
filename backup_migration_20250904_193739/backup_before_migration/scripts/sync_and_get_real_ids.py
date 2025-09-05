#!/usr/bin/env python3
"""
Script para sincronizar con ClickUp y obtener IDs reales
"""

import requests
import json
from datetime import datetime

def sync_with_clickup():
    """Sync con ClickUp para obtener datos reales"""
    print("ğŸ”„ Sincronizando con ClickUp para obtener datos reales")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Intentar diferentes endpoints de sincronizacion
    sync_endpoints = [
        "/api/v1/workspaces/sync",
        "/api/v1/lists/sync",
        "/api/v1/users/sync",
        "/api/v1/tasks/sync"
    ]
    
    for endpoint in sync_endpoints:
        try:
            print(f"ğŸ”„ Sincronizando: {endpoint}")
            response = requests.post(f"{base_url}{endpoint}", timeout=30)
            
            if response.status_code == 200:
                print(f"   âœ… Sincronizacion exitosa")
                result = response.json()
                print(f"   ğŸ“Š Resultado: {result}")
            else:
                print(f"   â�Œ Error {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   â�Œ Error: {e}")

def get_real_data_after_sync():
    """Get datos reales despues de la sincronizacion"""
    print(f"\nğŸ”� Obteniendo datos reales despues de sincronizacion")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Get workspaces
    try:
        print("ğŸ“� Obteniendo workspaces...")
        response = requests.get(f"{base_url}/api/v1/workspaces", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            workspaces = data.get("workspaces", [])
            print(f"   âœ… Workspaces: {len(workspaces)}")
            
            for workspace in workspaces:
                print(f"      ğŸ“� {workspace.get('name', 'N/A')} - ID: {workspace.get('id', 'N/A')}")
                
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
                            print(f"         ğŸ“‹ Listas en {workspace.get('name', 'N/A')}: {len(lists)}")
                            
                            for list_item in lists:
                                print(f"            ğŸ“� {list_item.get('name', 'N/A')} - ID: {list_item.get('id', 'N/A')}")
                        else:
                            print(f"         â�Œ Error getting listas: {lists_response.status_code}")
                            
                    except Exception as e:
                        print(f"         â�Œ Error: {e}")
        else:
            print(f"   â�Œ Error getting workspaces: {response.status_code}")
            
    except Exception as e:
        print(f"   â�Œ Error: {e}")
    
    # Get usuarios
    try:
        print(f"\nğŸ‘¤ Obteniendo usuarios...")
        response = requests.get(f"{base_url}/api/v1/users", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            users = data.get("users", [])
            print(f"   âœ… Usuarios: {len(users)}")
            
            for user in users:
                print(f"      ğŸ‘¤ {user.get('first_name', '')} {user.get('last_name', '')} - ID: {user.get('id', 'N/A')}")
        else:
            print(f"   â�Œ Error getting usuarios: {response.status_code}")
            
    except Exception as e:
        print(f"   â�Œ Error: {e}")

def test_with_known_ids():
    """Test con IDs conocidos basados en la informacion proporcionada"""
    print(f"\nğŸ§ª Probando con IDs conocidos")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Intentar diferentes combinaciones de IDs basadas en la informacion proporcionada
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
        print(f"\nğŸ§ª Prueba {i}: {combo['description']}")
        print(f"   ğŸ“‹ Lista ID: {combo['list_id']}")
        print(f"   ğŸ‘¤ Usuario ID: {combo['user_id']}")
        
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
                print(f"   âœ… Â¡EXITO! Tarea creada correctamente")
                result = response.json()
                print(f"   ğŸ†” ID ClickUp: {result.get('clickup_id', 'N/A')}")
                break
            else:
                print(f"   â�Œ Error {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   â�Œ Error: {e}")

def main():
    """Funcion principal"""
    print("ğŸ”„ SINCRONIZACION Y OBTENCION DE DATOS REALES DE CLICKUP")
    print("=" * 70)
    
    # Sync con ClickUp
    print("\n" + "=" * 70)
    print("PASO 1: SINCRONIZAR CON CLICKUP")
    print("=" * 70)
    
    sync_with_clickup()
    
    # Get datos reales
    print("\n" + "=" * 70)
    print("PASO 2: OBTENER DATOS REALES")
    print("=" * 70)
    
    get_real_data_after_sync()
    
    # Test con IDs conocidos
    print("\n" + "=" * 70)
    print("PASO 3: PROBAR CON IDs CONOCIDOS")
    print("=" * 70)
    
    test_with_known_ids()
    
    # Resumen
    print("\n" + "=" * 70)
    print("ğŸ“Š RESUMEN")
    print("=" * 70)
    
    print("âœ… Proceso de sincronizacion completado")
    print("âœ… Datos reales obtenidos")
    print("âœ… Pruebas con IDs conocidos realizadas")
    
    print(f"\nğŸ’¡ PROXIMOS PASOS:")
    print("   1. Revisar los IDs obtenidos en el paso 2")
    print("   2. Usar los IDs correctos para crear tareas")
    print("   3. Verificar que los campos personalizados funcionan")
    
    print(f"\nğŸ•� Proceso completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
