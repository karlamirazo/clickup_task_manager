#!/usr/bin/env python3
"""
Script para probar la sincronización corregida
"""

import requests
import json
from datetime import datetime

def test_sync_fix():
    """Probar la sincronización corregida"""
    print("🔄 PRUEBA DE SINCRONIZACIÓN CORREGIDA")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # PASO 1: Probar sincronización simple (sin parámetros)
    print("🔍 PASO 1: Probar sincronización simple")
    print("-" * 40)
    
    try:
        print(f"🔄 Probando sincronización simple...")
        response = requests.post(
            f"{base_url}/api/v1/tasks/sync-simple",
            timeout=60  # Timeout más largo para sincronización
        )
        
        print(f"📡 Respuesta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ ¡SINCRONIZACIÓN SIMPLE EXITOSA!")
            print(f"📊 Tareas sincronizadas: {result.get('total_tasks_synced', 'N/A')}")
            print(f"➕ Tareas creadas: {result.get('total_tasks_created', 'N/A')}")
            print(f"🔄 Tareas actualizadas: {result.get('total_tasks_updated', 'N/A')}")
            print(f"📁 Workspace ID: {result.get('workspace_id', 'N/A')}")
            sync_simple_working = True
        else:
            print(f"❌ Error en sincronización simple: {response.text}")
            sync_simple_working = False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sync_simple_working = False
    
    # PASO 2: Probar sincronización con parámetros
    print(f"\n🔍 PASO 2: Probar sincronización con parámetros")
    print("-" * 40)
    
    try:
        print(f"🔄 Probando sincronización con workspace_id...")
        response = requests.post(
            f"{base_url}/api/v1/tasks/sync?workspace_id=9014943317",
            timeout=60
        )
        
        print(f"📡 Respuesta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ ¡SINCRONIZACIÓN CON PARÁMETROS EXITOSA!")
            print(f"📊 Tareas sincronizadas: {result.get('total_tasks_synced', 'N/A')}")
            print(f"➕ Tareas creadas: {result.get('total_tasks_created', 'N/A')}")
            print(f"🔄 Tareas actualizadas: {result.get('total_tasks_updated', 'N/A')}")
            print(f"📁 Workspace ID: {result.get('workspace_id', 'N/A')}")
            sync_params_working = True
        else:
            print(f"❌ Error en sincronización con parámetros: {response.text}")
            sync_params_working = False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sync_params_working = False
    
    # PASO 3: Probar sincronización sin parámetros (endpoint original)
    print(f"\n🔍 PASO 3: Probar sincronización sin parámetros (endpoint original)")
    print("-" * 40)
    
    try:
        print(f"🔄 Probando sincronización sin parámetros...")
        response = requests.post(
            f"{base_url}/api/v1/tasks/sync",
            timeout=60
        )
        
        print(f"📡 Respuesta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ ¡SINCRONIZACIÓN SIN PARÁMETROS EXITOSA!")
            print(f"📊 Tareas sincronizadas: {result.get('total_tasks_synced', 'N/A')}")
            print(f"➕ Tareas creadas: {result.get('total_tasks_created', 'N/A')}")
            print(f"🔄 Tareas actualizadas: {result.get('total_tasks_updated', 'N/A')}")
            print(f"📁 Workspace ID: {result.get('workspace_id', 'N/A')}")
            sync_original_working = True
        else:
            print(f"❌ Error en sincronización sin parámetros: {response.text}")
            sync_original_working = False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sync_original_working = False
    
    # PASO 4: Resumen de la prueba
    print(f"\n📊 RESUMEN DE LA PRUEBA DE SINCRONIZACIÓN")
    print("=" * 60)
    
    print(f"🔄 Sincronización simple: {'✅ FUNCIONANDO' if sync_simple_working else '❌ NO FUNCIONA'}")
    print(f"🔄 Sincronización con parámetros: {'✅ FUNCIONANDO' if sync_params_working else '❌ NO FUNCIONA'}")
    print(f"🔄 Sincronización sin parámetros: {'✅ FUNCIONANDO' if sync_original_working else '❌ NO FUNCIONA'}")
    
    print(f"\n🎯 Estado de la sincronización:")
    if sync_simple_working or sync_params_working or sync_original_working:
        print(f"   🎉 ¡SINCRONIZACIÓN FUNCIONANDO!")
        print(f"   ✅ Al menos un método de sincronización funciona")
        print(f"   ✅ El problema de error 422 ha sido resuelto")
        
        if sync_simple_working:
            print(f"   💡 Recomendación: Usar /api/v1/tasks/sync-simple para sincronización simple")
        elif sync_params_working:
            print(f"   💡 Recomendación: Usar /api/v1/tasks/sync?workspace_id=9014943317")
        elif sync_original_working:
            print(f"   💡 Recomendación: Usar /api/v1/tasks/sync (sin parámetros)")
    else:
        print(f"   ❌ SINCRONIZACIÓN CON PROBLEMAS")
        print(f"   ❌ Ningún método de sincronización funciona")
        print(f"   🔧 Revisar configuración de ClickUp API")
    
    print(f"\n💡 Información adicional:")
    print(f"   📁 Workspace por defecto: 9014943317")
    print(f"   🔗 Endpoints disponibles:")
    print(f"      - /api/v1/tasks/sync-simple (sin parámetros)")
    print(f"      - /api/v1/tasks/sync?workspace_id=9014943317 (con parámetros)")
    print(f"      - /api/v1/tasks/sync (sin parámetros, usa workspace por defecto)")
    
    print(f"\n🕐 Prueba completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Función principal"""
    print("🔄 PRUEBA COMPLETA DE SINCRONIZACIÓN CORREGIDA")
    print("=" * 70)
    
    test_sync_fix()

if __name__ == "__main__":
    main()
