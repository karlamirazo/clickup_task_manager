#!/usr/bin/env python3
"""
Script para configurar OAuth con ClickUp usando solo el dominio
"""

import os
import webbrowser
from urllib.parse import urlencode

def print_banner():
    """Mostrar banner del script"""
    print("=" * 60)
    print("🔧 SOLUCIÓN OAUTH CLICKUP - SOLO DOMINIO")
    print("=" * 60)
    print()

def show_clickup_config():
    """Mostrar configuración para ClickUp"""
    print("📋 CONFIGURACIÓN PARA CLICKUP:")
    print("-" * 35)
    print("En la configuración de ClickUp, usa SOLO el dominio:")
    print()
    print("✅ URL de redirección: https://clickuptaskmanager-production.up.railway.app")
    print("❌ NO incluyas: /api/auth/callback")
    print()
    print("ClickUp redirigirá a: https://clickuptaskmanager-production.up.railway.app?code=...")
    print("Nuestra app interceptará esto y redirigirá al callback correcto")
    print()

def create_redirect_handler():
    """Crear el manejador de redirección"""
    print("🔧 CREANDO MANEJADOR DE REDIRECCIÓN:")
    print("-" * 40)
    
    handler_code = '''
@app.get("/")
async def root_redirect(request: Request):
    """Maneja la redirección desde ClickUp"""
    # Verificar si viene de ClickUp OAuth
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")
    
    if code or error:
        # Es un callback de OAuth, redirigir al endpoint correcto
        query_params = request.query_params
        redirect_url = f"/api/auth/callback?{query_params}"
        return RedirectResponse(url=redirect_url)
    
    # Si no es OAuth, mostrar la página normal
    return await show_login_page()

def show_login_page():
    """Mostrar página de login"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ClickUp Task Manager</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0;
            }
            .login-container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                padding: 40px;
                width: 100%;
                max-width: 400px;
                text-align: center;
            }
            .oauth-button {
                background: #667eea;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 10px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s ease;
                width: 100%;
            }
            .oauth-button:hover {
                background: #5a6fd8;
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h1>📋 ClickUp Task Manager</h1>
            <p>Gestiona tus tareas de manera inteligente</p>
            <a href="/oauth/clickup" class="oauth-button">
                🔐 Iniciar con ClickUp
            </a>
        </div>
    </body>
    </html>
    """)
'''
    
    print("Código del manejador:")
    print(handler_code)
    print()

def update_app_main():
    """Actualizar app/main.py con el nuevo manejador"""
    print("📝 ACTUALIZANDO app/main.py:")
    print("-" * 30)
    
    # Leer el archivo actual
    try:
        with open("app/main.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Verificar si ya tiene el manejador
        if "root_redirect" in content:
            print("✅ El manejador ya está presente")
            return True
        
        # Agregar el manejador
        new_content = content.replace(
            '@app.get("/")',
            '''@app.get("/")
async def root_redirect(request: Request):
    """Maneja la redirección desde ClickUp"""
    # Verificar si viene de ClickUp OAuth
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")
    
    if code or error:
        # Es un callback de OAuth, redirigir al endpoint correcto
        query_params = request.query_params
        redirect_url = f"/api/auth/callback?{query_params}"
        return RedirectResponse(url=redirect_url)
    
    # Si no es OAuth, mostrar la página normal
    return await show_login_page()

@app.get("/login")
async def show_login_page():'''
        )
        
        # Escribir el archivo actualizado
        with open("app/main.py", "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print("✅ app/main.py actualizado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando app/main.py: {e}")
        return False

def test_configuration():
    """Probar la configuración"""
    print("🧪 PROBANDO CONFIGURACIÓN:")
    print("-" * 30)
    
    # Generar URL de prueba
    client_id = "0J2LPSHXIM5PRB5VDE5CRJY7FJP86L0H"
    redirect_uri = "https://clickuptaskmanager-production.up.railway.app"  # Sin path
    
    auth_url = f"https://app.clickup.com/api/v2/oauth/authorize?" + urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'read:user read:workspace read:task write:task'
    })
    
    print(f"URL de prueba: {auth_url}")
    print()
    
    response = input("¿Abrir URL de prueba? (s/n): ").lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            webbrowser.open(auth_url)
            print("✅ URL abierta en el navegador")
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print_banner()
    
    show_clickup_config()
    create_redirect_handler()
    
    print("📋 PASOS A SEGUIR:")
    print("-" * 20)
    print("1. Ve a ClickUp y configura la URL como:")
    print("   https://clickuptaskmanager-production.up.railway.app")
    print("2. Guarda los cambios en ClickUp")
    print("3. Actualiza tu aplicación con el nuevo manejador")
    print("4. Prueba el flujo completo")
    print()
    
    response = input("¿Quieres que actualice app/main.py automáticamente? (s/n): ").lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        if update_app_main():
            print("✅ Aplicación actualizada correctamente")
        else:
            print("❌ Error actualizando la aplicación")
    
    test_configuration()
    
    print("\n✅ ¡Configuración completada!")
    print("🚀 Ahora ClickUp debería funcionar correctamente")

if __name__ == "__main__":
    main()
