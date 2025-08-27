#!/usr/bin/env python3
"""
Script de diagnóstico para problemas de creación de tareas en ClickUp
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.clickup_client import ClickUpClient
from core.config import settings

async def test_clickup_connection():
    """Probar la conexión con ClickUp"""
    print("🔍 Probando conexión con ClickUp...")
    
    try:
        # Crear cliente
        client = ClickUpClient(settings.CLICKUP_API_TOKEN)
        
        # Verificar token
        print(f"✅ Token configurado: {settings.CLICKUP_API_TOKEN[:20]}...")
        
        # Probar petición básica
        print("🔍 Probando petición básica...")
        response = await client._make_request("GET", "user")
        print(f"✅ Usuario autenticado: {response.get('user', {}).get('username', 'N/A')}")
        
        return client
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

async def test_task_creation(client: ClickUpClient):
    """Probar la creación de una tarea simple"""
    print("\n🔍 Probando creación de tarea...")
    
    try:
        # Datos de prueba
        test_data = {
            "name": "Tarea de Prueba - Debug",
            "description": "Esta es una tarea de prueba para diagnosticar problemas",
            "priority": 3
        }
        
        # Lista de prueba (usar una lista válida)
        list_id = "901411770471"  # PROYECTO 1
        
        print(f"📋 Enviando tarea a lista: {list_id}")
        print(f"📋 Datos: {test_data}")
        
        # Crear tarea
        result = await client.create_task(list_id, test_data)
        
        print(f"✅ Tarea creada exitosamente!")
        print(f"📋 ID de ClickUp: {result.get('id', 'N/A')}")
        print(f"📋 Resultado completo: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error creando tarea: {e}")
        print(f"🔍 Tipo de error: {type(e).__name__}")
        return None

async def test_custom_fields(client: ClickUpClient, list_id: str):
    """Probar campos personalizados"""
    print(f"\n🔍 Probando campos personalizados para lista: {list_id}")
    
    try:
        # Verificar campos disponibles
        fields_response = await client._make_request("GET", f"list/{list_id}/field")
        
        if "fields" in fields_response:
            print(f"✅ Campos encontrados: {len(fields_response['fields'])}")
            for field in fields_response['fields']:
                field_type = field.get('type', 'N/A')
                field_name = field.get('name', 'N/A')
                field_id = field.get('id', 'N/A')
                print(f"   📝 {field_name} ({field_type}) - ID: {field_id}")
        else:
            print(f"⚠️ No se encontraron campos en la respuesta")
            print(f"📋 Respuesta: {fields_response}")
            
    except Exception as e:
        print(f"❌ Error obteniendo campos: {e}")

async def main():
    """Función principal"""
    print("🚀 Iniciando diagnóstico de ClickUp...")
    
    # Probar conexión
    client = await test_clickup_connection()
    if not client:
        print("❌ No se pudo establecer conexión con ClickUp")
        return
    
    # Probar creación de tarea
    task_result = await test_task_creation(client)
    
    # Probar campos personalizados
    if task_result:
        list_id = "901411770471"
        await test_custom_fields(client, list_id)
    
    print("\n✅ Diagnóstico completado!")

if __name__ == "__main__":
    asyncio.run(main())
