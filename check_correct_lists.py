#!/usr/bin/env python3
"""
Verificar todas las listas y encontrar dónde están las tareas
"""

import asyncio
import sys
import os

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrations.clickup.client import ClickUpClient
from core.config import settings

async def check_all_lists():
    """Verificar todas las listas y tareas"""
    
    print("🔍 VERIFICANDO TODAS LAS LISTAS Y TAREAS")
    print("=" * 60)
    
    try:
        client = ClickUpClient()
        print("✅ Cliente ClickUp creado exitosamente")
        
        # Obtener espacios
        print(f"\n🏢 Obteniendo espacios del workspace: {settings.CLICKUP_WORKSPACE_ID}")
        spaces = await client.get_spaces(settings.CLICKUP_WORKSPACE_ID)
        
        for space in spaces:
            print(f"\n📁 ESPACIO: {space.get('name', 'Sin nombre')} (ID: {space['id']})")
            print("-" * 50)
            
            # Obtener listas del espacio
            lists = await client.get_lists(space['id'])
            
            for list_item in lists:
                print(f"\n📋 LISTA: {list_item.get('name', 'Sin nombre')} (ID: {list_item['id']})")
                print("-" * 30)
                
                # Obtener tareas de la lista
                try:
                    tasks = await client.get_tasks(list_item['id'])
                    print(f"   📝 Tareas: {len(tasks)} tareas")
                    
                    if tasks:
                        for i, task in enumerate(tasks[:5], 1):  # Mostrar solo las primeras 5
                            print(f"      {i}. {task.get('name', 'Sin nombre')} (ID: {task.get('id', 'Sin ID')})")
                        
                        if len(tasks) > 5:
                            print(f"      ... y {len(tasks) - 5} tareas más")
                    else:
                        print("      ⚠️ No hay tareas en esta lista")
                        
                except Exception as e:
                    print(f"      ❌ Error obteniendo tareas: {e}")
        
        # Verificar específicamente las listas donde están nuestras tareas
        print(f"\n🔍 VERIFICANDO LISTAS ESPECÍFICAS DE NUESTRAS TAREAS:")
        print("=" * 60)
        
        target_lists = [
            "901411770471",  # Lista con 8 tareas
            "901411770470",  # Lista con 1 tarea
            "901412119767"   # Lista "Tareas del Proyecto" (vacía)
        ]
        
        for list_id in target_lists:
            print(f"\n📋 LISTA ID: {list_id}")
            print("-" * 30)
            
            try:
                tasks = await client.get_tasks(list_id)
                print(f"   📝 Tareas: {len(tasks)} tareas")
                
                if tasks:
                    for i, task in enumerate(tasks[:3], 1):  # Mostrar solo las primeras 3
                        print(f"      {i}. {task.get('name', 'Sin nombre')} (ID: {task.get('id', 'Sin ID')})")
                    
                    if len(tasks) > 3:
                        print(f"      ... y {len(tasks) - 3} tareas más")
                else:
                    print("      ⚠️ No hay tareas en esta lista")
                    
            except Exception as e:
                print(f"      ❌ Error obteniendo tareas: {e}")
                
    except Exception as e:
        print(f"❌ Error general: {e}")
        print(f"🔍 Tipo de error: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(check_all_lists())

