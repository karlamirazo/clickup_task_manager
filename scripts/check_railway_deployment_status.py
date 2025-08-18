#!/usr/bin/env python3
"""
Script para verificar el estado del deployment en Railway
"""

import requests
import json
from datetime import datetime

def check_railway_deployment_status():
    """Verificar el estado del deployment en Railway"""
    print("🚂 VERIFICACIÓN DEL DEPLOYMENT EN RAILWAY")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # PASO 1: Verificar que la aplicación responde
    print("🔍 PASO 1: Verificar respuesta de la aplicación")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ La aplicación está respondiendo correctamente")
            print(f"📄 Tamaño de respuesta: {len(response.text)} caracteres")
        else:
            print(f"❌ La aplicación no está respondiendo correctamente")
            
    except Exception as e:
        print(f"❌ Error conectando a la aplicación: {e}")
        return False
    
    # PASO 2: Verificar endpoints principales
    print(f"\n🔍 PASO 2: Verificar endpoints principales")
    print("-" * 40)
    
    endpoints_to_test = [
        "/test-simple",
        "/api/v1/workspaces",
        "/api/v1/users",
        "/api/v1/tasks/",
        "/debug"
    ]
    
    working_endpoints = 0
    total_endpoints = len(endpoints_to_test)
    
    for endpoint in endpoints_to_test:
        try:
            print(f"🔍 Probando: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print(f"   ✅ Funcionando")
                working_endpoints += 1
            elif response.status_code == 422:
                print(f"   ⚠️ Error 422 (parámetros faltantes) - Normal para algunos endpoints")
            else:
                print(f"   ❌ Error {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # PASO 3: Verificar funcionalidad de creación de tareas
    print(f"\n🧪 PASO 3: Verificar creación de tareas")
    print("-" * 40)
    
    test_task_data = {
        "name": f"Test Railway Deployment - {datetime.now().strftime('%H:%M:%S')}",
        "description": "Tarea para verificar que el deployment en Railway funciona correctamente",
        "status": "to do",
        "priority": 3,
        "due_date": "2025-08-25",
        "assignee_id": "88425547",
        "list_id": "901411770471",
        "workspace_id": "9014943317",
        "custom_fields": {
            "Email": "test@railway.com",
            "Celular": "+52 55 9999 9999"
        }
    }
    
    try:
        print(f"🚀 Enviando tarea de prueba...")
        response = requests.post(
            f"{base_url}/api/v1/tasks/",
            json=test_task_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📡 Respuesta: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ ¡ÉXITO! Tarea creada correctamente")
            print(f"🆔 ID ClickUp: {result.get('clickup_id', 'N/A')}")
            print(f"📧 Campos personalizados: {result.get('custom_fields', 'N/A')}")
            task_creation_working = True
        else:
            print(f"❌ Error creando tarea: {response.text}")
            task_creation_working = False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        task_creation_working = False
    
    # PASO 4: Verificar logs de deployment
    print(f"\n📋 PASO 4: Verificar logs de deployment")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/debug", timeout=10)
        if response.status_code == 200:
            debug_info = response.json()
            print(f"✅ Endpoint de debug funcionando")
            print(f"📊 Información del deployment:")
            print(f"   🕐 Timestamp: {debug_info.get('timestamp', 'N/A')}")
            print(f"   🔧 Status: {debug_info.get('status', 'N/A')}")
        else:
            print(f"⚠️ Endpoint de debug no disponible")
            
    except Exception as e:
        print(f"❌ Error accediendo a debug: {e}")
    
    # PASO 5: Resumen del estado
    print(f"\n📊 RESUMEN DEL ESTADO DEL DEPLOYMENT")
    print("=" * 60)
    
    print(f"🌐 Aplicación web:")
    print(f"   ✅ URL: {base_url}")
    print(f"   ✅ Respuesta: {'SÍ' if response.status_code == 200 else 'NO'}")
    
    print(f"\n🔌 Endpoints:")
    print(f"   📊 Funcionando: {working_endpoints}/{total_endpoints}")
    print(f"   📈 Porcentaje: {(working_endpoints/total_endpoints)*100:.1f}%")
    
    print(f"\n🧪 Funcionalidad:")
    print(f"   📝 Creación de tareas: {'✅ FUNCIONANDO' if task_creation_working else '❌ NO FUNCIONA'}")
    print(f"   📧 Campos personalizados: {'✅ FUNCIONANDO' if task_creation_working else '❌ NO FUNCIONA'}")
    
    print(f"\n🎯 Estado general:")
    if working_endpoints >= 3 and task_creation_working:
        print(f"   🎉 ¡DEPLOYMENT FUNCIONANDO CORRECTAMENTE!")
        print(f"   ✅ La aplicación está operativa")
        print(f"   ✅ Los endpoints principales funcionan")
        print(f"   ✅ La creación de tareas funciona")
        print(f"   ✅ Los campos personalizados funcionan")
    elif working_endpoints >= 2:
        print(f"   ⚠️ DEPLOYMENT PARCIALMENTE FUNCIONANDO")
        print(f"   ✅ La aplicación responde")
        print(f"   ⚠️ Algunos endpoints tienen problemas")
    else:
        print(f"   ❌ DEPLOYMENT CON PROBLEMAS")
        print(f"   ❌ La aplicación no está funcionando correctamente")
    
    print(f"\n🕐 Verificación completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Función principal"""
    print("🚂 VERIFICACIÓN COMPLETA DEL DEPLOYMENT EN RAILWAY")
    print("=" * 70)
    
    check_railway_deployment_status()

if __name__ == "__main__":
    main()
