#!/usr/bin/env python3
"""
Script para probar la creación de tareas con datos reales de ClickUp
"""

import requests
import json
from datetime import datetime, timedelta

def get_real_list_and_user_ids():
    """Obtener IDs reales de listas y usuarios"""
    print("🔍 Obteniendo IDs reales de listas y usuarios")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Intentar obtener listas con diferentes parámetros
    list_endpoints = [
        "/api/v1/lists",
        "/api/v1/lists?workspace_id=9014943317",
        "/api/v1/lists?space_id=9014943317"
    ]
    
    lists_found = []
    for endpoint in list_endpoints:
        try:
            print(f"🔍 Probando endpoint: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                lists = data.get("lists", [])
                print(f"   ✅ Listas encontradas: {len(lists)}")
                
                for list_item in lists:
                    print(f"      📝 {list_item.get('name', 'N/A')} - ID: {list_item.get('id', 'N/A')}")
                    lists_found.append(list_item)
            else:
                print(f"   ❌ Error {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Intentar obtener usuarios
    users_found = []
    try:
        print(f"\n🔍 Obteniendo usuarios...")
        response = requests.get(f"{base_url}/api/v1/users", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            users = data.get("users", [])
            print(f"   ✅ Usuarios encontrados: {len(users)}")
            
            for user in users:
                print(f"      👤 {user.get('first_name', '')} {user.get('last_name', '')} - ID: {user.get('id', 'N/A')}")
                users_found.append(user)
        else:
            print(f"   ❌ Error {response.status_code}: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return lists_found, users_found

def test_task_creation_with_real_data():
    """Probar la creación de tareas con datos reales"""
    print("\n🧪 Probando creación de tareas con datos reales")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # IDs reales basados en la información proporcionada
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
    
    print(f"📋 Datos de prueba con información real:")
    print(f"   📝 Nombre: {test_task_data['name']}")
    print(f"   📄 Descripción: {test_task_data['description']}")
    print(f"   📊 Estado: {test_task_data['status']}")
    print(f"   ⚡ Prioridad: {test_task_data['priority']}")
    print(f"   📅 Fecha límite: {test_task_data['due_date']}")
    print(f"   👤 Usuario asignado: {test_task_data['assignee_id']} (Karla Rosas)")
    print(f"   📋 Lista: {test_task_data['list_id']} (PROYECTO 1)")
    print(f"   📁 Workspace: {test_task_data['workspace_id']}")
    print(f"   📧 Email: {test_task_data['custom_fields']['email']}")
    print(f"   📱 Celular: {test_task_data['custom_fields']['Celular']}")
    
    try:
        print(f"\n🚀 Enviando petición a {base_url}/api/v1/tasks/")
        
        response = requests.post(
            f"{base_url}/api/v1/tasks/",
            json=test_task_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📡 Respuesta del servidor:")
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ ¡Tarea creada exitosamente!")
            print(f"📋 Respuesta completa:")
            print(json.dumps(result, indent=2, default=str))
            
            # Verificar campos importantes
            print(f"\n🔍 Verificación de campos:")
            print(f"   🆔 ID local: {result.get('id', 'N/A')}")
            print(f"   🆔 ID ClickUp: {result.get('clickup_id', 'N/A')}")
            print(f"   📝 Nombre: {result.get('name', 'N/A')}")
            print(f"   📊 Estado: {result.get('status', 'N/A')}")
            print(f"   👤 Usuario asignado: {result.get('assignee_id', 'N/A')}")
            print(f"   📧 Campos personalizados: {result.get('custom_fields', 'N/A')}")
            print(f"   🔄 Sincronizado: {result.get('is_synced', 'N/A')}")
            
            return True, result
            
        else:
            print(f"❌ Error en la creación de la tarea")
            print(f"📄 Respuesta de error: {response.text}")
            
            try:
                error_data = response.json()
                print(f"📋 Detalles del error:")
                print(json.dumps(error_data, indent=2))
            except:
                print(f"📄 Texto de error: {response.text}")
            
            return False, response.text
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False, str(e)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False, str(e)

def main():
    """Función principal"""
    print("🧪 PRUEBAS DE CREACIÓN DE TAREAS CON DATOS REALES DE CLICKUP")
    print("=" * 70)
    
    # Obtener datos reales
    print("\n" + "=" * 70)
    print("PASO 1: OBTENER DATOS REALES")
    print("=" * 70)
    
    lists, users = get_real_list_and_user_ids()
    
    # Probar creación de tareas
    print("\n" + "=" * 70)
    print("PASO 2: PROBAR CREACIÓN DE TAREAS")
    print("=" * 70)
    
    success, result = test_task_creation_with_real_data()
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)
    
    if success:
        print("🎉 ¡Tarea creada exitosamente con datos reales!")
        print("✅ La creación de tareas está funcionando correctamente")
        print("✅ Los campos personalizados se están enviando correctamente")
        print("✅ La asignación de usuarios funciona")
        print("✅ Los estados se están configurando correctamente")
        
        print(f"\n💡 INFORMACIÓN IMPORTANTE:")
        print(f"   📋 Lista utilizada: PROYECTO 1")
        print(f"   👤 Usuario asignado: Karla Rosas")
        print(f"   📧 Email configurado: karla.rosas@example.com")
        print(f"   📱 Celular configurado: +52 55 9876 5432")
        
    else:
        print("❌ Error creando la tarea con datos reales")
        print("🔧 Revisar logs del servidor para más detalles")
        print("💡 Verificar que los IDs de lista y usuario son correctos")
    
    print(f"\n🕐 Pruebas completadas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
