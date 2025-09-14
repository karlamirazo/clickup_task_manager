#!/usr/bin/env python3
"""
Monitorear OAuth en tiempo real
"""

import time
import requests
import json
from datetime import datetime

def monitor_oauth():
    """Monitorear OAuth en tiempo real"""
    print("🔍 MONITOREANDO OAUTH EN TIEMPO REAL")
    print("=" * 50)
    print("Presiona Ctrl+C para detener")
    print()
    
    try:
        while True:
            # Probar URL de OAuth
            try:
                response = requests.get("http://127.0.0.1:8000/api/auth/clickup", allow_redirects=False)
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                if response.status_code == 307:
                    redirect_url = response.headers.get('Location', '')
                    print(f"[{timestamp}] ✅ OAuth funcionando")
                    print(f"[{timestamp}] 📊 Redirect: {redirect_url[:100]}...")
                    
                    # Verificar si la URL contiene los parámetros correctos
                    if 'client_id=' in redirect_url and 'redirect_uri=' in redirect_url:
                        print(f"[{timestamp}] ✅ Parámetros OAuth correctos")
                    else:
                        print(f"[{timestamp}] ❌ Parámetros OAuth faltantes")
                        
                else:
                    print(f"[{timestamp}] ❌ Error OAuth: {response.status_code}")
                    
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

def test_oauth_flow():
    """Probar flujo OAuth completo"""
    print("🧪 PROBANDO FLUJO OAUTH COMPLETO")
    print("=" * 50)
    
    try:
        # Probar URL de login
        login_response = requests.get("http://127.0.0.1:8000/api/auth/login")
        
        if login_response.status_code == 200:
            print("✅ Página de login accesible")
            
            # Probar URL de OAuth
            oauth_response = requests.get("http://127.0.0.1:8000/api/auth/clickup", allow_redirects=False)
            
            if oauth_response.status_code == 307:
                redirect_url = oauth_response.headers.get('Location', '')
                print("✅ URL de OAuth generada")
                print(f"📊 Redirect URL: {redirect_url}")
                
                # Verificar parámetros
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
                
            else:
                print(f"❌ Error en OAuth: {oauth_response.status_code}")
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🎯 MONITOR DE OAUTH CLICKUP")
    print("=" * 60)
    
    # Probar flujo OAuth
    test_oauth_flow()
    
    print("\n" + "=" * 60)
    print("¿Quieres monitorear en tiempo real? (y/n)")
    
    choice = input().lower()
    if choice == 'y':
        monitor_oauth()
    else:
        print("👋 ¡Hasta luego!")

if __name__ == "__main__":
    main()
