"""
Rutas de autenticación simplificadas
"""

from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import RedirectResponse, HTMLResponse
import os
import secrets
from urllib.parse import urlencode

router = APIRouter(prefix="/api/auth", tags=["autenticación simple"])

@router.get("/login", response_class=HTMLResponse)
async def login_page():
    """Página de login"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - ClickUp Manager</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .auth-container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                padding: 60px 40px;
                max-width: 500px;
                width: 100%;
                text-align: center;
            }
            .auth-container h1 {
                color: #333;
                margin-bottom: 20px;
                font-size: 2.5rem;
            }
            .auth-container p {
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1rem;
            }
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 10px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                margin: 10px;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
            }
            .btn-clickup {
                background: #7b68ee;
            }
            .btn-clickup:hover {
                background: #6a5acd;
            }
            .features {
                text-align: left;
                margin: 30px 0;
            }
            .features li {
                margin: 10px 0;
                color: #666;
            }
            .features i {
                color: #667eea;
                margin-right: 10px;
            }
        </style>
    </head>
    <body>
        <div class="auth-container">
            <h1>🔐 ClickUp Manager</h1>
            <p>Gestiona tus proyectos de manera eficiente con nuestra plataforma integrada con ClickUp</p>
            
            <ul class="features">
                <li><i>✓</i> Sincronización automática con ClickUp</li>
                <li><i>✓</i> Notificaciones inteligentes</li>
                <li><i>✓</i> Dashboard personalizado</li>
                <li><i>✓</i> Gestión de equipos</li>
            </ul>
            
            <a href="/api/auth/clickup" class="btn btn-clickup">
                🚀 Iniciar con ClickUp
            </a>
            
            <a href="/dashboard" class="btn">
                📊 Ver Dashboard
            </a>
            
            <p><small>O ve al <a href="/">inicio</a></small></p>
        </div>
    </body>
    </html>
    """)

@router.get("/clickup")
async def clickup_oauth_login():
    """Iniciar proceso de OAuth con ClickUp"""
    # Obtener configuración de OAuth
    client_id = os.getenv('CLICKUP_OAUTH_CLIENT_ID', '')
    redirect_uri = os.getenv('CLICKUP_OAUTH_REDIRECT_URI', 'https://clickuptaskmanager-production.up.railway.app/api/auth/callback')
    
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

@router.get("/callback")
async def clickup_oauth_callback(code: str = None, state: str = None, error: str = None):
    """Callback de OAuth de ClickUp"""
    if error:
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error de Autorización</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error {{ color: #e74c3c; background: #fdf2f2; padding: 20px; border-radius: 10px; margin: 20px; }}
            </style>
        </head>
        <body>
            <h1>❌ Error de Autorización</h1>
            <div class="error">
                <p>Error: {error}</p>
                <p>No se pudo completar la autenticación con ClickUp.</p>
            </div>
            <p><a href="/api/auth/login">← Intentar de nuevo</a></p>
        </body>
        </html>
        """)
    
    if not code:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error de Callback</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error {{ color: #e74c3c; background: #fdf2f2; padding: 20px; border-radius: 10px; margin: 20px; }}
            </style>
        </head>
        <body>
            <h1>❌ Error de Callback</h1>
            <div class="error">
                <p>No se recibió el código de autorización de ClickUp.</p>
            </div>
            <p><a href="/api/auth/login">← Volver al Login</a></p>
        </body>
        </html>
        """)
    
    # Por ahora, redirigir al dashboard con un mensaje de éxito
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Autenticación Exitosa</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
            .success {{ color: #27ae60; background: #f0f9f0; padding: 20px; border-radius: 10px; margin: 20px; }}
            .btn {{ background: #667eea; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; text-decoration: none; display: inline-block; margin: 10px; }}
        </style>
    </head>
    <body>
        <h1>✅ ¡Autenticación Exitosa!</h1>
        <div class="success">
            <p>Te has autenticado correctamente con ClickUp.</p>
            <p>Código recibido: {code[:20] if code else 'N/A'}...</p>
            <p><small>Nota: La integración completa de OAuth está en desarrollo.</small></p>
        </div>
        <a href="/dashboard" class="btn">📊 Ir al Dashboard</a>
        <a href="/api/auth/login" class="btn">🔐 Volver al Login</a>
    </body>
    </html>
    """)

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
