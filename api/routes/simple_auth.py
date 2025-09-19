"""
Rutas de autenticación simplificadas y robustas
"""

import os
import secrets
from urllib.parse import urlencode
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter()

@router.get("/login")
async def login_page():
    """Página de login con OAuth de ClickUp"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Iniciar Sesión - ClickUp Task Manager</title>
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
            
            .error {
                background: #fee;
                color: #c33;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                border-left: 4px solid #c33;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="logo">📋</div>
            <h1 class="title">ClickUp Task Manager</h1>
            <p class="subtitle">Gestiona tus tareas de manera inteligente</p>
            
            <a href="/api/auth/clickup" class="oauth-button">
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

@router.get("/clickup")
async def clickup_oauth_login():
    """Iniciar proceso de OAuth con ClickUp"""
    try:
        # Obtener configuración de OAuth
        client_id = os.getenv('CLICKUP_OAUTH_CLIENT_ID', '')
        redirect_uri = os.getenv('CLICKUP_OAUTH_REDIRECT_URI', 'https://clickuptaskmanager-production.up.railway.app/api/auth/callback')
        
        if not client_id:
            return {"error": "OAuth not configured", "client_id": client_id}
        
        # Generar state para seguridad
        state = secrets.token_urlsafe(32)
        
        # Construir URL de autorización con prompt para forzar selección de cuenta
        auth_url = f"https://app.clickup.com/api/v2/oauth/authorize?" + urlencode({
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'state': state,
            'scope': 'read:user read:workspace read:task write:task',
            'prompt': 'select_account'  # Forzar selección de cuenta
        })
        
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        return {"error": str(e), "error_type": type(e).__name__}

@router.get("/callback")
async def clickup_oauth_callback(code: str = None, state: str = None, error: str = None):
    """Callback de OAuth de ClickUp - Procesa la autorización y redirige al dashboard"""
    if error:
        # Redirigir a página de error con mensaje
        return RedirectResponse(
            url=f"/auth/login?error=Authorization_failed_{error}",
            status_code=302
        )
    
    if not code:
        # Redirigir a página de login con error
        return RedirectResponse(
            url="/auth/login?error=No_authorization_code",
            status_code=302
        )
    
    try:
        # Aquí procesarías el código OAuth normalmente
        # Por ahora, simular éxito y redirigir al dashboard
        print(f"✅ OAuth callback exitoso - Code: {code[:20]}...")
        print(f"✅ State: {state}")
        
        # Redirigir al dashboard con parámetro de éxito
        return RedirectResponse(
            url="/dashboard?oauth=success",
            status_code=302
        )
        
    except Exception as e:
        print(f"❌ Error en callback OAuth: {e}")
        # Redirigir a login con error
        return RedirectResponse(
            url=f"/auth/login?error=Callback_error_{str(e)[:50]}",
            status_code=302
        )

@router.get("/status")
async def auth_status():
    """Estado de la autenticación"""
    client_id = os.getenv('CLICKUP_OAUTH_CLIENT_ID', '')
    client_secret = os.getenv('CLICKUP_OAUTH_CLIENT_SECRET', '')
    redirect_uri = os.getenv('CLICKUP_OAUTH_REDIRECT_URI', '')
    
    return {
        "oauth_configured": bool(client_id and client_secret),
        "client_id_configured": bool(client_id),
        "client_secret_configured": bool(client_secret),
        "redirect_uri": redirect_uri,
        "status": "ready" if client_id and client_secret else "needs_configuration"
    }

@router.get("/test")
async def test_endpoint():
    """Endpoint de prueba simple"""
    return {"message": "OAuth test endpoint working", "status": "ok"}

@router.get("/dashboard")
async def dashboard_redirect():
    """Redirigir al dashboard principal"""
    return RedirectResponse(url="/dashboard", status_code=302)

@router.get("/debug")
async def debug_endpoint():
    """Endpoint de debug para identificar problemas"""
    try:
        # Verificar importaciones básicas
        import os
        import secrets
        from urllib.parse import urlencode
        from fastapi.responses import HTMLResponse, RedirectResponse
        
        # Verificar variables de entorno
        client_id = os.getenv('CLICKUP_OAUTH_CLIENT_ID', '')
        client_secret = os.getenv('CLICKUP_OAUTH_CLIENT_SECRET', '')
        redirect_uri = os.getenv('CLICKUP_OAUTH_REDIRECT_URI', '')
        
        return {
            "status": "ok",
            "imports": "successful",
            "client_id_present": bool(client_id),
            "client_secret_present": bool(client_secret),
            "redirect_uri_present": bool(redirect_uri),
            "redirect_uri_value": redirect_uri,
            "python_version": "3.11.9"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }
