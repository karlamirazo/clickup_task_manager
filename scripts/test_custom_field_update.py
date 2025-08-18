#!/usr/bin/env python3
"""
Script para probar específicamente la actualización de campos personalizados
"""

import asyncio
import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.clickup_client import ClickUpClient
from custom_field_config import get_custom_field_id

async def test_custom_field_update():
    """Probar la actualización de campos personalizados"""
    
    print("🧪 PROBANDO ACTUALIZACIÓN DE CAMPOS PERSONALIZADOS")
    print("=" * 60)
    
    # ID de la tarea que acabamos de crear
    task_id = "86b6af922"
    list_id = "901411770471"  # PROYECTO 1
    
    try:
        # Inicializar cliente ClickUp
        client = ClickUpClient()
        
        print(f"📋 Actualizando campos personalizados para tarea: {task_id}")
        
        # Obtener IDs de campos personalizados
        email_field_id = get_custom_field_id(list_id, "Email")
        celular_field_id = get_custom_field_id(list_id, "Celular")
        
        print(f"📧 Email Field ID: {email_field_id}")
        print(f"📱 Celular Field ID: {celular_field_id}")
        
        # Actualizar campo Email
        if email_field_id:
            print(f"\n📧 Actualizando campo Email...")
            try:
                result = await client.update_custom_field_value(task_id, email_field_id, "prueba.auto@test.com")
                print(f"✅ Email actualizado: {result}")
            except Exception as e:
                print(f"❌ Error actualizando Email: {e}")
        
        # Actualizar campo Celular
        if celular_field_id:
            print(f"\n📱 Actualizando campo Celular...")
            try:
                result = await client.update_custom_field_value(task_id, celular_field_id, "+52 55 9876 5432")
                print(f"✅ Celular actualizado: {result}")
            except Exception as e:
                print(f"❌ Error actualizando Celular: {e}")
        
        # Esperar un momento
        print(f"\n⏳ Esperando 3 segundos...")
        await asyncio.sleep(3)
        
        # Verificar el resultado
        print(f"\n🔍 Verificando resultado...")
        task_details = await client.get_task(task_id)
        
        if task_details:
            custom_fields = task_details.get('custom_fields', [])
            print(f"📧 Campos personalizados encontrados: {len(custom_fields)}")
            
            for field in custom_fields:
                field_name = field.get('name')
                field_value = field.get('value')
                print(f"   📧 {field_name}: {field_value}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_custom_field_update())
