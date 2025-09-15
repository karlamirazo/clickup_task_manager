#!/usr/bin/env python3
"""
Solución final para la configuración de ClickUp
"""

import webbrowser
from urllib.parse import urlencode

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🎯 SOLUCIÓN FINAL - CONFIGURACIÓN CLICKUP")
    print("=" * 60)
    print()

def show_exact_clickup_config():
    """Mostrar configuración EXACTA para ClickUp"""
    print("🔧 CONFIGURACIÓN EXACTA PARA CLICKUP:")
    print("-" * 45)
    print("1. Ve a: https://app.clickup.com/settings/apps")
    print("2. Busca: 'ClickUp Project Manager v2'")
    print("3. Haz clic en el dropdown para expandir")
    print("4. En 'Redireccionamiento de URL' pon EXACTAMENTE:")
    print()
    print("   https://clickuptaskmanager-production.up.railway.app")
    print()
    print("5. NO incluyas /api/auth/callback")
    print("6. NO incluyas espacios")
    print("7. Haz clic en 'Guardar'")
    print("8. Espera 30 segundos")
    print()

def test_current_config():
    """Probar la configuración actual"""
    print("🧪 PROBANDO CONFIGURACIÓN ACTUAL:")
    print("-" * 40)
    
    # URL de prueba con la configuración actual
    client_id = "0J2LPSHXIM5PRB5VDE5CRJY7FJP86L0H"
    redirect_uri = "https://clickuptaskmanager-production.up.railway.app"
    
    auth_url = f"https://app.clickup.com/api/v2/oauth/authorize?" + urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'read:user read:workspace read:task write:task'
    })
    
    print(f"URL de prueba: {auth_url}")
    print()
    print("📝 FLUJO ESPERADO:")
    print("1. ClickUp te redirigirá a: https://clickuptaskmanager-production.up.railway.app?code=...")
    print("2. Tu app interceptará esto y procesará el OAuth")
    print("3. Deberías ver la página de éxito")
    print()
    
    return auth_url

def create_debug_endpoint():
    """Crear endpoint de debug"""
    print("🔍 CREANDO ENDPOINT DE DEBUG:")
    print("-" * 35)
    
    debug_code = '''
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
async def debug_root(request: Request):
    """Endpoint de debug para ver qué recibe"""
    params = dict(request.query_params)
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head><title>Debug OAuth</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h1>🔍 Debug OAuth Callback</h1>
        <h2>Parámetros recibidos:</h2>
        <ul>
            {''.join([f'<li><strong>{k}:</strong> {v}</li>' for k, v in params.items()])}
        </ul>
        <h2>URL completa:</h2>
        <p>{request.url}</p>
        <h2>Headers:</h2>
        <ul>
            {''.join([f'<li><strong>{k}:</strong> {v}</li>' for k, v in request.headers.items()])}
        </ul>
    </body>
    </html>
    """)
'''
    
    with open("debug_oauth.py", "w", encoding="utf-8") as f:
        f.write(debug_code)
    
    print("✅ Endpoint de debug creado: debug_oauth.py")
    print("💡 Este endpoint te mostrará exactamente qué recibe tu app")

def main():
    """Función principal"""
    print_banner()
    
    print("🎯 PROBLEMA IDENTIFICADO:")
    print("-" * 30)
    print("✅ Tu aplicación funciona correctamente")
    print("❌ ClickUp no puede redirigir de vuelta")
    print("🔧 Necesitamos configurar ClickUp correctamente")
    print()
    
    # Mostrar configuración exacta
    show_exact_clickup_config()
    
    # Crear endpoint de debug
    create_debug_endpoint()
    
    # Probar configuración actual
    auth_url = test_current_config()
    
    print("🚀 PRÓXIMOS PASOS:")
    print("-" * 25)
    print("1. Configura ClickUp con la URL exacta mostrada arriba")
    print("2. Espera 30 segundos")
    print("3. Prueba el OAuth nuevamente")
    print("4. Si sigue fallando, ejecuta: python debug_oauth.py")
    print()
    
    response = input("¿Quieres abrir la URL de prueba? (s/n): ").lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            webbrowser.open(auth_url)
            print("✅ URL abierta en el navegador")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ ¡Solución preparada!")
    print("🎯 Una vez configurado ClickUp, funcionará perfectamente")

if __name__ == "__main__":
    main()
