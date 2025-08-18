#!/usr/bin/env python3
"""
Script para verificar el estado de una tarea en ClickUp
"""

import asyncio
import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.clickup_client import ClickUpClient

async def verify_clickup_task():
    """Verificar el estado de una tarea específica en ClickUp"""
    
    print("🔍 VERIFICANDO TAREA EN CLICKUP")
    print("=" * 50)
    
    # ID de la tarea que acabamos de crear
    task_id = "86b6afv2e"  # ID de la nueva tarea con actualización post-creación
    
    try:
        # Inicializar cliente ClickUp
        client = ClickUpClient()
        
        print(f"📋 Obteniendo detalles de la tarea: {task_id}")
        
        # Obtener detalles de la tarea
        task_details = await client.get_task(task_id)
        
        if task_details:
            print(f"✅ Tarea encontrada en ClickUp:")
            print(f"   📝 Nombre: {task_details.get('name')}")
            print(f"   📊 Estado: {task_details.get('status', {}).get('status', 'N/A')}")
            print(f"   👤 Asignado: {task_details.get('assignees', [])}")
            print(f"   📅 Fecha límite: {task_details.get('due_date')}")
            
            # Verificar campos personalizados
            custom_fields = task_details.get('custom_fields', [])
            print(f"\n📧 Campos personalizados encontrados: {len(custom_fields)}")
            
            for field in custom_fields:
                field_id = field.get('id')
                field_name = field.get('name')
                field_value = field.get('value')
                field_type = field.get('type')
                
                print(f"   📧 {field_name} (ID: {field_id}, Tipo: {field_type}): {field_value}")
                
                # Verificar si son los campos que esperamos
                if field_name in ["Email", "Celular"]:
                    expected_values = {
                        "Email": "prueba.auto@test.com",
                        "Celular": "+52 55 9876 5432"
                    }
                    
                    if field_value == expected_values.get(field_name):
                        print(f"      ✅ Valor correcto!")
                    else:
                        print(f"      ❌ Valor incorrecto. Esperado: {expected_values.get(field_name)}")
            
            # Verificar si faltan campos
            expected_fields = ["Email", "Celular"]
            found_fields = [field.get('name') for field in custom_fields]
            
            print(f"\n🔍 Análisis de campos:")
            for expected_field in expected_fields:
                if expected_field in found_fields:
                    print(f"   ✅ Campo '{expected_field}' encontrado")
                else:
                    print(f"   ❌ Campo '{expected_field}' NO encontrado")
        
        else:
            print(f"❌ No se pudo obtener la tarea")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_clickup_task())
