#!/usr/bin/env python3
"""
Aplicación ClickUp OAuth que captura TODAS las redirecciones
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from urllib.parse import urlencode
import os

app = FastAPI(title="ClickUp OAuth Universal")

@app.get("/")
async def handle_root(request: Request):
    """Maneja la raíz"""
    return await process_oauth_callback(request)

@app.get("/{path:path}")
async def handle_any_path(request: Request, path: str):
    """Maneja CUALQUIER ruta - esto es clave"""
    return await process_oauth_callback(request)

async def process_oauth_callback(request: Request):
    """Procesa el callback de OAuth desde cualquier ruta"""
    # Obtener parámetros de la URL
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")
    
    # Log para debug
    print(f"🔍 Ruta recibida: {request.url.path}")
    print(f"🔍 Parámetros: code={code}, state={state}, error={error}")
    
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
                    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
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
                    max-width: 600px;
                }}
                .success {{ color: #28a745; font-size: 4rem; margin-bottom: 20px; }}
                .code {{ 
                    background: #e8f5e8; 
                    padding: 15px; 
                    border-radius: 10px; 
                    margin: 20px 0; 
                    font-family: monospace;
                    word-break: break-all;
                    border: 2px solid #28a745;
                }}
                .info {{ 
                    background: #f8f9fa; 
                    padding: 15px; 
                    border-radius: 10px; 
                    margin: 20px 0;
                    text-align: left;
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
                
                <div class="info">
                    <strong>Información del callback:</strong><br>
                    • Ruta: {request.url.path}<br>
                    • Estado: {state or 'No especificado'}<br>
                    • URL completa: {request.url}<br>
                    • Método: {request.method}
                </div>
                
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
                body {{ 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px; 
                    background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
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
                }}
                .error {{ color: #dc3545; font-size: 4rem; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error">❌</div>
                <h1>Error OAuth</h1>
                <p><strong>Error:</strong> {error}</p>
                <p><strong>Ruta:</strong> {request.url.path}</p>
                <a href="/" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    Volver al inicio
                </a>
            </div>
        </body>
        </html>
        """)
    
    # Página principal de login
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ClickUp OAuth Universal</title>
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
                max-width: 500px;
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
            .logo { font-size: 4rem; margin-bottom: 20px; }
            .info { 
                background: #f8f9fa; 
                padding: 20px; 
                border-radius: 10px; 
                margin: 20px 0;
                text-align: left;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🔐</div>
            <h1>ClickUp OAuth Universal</h1>
            <p>Esta aplicación captura TODAS las redirecciones de ClickUp</p>
            
            <div class="info">
                <strong>Características:</strong><br>
                • Captura cualquier ruta de ClickUp<br>
                • Maneja URLs con y sin https://<br>
                • Compatible con dominios Railway<br>
                • Muestra información detallada del callback
            </div>
            
            <a href="/oauth" class="btn">Iniciar con ClickUp</a>
            <p><small>Esta versión SÍ funciona con ClickUp</small></p>
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

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando ClickUp OAuth Universal...")
    print("🌐 URL: https://clickuptaskmanager-production.up.railway.app")
    print("🔧 Captura TODAS las redirecciones de ClickUp")
    uvicorn.run(app, host="0.0.0.0", port=8000)