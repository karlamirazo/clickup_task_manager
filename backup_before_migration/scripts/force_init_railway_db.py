#!/usr/bin/env python3
"""
Script para forzar la inicialización de la base de datos en Railway
"""

import requests
import json
from datetime import datetime
import time

def force_init_railway_database():
    """Forzar la inicialización de la base de datos en Railway"""
    print("🗄️ FORZANDO INICIALIZACIÓN DE BASE DE DATOS EN RAILWAY")
    print("=" * 60)
    
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    
    print(f"🔗 URL: {railway_url}")
    print("⏳ Esperando a que Railway detecte los cambios...")
    
    # Esperar un poco para que Railway aplique los cambios
    time.sleep(10)
    
    # Intentar inicializar la base de datos
    print("\n🔄 Intentando inicializar base de datos...")
    
    try:
        response = requests.post(f"{railway_url}/api/v1/dashboard/init-db", timeout=30)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                print(f"❌ Error: {data['error']}")
                return False
            else:
                print("✅ Base de datos inicializada exitosamente!")
                return True
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            if response.text:
                print(f"   Detalle: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_dashboard_endpoints():
    """Probar los endpoints del dashboard después de la inicialización"""
    print("\n🔍 PROBANDO ENDPOINTS DEL DASHBOARD:")
    print("=" * 60)
    
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    
    endpoints = [
        "/api/v1/dashboard/stats?period=24h",
        "/api/v1/dashboard/notifications?limit=10"
    ]
    
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
                        print(f"   ❌ Error en respuesta: {str(data)[:100]}...")
                    else:
                        print(f"   ✅ Funcionando correctamente")
                        if "tasks" in data:
                            print(f"      📊 Tareas: {data.get('tasks', {}).get('total', 'N/A')}")
                except:
                    print(f"   ✅ Respuesta recibida")
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
                if response.text:
                    print(f"      Detalle: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def monitor_dashboard_status():
    """Monitorear el estado del dashboard"""
    print("\n📊 MONITOREANDO ESTADO DEL DASHBOARD:")
    print("=" * 60)
    
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        # Probar endpoint principal
        response = requests.get(f"{railway_url}/debug", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Estado del sistema:")
            print(f"   🌍 ENVIRONMENT: {data.get('configuration', {}).get('ENVIRONMENT', 'N/A')}")
            print(f"   🗄️  Base de datos: {data.get('database', {}).get('database_status', 'N/A')}")
            
            # Verificar si la base de datos está funcionando
            if "Connected" in str(data.get('database', {}).get('database_status', '')):
                print("   ✅ Base de datos conectada")
            else:
                print("   ❌ Base de datos no conectada")
                
        else:
            print(f"❌ Error obteniendo estado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print(f"🕐 Iniciando inicialización forzada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Monitorear estado actual
    monitor_dashboard_status()
    
    # Forzar inicialización
    success = force_init_railway_database()
    
    if success:
        print("\n🎉 ¡BASE DE DATOS INICIALIZADA EXITOSAMENTE!")
        print("⏳ Esperando a que se apliquen los cambios...")
        time.sleep(15)
        
        # Probar endpoints
        test_dashboard_endpoints()
        
        print("\n✅ VERIFICACIÓN COMPLETADA")
        print("💡 Ahora el dashboard principal debería mostrar los contadores correctamente")
        
    else:
        print("\n❌ NO SE PUDO INICIALIZAR LA BASE DE DATOS")
        print("💡 Verifica los logs de Railway para más detalles")
    
    print("\n" + "=" * 60)
    print("🏁 Script completado")

if __name__ == "__main__":
    main()
