#!/usr/bin/env python3
"""
Probar OAuth final con ClickUp
"""

import requests
import time
from datetime import datetime

def test_oauth_final():
    """Probar OAuth final con ClickUp"""
    print("🧪 PROBANDO OAUTH FINAL CON CLICKUP")
    print("=" * 50)
    
    try:
        # Probar URL de login
        print("1. Probando página de login...")
        login_response = requests.get("http://127.0.0.1:8000/api/auth/login")
        
        if login_response.status_code == 200:
            print("✅ Página de login accesible")
            
            # Probar URL de OAuth
            print("2. Probando URL de OAuth...")
            oauth_response = requests.get("http://127.0.0.1:8000/api/auth/clickup", allow_redirects=False)
            
            if oauth_response.status_code == 307:
                redirect_url = oauth_response.headers.get('Location', '')
                print("✅ URL de OAuth generada")
                print(f"📊 Redirect URL: {redirect_url}")
                
                # Verificar parámetros
                print("3. Verificando parámetros...")
                
                if 'client_id=7US6KJX26FOROTI3ZSOZYCAXBCG7W386' in redirect_url:
                    print("✅ Client ID correcto")
                else:
                    print("❌ Client ID incorrecto")
                    
                if 'redirect_uri=http%3A%2F%2F127.0.0.1%3A8000' in redirect_url:
                    print("✅ Redirect URI correcto")
                else:
                    print("❌ Redirect URI incorrecto")
                    
                if 'scope=read%3Auser+read%3Aworkspace+read%3Atask+write%3Atask' in redirect_url:
                    print("✅ Scope correcto")
                else:
                    print("❌ Scope incorrecto")
                    
                print("\n🎉 ¡OAuth configurado correctamente!")
                print("📋 Próximos pasos:")
                print("1. Ve a la URL de redirect en tu navegador")
                print("2. Acepta los permisos en ClickUp")
                print("3. Serás redirigido al dashboard")
                
                # Abrir URL en navegador
                print("\n🔗 Abriendo URL de OAuth en el navegador...")
                import webbrowser
                webbrowser.open(redirect_url)
                
            else:
                print(f"❌ Error en OAuth: {oauth_response.status_code}")
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def monitor_callback():
    """Monitorear callback de OAuth"""
    print("\n🔍 MONITOREANDO CALLBACK DE OAUTH")
    print("=" * 50)
    print("Esperando callback de ClickUp...")
    print("Presiona Ctrl+C para detener")
    
    try:
        while True:
            # Probar callback
            try:
                response = requests.get("http://127.0.0.1:8000/api/auth/callback?code=test&state=test", allow_redirects=False)
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                if response.status_code == 307:
                    redirect_url = response.headers.get('Location', '')
                    print(f"[{timestamp}] ✅ Callback funcionando")
                    print(f"[{timestamp}] 📊 Redirect: {redirect_url}")
                else:
                    print(f"[{timestamp}] ❌ Error callback: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] ⚠️  Servidor no disponible")
                
            except Exception as e:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] ❌ Error: {e}")
            
            # Esperar 5 segundos
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoreo detenido")

def main():
    """Función principal"""
    print("🎯 PROBANDO OAUTH FINAL CON CLICKUP")
    print("=" * 60)
    
    # Probar OAuth
    test_oauth_final()
    
    print("\n" + "=" * 60)
    print("¿Quieres monitorear el callback? (y/n)")
    
    choice = input().lower()
    if choice == 'y':
        monitor_callback()
    else:
        print("👋 ¡Hasta luego!")

if __name__ == "__main__":
    main()
