#!/usr/bin/env python3
"""
Verificar específicamente la tarea con ID 34
"""

import sys
import os

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import get_db
from models.task import Task

def check_task_34():
    """Verificar la tarea con ID 34"""
    
    print("🔍 VERIFICANDO TAREA CON ID 34")
    print("=" * 60)
    
    try:
        # Obtener sesión de BD
        db = next(get_db())
        
        # Buscar tarea con ID 34
        task = db.query(Task).filter(Task.id == 34).first()
        
        if task:
            print(f"✅ TAREA ENCONTRADA:")
            print(f"   🆔 ID Local: {task.id}")
            print(f"   🏷️ Nombre: {task.name}")
            print(f"   📋 Descripción: {task.description}")
            print(f"   📱 ClickUp ID: {task.clickup_id}")
            print(f"   🔄 Sincronizada: {'✅ SÍ' if task.is_synced else '❌ NO'}")
            print(f"   📅 Creada: {task.created_at}")
            print(f"   ✏️ Actualizada: {task.updated_at}")
            print(f"   📍 Lista: {task.list_id}")
            print(f"   🏢 Workspace: {task.workspace_id}")
            print(f"   👤 Asignado: {task.assignee_id}")
            print(f"   🎯 Estado: {task.status}")
            print(f"   ⚡ Prioridad: {task.priority}")
            print(f"   📅 Fecha límite: {task.due_date}")
        else:
            print("❌ No se encontró tarea con ID 34")
        
        # Buscar tarea con ClickUp ID 86b6g0h9n
        print(f"\n🔍 VERIFICANDO TAREA CON CLICKUP ID 86b6g0h9n:")
        print("-" * 50)
        
        clickup_task = db.query(Task).filter(Task.clickup_id == "86b6g0h9n").first()
        
        if clickup_task:
            print(f"✅ TAREA ENCONTRADA:")
            print(f"   🆔 ID Local: {clickup_task.id}")
            print(f"   🏷️ Nombre: {clickup_task.name}")
            print(f"   📋 Descripción: {clickup_task.description}")
            print(f"   📱 ClickUp ID: {clickup_task.clickup_id}")
            print(f"   🔄 Sincronizada: {'✅ SÍ' if clickup_task.is_synced else '❌ NO'}")
            print(f"   📅 Creada: {clickup_task.created_at}")
            print(f"   ✏️ Actualizada: {clickup_task.updated_at}")
            print(f"   📍 Lista: {clickup_task.list_id}")
            print(f"   🏢 Workspace: {clickup_task.workspace_id}")
            print(f"   👤 Asignado: {clickup_task.assignee_id}")
            print(f"   🎯 Estado: {clickup_task.status}")
            print(f"   ⚡ Prioridad: {clickup_task.priority}")
            print(f"   📅 Fecha límite: {clickup_task.due_date}")
        else:
            print("❌ No se encontró tarea con ClickUp ID 86b6g0h9n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"🔍 Tipo de error: {type(e).__name__}")

if __name__ == "__main__":
    check_task_34()

