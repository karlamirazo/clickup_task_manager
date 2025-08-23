#!/usr/bin/env python3
"""
Script de diagnóstico para problemas de conexión a la base de datos en Railway
"""

import os
import sys
import requests
import json
from datetime import datetime

def check_railway_environment():
    """Verificar variables de entorno de Railway"""
    print("🔍 DIAGNÓSTICO DE CONEXIÓN A BASE DE DATOS EN RAILWAY")
    print("=" * 60)
    
    # Verificar variables críticas
    critical_vars = [
        "DATABASE_URL",
        "ENVIRONMENT", 
        "PORT",
        "HOST"
    ]
    
    print("\n📋 VARIABLES DE ENTORNO CRÍTICAS:")
    for var in critical_vars:
        value = os.getenv(var)
        if value:
            if var == "DATABASE_URL":
                # Ocultar credenciales sensibles
                if "postgresql://" in value:
                    parts = value.split("@")
                    if len(parts) > 1:
                        safe_url = f"postgresql://***:***@{parts[1]}"
                        print(f"   ✅ {var}: {safe_url}")
                    else:
                        print(f"   ✅ {var}: {value[:50]}...")
                else:
                    print(f"   ✅ {var}: {value}")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: NO CONFIGURADA")
    
    # Verificar si estamos en Railway
    railway_env = os.getenv("RAILWAY_ENVIRONMENT")
    if railway_env:
        print(f"\n🚂 ENTORNO RAILWAY DETECTADO:")
        print(f"   ✅ RAILWAY_ENVIRONMENT: {railway_env}")
    else:
        print(f"\n⚠️  NO SE DETECTÓ ENTORNO RAILWAY")
        print(f"   Esto puede indicar que estás ejecutando localmente")

def test_database_connection():
    """Probar conexión directa a la base de datos"""
    print("\n🗄️ PRUEBA DE CONEXIÓN DIRECTA A BASE DE DATOS:")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("   ❌ DATABASE_URL no está configurada")
        return False
    
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Parsear la URL de la base de datos
        parsed = urlparse(database_url)
        print(f"   🔗 Host: {parsed.hostname}")
        print(f"   📊 Database: {parsed.path[1:] if parsed.path else 'N/A'}")
        print(f"   👤 User: {parsed.username}")
        print(f"   🔌 Port: {parsed.port or 5432}")
        
        # Intentar conexión
        print("   🔄 Intentando conexión...")
        conn = psycopg2.connect(database_url)
        
        # Verificar conexión
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"   ✅ Conexión exitosa!")
        print(f"   📋 PostgreSQL version: {version[0][:50]}...")
        
        # Verificar tablas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"   📊 Tablas encontradas: {len(tables)}")
            for table in tables[:5]:  # Mostrar solo las primeras 5
                print(f"      - {table[0]}")
            if len(tables) > 5:
                print(f"      ... y {len(tables) - 5} más")
        else:
            print("   ⚠️  No se encontraron tablas")
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        print("   ❌ psycopg2 no está instalado")
        print("   💡 Instala con: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
        return False

def test_railway_endpoints():
    """Probar endpoints de Railway para verificar estado"""
    print("\n🌐 PRUEBA DE ENDPOINTS DE RAILWAY:")
    
    # Obtener URL base de Railway
    railway_url = os.getenv("RAILWAY_STATIC_URL") or "https://clickuptaskmanager-production.up.railway.app"
    
    print(f"   🔗 URL base: {railway_url}")
    
    endpoints = [
        "/debug",
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
                
        except requests.exceptions.RequestException as e:
            print(f"      ❌ Error de conexión: {e}")
        except Exception as e:
            print(f"      ⚠️  Error inesperado: {e}")

def check_sqlalchemy_connection():
    """Verificar conexión a través de SQLAlchemy"""
    print("\n🐍 PRUEBA DE CONEXIÓN CON SQLALCHEMY:")
    
    try:
        # Agregar el directorio raíz al path
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from core.database import engine, get_db
        from core.config import settings
        from sqlalchemy import text
        
        print(f"   🔧 Engine creado: {engine is not None}")
        print(f"   📋 URL de base de datos: {settings.DATABASE_URL[:50]}...")
        
        # Verificar que el engine esté funcionando
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print("   ✅ Conexión SQLAlchemy exitosa")
                
                # Verificar tablas
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """))
                tables = [row[0] for row in result]
                
                if tables:
                    print(f"   📊 Tablas encontradas: {len(tables)}")
                    for table in tables[:5]:
                        print(f"      - {table}")
                    if len(tables) > 5:
                        print(f"      ... y {len(tables) - 5} más")
                else:
                    print("   ⚠️  No se encontraron tablas")
                    
        except Exception as e:
            print(f"   ❌ Error en conexión SQLAlchemy: {str(e)}")
            return False
            
        return True
        
    except ImportError as e:
        print(f"   ❌ Error importando módulos: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error inesperado: {str(e)}")
        return False

def generate_recommendations():
    """Generar recomendaciones basadas en los resultados"""
    print("\n💡 RECOMENDACIONES:")
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("   1️⃣  Configurar DATABASE_URL en Railway")
        print("      - Ve a tu proyecto en Railway")
        print("      - Variables > Agregar DATABASE_URL")
        print("      - Valor: postgresql://user:pass@host:port/db")
        
    elif "localhost" in database_url:
        print("   1️⃣  DATABASE_URL apunta a localhost")
        print("      - Esto indica que estás usando configuración local")
        print("      - En Railway, DATABASE_URL debe apuntar a la base de datos de Railway")
        
    print("   2️⃣  Verificar que la base de datos esté activa en Railway")
    print("      - Revisa el estado del servicio de base de datos")
    print("      - Asegúrate de que esté en el mismo proyecto")
    
    print("   3️⃣  Reiniciar el servicio después de cambios")
    print("      - Los cambios en variables de entorno requieren reinicio")
    
    print("   4️⃣  Verificar logs de Railway")
    print("      - Revisa los logs del servicio para errores de conexión")

def main():
    """Función principal de diagnóstico"""
    print(f"🕐 Iniciando diagnóstico: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ejecutar todas las verificaciones
    check_railway_environment()
    
    db_connection_ok = test_database_connection()
    sqlalchemy_ok = check_sqlalchemy_connection()
    
    test_railway_endpoints()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL DIAGNÓSTICO:")
    print(f"   🗄️  Conexión directa PostgreSQL: {'✅ OK' if db_connection_ok else '❌ FALLA'}")
    print(f"   🐍 Conexión SQLAlchemy: {'✅ OK' if sqlalchemy_ok else '❌ FALLA'}")
    
    if db_connection_ok and sqlalchemy_ok:
        print("\n🎉 ¡TODAS LAS CONEXIONES ESTÁN FUNCIONANDO!")
    else:
        print("\n⚠️  SE DETECTARON PROBLEMAS DE CONEXIÓN")
        generate_recommendations()
    
    print("\n" + "=" * 60)
    print("🏁 Diagnóstico completado")

if __name__ == "__main__":
    main()
