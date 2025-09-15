#!/usr/bin/env python3
"""
Aplicación simple de OAuth para ClickUp
"""

import os
import secrets
from urllib.parse import urlencode
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI(title="ClickUp OAuth Simple")

@app.get("/")
async def root_redirect(request: Request):
    """Maneja la redirección desde ClickUp OAuth"""
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

@app.get("/{path:path}")
async def catch_all_redirect(request: Request, path: str):
    """Maneja cualquier ruta que no sea la raíz"""
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

async def show_login_page():
    """Mostrar página de login"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ClickUp Task Manager</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
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
            
            .logo {
                font-size: 2.5rem;
                color: #667eea;
                margin-bottom: 10px;
            }
            
            .title {
                color: #333;
                margin-bottom: 30px;
                font-size: 1.5rem;
                font-weight: 600;
            }
            
            .subtitle {
                color: #666;
                margin-bottom: 40px;
                font-size: 1rem;
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
                margin-bottom: 20px;
            }
            
            .oauth-button:hover {
                background: #5a6fd8;
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            
            .features {
                text-align: left;
                margin-top: 30px;
            }
            
            .feature {
                display: flex;
                align-items: center;
                margin-bottom: 15px;
                color: #666;
                font-size: 0.9rem;
            }
            
            .feature-icon {
                margin-right: 10px;
                color: #667eea;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="logo">📋</div>
            <h1 class="title">ClickUp Task Manager</h1>
            <p class="subtitle">Gestiona tus tareas de manera inteligente</p>
            
            <a href="/oauth/clickup" class="oauth-button">
                🔐 Iniciar con ClickUp
            </a>
            
            <div class="features">
                <div class="feature">
                    <span class="feature-icon">✓</span>
                    Sincronización automática con ClickUp
                </div>
                <div class="feature">
                    <span class="feature-icon">✓</span>
                    Notificaciones inteligentes
                </div>
                <div class="feature">
                    <span class="feature-icon">✓</span>
                    Dashboard personalizado
                </div>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/oauth/clickup")
async def clickup_oauth():
    """OAuth de ClickUp"""
    # Obtener configuración de OAuth
    client_id = os.getenv('CLICKUP_OAUTH_CLIENT_ID', '')
    # Manejar tanto con https:// como sin https://
    redirect_uri = os.getenv('CLICKUP_OAUTH_REDIRECT_URI', 'https://clickuptaskmanager-production.up.railway.app')
    if not redirect_uri.startswith('http'):
        redirect_uri = f'https://{redirect_uri}'
    
    if not client_id:
        return {"error": "OAuth not configured", "client_id": client_id}
    
    # Generar state para seguridad
    state = secrets.token_urlsafe(32)
    
    # Construir URL de autorización
    auth_url = f"https://app.clickup.com/api/v2/oauth/authorize?" + urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'state': state,
        'scope': 'read:user read:workspace read:task write:task'
    })
    
    return RedirectResponse(url=auth_url)

@app.get("/oauth/callback")
async def clickup_oauth_callback(code: str = None, state: str = None, error: str = None):
    """Callback de OAuth de ClickUp"""
    if error:
        return {"error": f"Authorization error: {error}"}
    
    if not code:
        return {"error": "No authorization code received"}
    
    return {
        "message": "OAuth callback successful",
        "code": code[:20] + "..." if code else None,
        "state": state
    }

@app.get("/debug")
async def debug():
    """Endpoint de debug"""
    client_id = os.getenv('CLICKUP_OAUTH_CLIENT_ID', '')
    client_secret = os.getenv('CLICKUP_OAUTH_CLIENT_SECRET', '')
    redirect_uri = os.getenv('CLICKUP_OAUTH_REDIRECT_URI', '')
    
    return {
        "status": "ok",
        "client_id_present": bool(client_id),
        "client_secret_present": bool(client_secret),
        "redirect_uri_present": bool(redirect_uri),
        "redirect_uri_value": redirect_uri
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting simple OAuth app on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
