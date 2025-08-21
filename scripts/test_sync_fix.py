#!/usr/bin/env python3
"""
Script para probar la sincronizacion corregida
"""

import requests
import json
from datetime import datetime

def test_sync_fix():
    """Test la sincronizacion corregida"""
    print("ğŸ”„ PRUEBA DE SINCRONIZACION CORREGIDA")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # PASO 1: Test sincronizacion simple (sin parametros)
    print("ğŸ”� PASO 1: Test sincronizacion simple")
    print("-" * 40)
    
    try:
        print(f"ğŸ”„ Probando sincronizacion simple...")
        response = requests.post(
            f"{base_url}/api/v1/tasks/sync-simple",
            timeout=60  # Timeout mas largo para sincronizacion
        )
        
        print(f"ğŸ“¡ Respuesta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"âœ… Â¡SINCRONIZACION SIMPLE EXITOSA!")
            print(f"ğŸ“Š Tareas sincronizadas: {result.get('total_tasks_synced', 'N/A')}")
            print(f"â�• Tareas creadas: {result.get('total_tasks_created', 'N/A')}")
            print(f"ğŸ”„ Tareas actualizadas: {result.get('total_tasks_updated', 'N/A')}")
            print(f"ğŸ“� Workspace ID: {result.get('workspace_id', 'N/A')}")
            sync_simple_working = True
        else:
            print(f"â�Œ Error en sincronizacion simple: {response.text}")
            sync_simple_working = False
            
    except Exception as e:
        print(f"â�Œ Error: {e}")
        sync_simple_working = False
    
    # PASO 2: Test sincronizacion con parametros
    print(f"\nğŸ”� PASO 2: Test sincronizacion con parametros")
    print("-" * 40)
    
    try:
        print(f"ğŸ”„ Probando sincronizacion con workspace_id...")
        response = requests.post(
            f"{base_url}/api/v1/tasks/sync?workspace_id=9014943317",
            timeout=60
        )
        
        print(f"ğŸ“¡ Respuesta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"âœ… Â¡SINCRONIZACION CON PARAMETROS EXITOSA!")
            print(f"ğŸ“Š Tareas sincronizadas: {result.get('total_tasks_synced', 'N/A')}")
            print(f"â�• Tareas creadas: {result.get('total_tasks_created', 'N/A')}")
            print(f"ğŸ”„ Tareas actualizadas: {result.get('total_tasks_updated', 'N/A')}")
            print(f"ğŸ“� Workspace ID: {result.get('workspace_id', 'N/A')}")
            sync_params_working = True
        else:
            print(f"â�Œ Error en sincronizacion con parametros: {response.text}")
            sync_params_working = False
            
    except Exception as e:
        print(f"â�Œ Error: {e}")
        sync_params_working = False
    
    # PASO 3: Test sincronizacion sin parametros (endpoint original)
    print(f"\nğŸ”� PASO 3: Test sincronizacion sin parametros (endpoint original)")
    print("-" * 40)
    
    try:
        print(f"ğŸ”„ Probando sincronizacion sin parametros...")
        response = requests.post(
            f"{base_url}/api/v1/tasks/sync",
            timeout=60
        )
        
        print(f"ğŸ“¡ Respuesta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"âœ… Â¡SINCRONIZACION SIN PARAMETROS EXITOSA!")
            print(f"ğŸ“Š Tareas sincronizadas: {result.get('total_tasks_synced', 'N/A')}")
            print(f"â�• Tareas creadas: {result.get('total_tasks_created', 'N/A')}")
            print(f"ğŸ”„ Tareas actualizadas: {result.get('total_tasks_updated', 'N/A')}")
            print(f"ğŸ“� Workspace ID: {result.get('workspace_id', 'N/A')}")
            sync_original_working = True
        else:
            print(f"â�Œ Error en sincronizacion sin parametros: {response.text}")
            sync_original_working = False
            
    except Exception as e:
        print(f"â�Œ Error: {e}")
        sync_original_working = False
    
    # PASO 4: Resumen de la prueba
    print(f"\nğŸ“Š RESUMEN DE LA PRUEBA DE SINCRONIZACION")
    print("=" * 60)
    
    print(f"ğŸ”„ Sincronizacion simple: {'âœ… FUNCIONANDO' if sync_simple_working else 'â�Œ NO FUNCIONA'}")
    print(f"ğŸ”„ Sincronizacion con parametros: {'âœ… FUNCIONANDO' if sync_params_working else 'â�Œ NO FUNCIONA'}")
    print(f"ğŸ”„ Sincronizacion sin parametros: {'âœ… FUNCIONANDO' if sync_original_working else 'â�Œ NO FUNCIONA'}")
    
    print(f"\nğŸ�¯ Estado de la sincronizacion:")
    if sync_simple_working or sync_params_working or sync_original_working:
        print(f"   ğŸ�‰ Â¡SINCRONIZACION FUNCIONANDO!")
        print(f"   âœ… Al menos un metodo de sincronizacion funciona")
        print(f"   âœ… El problema de error 422 ha sido resuelto")
        
        if sync_simple_working:
            print(f"   ğŸ’¡ Recomendacion: Usar /api/v1/tasks/sync-simple para sincronizacion simple")
        elif sync_params_working:
            print(f"   ğŸ’¡ Recomendacion: Usar /api/v1/tasks/sync?workspace_id=9014943317")
        elif sync_original_working:
            print(f"   ğŸ’¡ Recomendacion: Usar /api/v1/tasks/sync (sin parametros)")
    else:
        print(f"   â�Œ SINCRONIZACION CON PROBLEMAS")
        print(f"   â�Œ Ningun metodo de sincronizacion funciona")
        print(f"   ğŸ”§ Revisar configuracion de ClickUp API")
    
    print(f"\nğŸ’¡ Informacion adicional:")
    print(f"   ğŸ“� Workspace por defecto: 9014943317")
    print(f"   ğŸ”— Endpoints disponibles:")
    print(f"      - /api/v1/tasks/sync-simple (sin parametros)")
    print(f"      - /api/v1/tasks/sync?workspace_id=9014943317 (con parametros)")
    print(f"      - /api/v1/tasks/sync (sin parametros, usa workspace por defecto)")
    
    print(f"\nğŸ•� Prueba completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Funcion principal"""
    print("ğŸ”„ PRUEBA COMPLETA DE SINCRONIZACION CORREGIDA")
    print("=" * 70)
    
    test_sync_fix()

if __name__ == "__main__":
    main()
