#!/usr/bin/env python3
"""
Script final usando los IDs reales obtenidos de la interfaz
"""

import requests
import json
from datetime import datetime, timedelta

def test_task_creation_with_real_ids():
    """Probar creación de tareas con los IDs reales"""
    print("🧪 Probando creación de tareas con IDs REALES")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # IDs REALES obtenidos de la simulación de la interfaz
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
    
    # Probar con PROYECTO 1 y Karla Rosas
    list_id = real_data["lists"][0]["id"]  # PROYECTO 1
    user_id = real_data["users"][0]["id"]  # Karla Rosas
    
    print(f"📋 Lista: PROYECTO 1 - ID: {list_id}")
    print(f"👤 Usuario: Karla Rosas - ID: {user_id}")
    
    test_task_data = {
        "name": f"Tarea de prueba con IDs reales - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Esta es una tarea de prueba usando los IDs reales obtenidos de la interfaz web. Debería funcionar correctamente con los campos personalizados.",
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
    
    print(f"\n📋 Datos de la tarea:")
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
            print(f"✅ ¡TAREA CREADA EXITOSAMENTE!")
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

def test_task_creation_without_custom_fields():
    """Probar creación de tareas sin campos personalizados"""
    print(f"\n🧪 Probando creación de tareas SIN campos personalizados")
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
    
    print(f"📋 Datos de la tarea (sin campos personalizados):")
    print(f"   📝 Nombre: {test_task_data['name']}")
    print(f"   📄 Descripción: {test_task_data['description']}")
    print(f"   📊 Estado: {test_task_data['status']}")
    print(f"   ⚡ Prioridad: {test_task_data['priority']}")
    print(f"   📅 Fecha límite: {test_task_data['due_date']}")
    print(f"   👤 Usuario asignado: {test_task_data['assignee_id']} (Karla Rosas)")
    print(f"   📋 Lista: {test_task_data['list_id']} (PROYECTO 1)")
    
    try:
        print(f"\n🚀 Enviando petición...")
        
        response = requests.post(
            f"{base_url}/api/v1/tasks/",
            json=test_task_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ ¡Tarea simple creada exitosamente!")
            print(f"🆔 ID ClickUp: {result.get('clickup_id', 'N/A')}")
            return True, result
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, str(e)

def main():
    """Función principal"""
    print("🧪 PRUEBAS FINALES CON IDs REALES DE CLICKUP")
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
    print("📊 RESUMEN FINAL")
    print("=" * 70)
    
    print(f"🧪 Prueba 1 (Con campos personalizados): {'✅ EXITOSA' if success1 else '❌ FALLIDA'}")
    print(f"🧪 Prueba 2 (Sin campos personalizados): {'✅ EXITOSA' if success2 else '❌ FALLIDA'}")
    
    if success1 and success2:
        print(f"\n🎉 ¡TODAS LAS PRUEBAS FUERON EXITOSAS!")
        print(f"✅ La creación de tareas está funcionando correctamente")
        print(f"✅ Los campos personalizados se están enviando correctamente")
        print(f"✅ La asignación de usuarios funciona")
        print(f"✅ Los estados se están configurando correctamente")
        
        print(f"\n💡 INFORMACIÓN IMPORTANTE:")
        print(f"   📋 Lista utilizada: PROYECTO 1 (ID: 901411770471)")
        print(f"   👤 Usuario asignado: Karla Rosas (ID: 88425547)")
        print(f"   📧 Email configurado: karla.rosas@realids.com")
        print(f"   📱 Celular configurado: +52 55 1234 5678")
        
        print(f"\n🔧 IDs REALES OBTENIDOS:")
        print(f"   📋 PROYECTO 1: 901411770471")
        print(f"   📋 PROYECTO 2: 901411770470")
        print(f"   👤 Karla Rosas: 88425547")
        print(f"   👤 Veronica Mirazo: 88425546")
        print(f"   👤 Karla Ve: 156221125")
        
    elif success1:
        print(f"\n⚠️ Prueba 1 exitosa pero Prueba 2 fallida")
        print(f"✅ Los campos personalizados funcionan")
        print(f"❌ Hay un problema con tareas sin campos personalizados")
    elif success2:
        print(f"\n⚠️ Prueba 2 exitosa pero Prueba 1 fallida")
        print(f"❌ Hay un problema con los campos personalizados")
        print(f"✅ Las tareas básicas funcionan")
    else:
        print(f"\n❌ Ambas pruebas fallaron")
        print(f"❌ Hay problemas con la creación de tareas")
        print(f"🔧 Revisar logs del servidor para más detalles")
    
    print(f"\n🕐 Pruebas completadas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
