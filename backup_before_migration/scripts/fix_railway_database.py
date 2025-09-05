#!/usr/bin/env python3
"""
Script para solucionar problemas de base de datos en Railway
"""

import os
import sys
import requests
import json
from datetime import datetime

def check_railway_database_status():
    """Verificar el estado de la base de datos en Railway"""
    print("🔍 VERIFICANDO ESTADO DE BASE DE DATOS EN RAILWAY")
    print("=" * 60)
    
    # URL base de Railway
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    
    print(f"🔗 URL de Railway: {railway_url}")
    
    # Probar endpoint principal
    try:
        response = requests.get(f"{railway_url}/debug", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint principal funcionando")
            
            # Extraer información de configuración
            if "configuration" in data:
                config = data["configuration"]
                print(f"   📋 CLICKUP_API_TOKEN: {config.get('CLICKUP_API_TOKEN', 'N/A')}")
                print(f"   🗄️  DATABASE_URL: {config.get('DATABASE_URL', 'N/A')}")
                print(f"   🌍 ENVIRONMENT: {config.get('ENVIRONMENT', 'N/A')}")
                
                # Verificar si DATABASE_URL está configurada
                if "Configured" in str(config.get('DATABASE_URL', '')):
                    print("   ✅ DATABASE_URL está configurada en Railway")
                    return True
                else:
                    print("   ❌ DATABASE_URL NO está configurada en Railway")
                    return False
            else:
                print("   ⚠️  No se pudo obtener información de configuración")
                return False
        else:
            print(f"❌ Error en endpoint principal: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando a Railway: {e}")
        return False

def test_database_endpoints():
    """Probar endpoints relacionados con la base de datos"""
    print("\n🗄️ PROBANDO ENDPOINTS DE BASE DE DATOS:")
    
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    endpoints = [
        "/api/v1/tasks/debug",
        "/api/v1/tasks/config",
        "/api/v1/tasks/test"
    ]
    
    for endpoint in endpoints:
        url = railway_url + endpoint
        print(f"\n   🔍 Probando: {endpoint}")
        
        try:
            response = requests.get(url, timeout=15)
            print(f"      📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"      ✅ Respuesta: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                except:
                    print(f"      ✅ Respuesta: {response.text[:200]}...")
            else:
                print(f"      ❌ Error: {response.text[:200]}...")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")

def generate_railway_fix_instructions():
    """Generar instrucciones para solucionar el problema en Railway"""
    print("\n💡 INSTRUCCIONES PARA SOLUCIONAR EN RAILWAY:")
    print("=" * 60)
    
    print("1️⃣  VERIFICAR SERVICIO DE BASE DE DATOS:")
    print("   - Ve a tu proyecto en Railway")
    print("   - Verifica que tengas un servicio de PostgreSQL activo")
    print("   - Asegúrate de que esté en el mismo proyecto que tu aplicación")
    
    print("\n2️⃣  CONFIGURAR VARIABLE DATABASE_URL:")
    print("   - En tu proyecto de Railway, ve a 'Variables'")
    print("   - Agrega una nueva variable:")
    print("     Nombre: DATABASE_URL")
    print("     Valor: (Railway lo genera automáticamente)")
    print("   - Si no se genera automáticamente, copia la URL de conexión del servicio PostgreSQL")
    
    print("\n3️⃣  CONFIGURAR OTRAS VARIABLES:")
    print("   - ENVIRONMENT: production")
    print("   - PORT: 8000")
    print("   - HOST: 0.0.0.0")
    
    print("\n4️⃣  REINICIAR SERVICIO:")
    print("   - Después de configurar las variables, reinicia tu servicio")
    print("   - Railway aplicará los cambios automáticamente")
    
    print("\n5️⃣  VERIFICAR LOGS:")
    print("   - Revisa los logs del servicio para confirmar la conexión")
    print("   - Busca mensajes de conexión exitosa a PostgreSQL")

def check_local_vs_railway():
    """Comparar configuración local vs Railway"""
    print("\n🔍 COMPARANDO CONFIGURACIÓN LOCAL VS RAILWAY:")
    print("=" * 60)
    
    # Configuración local
    print("🏠 CONFIGURACIÓN LOCAL:")
    local_db_url = "postgresql://postgres:admin123@localhost:5432/clickup_project_manager"
    print(f"   🗄️  DATABASE_URL: {local_db_url[:50]}...")
    print(f"   🌍 ENVIRONMENT: development")
    print(f"   🔌 PORT: 8000")
    print(f"   🏠 HOST: 127.0.0.1")
    
    # Configuración esperada en Railway
    print("\n🚂 CONFIGURACIÓN ESPERADA EN RAILWAY:")
    print(f"   🗄️  DATABASE_URL: postgresql://***:***@***.***.railway.app:5432/railway")
    print(f"   🌍 ENVIRONMENT: production")
    print(f"   🔌 PORT: 8000")
    print(f"   🏠 HOST: 0.0.0.0")
    
    print("\n⚠️  DIFERENCIAS CLAVE:")
    print("   - DATABASE_URL: Debe apuntar a la base de datos de Railway, no a localhost")
    print("   - ENVIRONMENT: Debe ser 'production' en Railway")
    print("   - HOST: Debe ser '0.0.0.0' para aceptar conexiones externas")

def main():
    """Función principal"""
    print(f"🕐 Iniciando verificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar estado actual
    db_configured = check_railway_database_status()
    
    # Probar endpoints
    test_database_endpoints()
    
    # Comparar configuraciones
    check_local_vs_railway()
    
    # Generar instrucciones de solución
    if not db_configured:
        generate_railway_fix_instructions()
    else:
        print("\n✅ La base de datos parece estar configurada correctamente en Railway")
        print("   Si aún hay problemas, revisa los logs del servicio")
    
    print("\n" + "=" * 60)
    print("🏁 Verificación completada")

if __name__ == "__main__":
    main()
