#!/usr/bin/env python3
"""
Script para verificar y corregir la estructura de la base de datos en Railway
"""

import requests
import json
from datetime import datetime

def check_railway_database_structure():
    """Verificar la estructura de la base de datos en Railway"""
    print("🔍 VERIFICANDO ESTRUCTURA DE BASE DE DATOS EN RAILWAY")
    print("=" * 60)
    
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Probar endpoints que usan la base de datos
    endpoints = [
        "/api/v1/tasks/debug",
        "/api/v1/tasks/config",
        "/api/v1/tasks/test"
    ]
    
    print(f"🔗 URL: {railway_url}")
    
    for endpoint in endpoints:
        url = railway_url + endpoint
        print(f"\n🔍 Probando: {endpoint}")
        
        try:
            response = requests.get(url, timeout=15)
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "error" in str(data).lower():
                        print(f"   ❌ Error: {str(data)[:200]}...")
                    else:
                        print(f"   ✅ Funcionando correctamente")
                except:
                    print(f"   ✅ Respuesta recibida")
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
                if response.text:
                    print(f"      Detalle: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Error de conexión: {e}")

def check_dashboard_errors():
    """Verificar errores específicos del dashboard"""
    print("\n📊 VERIFICANDO ERRORES DEL DASHBOARD:")
    print("=" * 60)
    
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Verificar archivos estáticos
    static_files = [
        "/dashboard-config.js",
        "/static/dashboard-config.js",
        "/static/script.js",
        "/static/styles.css"
    ]
    
    for file_path in static_files:
        url = railway_url + file_path
        print(f"\n🔍 Verificando: {file_path}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Archivo encontrado")
                content_type = response.headers.get('content-type', 'N/A')
                print(f"   📋 Content-Type: {content_type}")
            else:
                print(f"   ❌ Archivo no encontrado")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def generate_fix_instructions():
    """Generar instrucciones para solucionar los problemas"""
    print("\n💡 INSTRUCCIONES PARA SOLUCIONAR:")
    print("=" * 60)
    
    print("1️⃣  PROBLEMA DE ESTRUCTURA DE BASE DE DATOS:")
    print("   - La tabla notification_logs no tiene la columna notification_type")
    print("   - Esto indica que la base de datos no se ha inicializado correctamente")
    print("   - Solución: Ejecutar init_db() en Railway")
    
    print("\n2️⃣  PROBLEMA DE ARCHIVOS ESTÁTICOS:")
    print("   - dashboard-config.js no se encuentra (404)")
    print("   - Esto causa errores de JavaScript en el dashboard")
    print("   - Solución: Verificar configuración de archivos estáticos")
    
    print("\n3️⃣  PROBLEMA DE VARIABLES DE ENTORNO:")
    print("   - ENVIRONMENT sigue siendo 'development' en lugar de 'production'")
    print("   - Esto puede causar problemas de configuración")
    print("   - Solución: Configurar ENVIRONMENT=production en Railway")
    
    print("\n4️⃣  PASOS RECOMENDADOS:")
    print("   a) Configurar ENVIRONMENT=production en Railway")
    print("   b) Reiniciar el servicio para aplicar cambios")
    print("   c) Verificar que init_db() se ejecute correctamente")
    print("   d) Probar el dashboard nuevamente")

def check_environment_variables():
    """Verificar variables de entorno en Railway"""
    print("\n🌍 VERIFICANDO VARIABLES DE ENTORNO:")
    print("=" * 60)
    
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        response = requests.get(f"{railway_url}/debug", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "configuration" in data:
                config = data["configuration"]
                print("📋 Configuración actual:")
                print(f"   🌍 ENVIRONMENT: {config.get('ENVIRONMENT', 'N/A')}")
                print(f"   🗄️  DATABASE_URL: {config.get('DATABASE_URL', 'N/A')}")
                print(f"   📋 CLICKUP_API_TOKEN: {config.get('CLICKUP_API_TOKEN', 'N/A')}")
                
                # Verificar si ENVIRONMENT está configurado correctamente
                if config.get('ENVIRONMENT') == 'development':
                    print("\n⚠️  PROBLEMA DETECTADO:")
                    print("   ENVIRONMENT está configurado como 'development'")
                    print("   Debería ser 'production' en Railway")
                else:
                    print("\n✅ ENVIRONMENT configurado correctamente")
            else:
                print("❌ No se pudo obtener información de configuración")
        else:
            print(f"❌ Error obteniendo configuración: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print(f"🕐 Iniciando verificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar estructura de base de datos
    check_railway_database_structure()
    
    # Verificar errores del dashboard
    check_dashboard_errors()
    
    # Verificar variables de entorno
    check_environment_variables()
    
    # Generar instrucciones de solución
    generate_fix_instructions()
    
    print("\n" + "=" * 60)
    print("🏁 Verificación completada")

if __name__ == "__main__":
    main()
