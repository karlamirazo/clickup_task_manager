#!/usr/bin/env python3
"""
Script para probar específicamente la funcionalidad de actualización post-creación
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_post_creation_update():
    """Probar específicamente la funcionalidad de actualización post-creación"""
    
    print("🧪 PROBANDO ACTUALIZACIÓN POST-CREACIÓN")
    print("=" * 60)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Datos de prueba específicos para probar la actualización
    task_data = {
        "name": f"PRUEBA POST-CREACIÓN - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Tarea específica para probar actualización post-creación",
        "workspace_id": "9014943317",
        "list_id": "901411770471",  # PROYECTO 1
        "status": "in progress",  # Debería mapearse a "en curso"
        "priority": 1,  # Prioridad alta (diferente de 3)
        "assignees": "88425547",  # Karla Rosas
        "custom_fields": {
            "Email": "post.creacion@test.com",
            "Celular": "+52 55 9999 9999"
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📤 Creando tarea para probar actualización post-creación...")
            print(f"📋 Datos de prueba:")
            print(f"   📝 Nombre: {task_data['name']}")
            print(f"   📊 Estado: {task_data['status']} (debería mapearse a 'en curso')")
            print(f"   ⚡ Prioridad: {task_data['priority']} (diferente de 3)")
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
                    print(f"   🆔 ClickUp ID: {task_id}")
                    
                    # Esperar para que se procese la actualización post-creación
                    print(f"\n⏳ Esperando 15 segundos para actualización post-creación...")
                    await asyncio.sleep(15)
                    
                    print(f"\n🔍 Verificando resultado de actualización post-creación...")
                    print(f"🎯 INSTRUCCIONES PARA VERIFICAR EN CLICKUP:")
                    print(f"1. Ve a ClickUp y busca la tarea: '{task_data['name']}'")
                    print(f"2. Verifica que el ESTADO sea: 'en curso' (NO 'pendiente')")
                    print(f"3. Verifica que la PRIORIDAD sea: {task_data['priority']}")
                    print(f"4. Verifica que el campo 'Email' muestre: {task_data['custom_fields']['Email']}")
                    print(f"5. Verifica que el campo 'Celular' muestre: {task_data['custom_fields']['Celular']}")
                    
                    print(f"\n📋 Para verificar programáticamente, usa:")
                    print(f"   python scripts/verify_clickup_task.py")
                    print(f"   (Recuerda actualizar el task_id a: {task_id})")
                    
                    return task_id
                    
                else:
                    print(f"❌ Error creando tarea: {response.status}")
                    print(f"📄 Respuesta: {response_text}")
                    return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    task_id = asyncio.run(test_post_creation_update())
    if task_id:
        print(f"\n🔍 Para verificar en ClickUp, usa el ID: {task_id}")
        print(f"📋 Puedes usar: python scripts/verify_clickup_task.py")
        print(f"   (Recuerda actualizar el task_id en el script)")
