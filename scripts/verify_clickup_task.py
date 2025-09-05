#!/usr/bin/env python3
"""
Script para verificar el estado de una tarea en ClickUp
"""

import asyncio
import os
import sys
from datetime import datetime

# Agregar el directorio raiz al path para importar modulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.clickup.client import ClickUpClient

async def verify_clickup_task():
    """Verificar el estado de una tarea especifica en ClickUp"""
    
    print("ğŸ”� VERIFICANDO TAREA EN CLICKUP")
    print("=" * 50)
    
    # ID de la tarea que acabamos de crear
    task_id = "86b6agdar"  # ID de la nueva tarea despues del deployment final
    
    try:
        # Inicializar cliente ClickUp
        client = ClickUpClient()
        
        print(f"ğŸ“‹ Obteniendo detalles de la tarea: {task_id}")
        
        # Get detalles de la tarea
        task_details = await client.get_task(task_id)
        
        if task_details:
            print(f"âœ… Tarea encontrada en ClickUp:")
            print(f"   ğŸ“� Nombre: {task_details.get('name')}")
            print(f"   ğŸ“Š Estado: {task_details.get('status', {}).get('status', 'N/A')}")
            print(f"   ğŸ‘¤ Asignado: {task_details.get('assignees', [])}")
            print(f"   ğŸ“… Fecha limite: {task_details.get('due_date')}")
            
            # Verificar campos personalizados
            custom_fields = task_details.get('custom_fields', [])
            print(f"\nğŸ“§ Campos personalizados encontrados: {len(custom_fields)}")
            
            for field in custom_fields:
                field_id = field.get('id')
                field_name = field.get('name')
                field_value = field.get('value')
                field_type = field.get('type')
                
                print(f"   ğŸ“§ {field_name} (ID: {field_id}, Tipo: {field_type}): {field_value}")
                
                # Verificar si son los campos que esperamos
                if field_name in ["Email", "Celular"]:
                    expected_values = {
                        "Email": "direct.update@test.com",
                        "Celular": "+52 55 6666 6666"
                    }
                    
                    if field_value == expected_values.get(field_name):
                        print(f"      âœ… Valor correcto!")
                    else:
                        print(f"      â�Œ Valor incorrecto. Esperado: {expected_values.get(field_name)}")
            
            # Verificar si faltan campos
            expected_fields = ["Email", "Celular"]
            found_fields = [field.get('name') for field in custom_fields]
            
            print(f"\nğŸ”� Analisis de campos:")
            for expected_field in expected_fields:
                if expected_field in found_fields:
                    print(f"   âœ… Campo '{expected_field}' encontrado")
                else:
                    print(f"   â�Œ Campo '{expected_field}' NO encontrado")
        
        else:
            print(f"â�Œ No se pudo obtener la tarea")
    
    except Exception as e:
        print(f"â�Œ Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_clickup_task())
