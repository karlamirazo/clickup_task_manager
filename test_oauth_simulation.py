#!/usr/bin/env python3
"""
Probar OAuth con simulación para verificar el flujo completo
"""

import requests
import webbrowser
import time

def print_banner():
    """Mostrar banner"""
    print("=" * 60)
    print("🎯 PRUEBA DE OAUTH CON SIMULACIÓN")
    print("=" * 60)
    print()

def test_oauth_url():
    """Probar URL de OAuth"""
    print("1️⃣ PROBANDO URL DE OAUTH...")
    
    try:
        response = requests.get("http://localhost:8000/api/auth/clickup", allow_redirects=False)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 307:
            redirect_url = response.headers.get('Location', '')
            print(f"   ✅ URL generada correctamente")
            print(f"   🔗 URL: {redirect_url[:80]}...")
            return redirect_url
        else:
            print(f"   ❌ Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def simulate_clickup_callback():
    """Simular callback de ClickUp"""
    print("\n2️⃣ SIMULANDO CALLBACK DE CLICKUP...")
    
    # Simular código de autorización real
    simulated_code = "real_authorization_code_from_clickup_12345"
    simulated_state = "simulated_state_67890"
    
    callback_url = f"http://localhost:8000/api/auth/callback?code={simulated_code}&state={simulated_state}"
    print(f"   📤 Callback URL: {callback_url}")
    
    try:
        response = requests.get(callback_url, allow_redirects=False)
        print(f"   📊 Status: {response.status_code}")
        
        if 'Location' in response.headers:
            redirect_url = response.headers['Location']
            print(f"   🔄 Redirect: {redirect_url}")
            
            if '/dashboard' in redirect_url:
                print("   ✅ ¡Redirección al dashboard exitosa!")
                return True
            elif '/api/auth/login' in redirect_url:
                print("   ❌ Redirigiendo a login (error)")
                return False
            else:
                print(f"   ⚠️  Redirección inesperada")
                return False
        else:
            print("   ❌ No hay redirección")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_dashboard_access():
    """Probar acceso al dashboard"""
    print("\n3️⃣ PROBANDO ACCESO AL DASHBOARD...")
    
    try:
        response = requests.get("http://localhost:8000/dashboard")
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Dashboard accesible")
            return True
        else:
            print(f"   ❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def show_real_oauth_instructions():
    """Mostrar instrucciones para OAuth real"""
    print("\n📋 INSTRUCCIONES PARA OAUTH REAL")
    print("=" * 50)
    print("Para probar con ClickUp real:")
    print("1. Ve a: http://localhost:8000/api/auth/login")
    print("2. Haz clic en 'Iniciar con ClickUp'")
    print("3. En ClickUp, haz clic en 'Continue on web anyway'")
    print("4. Completa la autorización")
    print("5. ClickUp te redirigirá automáticamente")
    print()
    print("🔧 Si hay problemas:")
    print("   - Verifica que la aplicación esté ejecutándose")
    print("   - Verifica que el puerto 8000 esté libre")
    print("   - Revisa los logs de la aplicación")

def main():
    """Función principal"""
    print_banner()
    
    # Paso 1: Probar URL de OAuth
    oauth_url = test_oauth_url()
    if not oauth_url:
        print("❌ No se pudo generar URL de OAuth")
        return
    
    # Paso 2: Simular callback
    callback_ok = simulate_clickup_callback()
    
    # Paso 3: Probar dashboard
    dashboard_ok = test_dashboard_access()
    
    # Mostrar instrucciones
    show_real_oauth_instructions()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL")
    print("=" * 60)
    print(f"OAuth URL: {'✅ OK' if oauth_url else '❌ ERROR'}")
    print(f"Callback: {'✅ OK' if callback_ok else '❌ ERROR'}")
    print(f"Dashboard: {'✅ OK' if dashboard_ok else '❌ ERROR'}")
    
    if oauth_url and callback_ok and dashboard_ok:
        print("\n🎉 ¡TODO FUNCIONANDO!")
        print("   El OAuth está configurado correctamente")
        print("   Puedes probar con ClickUp real siguiendo las instrucciones")
    else:
        print("\n❌ HAY PROBLEMAS")
        print("   Revisa la configuración de la aplicación")

if __name__ == "__main__":
    main()

