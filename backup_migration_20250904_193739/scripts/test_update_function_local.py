#!/usr/bin/env python3
"""
Script para probar la funcion de actualizacion localmente
"""

import asyncio
import os
import sys
from datetime import datetime

# Agregar el directorio raiz al path para importar modulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.clickup_client import ClickUpClient
from api.routes.tasks import get_custom_field_id, has_custom_fields, update_custom_fields_direct

async def test_update_function_local():
    """Test la funcion de actualizacion localmente"""
    
    print("üß™ PROBANDO FUNCION DE ACTUALIZACION LOCALMENTE")
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
        
        print(f"üì§ Probando funcion de actualizacion directa...")
        print(f"   üÜî Task ID: {task_id}")
        print(f"   üìã List ID: {list_id}")
        print(f"   üìß Campos: {custom_fields}")
        
        # Verificar si la lista tiene campos personalizados
        if not has_custom_fields(list_id):
            print(f"‚ùå La lista {list_id} no tiene campos personalizados configureds")
            return
        
        print(f"‚úÖ La lista tiene campos personalizados configureds")
        
        # Test la funcion de actualizacion directa
        print(f"\nüîß Ejecutando funcion update_custom_fields_direct...")
        update_result = await update_custom_fields_direct(client, task_id, list_id, custom_fields)
        
        success_count = update_result.get('success_count', 0)
        error_count = update_result.get('error_count', 0)
        
        print(f"\nüìä RESULTADO DE LA FUNCION:")
        print(f"   ‚úÖ Campos actualizados: {success_count}")
        print(f"   ‚ùå Errores: {error_count}")
        
        if error_count > 0:
            print(f"   üìã Errores: {update_result.get('errors', [])}")
        
        # Esperar un momento
        print(f"\n‚è≥ Esperando 3 segundos...")
        await asyncio.sleep(3)
        
        # Verificar el resultado en ClickUp
        print(f"\nüîç Verificando resultado en ClickUp...")
        task_details = await client.get_task(task_id)
        
        if task_details:
            custom_fields_result = task_details.get('custom_fields', [])
            print(f"üìß Campos personalizados encontrados: {len(custom_fields_result)}")
            
            for field in custom_fields_result:
                field_name = field.get('name')
                field_value = field.get('value')
                print(f"   üìß {field_name}: {field_value}")
            
            # Verificar si los campos tienen los valores esperados
            email_field = next((f for f in custom_fields_result if f.get('name') == 'Email'), None)
            celular_field = next((f for f in custom_fields_result if f.get('name') == 'Celular'), None)
            
            if email_field and email_field.get('value') == custom_fields['Email']:
                print(f"\n‚úÖ Campo Email actualizado correctamente: {email_field.get('value')}")
            else:
                print(f"\n‚ùå Campo Email no se actualizo correctamente")
            
            if celular_field and celular_field.get('value') == custom_fields['Celular']:
                print(f"‚úÖ Campo Celular actualizado correctamente: {celular_field.get('value')}")
            else:
                print(f"‚ùå Campo Celular no se actualizo correctamente")
        
    except Exception as e:
        print(f"‚ùå Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_update_function_local())
