#!/usr/bin/env python3
"""
Script para crear una lista de prueba en ClickUp
"""

import requests
import json
from datetime import datetime

def create_test_list():
    """Create una lista de prueba en ClickUp"""
    print("ğŸ“‹ Creando lista de prueba en ClickUp")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Datos para crear la lista
    list_data = {
        "name": f"Lista de Prueba - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "description": "Lista creada automaticamente para pruebas de la aplicacion",
        "workspace_id": "9014943317",  # ID del workspace que obtuvimos
        "space_id": "9014943317"  # Usar el mismo ID como space_id
    }
    
    print(f"ğŸ“‹ Datos de la lista:")
    print(f"   ğŸ“� Nombre: {list_data['name']}")
    print(f"   ğŸ“„ Descripcion: {list_data['description']}")
    print(f"   ğŸ“� Workspace ID: {list_data['workspace_id']}")
    print(f"   ğŸ�  Space ID: {list_data['space_id']}")
    
    try:
        print(f"\nğŸš€ Enviando peticion para crear lista...")
        
        # Intentar crear la lista usando el endpoint de creacion de listas
        response = requests.post(
            f"{base_url}/api/v1/lists/",
            json=list_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"ğŸ“¡ Respuesta del servidor:")
        print(f"   ğŸ“Š Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"âœ… Â¡Lista creada exitosamente!")
            print(f"ğŸ“‹ Respuesta completa:")
            print(json.dumps(result, indent=2, default=str))
            
            return True, result
            
        else:
            print(f"â�Œ Error creating la lista")
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

def verify_list_creation():
    """Verificar que la lista se creo correctamente"""
    print(f"\nğŸ”� Verificando creacion de la lista...")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        # Verificar listas disponibles
        response = requests.get(
            f"{base_url}/api/v1/lists?space_id=9014943317",
            timeout=10
        )
        
        if response.status_code == 200:
            lists_data = response.json()
            lists = lists_data.get("lists", [])
            print(f"âœ… Listas disponibles: {len(lists)}")
            
            if lists:
                print(f"ğŸ“‹ Listas encontradas:")
                for list_item in lists:
                    print(f"   ğŸ“� Nombre: {list_item.get('name', 'N/A')}")
                    print(f"   ğŸ†” ID: {list_item.get('id', 'N/A')}")
                    print(f"   ğŸ“„ Descripcion: {list_item.get('description', 'N/A')}")
                    print(f"   ğŸ“Š Tareas: {list_item.get('task_count', 'N/A')}")
                    print(f"   ğŸ”„ Sincronizado: {list_item.get('is_synced', 'N/A')}")
                    print()
                
                return lists
            else:
                print("â�Œ No se encontraron listas")
                return []
        else:
            print(f"â�Œ Error getting listas: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"â�Œ Error verificando listas: {e}")
        return []

def main():
    """Funcion principal"""
    print("ğŸ“‹ CREACION DE LISTA DE PRUEBA EN CLICKUP")
    print("=" * 70)
    
    # Create lista de prueba
    print("\n" + "=" * 70)
    print("PASO 1: CREAR LISTA DE PRUEBA")
    print("=" * 70)
    
    success, result = create_test_list()
    
    # Verificar creacion
    print("\n" + "=" * 70)
    print("PASO 2: VERIFICAR CREACION")
    print("=" * 70)
    
    lists = verify_list_creation()
    
    # Resumen
    print("\n" + "=" * 70)
    print("ğŸ“Š RESUMEN")
    print("=" * 70)
    
    if success and lists:
        print("ğŸ�‰ Â¡Lista creada exitosamente!")
        print("âœ… La lista esta disponible para crear tareas")
        print("âœ… Puedes usar el ID de la lista para crear tareas")
        
        # Mostrar informacion para usar en pruebas
        if lists:
            first_list = lists[0]
            print(f"\nğŸ’¡ INFORMACION PARA PRUEBAS:")
            print(f"   ğŸ“‹ Lista ID: {first_list.get('id', 'N/A')}")
            print(f"   ğŸ“� Nombre: {first_list.get('name', 'N/A')}")
            print(f"   ğŸ“� Workspace ID: 9014943317")
            
            print(f"\nğŸ”§ COMANDO PARA PROBAR CREACION DE TAREAS:")
            print(f"python scripts/test_task_creation_with_custom_fields.py")
            
    elif success:
        print("âš ï¸� Lista creada pero no se pudo verificar")
        print("âœ… Intenta verificar manualmente en ClickUp")
        
    else:
        print("â�Œ Error creating la lista")
        print("ğŸ”§ Revisar logs del servidor para mas detalles")
        print("ğŸ’¡ Verificar que el token de ClickUp tiene permisos para crear listas")
    
    print(f"\nğŸ•� Proceso completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
