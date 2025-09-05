#!/usr/bin/env python3
"""
Script para verificar el estado de la base de datos en Railway
"""

import requests
import json
from datetime import datetime
import time

def verify_railway_database():
    """Verificar el estado de la base de datos en Railway"""
    print("🗄️ VERIFICANDO ESTADO DE LA BASE DE DATOS EN RAILWAY")
    print("=" * 60)
    
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    
    print(f"🔗 URL: {railway_url}")
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Verificar estado general del sistema
    print("\n1️⃣ VERIFICANDO ESTADO DEL SISTEMA:")
    try:
        response = requests.get(f"{railway_url}/debug", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Sistema funcionando")
            print(f"   🌍 ENVIRONMENT: {data.get('configuration', {}).get('ENVIRONMENT', 'N/A')}")
            print(f"   🗄️  Base de datos: {data.get('database', {}).get('database_status', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Verificar endpoint de inicialización
    print("\n2️⃣ VERIFICANDO ENDPOINT DE INICIALIZACIÓN:")
    try:
        response = requests.post(f"{railway_url}/api/init-db", timeout=15)
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                print(f"   ❌ Error: {data['error']}")
            else:
                print("   ✅ Base de datos inicializada exitosamente!")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            if response.text:
                print(f"      Detalle: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Verificar endpoints del dashboard
    print("\n3️⃣ VERIFICANDO ENDPOINTS DEL DASHBOARD:")
    
    endpoints = [
        "/api/v1/dashboard/stats?period=24h",
        "/api/v1/dashboard/notifications?limit=10"
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
                    if "error" in str(data).lower():
                        print(f"      ❌ Error en respuesta: {str(data)[:100]}...")
                    else:
                        print(f"      ✅ Funcionando correctamente")
                        if "tasks" in data:
                            print(f"         📊 Tareas: {data.get('tasks', {}).get('total', 'N/A')}")
                except:
                    print(f"      ✅ Respuesta recibida")
            else:
                print(f"      ❌ Error HTTP: {response.status_code}")
                if response.text:
                    print(f"         Detalle: {response.text[:100]}...")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # 4. Verificar estructura de la base de datos
    print("\n4️⃣ VERIFICANDO ESTRUCTURA DE LA BASE DE DATOS:")
    try:
        # Intentar obtener estadísticas para ver si hay errores de estructura
        response = requests.get(f"{railway_url}/api/v1/dashboard/stats?period=24h", timeout=15)
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                error_msg = str(data['error'])
                if "notification_type" in error_msg:
                    print("   ❌ Problema: Columna 'notification_type' no existe")
                    print("   💡 Solución: La base de datos necesita ser inicializada correctamente")
                elif "table" in error_msg.lower():
                    print("   ❌ Problema: Tabla no existe o estructura incorrecta")
                    print("   💡 Solución: Ejecutar inicialización de base de datos")
                else:
                    print(f"   ❌ Error desconocido: {error_msg[:100]}...")
            else:
                print("   ✅ Estructura de base de datos correcta")
        else:
            print(f"   ❌ No se pudo verificar estructura: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error verificando estructura: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Verificación completada")

def main():
    """Función principal"""
    print(f"🕐 Iniciando verificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    verify_railway_database()
    
    print("\n💡 RECOMENDACIONES:")
    print("   - Si la base de datos no se inicializó, espera a que Railway aplique los cambios")
    print("   - Una vez aplicados, ejecuta nuevamente este script")
    print("   - El dashboard debería funcionar correctamente después de la inicialización")

if __name__ == "__main__":
    main()
