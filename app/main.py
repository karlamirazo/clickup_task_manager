#!/usr/bin/env python3
"""
Aplicación ClickUp OAuth que maneja correctamente la redirección de vuelta
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from urllib.parse import urlencode
import os

app = FastAPI(title="ClickUp OAuth Complete")

@app.get("/")
async def handle_root(request: Request):
    """Maneja la raíz y redirecciones de ClickUp"""
    return await process_oauth_callback(request)

@app.get("/{path:path}")
async def handle_any_path(request: Request, path: str):
    """Maneja CUALQUIER ruta que ClickUp pueda usar"""
    return await process_oauth_callback(request)

async def process_oauth_callback(request: Request):
    """Procesa el callback de OAuth"""
    # Obtener parámetros de la URL
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")
    
    # Log para debug
    print(f"🔍 URL completa: {request.url}")
    print(f"🔍 Ruta: {request.url.path}")
    print(f"🔍 Parámetros: code={bool(code)}, state={state}, error={error}")
    
    # Si hay código de autorización, mostrar éxito y redirigir al dashboard
    if code:
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OAuth Exitoso</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 20px; 
                    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .container {{ 
                    background: white; 
                    padding: 30px; 
                    border-radius: 20px; 
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    max-width: 90%;
                    width: 400px;
                }}
                .success {{ color: #28a745; font-size: 3rem; margin-bottom: 20px; }}
                .btn {{ 
                    background: #667eea; 
                    color: white; 
                    padding: 15px 30px; 
                    text-decoration: none; 
                    border-radius: 10px; 
                    display: inline-block;
                    margin: 10px;
                    font-size: 1rem;
                    font-weight: bold;
                }}
                .btn:hover {{ background: #5a6fd8; }}
                .info {{ 
                    background: #f8f9fa; 
                    padding: 15px; 
                    border-radius: 10px; 
                    margin: 20px 0;
                    font-size: 0.9rem;
                }}
                @media (max-width: 480px) {{
                    .container {{ padding: 20px; }}
                    .success {{ font-size: 2rem; }}
                    .btn {{ padding: 12px 25px; font-size: 0.9rem; }}
                }}
            </style>
            <script>
                // Auto-redirigir al dashboard después de 3 segundos
                setTimeout(function() {{
                    window.location.href = '/dashboard';
                }}, 3000);
            </script>
        </head>
        <body>
            <div class="container">
                <div class="success">🎉</div>
                <h1>¡Autenticación Exitosa!</h1>
                <p>Te has conectado correctamente con ClickUp</p>
                
                <div class="info">
                    <strong>✅ OAuth completado</strong><br>
                    Redirigiendo al dashboard...
                </div>
                
                <a href="/dashboard" class="btn">Ir al Dashboard</a>
                <a href="/" class="btn" style="background: #6c757d;">Volver al inicio</a>
                
                <p><small>Si no se redirige automáticamente, haz clic en "Ir al Dashboard"</small></p>
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
            <title>Error OAuth</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 20px; 
                    background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .container {{ 
                    background: white; 
                    padding: 30px; 
                    border-radius: 20px; 
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    max-width: 90%;
                    width: 400px;
                }}
                .error {{ color: #dc3545; font-size: 3rem; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error">❌</div>
                <h1>Error de Autenticación</h1>
                <p><strong>Error:</strong> {error}</p>
                <a href="/" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    Intentar nuevamente
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
        <title>ClickUp Manager</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 20px; 
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
                max-width: 90%;
                width: 500px;
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
            .features {
                text-align: left;
                margin: 20px 0;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
            }
            .feature {
                margin: 10px 0;
                color: #666;
            }
            .feature-icon {
                color: #667eea;
                font-weight: bold;
                margin-right: 10px;
            }
            @media (max-width: 480px) {
                .container { padding: 20px; }
                .logo { font-size: 2rem; }
                .btn { padding: 12px 25px; font-size: 1rem; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">📋</div>
            <h1>ClickUp Manager</h1>
            <p>Gestiona tus proyectos de manera eficiente</p>
            
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
                <div class="feature">
                    <span class="feature-icon">✓</span>
                    Optimizado para móviles
                </div>
            </div>
            
            <a href="/oauth" class="btn">🔐 Iniciar con ClickUp</a>
            <p><small>Funciona mejor en dispositivos móviles</small></p>
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

@app.get("/dashboard")
async def dashboard():
    """Dashboard principal después del OAuth"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - ClickUp Manager</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0;
                padding: 20px;
                background: #f8f9fa;
            }
            .header {
                background: #667eea;
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
            }
            .card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .success {
                background: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎉 ¡Bienvenido a ClickUp Manager!</h1>
            <p>Tu autenticación OAuth fue exitosa</p>
        </div>
        
        <div class="success">
            <strong>✅ Conectado exitosamente</strong><br>
            Tu cuenta de ClickUp está ahora integrada con el sistema.
        </div>
        
        <div class="card">
            <h2>📊 Dashboard</h2>
            <p>Aquí puedes ver tus proyectos y tareas de ClickUp.</p>
            <p><strong>Estado:</strong> Conectado y sincronizado</p>
        </div>
        
        <div class="card">
            <h2>🔧 Próximos pasos</h2>
            <ul>
                <li>Sincronizar tareas automáticamente</li>
                <li>Configurar notificaciones</li>
                <li>Personalizar dashboard</li>
            </ul>
        </div>
        
        <p><a href="/" style="color: #667eea;">← Volver al inicio</a></p>
    </body>
    </html>
    """)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando ClickUp Manager con OAuth completo...")
    print("🌐 URL: https://clickuptaskmanager-production.up.railway.app")
    print("📱 Optimizado para dispositivos móviles")
    uvicorn.run(app, host="0.0.0.0", port=8000)