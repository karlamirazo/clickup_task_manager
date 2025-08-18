#!/usr/bin/env python3
"""
Script para probar la creación de tareas con todos los campos llenos
Simula lo que haría la interfaz web
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_interface_task_creation():
    """Probar la creación de tareas con todos los campos llenos"""
    
    print("🧪 PROBANDO CREACIÓN DE TAREAS CON TODOS LOS CAMPOS LLENOS")
    print("=" * 70)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Datos de prueba COMPLETOS (como los llenaría la interfaz)
    task_data = {
        "name": f"TAREA INTERFAZ COMPLETA - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Esta tarea debe mostrar TODOS los campos correctamente en ClickUp: estado, prioridad, fecha límite, usuario asignado, Email y Celular",
        "workspace_id": "9014943317",
        "list_id": "901411770471",  # PROYECTO 1 (tiene campos personalizados)
        "status": "in progress",  # Estado específico (NO "to do" por defecto)
        "priority": 1,  # Prioridad alta
        "due_date": "2025-08-25",
        "assignees": "88425547",  # Karla Rosas
        "custom_fields": {
            "Email": "interfaz.completa@test.com",
            "Celular": "+52 55 1234 5678"
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📤 Creando tarea con TODOS los campos llenos...")
            print(f"📋 Datos completos:")
            print(f"   📝 Nombre: {task_data['name']}")
            print(f"   📄 Descripción: {task_data['description']}")
            print(f"   📊 Estado: {task_data['status']}")
            print(f"   ⚡ Prioridad: {task_data['priority']}")
            print(f"   📅 Fecha límite: {task_data['due_date']}")
            print(f"   👤 Usuario asignado: {task_data['assignees']}")
            print(f"   📧 Email: {task_data['custom_fields']['Email']}")
            print(f"   📱 Celular: {task_data['custom_fields']['Celular']}")
            
            # Crear tarea
            async with session.post(
                f"{base_url}/api/v1/tasks/",
                json=task_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"\n📡 Status de creación: {response.status}")
                response_text = await response.text()
                print(f"📄 Respuesta: {response_text}")
                
                if response.status == 201:
                    task_response = json.loads(response_text)
                    task_id = task_response.get('clickup_id')
                    print(f"\n✅ Tarea creada exitosamente!")
                    print(f"   🆔 ID Local: {task_response.get('id')}")
                    print(f"   🆔 ClickUp ID: {task_id}")
                    print(f"   📝 Nombre: {task_response.get('name')}")
                    print(f"   📊 Estado: {task_response.get('status')}")
                    print(f"   ⚡ Prioridad: {task_response.get('priority')}")
                    print(f"   👤 Usuario asignado: {task_response.get('assignee_id')}")
                    print(f"   📧 Campos personalizados: {task_response.get('custom_fields')}")
                    
                    # Esperar un momento para que ClickUp procese
                    print(f"\n⏳ Esperando 5 segundos para que ClickUp procese...")
                    await asyncio.sleep(5)
                    
                    # Verificar que la tarea se guardó correctamente en la BD local
                    print(f"\n🔍 Verificando tarea en BD local...")
                    async with session.get(f"{base_url}/api/v1/tasks/{task_response.get('id')}") as detail_response:
                        if detail_response.status == 200:
                            detail_data = json.loads(await detail_response.text())
                            print(f"✅ Tarea encontrada en BD local:")
                            print(f"   📊 Estado: {detail_data.get('status')}")
                            print(f"   ⚡ Prioridad: {detail_data.get('priority')}")
                            print(f"   👤 Usuario asignado: {detail_data.get('assignee_id')}")
                            print(f"   📧 Campos personalizados: {detail_data.get('custom_fields')}")
                        else:
                            print(f"❌ Error obteniendo detalles: {detail_response.status}")
                    
                    print(f"\n🎯 INSTRUCCIONES PARA VERIFICAR EN CLICKUP:")
                    print(f"1. Ve a ClickUp y busca la tarea: '{task_data['name']}'")
                    print(f"2. Verifica que el ESTADO sea: {task_data['status']} (NO 'pendiente')")
                    print(f"3. Verifica que la PRIORIDAD sea: {task_data['priority']}")
                    print(f"4. Verifica que el USUARIO ASIGNADO sea: Karla Rosas")
                    print(f"5. Verifica que la FECHA LÍMITE sea: {task_data['due_date']}")
                    print(f"6. Verifica que el campo 'Email' muestre: {task_data['custom_fields']['Email']}")
                    print(f"7. Verifica que el campo 'Celular' muestre: {task_data['custom_fields']['Celular']}")
                    
                    return task_id
                    
                else:
                    print(f"❌ Error creando tarea: {response.status}")
                    print(f"📄 Respuesta: {response_text}")
                    return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    task_id = asyncio.run(test_interface_task_creation())
    if task_id:
        print(f"\n🔍 Para verificar en ClickUp, usa el ID: {task_id}")
        print(f"📋 Puedes usar: python scripts/verify_clickup_task.py")
        print(f"   (Recuerda actualizar el task_id en el script)")
