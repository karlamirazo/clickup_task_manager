#!/usr/bin/env python3
"""
Script de monitoreo en tiempo real para verificar el estado de Railway
"""

import requests
import json
import time
from datetime import datetime
import sys

def check_railway_status():
    """Verificar estado actual de Railway"""
    railway_url = "https://ctm-pro.up.railway.app"
    
    print(f"🔍 Verificando estado de Railway: {datetime.now().strftime('%H:%M:%S')}")
    print(f"🔗 URL: {railway_url}")
    
    try:
        # Probar endpoint principal
        response = requests.get(f"{railway_url}/debug", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint principal: FUNCIONANDO")
            
            # Extraer información de configuración
            if "configuration" in data:
                config = data["configuration"]
                print(f"   📋 CLICKUP_API_TOKEN: {config.get('CLICKUP_API_TOKEN', 'N/A')}")
                print(f"   🗄️  DATABASE_URL: {config.get('DATABASE_URL', 'N/A')}")
                print(f"   🌍 ENVIRONMENT: {config.get('ENVIRONMENT', 'N/A')}")
                
                # Verificar si DATABASE_URL está configurada
                if "Configured" in str(config.get('DATABASE_URL', '')):
                    print("   ✅ DATABASE_URL: CONFIGURADA")
                    db_status = "✅ CONFIGURADA"
                else:
                    print("   ❌ DATABASE_URL: NO CONFIGURADA")
                    db_status = "❌ NO CONFIGURADA"
            else:
                print("   ⚠️  No se pudo obtener información de configuración")
                db_status = "⚠️  ERROR"
                
        else:
            print(f"❌ Endpoint principal: ERROR {response.status_code}")
            db_status = "❌ ERROR"
            
    except Exception as e:
        print(f"❌ Error conectando a Railway: {e}")
        db_status = "❌ ERROR"
    
    return db_status

def test_database_endpoints():
    """Probar endpoints de base de datos"""
    railway_url = "https://ctm-pro.up.railway.app"
    endpoints = [
        "/api/v1/tasks/debug",
        "/api/v1/tasks/config",
        "/api/v1/tasks/test"
    ]
    
    print("\n🗄️ Probando endpoints de base de datos:")
    
    for endpoint in endpoints:
        url = railway_url + endpoint
        print(f"\n   🔍 {endpoint}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"      📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "error" in str(data).lower():
                        print(f"      ❌ Error en respuesta: {str(data)[:100]}...")
                    else:
                        print(f"      ✅ Funcionando correctamente")
                except:
                    print(f"      ✅ Respuesta recibida")
            else:
                print(f"      ❌ Error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Error de conexión: {e}")

def monitor_continuously(interval=30):
    """Monitorear continuamente el estado de Railway"""
    print("🚀 INICIANDO MONITOREO CONTINUO DE RAILWAY")
    print("=" * 60)
    print(f"⏱️  Intervalo de verificación: {interval} segundos")
    print("🔄 Presiona Ctrl+C para detener")
    print("=" * 60)
    
    try:
        while True:
            print(f"\n{'='*60}")
            db_status = check_railway_status()
            
            if "✅ CONFIGURADA" in db_status:
                print("\n🎉 ¡BASE DE DATOS CONFIGURADA CORRECTAMENTE!")
                print("🔍 Verificando funcionalidad completa...")
                test_database_endpoints()
                
                print("\n✅ VERIFICACIÓN COMPLETADA - SISTEMA FUNCIONANDO")
                print("💡 Puedes detener el monitoreo con Ctrl+C")
                break
            else:
                print(f"\n⏳ Base de datos aún no configurada correctamente")
                print(f"🔄 Reintentando en {interval} segundos...")
                time.sleep(interval)
                
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoreo detenido por el usuario")
        print("✅ Script terminado correctamente")

def main():
    """Función principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        # Modo monitoreo continuo
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        monitor_continuously(interval)
    else:
        # Modo verificación única
        print("🔍 VERIFICACIÓN ÚNICA DEL ESTADO DE RAILWAY")
        print("=" * 60)
        
        db_status = check_railway_status()
        test_database_endpoints()
        
        print("\n" + "=" * 60)
        if "✅ CONFIGURADA" in db_status:
            print("🎉 ¡SISTEMA FUNCIONANDO CORRECTAMENTE!")
        else:
            print("⚠️  SISTEMA AÚN CON PROBLEMAS")
            print("💡 Usa --continuous para monitoreo continuo")
            print("   Ejemplo: python scripts/monitor_railway_status.py --continuous 30")

if __name__ == "__main__":
    main()

