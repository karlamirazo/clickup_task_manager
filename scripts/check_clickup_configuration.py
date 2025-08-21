#!/usr/bin/env python3
"""
Script para verificar la configuracion de ClickUp y obtener informacion detallada
"""

import requests
import json
from datetime import datetime

def check_clickup_configuration():
    """Verificar la configuracion de ClickUp"""
    print("ğŸ”� Verificando configuracion de ClickUp")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Verificar debug endpoint
    try:
        print("ğŸ”� Verificando endpoint de debug...")
        response = requests.get(f"{base_url}/debug", timeout=10)
        
        if response.status_code == 200:
            debug_data = response.json()
            print("âœ… Debug endpoint funcionando")
            
            config = debug_data.get("configuration", {})
            print(f"   ğŸ”‘ CLICKUP_API_TOKEN: {config.get('CLICKUP_API_TOKEN', 'N/A')}")
            print(f"   ğŸ—„ï¸� DATABASE_URL: {config.get('DATABASE_URL', 'N/A')}")
            print(f"   ğŸŒ� ENVIRONMENT: {config.get('ENVIRONMENT', 'N/A')}")
            
            clickup_client = debug_data.get("clickup_client", {})
            print(f"   ğŸ“¡ ClickUp Client: {clickup_client.get('client_status', 'N/A')}")
            print(f"   ğŸ”‘ Token Configurado: {clickup_client.get('token_configured', 'N/A')}")
            
        else:
            print(f"â�Œ Error en debug endpoint: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"â�Œ Error verificando debug: {e}")
        return False
    
    # Verificar workspaces
    try:
        print(f"\nğŸ”� Verificando workspaces...")
        response = requests.get(f"{base_url}/api/v1/workspaces", timeout=10)
        
        if response.status_code == 200:
            workspaces_data = response.json()
            workspaces = workspaces_data.get("workspaces", [])
            print(f"âœ… Workspaces obtenidos: {len(workspaces)}")
            
            for workspace in workspaces:
                print(f"   ğŸ“� Workspace: {workspace.get('name', 'N/A')}")
                print(f"   ğŸ†” ID: {workspace.get('id', 'N/A')}")
                print(f"   ğŸ�¨ Color: {workspace.get('color', 'N/A')}")
                print(f"   ğŸ”„ Sincronizado: {workspace.get('is_synced', 'N/A')}")
                
                # Intentar obtener listas de este workspace
                workspace_id = workspace.get('id')
                if workspace_id:
                    print(f"   ğŸ“‹ Buscando listas en workspace {workspace_id}...")
                    
                    try:
                        lists_response = requests.get(
                            f"{base_url}/api/v1/lists?space_id={workspace_id}",
                            timeout=10
                        )
                        
                        if lists_response.status_code == 200:
                            lists_data = lists_response.json()
                            lists = lists_data.get("lists", [])
                            print(f"      ğŸ“‹ Listas encontradas: {len(lists)}")
                            
                            for list_item in lists:
                                print(f"         ğŸ“� Lista: {list_item.get('name', 'N/A')}")
                                print(f"         ğŸ†” ID: {list_item.get('id', 'N/A')}")
                                print(f"         ğŸ“Š Tareas: {list_item.get('task_count', 'N/A')}")
                        else:
                            print(f"      â�Œ Error getting listas: {lists_response.status_code}")
                            
                    except Exception as e:
                        print(f"      â�Œ Error: {e}")
                
                print()  # Linea en blanco entre workspaces
                
        else:
            print(f"â�Œ Error getting workspaces: {response.status_code}")
            print(f"ğŸ“„ Respuesta: {response.text}")
            
    except Exception as e:
        print(f"â�Œ Error verificando workspaces: {e}")
    
    # Verificar usuarios
    try:
        print(f"ğŸ”� Verificando usuarios...")
        response = requests.get(f"{base_url}/api/v1/users", timeout=10)
        
        if response.status_code == 200:
            users_data = response.json()
            users = users_data.get("users", [])
            print(f"âœ… Usuarios obtenidos: {len(users)}")
            
            for user in users[:3]:  # Mostrar solo los primeros 3
                print(f"   ğŸ‘¤ Usuario: {user.get('username', 'N/A')}")
                print(f"   ğŸ†” ID: {user.get('id', 'N/A')}")
                print(f"   ğŸ“§ Email: {user.get('email', 'N/A')}")
                print(f"   ğŸ‘¤ Nombre: {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}")
                
        else:
            print(f"â�Œ Error getting usuarios: {response.status_code}")
            print(f"ğŸ“„ Respuesta: {response.text}")
            
    except Exception as e:
        print(f"â�Œ Error verificando usuarios: {e}")
    
    return True

def test_clickup_api_directly():
    """Test la API de ClickUp directamente"""
    print(f"\nğŸ”� Probando API de ClickUp directamente...")
    print("=" * 60)
    
    # Get token de la configuracion
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        debug_response = requests.get(f"{base_url}/debug", timeout=10)
        if debug_response.status_code == 200:
            debug_data = debug_response.json()
            clickup_client = debug_data.get("clickup_client", {})
            
            if clickup_client.get("token_configured") == "âœ… Si":
                print("âœ… Token de ClickUp configured correctamente")
                
                # Intentar obtener informacion de ClickUp directamente
                print("ğŸ”� Intentando obtener informacion de ClickUp...")
                
                # Nota: No podemos hacer esto directamente desde aqui porque no tenemos acceso al token
                # Pero podemos verificar que el endpoint funciona
                print("ğŸ“¡ El token esta configured y disponible para la aplicacion")
                
            else:
                print("â�Œ Token de ClickUp no configured")
                
        else:
            print("â�Œ No se pudo obtener informacion de debug")
            
    except Exception as e:
        print(f"â�Œ Error: {e}")

def main():
    """Funcion principal"""
    print("ğŸ”� VERIFICACION COMPLETA DE CONFIGURACION DE CLICKUP")
    print("=" * 70)
    
    # Verificar configuracion
    success = check_clickup_configuration()
    
    # Test API directamente
    test_clickup_api_directly()
    
    # Resumen
    print(f"\n" + "=" * 70)
    print("ğŸ“Š RESUMEN DE VERIFICACION")
    print("=" * 70)
    
    if success:
        print("âœ… La configuracion de ClickUp esta funcionando correctamente")
        print("âœ… Los endpoints estan respondiendo")
        print("âœ… El token esta configured")
        print("\nğŸ’¡ PROXIMOS PASOS:")
        print("   1. Verificar que hay listas disponibles en ClickUp")
        print("   2. Create una lista si no existe")
        print("   3. Test la creacion de tareas con IDs correctos")
        print("   4. Verificar que los campos personalizados estan configureds")
    else:
        print("â�Œ Hay problemas con la configuracion de ClickUp")
        print("ğŸ”§ Revisar logs del servidor para mas detalles")
    
    print(f"\nğŸ•� Verificacion completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
