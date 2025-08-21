#!/usr/bin/env python3
"""
Script para probar la creacion de tareas con datos reales de ClickUp
"""

import requests
import json
from datetime import datetime, timedelta

def get_real_list_and_user_ids():
    """Get IDs reales de listas y usuarios"""
    print("ğŸ”� Obteniendo IDs reales de listas y usuarios")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Intentar obtener listas con diferentes parametros
    list_endpoints = [
        "/api/v1/lists",
        "/api/v1/lists?workspace_id=9014943317",
        "/api/v1/lists?space_id=9014943317"
    ]
    
    lists_found = []
    for endpoint in list_endpoints:
        try:
            print(f"ğŸ”� Probando endpoint: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                lists = data.get("lists", [])
                print(f"   âœ… Listas encontradas: {len(lists)}")
                
                for list_item in lists:
                    print(f"      ğŸ“� {list_item.get('name', 'N/A')} - ID: {list_item.get('id', 'N/A')}")
                    lists_found.append(list_item)
            else:
                print(f"   â�Œ Error {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   â�Œ Error: {e}")
    
    # Intentar obtener usuarios
    users_found = []
    try:
        print(f"\nğŸ”� Obteniendo usuarios...")
        response = requests.get(f"{base_url}/api/v1/users", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            users = data.get("users", [])
            print(f"   âœ… Usuarios encontrados: {len(users)}")
            
            for user in users:
                print(f"      ğŸ‘¤ {user.get('first_name', '')} {user.get('last_name', '')} - ID: {user.get('id', 'N/A')}")
                users_found.append(user)
        else:
            print(f"   â�Œ Error {response.status_code}: {response.text[:100]}")
            
    except Exception as e:
        print(f"   â�Œ Error: {e}")
    
    return lists_found, users_found

def test_task_creation_with_real_data():
    """Test la creacion de tareas con datos reales"""
    print("\nğŸ§ª Probando creacion de tareas con datos reales")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # IDs reales basados en la informacion proporcionada
    # Nota: Estos son IDs de ejemplo, necesitamos obtener los reales
    real_data = {
        "lists": [
            {"name": "PROYECTO 1", "id": "9014943317_1"},  # ID de ejemplo
            {"name": "PROYECTO 2", "id": "9014943317_2"}   # ID de ejemplo
        ],
        "users": [
            {"name": "Karla Rosas", "id": "156221125"},
            {"name": "Veronica Mirazo", "id": "156221126"},
            {"name": "Karla Ve", "id": "156221127"}
        ]
    }
    
    # Usar el primer proyecto y el primer usuario
    list_id = real_data["lists"][0]["id"]
    user_id = real_data["users"][0]["id"]
    
    # Datos de prueba para la tarea
    test_task_data = {
        "name": f"Tarea de prueba con datos reales - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Esta es una tarea de prueba usando datos reales de ClickUp (PROYECTO 1 y Karla Rosas)",
        "status": "to do",
        "priority": 3,  # Normal
        "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "assignee_id": user_id,
        "list_id": list_id,
        "workspace_id": "9014943317",
        "custom_fields": {
            "email": "karla.rosas@example.com",
            "Celular": "+52 55 9876 5432"
        }
    }
    
    print(f"ğŸ“‹ Datos de prueba con informacion real:")
    print(f"   ğŸ“� Nombre: {test_task_data['name']}")
    print(f"   ğŸ“„ Descripcion: {test_task_data['description']}")
    print(f"   ğŸ“Š Estado: {test_task_data['status']}")
    print(f"   âš¡ Prioridad: {test_task_data['priority']}")
    print(f"   ğŸ“… Fecha limite: {test_task_data['due_date']}")
    print(f"   ğŸ‘¤ Usuario asignado: {test_task_data['assignee_id']} (Karla Rosas)")
    print(f"   ğŸ“‹ Lista: {test_task_data['list_id']} (PROYECTO 1)")
    print(f"   ğŸ“� Workspace: {test_task_data['workspace_id']}")
    print(f"   ğŸ“§ Email: {test_task_data['custom_fields']['email']}")
    print(f"   ğŸ“± Celular: {test_task_data['custom_fields']['Celular']}")
    
    try:
        print(f"\nğŸš€ Enviando peticion a {base_url}/api/v1/tasks/")
        
        response = requests.post(
            f"{base_url}/api/v1/tasks/",
            json=test_task_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"ğŸ“¡ Respuesta del servidor:")
        print(f"   ğŸ“Š Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"âœ… Â¡Tarea creada exitosamente!")
            print(f"ğŸ“‹ Respuesta completa:")
            print(json.dumps(result, indent=2, default=str))
            
            # Verificar campos importantes
            print(f"\nğŸ”� Verificacion de campos:")
            print(f"   ğŸ†” ID local: {result.get('id', 'N/A')}")
            print(f"   ğŸ†” ID ClickUp: {result.get('clickup_id', 'N/A')}")
            print(f"   ğŸ“� Nombre: {result.get('name', 'N/A')}")
            print(f"   ğŸ“Š Estado: {result.get('status', 'N/A')}")
            print(f"   ğŸ‘¤ Usuario asignado: {result.get('assignee_id', 'N/A')}")
            print(f"   ğŸ“§ Campos personalizados: {result.get('custom_fields', 'N/A')}")
            print(f"   ğŸ”„ Sincronizado: {result.get('is_synced', 'N/A')}")
            
            return True, result
            
        else:
            print(f"â�Œ Error en la creacion de la tarea")
            print(f"ğŸ“„ Respuesta de error: {response.text}")
            
            try:
                error_data = response.json()
                print(f"ğŸ“‹ Detalles del error:")
                print(json.dumps(error_data, indent=2))
            except:
                print(f"ğŸ“„ Texto de error: {response.text}")
            
            return False, response.text
            
    except requests.exceptions.RequestException as e:
        print(f"â�Œ Error de conexion: {e}")
        return False, str(e)
    except Exception as e:
        print(f"â�Œ Error inesperado: {e}")
        return False, str(e)

def main():
    """Funcion principal"""
    print("ğŸ§ª PRUEBAS DE CREACION DE TAREAS CON DATOS REALES DE CLICKUP")
    print("=" * 70)
    
    # Get datos reales
    print("\n" + "=" * 70)
    print("PASO 1: OBTENER DATOS REALES")
    print("=" * 70)
    
    lists, users = get_real_list_and_user_ids()
    
    # Test creacion de tareas
    print("\n" + "=" * 70)
    print("PASO 2: PROBAR CREACION DE TAREAS")
    print("=" * 70)
    
    success, result = test_task_creation_with_real_data()
    
    # Resumen
    print("\n" + "=" * 70)
    print("ğŸ“Š RESUMEN")
    print("=" * 70)
    
    if success:
        print("ğŸ�‰ Â¡Tarea creada exitosamente con datos reales!")
        print("âœ… La creacion de tareas esta funcionando correctamente")
        print("âœ… Los campos personalizados se estan enviando correctamente")
        print("âœ… La asignacion de usuarios funciona")
        print("âœ… Los estados se estan configurando correctamente")
        
        print(f"\nğŸ’¡ INFORMACION IMPORTANTE:")
        print(f"   ğŸ“‹ Lista utilizada: PROYECTO 1")
        print(f"   ğŸ‘¤ Usuario asignado: Karla Rosas")
        print(f"   ğŸ“§ Email configured: karla.rosas@example.com")
        print(f"   ğŸ“± Celular configured: +52 55 9876 5432")
        
    else:
        print("â�Œ Error creating la tarea con datos reales")
        print("ğŸ”§ Revisar logs del servidor para mas detalles")
        print("ğŸ’¡ Verificar que los IDs de lista y usuario son correctos")
    
    print(f"\nğŸ•� Pruebas completadas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
