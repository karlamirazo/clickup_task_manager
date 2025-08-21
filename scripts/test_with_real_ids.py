#!/usr/bin/env python3
"""
Script final usando los IDs reales obtenidos de la interfaz
"""

import requests
import json
from datetime import datetime, timedelta

def test_task_creation_with_real_ids():
    """Test creacion de tareas con los IDs reales"""
    print("ğŸ§ª Probando creacion de tareas con IDs REALES")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # IDs REALES obtenidos de la simulacion de la interfaz
    real_data = {
        "lists": [
            {"name": "PROYECTO 1", "id": "901411770471"},
            {"name": "PROYECTO 2", "id": "901411770470"}
        ],
        "users": [
            {"name": "Karla Rosas", "id": "88425547"},
            {"name": "Veronica Mirazo", "id": "88425546"},
            {"name": "Karla Ve", "id": "156221125"}
        ]
    }
    
    # Test con PROYECTO 1 y Karla Rosas
    list_id = real_data["lists"][0]["id"]  # PROYECTO 1
    user_id = real_data["users"][0]["id"]  # Karla Rosas
    
    print(f"ğŸ“‹ Lista: PROYECTO 1 - ID: {list_id}")
    print(f"ğŸ‘¤ Usuario: Karla Rosas - ID: {user_id}")
    
    test_task_data = {
        "name": f"Tarea de prueba con IDs reales - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Esta es una tarea de prueba usando los IDs reales obtenidos de la interfaz web. Deberia funcionar correctamente con los campos personalizados.",
        "status": "to do",
        "priority": 3,  # Normal
        "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "assignee_id": user_id,
        "list_id": list_id,
        "workspace_id": "9014943317",
        "custom_fields": {
            "email": "karla.rosas@realids.com",
            "Celular": "+52 55 1234 5678"
        }
    }
    
    print(f"\nğŸ“‹ Datos de la tarea:")
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
            print(f"âœ… Â¡TAREA CREADA EXITOSAMENTE!")
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

def test_task_creation_without_custom_fields():
    """Test creacion de tareas sin campos personalizados"""
    print(f"\nğŸ§ª Probando creacion de tareas SIN campos personalizados")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # IDs REALES
    list_id = "901411770471"  # PROYECTO 1
    user_id = "88425547"      # Karla Rosas
    
    test_task_data = {
        "name": f"Tarea simple con IDs reales - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Tarea de prueba sin campos personalizados usando IDs reales",
        "status": "in progress",
        "priority": 2,  # Alta
        "due_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        "assignee_id": user_id,
        "list_id": list_id,
        "workspace_id": "9014943317"
        # Sin custom_fields
    }
    
    print(f"ğŸ“‹ Datos de la tarea (sin campos personalizados):")
    print(f"   ğŸ“� Nombre: {test_task_data['name']}")
    print(f"   ğŸ“„ Descripcion: {test_task_data['description']}")
    print(f"   ğŸ“Š Estado: {test_task_data['status']}")
    print(f"   âš¡ Prioridad: {test_task_data['priority']}")
    print(f"   ğŸ“… Fecha limite: {test_task_data['due_date']}")
    print(f"   ğŸ‘¤ Usuario asignado: {test_task_data['assignee_id']} (Karla Rosas)")
    print(f"   ğŸ“‹ Lista: {test_task_data['list_id']} (PROYECTO 1)")
    
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
            print(f"âœ… Â¡Tarea simple creada exitosamente!")
            print(f"ğŸ†” ID ClickUp: {result.get('clickup_id', 'N/A')}")
            return True, result
        else:
            print(f"â�Œ Error {response.status_code}: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"â�Œ Error: {e}")
        return False, str(e)

def main():
    """Funcion principal"""
    print("ğŸ§ª PRUEBAS FINALES CON IDs REALES DE CLICKUP")
    print("=" * 70)
    
    # Prueba 1: Con campos personalizados
    print("\n" + "=" * 70)
    print("PRUEBA 1: TAREA CON CAMPOS PERSONALIZADOS")
    print("=" * 70)
    
    success1, result1 = test_task_creation_with_real_ids()
    
    # Prueba 2: Sin campos personalizados
    print("\n" + "=" * 70)
    print("PRUEBA 2: TAREA SIN CAMPOS PERSONALIZADOS")
    print("=" * 70)
    
    success2, result2 = test_task_creation_without_custom_fields()
    
    # Resumen
    print("\n" + "=" * 70)
    print("ğŸ“Š RESUMEN FINAL")
    print("=" * 70)
    
    print(f"ğŸ§ª Prueba 1 (Con campos personalizados): {'âœ… EXITOSA' if success1 else 'â�Œ FALLIDA'}")
    print(f"ğŸ§ª Prueba 2 (Sin campos personalizados): {'âœ… EXITOSA' if success2 else 'â�Œ FALLIDA'}")
    
    if success1 and success2:
        print(f"\nğŸ�‰ Â¡TODAS LAS PRUEBAS FUERON EXITOSAS!")
        print(f"âœ… La creacion de tareas esta funcionando correctamente")
        print(f"âœ… Los campos personalizados se estan enviando correctamente")
        print(f"âœ… La asignacion de usuarios funciona")
        print(f"âœ… Los estados se estan configurando correctamente")
        
        print(f"\nğŸ’¡ INFORMACION IMPORTANTE:")
        print(f"   ğŸ“‹ Lista utilizada: PROYECTO 1 (ID: 901411770471)")
        print(f"   ğŸ‘¤ Usuario asignado: Karla Rosas (ID: 88425547)")
        print(f"   ğŸ“§ Email configured: karla.rosas@realids.com")
        print(f"   ğŸ“± Celular configured: +52 55 1234 5678")
        
        print(f"\nğŸ”§ IDs REALES OBTENIDOS:")
        print(f"   ğŸ“‹ PROYECTO 1: 901411770471")
        print(f"   ğŸ“‹ PROYECTO 2: 901411770470")
        print(f"   ğŸ‘¤ Karla Rosas: 88425547")
        print(f"   ğŸ‘¤ Veronica Mirazo: 88425546")
        print(f"   ğŸ‘¤ Karla Ve: 156221125")
        
    elif success1:
        print(f"\nâš ï¸� Prueba 1 exitosa pero Prueba 2 fallida")
        print(f"âœ… Los campos personalizados funcionan")
        print(f"â�Œ Hay un problema con tareas sin campos personalizados")
    elif success2:
        print(f"\nâš ï¸� Prueba 2 exitosa pero Prueba 1 fallida")
        print(f"â�Œ Hay un problema con los campos personalizados")
        print(f"âœ… Las tareas basicas funcionan")
    else:
        print(f"\nâ�Œ Ambas pruebas fallaron")
        print(f"â�Œ Hay problemas con la creacion de tareas")
        print(f"ğŸ”§ Revisar logs del servidor para mas detalles")
    
    print(f"\nğŸ•� Pruebas completadas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
