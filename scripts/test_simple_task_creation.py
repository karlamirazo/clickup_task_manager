#!/usr/bin/env python3
"""
Script para probar creación simple de tareas y verificar actualización post-creación
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_simple_task_creation():
    """Probar creación simple de tareas"""
    
    print("🧪 PROBANDO CREACIÓN SIMPLE DE TAREAS")
    print("=" * 50)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Datos de prueba SIMPLES
    task_data = {
        "name": f"TAREA SIMPLE - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Tarea simple para probar actualización post-creación",
        "workspace_id": "9014943317",
        "list_id": "901411770471",  # PROYECTO 1
        "status": "in progress",  # Debería mapearse a "en curso"
        "priority": 2,  # Prioridad media
        "assignees": "88425547",  # Karla Rosas
        "custom_fields": {
            "Email": "simple@test.com",
            "Celular": "+52 55 1111 1111"
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📤 Creando tarea simple...")
            print(f"📋 Datos: {task_data['name']}")
            print(f"   📊 Estado: {task_data['status']} (debería mapearse a 'en curso')")
            print(f"   ⚡ Prioridad: {task_data['priority']}")
            print(f"   📧 Email: {task_data['custom_fields']['Email']}")
            
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
                    print(f"   🆔 ClickUp ID: {task_id}")
                    
                    # Esperar para que se procese la actualización post-creación
                    print(f"\n⏳ Esperando 10 segundos para actualización post-creación...")
                    await asyncio.sleep(10)
                    
                    print(f"\n🎯 INSTRUCCIONES PARA VERIFICAR:")
                    print(f"1. Ve a ClickUp y busca la tarea: '{task_data['name']}'")
                    print(f"2. Verifica que el ESTADO sea: 'en curso' (NO 'pendiente')")
                    print(f"3. Verifica que la PRIORIDAD sea: {task_data['priority']}")
                    print(f"4. Verifica que el campo 'Email' muestre: {task_data['custom_fields']['Email']}")
                    print(f"5. Verifica que el campo 'Celular' muestre: {task_data['custom_fields']['Celular']}")
                    
                    return task_id
                    
                else:
                    print(f"❌ Error creando tarea: {response.status}")
                    print(f"📄 Respuesta: {response_text}")
                    return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    task_id = asyncio.run(test_simple_task_creation())
    if task_id:
        print(f"\n🔍 Para verificar en ClickUp, usa el ID: {task_id}")
        print(f"📋 Puedes usar: python scripts/verify_clickup_task.py")
        print(f"   (Recuerda actualizar el task_id en el script)")
