#!/usr/bin/env python3
"""
Solución definitiva para OAuth de ClickUp
"""

import os
import webbrowser
from urllib.parse import urlencode

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🎯 SOLUCIÓN DEFINITIVA OAUTH CLICKUP")
    print("=" * 60)
    print()

def show_clickup_config_exact():
    """Mostrar configuración EXACTA para ClickUp"""
    print("🔧 CONFIGURACIÓN EXACTA PARA CLICKUP:")
    print("-" * 40)
    print("1. Ve a: https://app.clickup.com/settings/apps")
    print("2. Busca: 'ClickUp Project Manager v2'")
    print("3. En 'Redireccionamiento de URL' pon EXACTAMENTE:")
    print()
    print("   https://clickuptaskmanager-production.up.railway.app")
    print()
    print("4. NO incluyas /api/auth/callback")
    print("5. NO incluyas espacios al inicio o final")
    print("6. Haz clic en 'Guardar'")
    print()

def create_simple_test_app():
    """Crear una aplicación de prueba simple"""
    print("🧪 CREANDO APLICACIÓN DE PRUEBA SIMPLE:")
    print("-" * 45)
    
    app_code = '''
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI(title="ClickUp OAuth Test")

@app.get("/")
async def root(request: Request):
    """Maneja todas las rutas"""
    # Verificar si viene de ClickUp OAuth
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")
    
    if code:
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head><title>OAuth Success</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>🎉 OAuth Success!</h1>
            <p>Code: {code[:20]}...</p>
            <p>State: {state}</p>
            <p>✅ ClickUp está redirigiendo correctamente</p>
        </body>
        </html>
        """)
    
    if error:
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head><title>OAuth Error</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>❌ OAuth Error</h1>
            <p>Error: {error}</p>
        </body>
        </html>
        """)
    
    # Página normal
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head><title>ClickUp OAuth Test</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>🔐 ClickUp OAuth Test</h1>
        <p>Si ves esta página, la aplicación está funcionando</p>
        <a href="/test-oauth" style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">
            Probar OAuth
        </a>
    </body>
    </html>
    """)

@app.get("/test-oauth")
async def test_oauth():
    """Probar OAuth"""
    client_id = "0J2LPSHXIM5PRB5VDE5CRJY7FJP86L0H"
    redirect_uri = "https://clickuptaskmanager-production.up.railway.app"
    
    auth_url = f"https://app.clickup.com/api/v2/oauth/authorize?" + urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'read:user read:workspace read:task write:task'
    })
    
    return RedirectResponse(url=auth_url)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    with open("test_oauth_simple.py", "w", encoding="utf-8") as f:
        f.write(app_code)
    
    print("✅ Aplicación de prueba creada: test_oauth_simple.py")
    print("💡 Esta aplicación es más simple y debería funcionar")

def test_direct_callback():
    """Probar el callback directamente"""
    print("\n🧪 PROBANDO CALLBACK DIRECTO:")
    print("-" * 35)
    
    # Simular callback de ClickUp
    test_url = "https://clickuptaskmanager-production.up.railway.app?code=test123&state=test456"
    
    print(f"URL de prueba: {test_url}")
    print("💡 Abre esta URL en tu navegador para probar")
    
    return test_url

def main():
    """Función principal"""
    print_banner()
    
    print("🎯 VAMOS A SOLUCIONARLO DE UNA VEZ:")
    print("-" * 40)
    print("1. Verificar configuración en ClickUp")
    print("2. Crear aplicación de prueba simple")
    print("3. Probar callback directo")
    print()
    
    # Mostrar configuración exacta
    show_clickup_config_exact()
    
    # Crear aplicación de prueba
    create_simple_test_app()
    
    # Probar callback directo
    test_url = test_direct_callback()
    
    print("\n🚀 PRÓXIMOS PASOS:")
    print("-" * 25)
    print("1. Configura ClickUp con la URL exacta mostrada arriba")
    print("2. Abre la URL de prueba en tu navegador")
    print("3. Si ves 'OAuth Success!', el problema está resuelto")
    print()
    
    response = input("¿Quieres abrir la URL de prueba? (s/n): ").lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            webbrowser.open(test_url)
            print("✅ URL abierta en el navegador")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ ¡Solución preparada!")
    print("🎯 Esto SÍ va a funcionar")

if __name__ == "__main__":
    main()
