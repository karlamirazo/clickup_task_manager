#!/usr/bin/env python3
"""
Script para probar la función de actualización localmente
"""

import asyncio
import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.clickup_client import ClickUpClient
from api.routes.tasks import get_custom_field_id, has_custom_fields, update_custom_fields_direct

async def test_update_function_local():
    """Probar la función de actualización localmente"""
    
    print("🧪 PROBANDO FUNCIÓN DE ACTUALIZACIÓN LOCALMENTE")
    print("=" * 60)
    
    # ID de la tarea que acabamos de crear
    task_id = "86b6afh40"
    list_id = "901411770471"  # PROYECTO 1
    
    # Datos para actualizar
    custom_fields = {
        "Email": "local.test@test.com",
        "Celular": "+52 55 7777 7777"
    }
    
    try:
        # Inicializar cliente ClickUp
        client = ClickUpClient()
        
        print(f"📤 Probando función de actualización directa...")
        print(f"   🆔 Task ID: {task_id}")
        print(f"   📋 List ID: {list_id}")
        print(f"   📧 Campos: {custom_fields}")
        
        # Verificar si la lista tiene campos personalizados
        if not has_custom_fields(list_id):
            print(f"❌ La lista {list_id} no tiene campos personalizados configurados")
            return
        
        print(f"✅ La lista tiene campos personalizados configurados")
        
        # Probar la función de actualización directa
        print(f"\n🔧 Ejecutando función update_custom_fields_direct...")
        update_result = await update_custom_fields_direct(client, task_id, list_id, custom_fields)
        
        success_count = update_result.get('success_count', 0)
        error_count = update_result.get('error_count', 0)
        
        print(f"\n📊 RESULTADO DE LA FUNCIÓN:")
        print(f"   ✅ Campos actualizados: {success_count}")
        print(f"   ❌ Errores: {error_count}")
        
        if error_count > 0:
            print(f"   📋 Errores: {update_result.get('errors', [])}")
        
        # Esperar un momento
        print(f"\n⏳ Esperando 3 segundos...")
        await asyncio.sleep(3)
        
        # Verificar el resultado en ClickUp
        print(f"\n🔍 Verificando resultado en ClickUp...")
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
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_update_function_local())
