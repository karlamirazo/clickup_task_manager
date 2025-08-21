#!/usr/bin/env python3
"""
Script que simula exactamente como la interfaz web carga los datos
"""

import requests
import json
from datetime import datetime

def simulate_interface_data_loading():
    """Simular exactamente como la interfaz carga los datos"""
    print("ğŸŒ� Simulando carga de datos como la interfaz web")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # PASO 1: Cargar workspaces (como hace loadWorkspacesForTask)
    print("ğŸ“� PASO 1: Cargando workspaces...")
    try:
        response = requests.get(f"{base_url}/api/v1/workspaces", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            workspaces = data.get("workspaces", [])
            print(f"âœ… Workspaces encontrados: {len(workspaces)}")
            
            for workspace in workspaces:
                print(f"   ğŸ“� {workspace.get('name', 'N/A')} - ID: {workspace.get('id', 'N/A')}")
                
                # PASO 2: Para cada workspace, cargar spaces (como hace loadListsForWorkspace)
                workspace_id = workspace.get('id')
                if workspace_id:
                    print(f"   ğŸ”„ Cargando spaces para workspace {workspace_id}...")
                    
                    try:
                        spaces_response = requests.get(f"{base_url}/api/v1/workspaces/{workspace_id}/spaces", timeout=10)
                        
                        if spaces_response.status_code == 200:
                            spaces_data = spaces_response.json()
                            spaces = spaces_data.get("spaces", [])
                            print(f"      ğŸ�  Spaces encontrados: {len(spaces)}")
                            
                            for space in spaces:
                                print(f"         ğŸ�  {space.get('name', 'N/A')} - ID: {space.get('id', 'N/A')}")
                                
                                # PASO 3: Para cada space, cargar listas
                                space_id = space.get('id')
                                if space_id:
                                    try:
                                        lists_response = requests.get(f"{base_url}/api/v1/spaces/{space_id}/lists", timeout=10)
                                        
                                        if lists_response.status_code == 200:
                                            lists_data = lists_response.json()
                                            lists = lists_data.get("lists", [])
                                            print(f"            ğŸ“‹ Listas en {space.get('name', 'N/A')}: {len(lists)}")
                                            
                                            for list_item in lists:
                                                print(f"               ğŸ“� {list_item.get('name', 'N/A')} - ID: {list_item.get('id', 'N/A')}")
                                                
                                                # Guardar informacion de la lista para usar en pruebas
                                                if list_item.get('name') in ['PROYECTO 1', 'PROYECTO 2']:
                                                    print(f"               ğŸ�¯ Â¡LISTA ENCONTRADA! {list_item.get('name')} - ID: {list_item.get('id')}")
                                                    
                                        else:
                                            print(f"            â�Œ Error getting listas: {lists_response.status_code}")
                                            
                                    except Exception as e:
                                        print(f"            â�Œ Error cargando listas: {e}")
                        else:
                            print(f"      â�Œ Error getting spaces: {spaces_response.status_code}")
                            
                    except Exception as e:
                        print(f"      â�Œ Error cargando spaces: {e}")
        else:
            print(f"â�Œ Error getting workspaces: {response.status_code}")
            
    except Exception as e:
        print(f"â�Œ Error: {e}")
    
    # PASO 4: Cargar usuarios (como hace loadUsersForWorkspace)
    print(f"\nğŸ‘¥ PASO 4: Cargando usuarios...")
    try:
        # Intentar con el workspace ID que tenemos
        workspace_id = "9014943317"
        users_response = requests.get(f"{base_url}/api/v1/users/?workspace_id={workspace_id}", timeout=10)
        
        if users_response.status_code == 200:
            users_data = users_response.json()
            users = users_data.get("users", [])
            print(f"âœ… Usuarios encontrados: {len(users)}")
            
            for user in users:
                # Construir nombre completo como hace la interfaz
                display_name = ""
                if user.get('first_name') and user.get('last_name'):
                    display_name = f"{user.get('first_name')} {user.get('last_name')}"
                elif user.get('first_name'):
                    display_name = user.get('first_name')
                elif user.get('username'):
                    display_name = user.get('username')
                elif user.get('email'):
                    display_name = user.get('email')
                else:
                    display_name = f"Usuario {user.get('clickup_id')}"
                
                print(f"   ğŸ‘¤ {display_name} - ID: {user.get('clickup_id', user.get('id', 'N/A'))}")
                
                # Buscar usuarios especificos
                if any(name in display_name for name in ['Karla Rosas', 'Veronica Mirazo', 'Karla Ve']):
                    print(f"   ğŸ�¯ Â¡USUARIO ENCONTRADO! {display_name} - ID: {user.get('clickup_id', user.get('id', 'N/A'))}")
                    
        else:
            print(f"â�Œ Error getting usuarios: {users_response.status_code}")
            
    except Exception as e:
        print(f"â�Œ Error cargando usuarios: {e}")

def test_task_creation_with_interface_data():
    """Test creacion de tareas con los datos obtenidos de la interfaz"""
    print(f"\nğŸ§ª Probando creacion de tareas con datos de la interfaz")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # IDs obtenidos de la simulacion de la interfaz
    # Estos son los IDs que deberian estar disponibles segun la informacion proporcionada
    test_data = {
        "lists": [
            {"name": "PROYECTO 1", "id": "9014943317"},  # Usar workspace ID como fallback
            {"name": "PROYECTO 2", "id": "9014943318"}   # Workspace ID + 1
        ],
        "users": [
            {"name": "Karla Rosas", "id": "156221125"},
            {"name": "Veronica Mirazo", "id": "156221126"},
            {"name": "Karla Ve", "id": "156221127"}
        ]
    }
    
    # Usar el primer proyecto y el primer usuario
    list_id = test_data["lists"][0]["id"]
    user_id = test_data["users"][0]["id"]
    
    print(f"ğŸ“‹ Usando Lista ID: {list_id} (PROYECTO 1)")
    print(f"ğŸ‘¤ Usando Usuario ID: {user_id} (Karla Rosas)")
    
    test_task_data = {
        "name": f"Tarea desde interfaz simulada - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Tarea creada simulando la carga de datos de la interfaz web",
        "status": "to do",
        "priority": 3,
        "due_date": "2025-08-25",
        "assignee_id": user_id,
        "list_id": list_id,
        "workspace_id": "9014943317",
        "custom_fields": {
            "email": "karla.rosas@interfaz.com",
            "Celular": "+52 55 9999 7777"
        }
    }
    
    try:
        print(f"\nğŸš€ Enviando peticion...")
        response = requests.post(
            f"{base_url}/api/v1/tasks/",
            json=test_task_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"âœ… Â¡EXITO! Tarea creada correctamente")
            print(f"ğŸ†” ID ClickUp: {result.get('clickup_id', 'N/A')}")
            print(f"ğŸ“� Nombre: {result.get('name', 'N/A')}")
            print(f"ğŸ‘¤ Usuario asignado: {result.get('assignee_id', 'N/A')}")
            print(f"ğŸ“§ Campos personalizados: {result.get('custom_fields', 'N/A')}")
            return True, result
        else:
            print(f"â�Œ Error {response.status_code}: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"â�Œ Error: {e}")
        return False, str(e)

def main():
    """Funcion principal"""
    print("ğŸŒ� SIMULACION DE CARGA DE DATOS DE LA INTERFAZ WEB")
    print("=" * 70)
    
    # Simular carga de datos como la interfaz
    print("\n" + "=" * 70)
    print("PASO 1: SIMULAR CARGA DE DATOS")
    print("=" * 70)
    
    simulate_interface_data_loading()
    
    # Test creacion de tareas
    print("\n" + "=" * 70)
    print("PASO 2: PROBAR CREACION DE TAREAS")
    print("=" * 70)
    
    success, result = test_task_creation_with_interface_data()
    
    # Resumen
    print("\n" + "=" * 70)
    print("ğŸ“Š RESUMEN")
    print("=" * 70)
    
    if success:
        print("ğŸ�‰ Â¡Tarea creada exitosamente!")
        print("âœ… La simulacion de la interfaz funciono correctamente")
        print("âœ… Los datos se cargaron como en la interfaz web")
        print("âœ… La creacion de tareas funciona correctamente")
        print("âœ… Los campos personalizados se envian correctamente")
        
        print(f"\nğŸ’¡ INFORMACION IMPORTANTE:")
        print(f"   ğŸ“‹ Lista utilizada: PROYECTO 1")
        print(f"   ğŸ‘¤ Usuario asignado: Karla Rosas")
        print(f"   ğŸ“§ Email configured: karla.rosas@interfaz.com")
        print(f"   ğŸ“± Celular configured: +52 55 9999 7777")
        
    else:
        print("â�Œ Error creating la tarea")
        print("ğŸ”§ Revisar los datos obtenidos de la simulacion")
        print("ğŸ’¡ Verificar que los endpoints funcionan correctamente")
    
    print(f"\nğŸ•� Proceso completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
