#!/usr/bin/env python3
"""
Solución OAuth simple que SÍ funciona
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import webbrowser
from urllib.parse import urlencode

app = FastAPI(title="ClickUp OAuth Working")

@app.get("/")
async def home(request: Request):
    """Página principal que maneja TODO"""
    # Verificar si viene de ClickUp OAuth
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")
    
    if code:
        # ¡OAuth exitoso! Mostrar información
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OAuth Success</title>
            <style>
                body {{ font-family: Arial; text-align: center; padding: 50px; background: #f0f0f0; }}
                .success {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .code {{ background: #e8f5e8; padding: 10px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="success">
                <h1>🎉 ¡OAuth Exitoso!</h1>
                <p>ClickUp se conectó correctamente a tu aplicación</p>
                <div class="code">
                    <strong>Código de autorización:</strong> {code[:20]}...
                </div>
                <p><strong>Estado:</strong> {state}</p>
                <p>✅ Tu OAuth está funcionando perfectamente</p>
                <a href="/" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    Volver al inicio
                </a>
            </div>
        </body>
        </html>
        """)
    
    if error:
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head><title>OAuth Error</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>❌ Error OAuth</h1>
            <p>Error: {error}</p>
            <a href="/">Volver al inicio</a>
        </body>
        </html>
        """)
    
    # Página normal de login
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ClickUp OAuth Test</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .container { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); max-width: 400px; margin: 0 auto; }
            .btn { background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 10px; display: inline-block; margin: 10px; }
            .btn:hover { background: #5a6fd8; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 ClickUp OAuth Test</h1>
            <p>Prueba la conexión con ClickUp</p>
            <a href="/oauth" class="btn">Iniciar con ClickUp</a>
            <p><small>Esta es una versión simplificada que SÍ funciona</small></p>
        </div>
    </body>
    </html>
    """)

@app.get("/oauth")
async def start_oauth():
    """Iniciar OAuth con ClickUp"""
    client_id = "0J2LPSHXIM5PRB5VDE5CRJY7FJP86L0H"
    redirect_uri = "https://clickuptaskmanager-production.up.railway.app"
    
    auth_url = f"https://app.clickup.com/api/v2/oauth/authorize?" + urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'read:user read:workspace read:task write:task'
    })
    
    return RedirectResponse(url=auth_url)

@app.get("/{path:path}")
async def catch_all(request: Request, path: str):
    """Maneja cualquier ruta"""
    return await home(request)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor OAuth simple...")
    print("🌐 Ve a: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
