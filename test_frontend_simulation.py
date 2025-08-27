#!/usr/bin/env python3
"""
Script que simula exactamente lo que hace el frontend al crear una tarea
"""

import asyncio
import sys
import os
import json

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.clickup_client import ClickUpClient
from core.config import settings

async def simulate_frontend_task_creation():
    """Simular exactamente lo que hace el frontend"""
    print("🚀 Simulando creación de tarea desde el frontend...")
    
    try:
        # Crear cliente
        client = ClickUpClient(settings.CLICKUP_API_TOKEN)
        
        # Simular datos del formulario del frontend
        form_data = {
            "name": "Tarea desde Frontend - Test",
            "description": "Esta tarea se crea simulando el frontend",
            "status": "to do",
            "priority": 3,
            "assignee_id": None,
            "due_date": "2025-01-25",
            "list_id": "901411770471",
            "workspace_id": "9014943317",
            "custom_fields": {
                "Email": "test@example.com",
                "Celular": "555-1234"
            }
        }
        
        print(f"📋 Datos del formulario: {json.dumps(form_data, indent=2)}")
        
        # Simular el proceso de la función create_task_FINAL_VERSION
        
        # 1. Procesar usuario asignado
        clickup_assignee_id = None
        if form_data["assignee_id"]:
            # Aquí iría la lógica de mapeo de usuarios
            pass
        
        # 2. Mapear estado
        status_mapping = {
            "to do": "pendiente",
            "todo": "pendiente", 
            "pending": "pendiente",
            "pendiente": "pendiente",
            "in progress": "en curso",
            "in_progress": "en curso",
            "en curso": "en curso",
            "en progreso": "en progreso",
            "working": "en curso",
            "active": "en curso",
            "review": "en curso",
            "testing": "en curso",
            "complete": "completado",
            "completed": "completado",
            "completado": "completado",
            "done": "completado"
        }
        
        clickup_status = status_mapping.get(form_data["status"].lower(), "pendiente")
        print(f"🔄 Estado mapeado: {form_data['status']} -> {clickup_status}")
        
        # 3. Preparar datos para ClickUp
        clickup_task_data = {
            "name": form_data["name"],
            "description": form_data["description"] or "",
            "status": clickup_status,
            "priority": form_data["priority"] or 3,
            "due_date": int(asyncio.get_event_loop().time() * 1000) if form_data["due_date"] else None,
            "assignees": [clickup_assignee_id] if clickup_assignee_id else [],
            "custom_fields": form_data["custom_fields"] or {}
        }
        
        print(f"📋 Datos para ClickUp: {json.dumps(clickup_task_data, indent=2)}")
        
        # 4. Crear tarea en ClickUp
        print("🔍 Creando tarea en ClickUp...")
        clickup_response = await client.create_task(form_data["list_id"], clickup_task_data)
        
        if not clickup_response or "id" not in clickup_response:
            raise Exception("No se recibió ID de tarea de ClickUp")
        
        clickup_task_id = clickup_response["id"]
        print(f"✅ Tarea creada en ClickUp con ID: {clickup_task_id}")
        
        # 5. Simular actualización de campos personalizados
        if form_data["custom_fields"]:
            print("📝 Actualizando campos personalizados...")
            
            # Simular la función update_custom_fields_direct
            for field_name, field_value in form_data["custom_fields"].items():
                print(f"   📝 Actualizando {field_name}: {field_value}")
                
                # Aquí iría la lógica de actualización de campos personalizados
                # Por ahora solo simulamos
                print(f"   ✅ Campo {field_name} actualizado (simulado)")
        
        print(f"✅ Simulación completada exitosamente!")
        print(f"📋 Tarea creada en ClickUp: {clickup_task_id}")
        
        return clickup_task_id
        
    except Exception as e:
        print(f"❌ Error en simulación: {e}")
        print(f"🔍 Tipo de error: {type(e).__name__}")
        return None

async def main():
    """Función principal"""
    print("🚀 Iniciando simulación del frontend...")
    
    # Simular creación de tarea
    task_id = await simulate_frontend_task_creation()
    
    if task_id:
        print(f"\n✅ Simulación exitosa! Tarea creada: {task_id}")
    else:
        print(f"\n❌ Simulación falló")
    
    print("\n✅ Simulación completada!")

if __name__ == "__main__":
    asyncio.run(main())
