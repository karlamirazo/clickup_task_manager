#!/usr/bin/env python3
"""
Script para probar el endpoint de actualización manual de campos personalizados
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_manual_update_endpoint():
    """Probar el endpoint de actualización manual"""
    
    print("🧪 PROBANDO ENDPOINT DE ACTUALIZACIÓN MANUAL")
    print("=" * 60)
    
    # URL de la API
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # ID de la tarea que acabamos de crear (la última)
    task_id = "86b6afbct"
    list_id = "901411770471"  # PROYECTO 1
    
    # Datos para actualizar
    custom_fields = {
        "Email": "manual.update@test.com",
        "Celular": "+52 55 9999 9999"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"📤 Actualizando campos personalizados...")
            print(f"   🆔 Task ID: {task_id}")
            print(f"   📋 List ID: {list_id}")
            print(f"   📧 Campos: {custom_fields}")
            
            # Llamar al endpoint de actualización manual
            async with session.post(
                f"{base_url}/api/v1/tasks/{task_id}/update-custom-fields",
                json=custom_fields,
                params={"list_id": list_id},
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"📡 Status: {response.status}")
                response_text = await response.text()
                print(f"📄 Respuesta: {response_text}")
                
                if response.status == 200:
                    result = json.loads(response_text)
                    print(f"✅ Actualización manual exitosa!")
                    print(f"   📊 Campos actualizados: {result.get('success_count')}")
                    print(f"   ❌ Errores: {result.get('error_count')}")
                    print(f"   📧 Detalles: {result.get('updated_fields')}")
                    
                    # Esperar un momento
                    print(f"\n⏳ Esperando 3 segundos...")
                    await asyncio.sleep(3)
                    
                    # Verificar el resultado en ClickUp
                    print(f"\n🔍 Verificando resultado en ClickUp...")
                    
                    # Usar el cliente ClickUp directamente
                    import os
                    import sys
                    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    from core.clickup_client import ClickUpClient
                    
                    client = ClickUpClient()
                    task_details = await client.get_task(task_id)
                    
                    if task_details:
                        custom_fields_result = task_details.get('custom_fields', [])
                        print(f"📧 Campos personalizados encontrados: {len(custom_fields_result)}")
                        
                        for field in custom_fields_result:
                            field_name = field.get('name')
                            field_value = field.get('value')
                            print(f"   📧 {field_name}: {field_value}")
                        
                        # Verificar si los campos tienen los valores esperados
                        email_field = next((f for f in custom_fields_result if f.get('name') == 'Email'), None)
                        celular_field = next((f for f in custom_fields_result if f.get('name') == 'Celular'), None)
                        
                        if email_field and email_field.get('value') == custom_fields['Email']:
                            print(f"\n✅ Campo Email actualizado correctamente: {email_field.get('value')}")
                        else:
                            print(f"\n❌ Campo Email no se actualizó correctamente")
                        
                        if celular_field and celular_field.get('value') == custom_fields['Celular']:
                            print(f"✅ Campo Celular actualizado correctamente: {celular_field.get('value')}")
                        else:
                            print(f"❌ Campo Celular no se actualizó correctamente")
                    
                else:
                    print(f"❌ Error en actualización manual: {response.status}")
                    print(f"📄 Respuesta: {response_text}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_manual_update_endpoint())
