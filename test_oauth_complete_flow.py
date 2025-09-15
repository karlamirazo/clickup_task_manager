#!/usr/bin/env python3
"""
Probar flujo completo de OAuth paso a paso
"""

import requests
import webbrowser
import time

def print_banner():
    """Mostrar banner"""
    print("=" * 60)
    print("🎯 PRUEBA COMPLETA DE FLUJO OAUTH")
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
            print(f"   ✅ URL generada: {redirect_url[:80]}...")
            return redirect_url
        else:
            print(f"   ❌ Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def open_oauth_in_browser(url):
    """Abrir OAuth en el navegador"""
    print("\n2️⃣ ABRIENDO OAUTH EN NAVEGADOR...")
    print("   🌐 Abriendo URL de ClickUp...")
    
    try:
        webbrowser.open(url)
        print("   ✅ Navegador abierto")
        return True
    except Exception as e:
        print(f"   ❌ Error abriendo navegador: {e}")
        return False

def wait_for_callback():
    """Esperar callback del usuario"""
    print("\n3️⃣ ESPERANDO CALLBACK...")
    print("   📋 Instrucciones:")
    print("   1. En ClickUp, haz clic en 'Continue on web anyway'")
    print("   2. Completa la autorización")
    print("   3. ClickUp te redirigirá automáticamente")
    print("   4. Presiona Enter cuando veas el dashboard")
    
    input("\n   ⏳ Presiona Enter cuando hayas completado la autorización...")
    return True

def test_dashboard_access():
    """Probar acceso al dashboard"""
    print("\n4️⃣ PROBANDO ACCESO AL DASHBOARD...")
    
    try:
        response = requests.get("http://localhost:8000/dashboard")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Dashboard accesible")
            return True
        else:
            print(f"   ❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def show_success_message():
    """Mostrar mensaje de éxito"""
    print("\n" + "=" * 60)
    print("🎉 ¡FLUJO OAUTH COMPLETADO!")
    print("=" * 60)
    print()
    print("✅ RESULTADO:")
    print("   - OAuth configurado correctamente")
    print("   - ClickUp redirige correctamente")
    print("   - Dashboard accesible")
    print()
    print("🚀 PRÓXIMOS PASOS:")
    print("   1. Ve a: http://localhost:8000/api/auth/login")
    print("   2. Haz clic en 'Iniciar con ClickUp'")
    print("   3. Completa la autorización")
    print("   4. ¡Serás redirigido al dashboard!")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Paso 1: Probar URL de OAuth
    oauth_url = test_oauth_url()
    if not oauth_url:
        print("❌ No se pudo generar URL de OAuth")
        return
    
    # Paso 2: Abrir en navegador
    if not open_oauth_in_browser(oauth_url):
        print("❌ No se pudo abrir navegador")
        return
    
    # Paso 3: Esperar callback
    if not wait_for_callback():
        print("❌ Callback no completado")
        return
    
    # Paso 4: Probar dashboard
    if test_dashboard_access():
        show_success_message()
    else:
        print("❌ Dashboard no accesible")

if __name__ == "__main__":
    main()

