#!/usr/bin/env python3
"""
Sincronizar BD local con Railway
"""

import requests
import json
import sys
import os

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import get_db
from models.task import Task
from sqlalchemy import text

def sync_local_with_railway():
    """Sincronizar BD local con Railway"""
    
    print("🔄 SINCRONIZANDO BD LOCAL CON RAILWAY")
    print("=" * 60)
    
    try:
        # Obtener sesión de BD
        db = next(get_db())
        
        # 1. Obtener tareas de Railway
        print("📡 Obteniendo tareas de Railway...")
        base_url = "https://clickuptaskmanager-production.up.railway.app"
        
        response = requests.get(
            f"{base_url}/api/v1/tasks/",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"❌ Error obteniendo tareas de Railway: {response.status_code}")
            return
        
        railway_tasks = response.json()
        print(f"✅ Tareas obtenidas de Railway: {len(railway_tasks)}")
        
        # 2. Obtener tareas locales
        print("\n📊 Obteniendo tareas locales...")
        local_tasks = db.query(Task).all()
        print(f"✅ Tareas locales: {len(local_tasks)}")
        
        # 3. Crear mapeo de tareas por ClickUp ID
        print("\n🗺️ Creando mapeo de tareas...")
        local_tasks_map = {task.clickup_id: task for task in local_tasks if task.clickup_id}
        railway_tasks_map = {task['clickup_id']: task for task in railway_tasks if task.get('clickup_id')}
        
        print(f"✅ Tareas locales con ClickUp ID: {len(local_tasks_map)}")
        print(f"✅ Tareas Railway con ClickUp ID: {len(railway_tasks_map)}")
        
        # 4. Sincronizar tareas existentes
        print("\n🔄 Sincronizando tareas existentes...")
        synced_count = 0
        
        for clickup_id, railway_task in railway_tasks_map.items():
            if clickup_id in local_tasks_map:
                local_task = local_tasks_map[clickup_id]
                
                # Verificar si necesita actualización
                needs_update = False
                
                if local_task.name != railway_task['name']:
                    print(f"   📝 Actualizando nombre: '{local_task.name}' → '{railway_task['name']}'")
                    local_task.name = railway_task['name']
                    needs_update = True
                
                if local_task.status != railway_task['status']:
                    print(f"   🎯 Actualizando estado: '{local_task.status}' → '{railway_task['status']}'")
                    local_task.status = railway_task['status']
                    needs_update = True
                
                if local_task.priority != railway_task['priority']:
                    print(f"   ⚡ Actualizando prioridad: {local_task.priority} → {railway_task['priority']}")
                    local_task.priority = railway_task['priority']
                    needs_update = True
                
                if needs_update:
                    local_task.updated_at = railway_task['updated_at']
                    local_task.is_synced = True
                    synced_count += 1
        
        # 5. Crear tareas nuevas de Railway
        print(f"\n🆕 Creando tareas nuevas de Railway...")
        new_count = 0
        
        for railway_task in railway_tasks:
            clickup_id = railway_task.get('clickup_id')
            if clickup_id and clickup_id not in local_tasks_map:
                print(f"   ➕ Creando tarea: {railway_task['name']} (ClickUp ID: {clickup_id})")
                
                new_task = Task(
                    clickup_id=clickup_id,
                    name=railway_task['name'],
                    description=railway_task['description'],
                    status=railway_task['status'],
                    priority=railway_task['priority'],
                    due_date=railway_task['due_date'],
                    workspace_id=railway_task['workspace_id'],
                    list_id=railway_task['list_id'],
                    assignee_id=railway_task['assignee_id'],
                    creator_id=railway_task['creator_id'],
                    is_synced=True,
                    created_at=railway_task['created_at'],
                    updated_at=railway_task['updated_at']
                )
                
                db.add(new_task)
                new_count += 1
        
        # 6. Commit cambios
        if synced_count > 0 or new_count > 0:
            db.commit()
            print(f"\n✅ Sincronización completada:")
            print(f"   📝 Tareas actualizadas: {synced_count}")
            print(f"   ➕ Tareas nuevas: {new_count}")
        else:
            print(f"\n✅ BD local ya está sincronizada con Railway")
        
        # 7. Verificar resultado
        print(f"\n🔍 Verificando resultado...")
        final_local_tasks = db.query(Task).all()
        print(f"✅ Total de tareas en BD local: {len(final_local_tasks)}")
        
        # Mostrar tareas con ClickUp ID 86b6g0h9n
        simulador_task = db.query(Task).filter(Task.clickup_id == "86b6g0h9n").first()
        if simulador_task:
            print(f"\n📋 Tarea 'simulador' actualizada:")
            print(f"   🆔 ID Local: {simulador_task.id}")
            print(f"   🏷️ Nombre: {simulador_task.name}")
            print(f"   🎯 Estado: {simulador_task.status}")
            print(f"   ⚡ Prioridad: {simulador_task.priority}")
            print(f"   📅 Actualizada: {simulador_task.updated_at}")
        
    except Exception as e:
        print(f"❌ Error en sincronización: {e}")
        print(f"🔍 Tipo de error: {type(e).__name__}")

if __name__ == "__main__":
    sync_local_with_railway()

