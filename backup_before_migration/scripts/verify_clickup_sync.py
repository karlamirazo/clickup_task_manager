#!/usr/bin/env python3
"""
Script para verificar directamente en ClickUp si las tareas se están sincronizando
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "https://clickuptaskmanager-production.up.railway.app"

def get_railway_tasks():
    """Obtener tareas desde Railway"""
    print("🔍 Obteniendo tareas desde Railway...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/tasks/")
        if response.status_code == 200:
            data = response.json()
            # Verificar si data es una lista o un diccionario
            if isinstance(data, list):
                tasks = data
            else:
                tasks = data.get('tasks', [])
            
            print(f"✅ Tareas en Railway: {len(tasks)} encontradas")
            
            # Mostrar las últimas 5 tareas
            recent_tasks = tasks[-5:] if len(tasks) > 5 else tasks
            for task in recent_tasks:
                print(f"   📋 ID: {task.get('id')} | ClickUp ID: {task.get('clickup_id')} | Nombre: {task.get('name')} | Sincronizada: {task.get('is_synced')}")
            
            return tasks
        else:
            print(f"❌ Error obteniendo tareas: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def verify_clickup_task(clickup_id):
    """Verificar si una tarea existe en ClickUp usando la API"""
    print(f"\n🔍 Verificando tarea en ClickUp: {clickup_id}")
    
    try:
        # Usar el endpoint de Railway para obtener la tarea específica
        response = requests.get(f"{BASE_URL}/api/v1/tasks/{clickup_id}")
        if response.status_code == 200:
            task_data = response.json()
            print(f"✅ Tarea encontrada en Railway:")
            print(f"   📋 ID local: {task_data.get('id')}")
            print(f"   📋 ClickUp ID: {task_data.get('clickup_id')}")
            print(f"   📋 Nombre: {task_data.get('name')}")
            print(f"   📋 Estado: {task_data.get('status')}")
            print(f"   📋 Sincronizada: {task_data.get('is_synced')}")
            print(f"   📋 Última sincronización: {task_data.get('last_sync')}")
            
            # Intentar obtener la tarea directamente desde ClickUp
            print(f"\n🔍 Intentando obtener tarea directamente desde ClickUp...")
            
            # Usar el endpoint de debug para ver si hay algún problema
            debug_response = requests.get(f"{BASE_URL}/debug")
            if debug_response.status_code == 200:
                debug_data = debug_response.json()
                print(f"   📋 Estado del cliente ClickUp: {debug_data.get('clickup_client', {})}")
                
                # Verificar si hay algún problema de conexión
                if debug_data.get('clickup_client', {}).get('client_status') == 'Available':
                    print("   ✅ Cliente ClickUp disponible")
                else:
                    print("   ❌ Cliente ClickUp no disponible")
            
            return True
        else:
            print(f"❌ Tarea no encontrada en Railway: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando tarea: {e}")
        return False

def test_clickup_api_directly():
    """Probar la API de ClickUp directamente"""
    print(f"\n🔍 Probando API de ClickUp directamente...")
    
    try:
        # Obtener workspaces desde Railway
        response = requests.get(f"{BASE_URL}/api/v1/workspaces/")
        if response.status_code == 200:
            data = response.json()
            workspaces = data.get('workspaces', [])
            
            if workspaces:
                workspace_id = workspaces[0]['id']
                print(f"   📋 Usando workspace: {workspaces[0]['name']} (ID: {workspace_id})")
                
                # Obtener listas del workspace
                list_response = requests.get(f"{BASE_URL}/api/v1/lists/?workspace_id={workspace_id}")
                if list_response.status_code == 200:
                    list_data = list_response.json()
                    lists = list_data.get('lists', [])
                    
                    if lists:
                        list_id = lists[0]['id']
                        print(f"   📋 Usando lista: {lists[0]['name']} (ID: {list_id})")
                        
                        # Intentar obtener tareas de la lista directamente
                        print(f"\n🔍 Intentando obtener tareas de la lista desde ClickUp...")
                        
                        # Usar el endpoint de Railway que debería sincronizar con ClickUp
                        task_response = requests.get(f"{BASE_URL}/api/v1/tasks/?list_id={list_id}")
                        if task_response.status_code == 200:
                            task_data = task_response.json()
                            tasks = task_data.get('tasks', [])
                            print(f"   📋 Tareas en la lista: {len(tasks)}")
                            
                            for task in tasks[:3]:  # Mostrar solo las primeras 3
                                print(f"      - {task.get('name')} (ClickUp ID: {task.get('clickup_id')})")
                        else:
                            print(f"   ❌ Error obteniendo tareas de la lista: {task_response.status_code}")
                    else:
                        print("   ❌ No hay listas disponibles")
                else:
                    print(f"   ❌ Error obteniendo listas: {list_response.status_code}")
            else:
                print("   ❌ No hay workspaces disponibles")
        else:
            print(f"❌ Error obteniendo workspaces: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error probando API de ClickUp: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando verificación de sincronización con ClickUp")
    print(f"📍 URL base: {BASE_URL}")
    print("=" * 70)
    
    # 1. Obtener tareas desde Railway
    tasks = get_railway_tasks()
    
    if tasks:
        # 2. Verificar la tarea más reciente
        latest_task = tasks[-1]
        clickup_id = latest_task.get('clickup_id')
        
        if clickup_id:
            verify_clickup_task(clickup_id)
        else:
            print("❌ La tarea más reciente no tiene ClickUp ID")
    
    # 3. Probar API de ClickUp directamente
    test_clickup_api_directly()
    
    print("\n" + "=" * 70)
    print("🏁 Verificación completada")
    
    print("\n💡 POSIBLES CAUSAS:")
    print("   1. Token de ClickUp expirado o inválido")
    print("   2. Problema de permisos en ClickUp")
    print("   3. Error en la API de ClickUp")
    print("   4. Problema de sincronización en Railway")

if __name__ == "__main__":
    main()
