#!/usr/bin/env python3
"""
Script para verificar la estructura actual de las tablas en Railway
"""

import requests
import json
from datetime import datetime

def check_railway_table_structure():
    """Verificar la estructura actual de las tablas en Railway"""
    print("🔍 VERIFICANDO ESTRUCTURA DE TABLAS EN RAILWAY")
    print("=" * 60)
    
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    
    print(f"🔗 URL: {railway_url}")
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Verificar si existe un endpoint para ver la estructura de la BD
    print("\n1️⃣ VERIFICANDO ENDPOINTS DE ESTRUCTURA:")
    
    # Intentar acceder a endpoints que podrían mostrar información de la BD
    debug_endpoints = [
        "/debug",
        "/api",
        "/api/v1/tasks/debug"
    ]
    
    for endpoint in debug_endpoints:
        url = railway_url + endpoint
        print(f"\n   🔍 Probando: {endpoint}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"      📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "database" in str(data).lower():
                        print("      ✅ Contiene información de base de datos")
                        # Buscar información específica de tablas
                        if "tables" in str(data).lower():
                            print("      📋 Información de tablas disponible")
                        if "notification_logs" in str(data).lower():
                            print("      📋 Tabla notification_logs mencionada")
                    else:
                        print("      ℹ️ Respuesta recibida (sin info de BD)")
                except:
                    print("      ✅ Respuesta recibida")
            else:
                print(f"      ❌ Error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # 2. Intentar crear una tarea de prueba para ver si las tablas funcionan
    print("\n2️⃣ PROBANDO CREACIÓN DE TAREA:")
    try:
        test_task = {
            "name": "Tarea de prueba - Verificación de BD",
            "description": "Tarea temporal para verificar estructura de base de datos",
            "status": "to do",
            "priority": "medium",
            "due_date": "2025-12-31"
        }
        
        response = requests.post(
            f"{railway_url}/api/v1/tasks/",
            json=test_task,
            timeout=15
        )
        
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Tarea creada exitosamente")
            print(f"   📋 ID: {data.get('id', 'N/A')}")
            print(f"   📋 Nombre: {data.get('name', 'N/A')}")
        elif response.status_code == 422:
            print("   ⚠️ Error de validación (puede ser normal)")
            if response.text:
                print(f"      Detalle: {response.text[:200]}...")
        else:
            print(f"   ❌ Error: {response.status_code}")
            if response.text:
                print(f"      Detalle: {response.text[:200]}...")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Verificar si hay datos en las tablas existentes
    print("\n3️⃣ VERIFICANDO DATOS EXISTENTES:")
    
    # Intentar obtener tareas existentes
    try:
        response = requests.get(f"{railway_url}/api/v1/tasks/", timeout=15)
        print(f"   📊 Status de /api/v1/tasks/: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   ✅ Tareas encontradas: {len(data)}")
                if data:
                    print(f"   📋 Primera tarea: {data[0].get('name', 'N/A')}")
            else:
                print(f"   ℹ️ Respuesta: {type(data)}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Análisis del problema
    print("\n4️⃣ ANÁLISIS DEL PROBLEMA:")
    print("   🔍 El endpoint /api/init-db dice que fue exitoso")
    print("   🔍 Pero la columna notification_type sigue sin existir")
    print("   💡 Posibles causas:")
    print("      - La función init_db() no está funcionando correctamente")
    print("      - Las tablas no se están recreando")
    print("      - Hay un problema con el modelo NotificationLog")
    print("      - Railway está usando una versión en caché")
    
    print("\n" + "=" * 60)
    print("🏁 Verificación de estructura completada")

def main():
    """Función principal"""
    print(f"🕐 Iniciando verificación de estructura: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    check_railway_table_structure()
    
    print("\n💡 PRÓXIMOS PASOS:")
    print("   - Verificar si las tablas se crearon correctamente")
    print("   - Revisar los logs de Railway para errores")
    print("   - Considerar recrear la base de datos desde cero")

if __name__ == "__main__":
    main()
