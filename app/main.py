#!/usr/bin/env python3
"""
Aplicación ClickUp OAuth que funciona con el comportamiento real de ClickUp
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from urllib.parse import urlencode
import os

app = FastAPI(title="ClickUp OAuth Working")

@app.get("/")
async def handle_root(request: Request):
    """Maneja la raíz y cualquier redirección de ClickUp"""
    # Obtener parámetros de la URL
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")
    
    # Si hay código de autorización, es un callback exitoso
    if code:
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OAuth Success</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .container {{ 
                    background: white; 
                    padding: 40px; 
                    border-radius: 20px; 
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    max-width: 500px;
                }}
                .success {{ color: #28a745; font-size: 3rem; margin-bottom: 20px; }}
                .code {{ 
                    background: #e8f5e8; 
                    padding: 15px; 
                    border-radius: 10px; 
                    margin: 20px 0; 
                    font-family: monospace;
                    word-break: break-all;
                }}
                .btn {{ 
                    background: #667eea; 
                    color: white; 
                    padding: 15px 30px; 
                    text-decoration: none; 
                    border-radius: 10px; 
                    display: inline-block;
                    margin: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success">🎉</div>
                <h1>¡OAuth Exitoso!</h1>
                <p>ClickUp se conectó correctamente a tu aplicación</p>
                <div class="code">
                    <strong>Código de autorización:</strong><br>
                    {code}
                </div>
                <p><strong>Estado:</strong> {state or 'No especificado'}</p>
                <p>✅ Tu integración OAuth está funcionando perfectamente</p>
                <a href="/" class="btn">Probar nuevamente</a>
            </div>
        </body>
        </html>
        """)
    
    # Si hay error, mostrarlo
    if error:
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OAuth Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error {{ color: #dc3545; font-size: 3rem; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="error">❌</div>
            <h1>Error OAuth</h1>
            <p><strong>Error:</strong> {error}</p>
            <a href="/" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Volver al inicio
            </a>
        </body>
        </html>
        """)
    
    # Página principal de login
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ClickUp OAuth Test</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container { 
                background: white; 
                padding: 40px; 
                border-radius: 20px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                max-width: 400px;
            }
            .btn { 
                background: #667eea; 
                color: white; 
                padding: 15px 30px; 
                text-decoration: none; 
                border-radius: 10px; 
                display: inline-block;
                margin: 10px;
                font-size: 1.1rem;
                font-weight: bold;
            }
            .btn:hover { background: #5a6fd8; }
            .logo { font-size: 3rem; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🔐</div>
            <h1>ClickUp OAuth Test</h1>
            <p>Prueba la integración con ClickUp</p>
            <a href="/oauth" class="btn">Iniciar con ClickUp</a>
            <p><small>Esta aplicación maneja correctamente las redirecciones de ClickUp</small></p>
        </div>
    </body>
    </html>
    """)

@app.get("/oauth")
async def start_oauth():
    """Iniciar el flujo OAuth con ClickUp"""
    client_id = "0J2LPSHXIM5PRB5VDE5CRJY7FJP86L0H"
    redirect_uri = "https://clickuptaskmanager-production.up.railway.app"
    
    # Construir URL de autorización
    auth_url = f"https://app.clickup.com/api/v2/oauth/authorize?" + urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'read:user read:workspace read:task write:task'
    })
    
    return RedirectResponse(url=auth_url)

@app.get("/{path:path}")
async def handle_any_path(request: Request, path: str):
    """Maneja cualquier ruta que no sea la raíz o /oauth"""
    # Redirigir a la función principal para manejar OAuth
    return await handle_root(request)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando ClickUp OAuth App...")
    print("🌐 URL: https://clickuptaskmanager-production.up.railway.app")
    print("🔧 Configurado para manejar el comportamiento real de ClickUp")
    uvicorn.run(app, host="0.0.0.0", port=8000)