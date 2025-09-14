#!/usr/bin/env python3
"""
Verificar despliegue en Railway
"""

import requests
import json

def check_railway_deployment():
    """Verificar despliegue en Railway"""
    print("🔍 VERIFICANDO DESPLIEGUE EN RAILWAY")
    print("=" * 50)
    
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Probar diferentes endpoints
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
                print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
                if endpoint == "/health":
                    try:
                        data = response.json()
                        print(f"   Health data: {data}")
                    except:
                        pass
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    # Verificar si es un problema de Railway
    print(f"\n🔍 Verificando estado de Railway...")
    try:
        # Probar con User-Agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(railway_url, headers=headers, timeout=10)
        print(f"Status con User-Agent: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Railway responde con User-Agent")
            print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        else:
            print(f"❌ Railway no responde correctamente")
            
    except Exception as e:
        print(f"❌ Error verificando Railway: {e}")

def check_railway_logs():
    """Verificar logs de Railway"""
    print(f"\n📋 INSTRUCCIONES PARA VERIFICAR RAILWAY:")
    print("=" * 50)
    print("1. Ve a: https://railway.app/dashboard")
    print("2. Busca tu proyecto 'clickuptaskmanager'")
    print("3. Haz clic en el servicio")
    print("4. Ve a la pestaña 'Deployments'")
    print("5. Revisa los logs del último despliegue")
    print("6. Busca errores como:")
    print("   - 'Module not found'")
    print("   - 'Import error'")
    print("   - 'Port binding error'")
    print("   - 'Database connection error'")

def suggest_fixes():
    """Sugerir soluciones"""
    print(f"\n🛠️  POSIBLES SOLUCIONES:")
    print("=" * 30)
    print("1. **Verificar que main_simple.py esté en la raíz**")
    print("2. **Verificar que requirements.txt esté actualizado**")
    print("3. **Verificar variables de entorno en Railway**")
    print("4. **Verificar que la base de datos esté configurada**")
    print("5. **Verificar que el puerto esté configurado correctamente**")

def main():
    """Función principal"""
    print("🔍 DIAGNÓSTICO DE RAILWAY")
    print("=" * 60)
    
    # Verificar despliegue
    check_railway_deployment()
    
    # Verificar logs
    check_railway_logs()
    
    # Sugerir soluciones
    suggest_fixes()
    
    print(f"\n" + "=" * 60)
    print("📋 PRÓXIMOS PASOS:")
    print("1. Revisa los logs de Railway")
    print("2. Verifica la configuración")
    print("3. Redespliega si es necesario")
    print("4. Prueba OAuth una vez que funcione")

if __name__ == "__main__":
    main()
