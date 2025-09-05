#!/usr/bin/env python3
"""
Script para forzar actualizacion directa usando ClickUpClient
"""

import asyncio
import os
import sys
from datetime import datetime

# Agregar el directorio raiz al path para importar modulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.clickup.client import ClickUpClient

async def force_update_direct():
    """Forzar actualizacion directa usando ClickUpClient"""
    
    print("ğŸ§ª FORZANDO ACTUALIZACION DIRECTA")
    print("=" * 50)
    
    # ID de la tarea que acabamos de crear
    task_id = "86b6agdar"
    list_id = "901411770471"  # PROYECTO 1
    
    # Datos para actualizar
    custom_fields = {
        "Email": "direct.update@test.com",
        "Celular": "+52 55 6666 6666"
    }
    
    try:
        # Inicializar cliente ClickUp
        client = ClickUpClient()
        
        print(f"ğŸ“¤ Actualizando campos personalizados directamente...")
        print(f"   ğŸ†” Task ID: {task_id}")
        print(f"   ğŸ“‹ List ID: {list_id}")
        print(f"   ğŸ“§ Campos: {custom_fields}")
        
        # Configuracion de campos personalizados (copiada del archivo tasks.py)
        CUSTOM_FIELD_IDS = {
            "901411770471": {  # PROYECTO 1
                "Email": "6464a671-73dd-4be5-b720-b5f0fe5adb04",
                "Celular": "51fa0661-0995-4c37-ba8d-3307aef300ca"
            }
        }
        
        def get_custom_field_id(list_id: str, field_name: str) -> str:
            """Get ID del campo personalizado por nombre"""
            return CUSTOM_FIELD_IDS.get(list_id, {}).get(field_name)
        
        # Update campos personalizados uno por uno
        updated_fields = {}
        errors = []
        
        for field_name, field_value in custom_fields.items():
            field_id = get_custom_field_id(list_id, field_name)
            if field_id:
                try:
                    print(f"   ğŸ“§ Actualizando {field_name} (ID: {field_id}) con valor: {field_value}")
                    result = await client.update_custom_field_value(task_id, field_id, field_value)
                    updated_fields[field_name] = {
                        "status": "success",
                        "field_id": field_id,
                        "result": result
                    }
                    print(f"   âœ… Campo {field_name} actualizado exitosamente")
                except Exception as e:
                    error_msg = f"Error updating {field_name}: {str(e)}"
                    errors.append(error_msg)
                    updated_fields[field_name] = {
                        "status": "error",
                        "field_id": field_id,
                        "error": str(e)
                    }
                    print(f"   â�Œ {error_msg}")
            else:
                error_msg = f"No se encontro ID para el campo: {field_name}"
                errors.append(error_msg)
                updated_fields[field_name] = {
                    "status": "error",
                    "field_id": None,
                    "error": error_msg
                }
                print(f"   âš ï¸� {error_msg}")
        
        # Mostrar resumen
        success_count = len([f for f in updated_fields.values() if f["status"] == "success"])
        error_count = len([f for f in updated_fields.values() if f["status"] == "error"])
        
        print(f"\nğŸ“Š RESUMEN DE ACTUALIZACION:")
        print(f"   âœ… Campos actualizados: {success_count}")
        print(f"   â�Œ Errores: {error_count}")
        
        if error_count > 0:
            print(f"   ğŸ“‹ Errores: {errors}")
        
        # Esperar un momento
        print(f"\nâ�³ Esperando 5 segundos...")
        await asyncio.sleep(5)
        
        # Verificar el resultado
        print(f"\nğŸ”� Verificando resultado en ClickUp...")
        task_details = await client.get_task(task_id)
        
        if task_details:
            custom_fields_result = task_details.get('custom_fields', [])
            print(f"ğŸ“§ Campos personalizados encontrados: {len(custom_fields_result)}")
            
            for field in custom_fields_result:
                field_name = field.get('name')
                field_value = field.get('value')
                print(f"   ğŸ“§ {field_name}: {field_value}")
            
            # Verificar si los campos tienen los valores esperados
            email_field = next((f for f in custom_fields_result if f.get('name') == 'Email'), None)
            celular_field = next((f for f in custom_fields_result if f.get('name') == 'Celular'), None)
            
            if email_field and email_field.get('value') == custom_fields['Email']:
                print(f"\nâœ… Campo Email actualizado correctamente: {email_field.get('value')}")
            else:
                print(f"\nâ�Œ Campo Email no se actualizo correctamente")
            
            if celular_field and celular_field.get('value') == custom_fields['Celular']:
                print(f"âœ… Campo Celular actualizado correctamente: {celular_field.get('value')}")
            else:
                print(f"â�Œ Campo Celular no se actualizo correctamente")
        
        return success_count > 0
        
    except Exception as e:
        print(f"â�Œ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(force_update_direct())
    if success:
        print(f"\nğŸ”� Para verificar en ClickUp, usa el ID: 86b6agdar")
        print(f"ğŸ“‹ Puedes usar: python scripts/verify_clickup_task.py")
        print(f"   (Recuerda actualizar el task_id a: 86b6agdar)")
    else:
        print(f"\nâ�Œ La actualizacion directa fallo")

