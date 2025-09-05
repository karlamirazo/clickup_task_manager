#!/usr/bin/env python3
"""
Verificar tareas en la base de datos local
"""

import sys
import os

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import get_db
from models.task import Task

def check_local_tasks():
    """Verificar tareas en la BD local"""
    
    print("🔍 VERIFICANDO TAREAS EN BASE DE DATOS LOCAL")
    print("=" * 60)
    
    try:
        # Obtener sesión de BD
        db = next(get_db())
        
        # Obtener todas las tareas
        tasks = db.query(Task).all()
        
        print(f"\n📊 TOTAL DE TAREAS EN BD LOCAL: {len(tasks)}")
        print("-" * 50)
        
        if not tasks:
            print("⚠️ No hay tareas en la base de datos local")
            return
        
        # Mostrar detalles de cada tarea
        for i, task in enumerate(tasks, 1):
            print(f"\n📝 TAREA {i}:")
            print(f"   🆔 ID Local: {task.id}")
            print(f"   🏷️ Nombre: {task.name}")
            print(f"   📋 Descripción: {task.description[:100] + '...' if len(task.description or '') > 100 else task.description}")
            print(f"   📱 ClickUp ID: {task.clickup_id or 'NO SINCRONIZADA'}")
            print(f"   🔄 Sincronizada: {'✅ SÍ' if task.is_synced else '❌ NO'}")
            print(f"   📅 Creada: {task.created_at}")
            print(f"   ✏️ Actualizada: {task.updated_at}")
            print(f"   📍 Lista: {task.list_id}")
            print(f"   🏢 Workspace: {task.workspace_id}")
            print(f"   👤 Asignado: {task.assignee_id}")
            print(f"   🎯 Estado: {task.status}")
            print(f"   ⚡ Prioridad: {task.priority}")
            print(f"   📅 Fecha límite: {task.due_date}")
            print("-" * 30)
        
        # Verificar tareas no sincronizadas
        unsynced_tasks = db.query(Task).filter(Task.is_synced == False).all()
        if unsynced_tasks:
            print(f"\n⚠️ TAREAS NO SINCRONIZADAS: {len(unsynced_tasks)}")
            print("-" * 50)
            for task in unsynced_tasks:
                print(f"   ❌ {task.name} (ID: {task.id})")
        
        # Verificar tareas sin ClickUp ID
        tasks_without_clickup = db.query(Task).filter(Task.clickup_id.is_(None)).all()
        if tasks_without_clickup:
            print(f"\n⚠️ TAREAS SIN ID DE CLICKUP: {len(tasks_without_clickup)}")
            print("-" * 50)
            for task in tasks_without_clickup:
                print(f"   ❌ {task.name} (ID: {task.id})")
        
        # Buscar la tarea "simulador 2"
        simulador_tasks = db.query(Task).filter(Task.name.like('%simulador%')).all()
        if simulador_tasks:
            print(f"\n🔍 TAREAS CON 'SIMULADOR' EN EL NOMBRE: {len(simulador_tasks)}")
            print("-" * 50)
            for task in simulador_tasks:
                print(f"   📝 {task.name} (ID: {task.id}, ClickUp ID: {task.clickup_id})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"🔍 Tipo de error: {type(e).__name__}")

if __name__ == "__main__":
    check_local_tasks()
