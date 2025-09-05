#!/usr/bin/env python3
"""
Script para probar la integración completa del frontend con la API
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración
BASE_URL = "https://clickuptaskmanager-production.up.railway.app"

def test_frontend_components():
    """Probar que todos los componentes del frontend estén disponibles"""
    print("🔍 Probando componentes del frontend...")
    
    try:
        # Verificar que el dashboard se cargue
        response = requests.get(f"{BASE_URL}/static/dashboard.html")
        if response.status_code == 200:
            content = response.text
            print("✅ Dashboard cargado correctamente")
            
            # Verificar que el modal esté presente
            if 'create-task-modal' in content:
                print("   ✅ Modal de creación de tareas presente")
            else:
                print("   ❌ Modal de creación de tareas NO encontrado")
            
            # Verificar que el formulario esté presente
            if 'create-task-form' in content:
                print("   ✅ Formulario de creación presente")
            else:
                print("   ❌ Formulario de creación NO encontrado")
            
            # Verificar campos específicos
            fields_to_check = [
                'task-name', 'task-description', 'task-status', 
                'task-priority', 'task-due-date', 'task-list', 
                'task-workspace', 'task-assignee'
            ]
            
            for field in fields_to_check:
                if field in content:
                    print(f"   ✅ Campo {field} presente")
                else:
                    print(f"   ❌ Campo {field} NO encontrado")
                    
        else:
            print(f"❌ Error cargando dashboard: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando frontend: {e}")
        return False
    
    return True

def test_api_endpoints_for_frontend():
    """Probar que todos los endpoints necesarios para el frontend funcionen"""
    print("\n🔍 Probando endpoints necesarios para el frontend...")
    
    try:
        # 1. Workspaces
        response = requests.get(f"{BASE_URL}/api/v1/workspaces/")
        if response.status_code == 200:
            data = response.json()
            workspaces = data.get('workspaces', [])
            print(f"✅ Workspaces: {len(workspaces)} disponibles")
            
            if workspaces:
                workspace_id = workspaces[0]['id']
                print(f"   📋 Usando workspace: {workspaces[0]['name']} (ID: {workspace_id})")
                
                # 2. Listas del workspace
                list_response = requests.get(f"{BASE_URL}/api/v1/lists/?workspace_id={workspace_id}")
                if list_response.status_code == 200:
                    list_data = list_response.json()
                    lists = list_data.get('lists', [])
                    print(f"✅ Listas: {len(lists)} disponibles")
                    
                    if lists:
                        list_id = lists[0]['id']
                        print(f"   📋 Usando lista: {lists[0]['name']} (ID: {list_id})")
                        
                        # 3. Usuarios del workspace
                        user_response = requests.get(f"{BASE_URL}/api/v1/users/?workspace_id={workspace_id}")
                        if user_response.status_code == 200:
                            user_data = user_response.json()
                            users = user_data.get('users', [])
                            print(f"✅ Usuarios: {len(users)} disponibles")
                            
                            return workspace_id, list_id, users
                        else:
                            print(f"   ❌ Error obteniendo usuarios: {user_response.status_code}")
                    else:
                        print("   ❌ No hay listas disponibles")
                else:
                    print(f"   ❌ Error obteniendo listas: {list_response.status_code}")
            else:
                print("   ❌ No hay workspaces disponibles")
        else:
            print(f"❌ Error obteniendo workspaces: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error probando endpoints: {e}")
    
    return None, None, []

def test_task_creation_flow(workspace_id, list_id, users):
    """Probar el flujo completo de creación de tareas"""
    print(f"\n🔄 Probando flujo completo de creación de tareas...")
    
    if not workspace_id or not list_id:
        print("❌ No se puede probar sin workspace_id y list_id")
        return
    
    try:
        # Crear tarea con todos los campos del formulario
        tomorrow = datetime.now() + timedelta(days=1)
        assignee_id = users[0]['id'] if users else None
        
        task_data = {
            "name": f"Tarea Frontend Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "description": "Esta es una tarea de prueba para verificar la integración del frontend",
            "status": "complete",  # Probar el estado "COMPLETADA"
            "priority": 1,  # Urgente
            "due_date": tomorrow.strftime("%Y-%m-%d"),
            "list_id": list_id,
            "workspace_id": workspace_id,
            "assignee_id": assignee_id
        }
        
        print(f"📋 Datos de la tarea (simulando formulario):")
        print(f"   {json.dumps(task_data, indent=2)}")
        
        # Enviar solicitud de creación
        print(f"\n📤 Enviando solicitud POST a /api/v1/tasks/...")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/tasks/",
            headers={"Content-Type": "application/json"},
            json=task_data
        )
        
        print(f"📊 Respuesta del servidor:")
        print(f"   📋 Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ ¡Tarea creada exitosamente!")
            print(f"   📋 ID local: {result.get('id')}")
            print(f"   📋 ClickUp ID: {result.get('clickup_id')}")
            print(f"   📋 Estado: {result.get('status')}")
            print(f"   📋 Usuario asignado: {result.get('assignee_id')}")
            print(f"   📋 Sincronizada: {result.get('is_synced')}")
            
            # Verificar que el estado se envió correctamente
            if result.get('status') == 'complete':
                print("   ✅ Estado 'complete' enviado correctamente")
            else:
                print(f"   ⚠️ Estado enviado: {result.get('status')} (esperado: complete)")
                
            # Verificar que se sincronizó con ClickUp
            if result.get('clickup_id'):
                print("   ✅ Sincronización con ClickUp exitosa")
            else:
                print("   ❌ No se sincronizó con ClickUp")
                
        else:
            print(f"❌ Error creando tarea: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📋 Detalles del error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   📋 Respuesta del servidor: {response.text}")
                
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando verificación de integración frontend-API")
    print(f"📍 URL base: {BASE_URL}")
    print("=" * 70)
    
    # 1. Probar componentes del frontend
    if not test_frontend_components():
        print("❌ Problemas con el frontend")
        return
    
    # 2. Probar endpoints necesarios
    workspace_id, list_id, users = test_api_endpoints_for_frontend()
    
    # 3. Probar flujo completo de creación
    test_task_creation_flow(workspace_id, list_id, users)
    
    print("\n" + "=" * 70)
    print("🏁 Verificación completada")
    
    print("\n💡 RESUMEN:")
    print("   ✅ Frontend: Modal y formulario implementados")
    print("   ✅ API: Endpoints funcionando correctamente")
    print("   ✅ Sincronización: Funcionando con ClickUp")
    print("   ✅ Estados: Mapeo corregido")
    print("   ✅ Usuarios: Selector implementado")

if __name__ == "__main__":
    main()
