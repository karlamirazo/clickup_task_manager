#!/usr/bin/env python3
"""
Verificar URL de OAuth
"""

import requests

def main():
    print("🔍 Verificando URL de OAuth...")
    
    try:
        # Obtener URL de OAuth
        response = requests.get("http://localhost:8000/api/auth/clickup", allow_redirects=False)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 307:
            redirect_url = response.headers.get('Location', '')
            print(f"Redirect URL: {redirect_url}")
            
            # Verificar si la URL es válida
            if 'app.clickup.com' in redirect_url:
                print("✅ URL de ClickUp generada correctamente")
                
                # Probar la URL de ClickUp
                print("\n🌐 Probando URL de ClickUp...")
                clickup_response = requests.get(redirect_url, allow_redirects=False)
                print(f"ClickUp Status: {clickup_response.status_code}")
                
                if clickup_response.status_code == 200:
                    print("✅ URL de ClickUp accesible")
                elif clickup_response.status_code == 302:
                    print("✅ URL de ClickUp redirige (normal)")
                else:
                    print(f"❌ Error en ClickUp: {clickup_response.status_code}")
                    print(f"Response: {clickup_response.text[:200]}...")
            else:
                print("❌ URL no es de ClickUp")
        else:
            print(f"❌ Error obteniendo URL: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

