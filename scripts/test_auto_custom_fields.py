#!/usr/bin/env python3
"""
Script para probar la actualización automática de campos personalizados
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_auto_custom_fields():
    """Probar la actualización automática de campos personalizados"""
    
    print("🧪 PROBANDO ACTUALIZACIÓN AUTOMÁTICA DE CAMPOS PERSONALIZADOS")
    print("=" * 70)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Datos de prueba con campos personalizados
    task_data = {
        "name": f"PRUEBA AUTO CAMPOS - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Esta tarea debe mostrar automáticamente Email y Celular en ClickUp",
        "workspace_id": "9014943317",
        "list_id": "901411770471",  # PROYECTO 1 (tiene campos personalizados)
        "status": "in progress",
        "priority": 1,
        "due_date": "2025-08-25",
        "assignees": "88425547",  # Karla Rosas
        "custom_fields": {
            "Email": "prueba.auto@test.com",
            "Celular": "+52 55 9876 5432"
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📤 Creando tarea con campos personalizados...")
            print(f"📋 Datos: {json.dumps(task_data, indent=2)}")
            
            async with session.post(
                f"{base_url}/api/v1/tasks/",
                json=task_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"📡 Status: {response.status}")
                response_text = await response.text()
                print(f"📄 Respuesta: {response_text}")
                
                if response.status == 201:
                    task_response = json.loads(response_text)
                    print(f"✅ Tarea creada exitosamente!")
                    print(f"   🆔 ID Local: {task_response.get('id')}")
                    print(f"   🆔 ClickUp ID: {task_response.get('clickup_id')}")
                    print(f"   📝 Nombre: {task_response.get('name')}")
                    print(f"   📧 Campos personalizados: {task_response.get('custom_fields')}")
                    
                    print(f"\n🎯 INSTRUCCIONES PARA VERIFICAR:")
                    print(f"1. Ve a ClickUp y busca la tarea: '{task_data['name']}'")
                    print(f"2. Verifica que los campos 'Email' y 'Celular' estén llenos")
                    print(f"3. Email debe mostrar: {task_data['custom_fields']['Email']}")
                    print(f"4. Celular debe mostrar: {task_data['custom_fields']['Celular']}")
                    
                    # Esperar un momento para que ClickUp procese
                    print(f"\n⏳ Esperando 5 segundos para que ClickUp procese...")
                    await asyncio.sleep(5)
                    
                    # Verificar que la tarea se guardó correctamente en la BD local
                    print(f"\n🔍 Verificando tarea en BD local...")
                    async with session.get(f"{base_url}/api/v1/tasks/{task_response.get('id')}") as detail_response:
                        if detail_response.status == 200:
                            detail_data = json.loads(await detail_response.text())
                            print(f"✅ Tarea encontrada en BD local:")
                            print(f"   📧 Campos personalizados: {detail_data.get('custom_fields')}")
                            print(f"   📊 Estado: {detail_data.get('status')}")
                            print(f"   👤 Usuario asignado: {detail_data.get('assignee_id')}")
                        else:
                            print(f"❌ Error obteniendo detalles: {detail_response.status}")
                    
                else:
                    print(f"❌ Error creando tarea: {response.status}")
                    print(f"📄 Respuesta: {response_text}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_auto_custom_fields())
