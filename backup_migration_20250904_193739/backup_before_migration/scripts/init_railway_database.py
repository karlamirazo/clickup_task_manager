#!/usr/bin/env python3
"""
Script para inicializar la base de datos en Railway
"""

import requests
import json
from datetime import datetime

def init_railway_database():
    """Inicializar la base de datos en Railway"""
    print("🗄️ INICIALIZANDO BASE DE DATOS EN RAILWAY")
    print("=" * 60)
    
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Crear un endpoint temporal para inicializar la base de datos
    # Primero vamos a verificar si ya existe un endpoint de inicialización
    endpoints = [
        "/api/v1/tasks/init-db",
        "/init-db",
        "/api/init-db",
        "/debug"
    ]
    
    print(f"🔗 URL: {railway_url}")
    
    # Buscar un endpoint de inicialización
    init_endpoint = None
    for endpoint in endpoints:
        url = railway_url + endpoint
        print(f"\n🔍 Probando: {endpoint}")
        
        try:
            response = requests.get(url, timeout=15)
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Endpoint disponible")
                if "init" in endpoint.lower():
                    init_endpoint = endpoint
                    break
            else:
                print(f"   ❌ Endpoint no disponible")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    if not init_endpoint:
        print("\n⚠️  No se encontró un endpoint de inicialización")
        print("   Necesitamos crear uno o usar el endpoint de debug")
        init_endpoint = "/debug"
    
    # Intentar inicializar la base de datos
    print(f"\n🔄 Intentando inicializar base de datos usando: {init_endpoint}")
    
    try:
        # Para el endpoint de debug, vamos a verificar el estado actual
        if init_endpoint == "/debug":
            response = requests.get(railway_url + init_endpoint, timeout=15)
            if response.status_code == 200:
                data = response.json()
                print("✅ Estado actual del sistema:")
                print(f"   🗄️  Base de datos: {data.get('database', {}).get('database_status', 'N/A')}")
                print(f"   🌍 ENVIRONMENT: {data.get('configuration', {}).get('ENVIRONMENT', 'N/A')}")
                
                # Verificar si la base de datos está conectada
                if "Connected" in str(data.get('database', {}).get('database_status', '')):
                    print("\n✅ Base de datos conectada correctamente")
                    print("   El problema puede ser que las tablas no se crearon correctamente")
                else:
                    print("\n❌ Base de datos no está conectada")
                    
        else:
            # Si hay un endpoint de inicialización específico
            response = requests.post(railway_url + init_endpoint, timeout=30)
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Base de datos inicializada correctamente")
            else:
                print(f"   ❌ Error inicializando base de datos: {response.text[:200]}...")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def check_database_tables():
    """Verificar qué tablas existen en la base de datos"""
    print("\n📊 VERIFICANDO TABLAS EN LA BASE DE DATOS:")
    print("=" * 60)
    
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Intentar obtener información de las tablas
    try:
        # Usar el endpoint de debug para obtener información de la base de datos
        response = requests.get(railway_url + "/debug", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("📋 Información del sistema:")
            
            if "database" in data:
                db_info = data["database"]
                print(f"   🗄️  Tipo: {db_info.get('database_type', 'N/A')}")
                print(f"   📊 Estado: {db_info.get('database_status', 'N/A')}")
            
            if "configuration" in data:
                config = data["configuration"]
                print(f"   🌍 ENVIRONMENT: {config.get('ENVIRONMENT', 'N/A')}")
                print(f"   🗄️  DATABASE_URL: {config.get('DATABASE_URL', 'N/A')}")
                
        else:
            print(f"❌ Error obteniendo información: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def generate_railway_fix_instructions():
    """Generar instrucciones específicas para Railway"""
    print("\n💡 INSTRUCCIONES PARA RAILWAY:")
    print("=" * 60)
    
    print("1️⃣  CONFIGURAR VARIABLES DE ENTORNO:")
    print("   - Ve a tu proyecto en Railway")
    print("   - Variables > Agregar:")
    print("     ENVIRONMENT = production")
    print("     HOST = 0.0.0.0")
    print("     PORT = 8000")
    
    print("\n2️⃣  VERIFICAR SERVICIO DE BASE DE DATOS:")
    print("   - Asegúrate de que PostgreSQL esté activo")
    print("   - Verifica que esté en el mismo proyecto")
    print("   - Estado debe ser 'Running'")
    
    print("\n3️⃣  REINICIAR SERVICIO:")
    print("   - Después de configurar variables, reinicia el servicio")
    print("   - Railway aplicará los cambios automáticamente")
    
    print("\n4️⃣  VERIFICAR INICIALIZACIÓN:")
    print("   - La base de datos debe inicializarse automáticamente")
    print("   - Las tablas deben crearse con la estructura correcta")
    print("   - Verificar que no haya errores en los logs")
    
    print("\n5️⃣  PROBAR DASHBOARD:")
    print("   - Una vez configurado, prueba el dashboard")
    print("   - Debe mostrar datos reales de ClickUp")
    print("   - No debe haber errores de JavaScript")

def main():
    """Función principal"""
    print(f"🕐 Iniciando inicialización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar estado actual
    check_database_tables()
    
    # Intentar inicializar base de datos
    init_railway_database()
    
    # Generar instrucciones
    generate_railway_fix_instructions()
    
    print("\n" + "=" * 60)
    print("🏁 Inicialización completada")

if __name__ == "__main__":
    main()
