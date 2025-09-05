#!/usr/bin/env python3
"""
Script para probar la actualizacion manual de campos personalizados directamente
"""

import asyncio
import os
import sys
from datetime import datetime

# Agregar el directorio raiz al path para importar modulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.clickup.client import ClickUpClient
from api.routes.tasks import get_custom_field_id, has_custom_fields

async def test_manual_update_direct():
    """Test la actualizacion manual directamente"""
    
    print("üß™ PROBANDO ACTUALIZACION MANUAL DIRECTA")
    print("=" * 60)
    
    # ID de la tarea que acabamos de crear (la ultima)
    task_id = "86b6afn4r"
    list_id = "901411770471"  # PROYECTO 1
    
    # Datos para actualizar
    custom_fields = {
        "Email": "direct.update@test.com",
        "Celular": "+52 55 8888 8888"
    }
    
    try:
        # Inicializar cliente ClickUp
        client = ClickUpClient()
        
        print(f"üì§ Actualizando campos personalizados...")
        print(f"   üÜî Task ID: {task_id}")
        print(f"   üìã List ID: {list_id}")
        print(f"   üìß Campos: {custom_fields}")
        
        # Verificar si la lista tiene campos personalizados
        if not has_custom_fields(list_id):
            print(f"‚ùå La lista {list_id} no tiene campos personalizados configureds")
            return
        
        print(f"‚úÖ La lista tiene campos personalizados configureds")
        
        # Update cada campo
        updated_fields = {}
        errors = []
        
        for field_name, field_value in custom_fields.items():
            field_id = get_custom_field_id(list_id, field_name)
            if field_id:
                try:
                    print(f"\nüìß Actualizando {field_name} (ID: {field_id}) con valor: {field_value}")
                    result = await client.update_custom_field_value(task_id, field_id, field_value)
                    updated_fields[field_name] = {
                        "status": "success",
                        "field_id": field_id,
                        "result": result
                    }
                    print(f"‚úÖ Campo {field_name} actualizado exitosamente")
                except Exception as e:
                    error_msg = f"Error updating {field_name}: {str(e)}"
                    errors.append(error_msg)
                    updated_fields[field_name] = {
                        "status": "error",
                        "field_id": field_id,
                        "error": str(e)
                    }
                    print(f"‚ùå {error_msg}")
            else:
                error_msg = f"No se encontro ID para el campo: {field_name}"
                errors.append(error_msg)
                updated_fields[field_name] = {
                    "status": "error",
                    "field_id": None,
                    "error": error_msg
                }
                print(f"‚ö†Ô∏è {error_msg}")
        
        # Mostrar resumen
        print(f"\nüìä RESUMEN DE ACTUALIZACION")
        print(f"   ‚úÖ Campos actualizados: {len([f for f in updated_fields.values() if f['status'] == 'success'])}")
        print(f"   ‚ùå Errores: {len([f for f in updated_fields.values() if f['status'] == 'error'])}")
        
        for field_name, result in updated_fields.items():
            status_icon = "‚úÖ" if result["status"] == "success" else "‚ùå"
            print(f"   {status_icon} {field_name}: {result['status']}")
        
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
    asyncio.run(test_manual_update_direct())
