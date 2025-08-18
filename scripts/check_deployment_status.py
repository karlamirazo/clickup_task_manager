#!/usr/bin/env python3
"""
Script para verificar el estado del deployment y logs del sistema
"""

import requests
import json
import os
from datetime import datetime

def check_endpoint(url, endpoint_name):
    """Verificar un endpoint específico"""
    try:
        full_url = f"{url}{endpoint_name}"
        print(f"🔍 Verificando {endpoint_name}...")
        
        response = requests.get(full_url, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ {endpoint_name}: OK (Status: {response.status_code})")
            try:
                data = response.json()
                return data
            except:
                print(f"   📄 Respuesta: {response.text[:200]}...")
                return {"raw_content": response.text[:200]}
        else:
            print(f"   ❌ {endpoint_name}: Error (Status: {response.status_code})")
            print(f"   📄 Respuesta: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ {endpoint_name}: Error de conexión - {e}")
        return None
    except Exception as e:
        print(f"   ❌ {endpoint_name}: Error inesperado - {e}")
        return None

def check_logging_system():
    """Verificar el sistema de logging local"""
    print("\n📊 Verificando sistema de logging local...")
    
    # Verificar archivo DEPLOYMENT_SUMMARY.txt
    if os.path.exists("DEPLOYMENT_SUMMARY.txt"):
        with open("DEPLOYMENT_SUMMARY.txt", "r", encoding="utf-8") as f:
            content = f.read()
            entries = content.count("## [")
            print(f"   ✅ DEPLOYMENT_SUMMARY.txt: {entries} entradas de log")
            
            # Mostrar las últimas 3 entradas
            lines = content.split('\n')
            recent_entries = []
            for i, line in enumerate(lines):
                if line.startswith("## ["):
                    recent_entries.append(line)
                    if len(recent_entries) >= 3:
                        break
            
            print(f"   📝 Últimas entradas:")
            for entry in recent_entries:
                print(f"      - {entry}")
    else:
        print("   ❌ DEPLOYMENT_SUMMARY.txt: No encontrado")

def main():
    """Función principal"""
    print("🚀 Verificando estado del deployment en Railway")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Verificar endpoints básicos
    print("\n🔍 Verificando endpoints básicos...")
    
    health_data = check_endpoint(base_url, "/health")
    debug_data = check_endpoint(base_url, "/debug")
    api_data = check_endpoint(base_url, "/api")
    
    # Verificar endpoints de logging (pueden no estar disponibles)
    print("\n🔍 Verificando endpoints de logging...")
    test_logging_data = check_endpoint(base_url, "/test-logging")
    
    # Verificar endpoints de tareas
    print("\n🔍 Verificando endpoints de tareas...")
    tasks_debug = check_endpoint(base_url, "/api/v1/tasks/debug-code")
    
    # Verificar sistema de logging local
    check_logging_system()
    
    # Resumen del estado
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL ESTADO DEL DEPLOYMENT")
    print("=" * 60)
    
    endpoints_status = {
        "Health": health_data is not None,
        "Debug": debug_data is not None,
        "API": api_data is not None,
        "Test Logging": test_logging_data is not None,
        "Tasks Debug": tasks_debug is not None
    }
    
    for endpoint, status in endpoints_status.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {endpoint}: {'Funcionando' if status else 'No disponible'}")
    
    # Información adicional del debug
    if debug_data:
        print(f"\n📋 Información del sistema:")
        print(f"   - Timestamp: {debug_data.get('timestamp', 'N/A')}")
        
        config = debug_data.get('configuration', {})
        print(f"   - CLICKUP_API_TOKEN: {config.get('CLICKUP_API_TOKEN', 'N/A')}")
        print(f"   - DATABASE_URL: {config.get('DATABASE_URL', 'N/A')}")
        print(f"   - ENVIRONMENT: {config.get('ENVIRONMENT', 'N/A')}")
        
        db = debug_data.get('database', {})
        print(f"   - Database Type: {db.get('database_type', 'N/A')}")
        print(f"   - Database Status: {db.get('database_status', 'N/A')}")
        
        clickup = debug_data.get('clickup_client', {})
        print(f"   - ClickUp Client: {clickup.get('client_status', 'N/A')}")
        print(f"   - Token Configurado: {clickup.get('token_configured', 'N/A')}")
    
    # Verificar si el sistema de logging está funcionando
    if test_logging_data:
        print(f"\n🎉 Sistema de logging funcionando correctamente!")
        print(f"   - Status: {test_logging_data.get('status', 'N/A')}")
        print(f"   - Message: {test_logging_data.get('message', 'N/A')}")
    else:
        print(f"\n⚠️ Sistema de logging no disponible en endpoint /test-logging")
        print(f"   - Esto puede indicar que el deployment aún está en proceso")
        print(f"   - O que el endpoint no se desplegó correctamente")
    
    print(f"\n🕐 Verificación completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
