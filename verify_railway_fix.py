#!/usr/bin/env python3
"""
Verificar que Railway esté funcionando correctamente
"""

import requests
import time

def verify_railway_fix():
    """Verificar que Railway esté funcionando"""
    print("🔍 VERIFICANDO QUE RAILWAY ESTÉ FUNCIONANDO")
    print("=" * 60)
    
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Esperar un poco para que Railway se actualice
    print("⏳ Esperando 30 segundos para que Railway se actualice...")
    time.sleep(30)
    
    # Probar endpoints
    print("1. Probando endpoints...")
    endpoints = [
        "/",
        "/health", 
        "/docs",
        "/api/auth/login",
        "/api/auth/clickup"
    ]
    
    for endpoint in endpoints:
        url = f"{railway_url}{endpoint}"
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', 'N/A')
                print(f"   Content-Type: {content_type}")
                
                if endpoint == "/health":
                    try:
                        data = response.json()
                        print(f"   Health data: {data}")
                    except:
                        print(f"   Health response: {response.text[:100]}...")
            elif response.status_code == 404:
                print(f"   ❌ No encontrado - Railway no está usando main.py")
            elif response.status_code == 500:
                print(f"   ❌ Error interno del servidor")
            else:
                print(f"   ⚠️  Status inesperado: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"❌ {endpoint}: Timeout - Railway no responde")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint}: Error de conexión - Railway no disponible")
        except Exception as e:
            print(f"❌ {endpoint}: Error: {e}")
    
    print(f"\n2. Verificando configuración...")
    print("📋 Si sigue fallando:")
    print("   1. Ve a Railway Dashboard")
    print("   2. Verifica que Start Command sea: python main.py")
    print("   3. Verifica que las variables estén configuradas")
    print("   4. Haz clic en 'Redeploy'")
    print("   5. Espera a que termine el deploy")

def main():
    """Función principal"""
    print("🔍 VERIFICAR QUE RAILWAY ESTÉ FUNCIONANDO")
    print("=" * 70)
    
    # Verificar Railway
    verify_railway_fix()
    
    print(f"\n" + "=" * 70)
    print("📋 Si Railway sigue fallando:")
    print("1. Verifica la configuración en Railway Dashboard")
    print("2. Redespliega manualmente")
    print("3. Revisa los logs de Railway")

if __name__ == "__main__":
    main()
