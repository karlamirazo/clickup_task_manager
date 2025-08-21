#!/usr/bin/env python3
"""
Script para obtener IDs de listas y usuarios desde la interfaz web
"""

import requests
import json
from datetime import datetime

def get_interface_data():
    """Get datos desde la interfaz web"""
    print("ğŸŒ� Obteniendo datos desde la interfaz web")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Get la pagina principal
    try:
        print("ğŸ“„ Obteniendo pagina principal...")
        response = requests.get(f"{base_url}/", timeout=10)
        
        if response.status_code == 200:
            print("âœ… Pagina principal obtenida")
            print(f"ğŸ“Š Tamano: {len(response.text)} caracteres")
            
            # Buscar datos en el HTML
            html_content = response.text
            
            # Buscar posibles IDs de listas y usuarios en el HTML
            print("\nğŸ”� Buscando IDs en el HTML...")
            
            # Buscar patrones de IDs
            import re
            
            # Buscar IDs de listas (patrones comunes)
            list_patterns = [
                r'list_id["\']?\s*:\s*["\']?(\d+)["\']?',
                r'lista["\']?\s*:\s*["\']?(\d+)["\']?',
                r'PROYECTO.*?(\d+)',
                r'id["\']?\s*:\s*["\']?(\d+)["\']?.*?lista',
            ]
            
            # Buscar IDs de usuarios
            user_patterns = [
                r'user_id["\']?\s*:\s*["\']?(\d+)["\']?',
                r'usuario["\']?\s*:\s*["\']?(\d+)["\']?',
                r'Karla.*?(\d+)',
                r'Veronica.*?(\d+)',
            ]
            
            lists_found = set()
            users_found = set()
            
            for pattern in list_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    lists_found.add(match)
            
            for pattern in user_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    users_found.add(match)
            
            print(f"ğŸ“‹ IDs de listas encontrados: {list(lists_found)}")
            print(f"ğŸ‘¤ IDs de usuarios encontrados: {list(users_found)}")
            
            return list(lists_found), list(users_found)
            
        else:
            print(f"â�Œ Error getting pagina: {response.status_code}")
            return [], []
            
    except Exception as e:
        print(f"â�Œ Error: {e}")
        return [], []

def get_api_data():
    """Get datos desde los endpoints de la API"""
    print(f"\nğŸ”Œ Obteniendo datos desde la API")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Intentar obtener datos de diferentes endpoints
    endpoints = [
        "/api/v1/workspaces",
        "/api/v1/lists?space_id=9014943317",
        "/api/v1/users",
        "/api/v1/spaces?workspace_id=9014943317"
    ]
    
    all_data = {}
    
    for endpoint in endpoints:
        try:
            print(f"ğŸ”� Probando: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                all_data[endpoint] = data
                print(f"   âœ… Datos obtenidos")
                
                # Mostrar informacion relevante
                if "workspaces" in data:
                    workspaces = data["workspaces"]
                    print(f"   ğŸ“� Workspaces: {len(workspaces)}")
                    for ws in workspaces:
                        print(f"      ğŸ“� {ws.get('name', 'N/A')} - ID: {ws.get('id', 'N/A')}")
                
                if "lists" in data:
                    lists = data["lists"]
                    print(f"   ğŸ“‹ Listas: {len(lists)}")
                    for lst in lists:
                        print(f"      ğŸ“� {lst.get('name', 'N/A')} - ID: {lst.get('id', 'N/A')}")
                
                if "users" in data:
                    users = data["users"]
                    print(f"   ğŸ‘¤ Usuarios: {len(users)}")
                    for user in users:
                        print(f"      ğŸ‘¤ {user.get('first_name', '')} {user.get('last_name', '')} - ID: {user.get('id', 'N/A')}")
                
                if "spaces" in data:
                    spaces = data["spaces"]
                    print(f"   ğŸ�  Spaces: {len(spaces)}")
                    for space in spaces:
                        print(f"      ğŸ�  {space.get('name', 'N/A')} - ID: {space.get('id', 'N/A')}")
                        
            else:
                print(f"   â�Œ Error {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   â�Œ Error: {e}")
    
    return all_data

def test_task_creation_with_found_ids(lists_found, users_found):
    """Test creacion de tareas con los IDs encontrados"""
    print(f"\nğŸ§ª Probando creacion de tareas con IDs encontrados")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    if not lists_found or not users_found:
        print("â�Œ No se encontraron suficientes IDs para probar")
        return
    
    # Usar el primer ID de lista y usuario encontrados
    list_id = lists_found[0] if lists_found else "9014943317"
    user_id = users_found[0] if users_found else "156221125"
    
    print(f"ğŸ“‹ Usando Lista ID: {list_id}")
    print(f"ğŸ‘¤ Usando Usuario ID: {user_id}")
    
    test_task_data = {
        "name": f"Tarea desde interfaz - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Tarea creada usando IDs obtenidos desde la interfaz web",
        "status": "to do",
        "priority": 3,
        "due_date": "2025-08-25",
        "assignee_id": user_id,
        "list_id": list_id,
        "workspace_id": "9014943317",
        "custom_fields": {
            "email": "test@interfaz.com",
            "Celular": "+52 55 9999 8888"
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
    print("ğŸ”� OBTENCION DE IDs DESDE LA INTERFAZ WEB")
    print("=" * 70)
    
    # Get datos desde la interfaz
    print("\n" + "=" * 70)
    print("PASO 1: OBTENER DATOS DESDE LA INTERFAZ")
    print("=" * 70)
    
    lists_found, users_found = get_interface_data()
    
    # Get datos desde la API
    print("\n" + "=" * 70)
    print("PASO 2: OBTENER DATOS DESDE LA API")
    print("=" * 70)
    
    api_data = get_api_data()
    
    # Test creacion de tareas
    print("\n" + "=" * 70)
    print("PASO 3: PROBAR CREACION DE TAREAS")
    print("=" * 70)
    
    success, result = test_task_creation_with_found_ids(lists_found, users_found)
    
    # Resumen
    print("\n" + "=" * 70)
    print("ğŸ“Š RESUMEN")
    print("=" * 70)
    
    print(f"ğŸ“‹ IDs de listas encontrados: {lists_found}")
    print(f"ğŸ‘¤ IDs de usuarios encontrados: {users_found}")
    
    if success:
        print("ğŸ�‰ Â¡Tarea creada exitosamente!")
        print("âœ… Los IDs obtenidos desde la interfaz son correctos")
        print("âœ… La creacion de tareas funciona correctamente")
        print("âœ… Los campos personalizados se envian correctamente")
    else:
        print("â�Œ Error creating la tarea")
        print("ğŸ”§ Revisar los IDs obtenidos")
    
    print(f"\nğŸ•� Proceso completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
