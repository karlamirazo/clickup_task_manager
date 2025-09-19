#!/usr/bin/env python3
"""
Script de diagnóstico completo para el error 404 en OAuth
"""

import os
import requests
from datetime import datetime

def print_header():
    """Imprimir cabecera del script"""
    print("=" * 80)
    print("🔍 DIAGNÓSTICO COMPLETO OAUTH 404")
    print("=" * 80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def test_app_endpoints():
    """Probar todos los endpoints de la aplicación"""
    print("🌐 PROBANDO ENDPOINTS DE LA APLICACIÓN...")
    print("-" * 60)
    
    base_url = "https://ctm-pro.up.railway.app"
    
    endpoints_to_test = [
        "/",
        "/callback",
        "/api/auth/login",
        "/api/auth/callback", 
        "/api/auth/status",
        "/dashboard"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            url = f"{base_url}{endpoint}"
            print(f"📍 Probando: {endpoint}")
            
            response = requests.get(url, timeout=10, allow_redirects=False)
            
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📄 Headers: {dict(list(response.headers.items())[:3])}")
            
            if 'location' in response.headers:
                print(f"   🔄 Redirect: {response.headers['location']}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
        
        print()

def test_oauth_callback_simulation():
    """Simular callback OAuth con parámetros"""
    print("🔐 SIMULANDO CALLBACK OAUTH...")
    print("-" * 60)
    
    base_url = "https://ctm-pro.up.railway.app"
    
    # Simular diferentes escenarios de callback
    test_cases = [
        {
            "name": "Callback raíz con code",
            "url": f"{base_url}/?code=test_code_123&state=test_state_456"
        },
        {
            "name": "Callback /callback con code", 
            "url": f"{base_url}/callback?code=test_code_123&state=test_state_456"
        },
        {
            "name": "Callback /api/auth/callback con code",
            "url": f"{base_url}/api/auth/callback?code=test_code_123&state=test_state_456"
        },
        {
            "name": "Callback con error",
            "url": f"{base_url}/?error=access_denied"
        }
    ]
    
    for test_case in test_cases:
        try:
            print(f"🧪 {test_case['name']}")
            print(f"   URL: {test_case['url']}")
            
            response = requests.get(test_case['url'], timeout=10, allow_redirects=False)
            
            print(f"   ✅ Status: {response.status_code}")
            
            if response.status_code == 404:
                print(f"   ❌ ERROR 404 - Endpoint no encontrado")
            elif response.status_code in [301, 302, 307, 308]:
                print(f"   🔄 Redirect a: {response.headers.get('location', 'N/A')}")
            elif response.status_code == 200:
                print(f"   ✅ Respuesta OK")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
        
        print()

def check_environment_config():
    """Verificar configuración de variables de entorno"""
    print("⚙️ VERIFICANDO CONFIGURACIÓN...")
    print("-" * 60)
    
    # Verificar archivos de configuración locales
    config_files = ['.env', 'env.production', 'env.oauth.simple']
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"📄 {config_file}:")
            with open(config_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if 'CLICKUP_OAUTH_REDIRECT_URI' in line:
                        print(f"   {line.strip()}")
            print()

def print_solution_steps():
    """Imprimir pasos de solución"""
    print("🔧 PASOS DE SOLUCIÓN...")
    print("-" * 60)
    print("1. ✅ VERIFICAR VARIABLE EN RAILWAY:")
    print("   • Debe ser: CLICKUP_OAUTH_REDIRECT_URI=https://ctm-pro.up.railway.app")
    print("   • NO olvidar el https://")
    print()
    print("2. ✅ VERIFICAR CLICKUP:")
    print("   • Redirect URI: ctm-pro.up.railway.app (sin https://)")
    print("   • ClickUp agrega automáticamente https://")
    print()
    print("3. ✅ REINICIAR SERVICIO:")
    print("   • Después de cambiar variables en Railway")
    print("   • Esperar 2-3 minutos para el deploy")
    print()
    print("4. ✅ PROBAR OAUTH:")
    print("   • Ir a: https://ctm-pro.up.railway.app")
    print("   • Clic en 'Iniciar con ClickUp'")
    print("   • Verificar que redirige correctamente")

def main():
    """Función principal"""
    print_header()
    
    # Probar endpoints
    test_app_endpoints()
    
    # Simular callbacks OAuth
    test_oauth_callback_simulation()
    
    # Verificar configuración
    check_environment_config()
    
    # Mostrar solución
    print_solution_steps()
    
    print("\n" + "=" * 80)
    print("✅ DIAGNÓSTICO COMPLETADO")
    print("=" * 80)
    print("🎯 Si algún endpoint devuelve 404, ese es el problema")
    print("🔧 Sigue los pasos de solución para corregirlo")

if __name__ == "__main__":
    main()
