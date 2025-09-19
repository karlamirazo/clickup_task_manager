#!/usr/bin/env python3
"""
Aplicación principal simplificada de ClickUp Project Manager
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Importar configuración
from core.config import settings

# Importar solo las rutas esenciales
from api.routes import auth

# Crear aplicación FastAPI
app = FastAPI(
    title="ClickUp Project Manager",
    description="Sistema de gestión de proyectos integrado con ClickUp",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ruta principal - CALLBACK OAUTH DEFINITIVO
@app.get("/", response_class=HTMLResponse)
async def root(code: str = None, state: str = None, error: str = None):
    """ENDPOINT RAÍZ - ClickUp solo acepta dominio sin paths"""
    
    # Si vienen parámetros OAuth, manejar como callback
    if code or error:
        print(f"🔐 OAuth ROOT Callback - Code: {code[:20] if code else 'None'}...")
        print(f"🔐 State: {state}")
        print(f"🔐 Error: {error}")
        
        if error:
            print(f"❌ Error OAuth: {error}")
            return RedirectResponse(url=f"/api/auth/login?error=OAuth_error_{error}")
        
        if code:
            print("✅ OAuth ROOT exitoso - Redirigiendo al dashboard")
            # ✅ OAuth exitoso - Redirigir directamente al dashboard
            return RedirectResponse(url="/dashboard?oauth=success")
        
        print("❌ No se recibió código OAuth")
        return RedirectResponse(url="/api/auth/login?error=No_authorization_code")
    
    # Si no hay parámetros OAuth, mostrar página principal
    print("🏠 Acceso normal a página principal")
    return RedirectResponse(url="/api/auth/login")

# Callback de OAuth desde ClickUp - ENDPOINT PRINCIPAL
@app.get("/callback")
async def oauth_callback(code: str = None, state: str = None, error: str = None):
    """Callback de OAuth desde ClickUp - Maneja la redirección directamente"""
    print(f"🔐 OAuth Callback recibido - Code: {code[:20] if code else 'None'}...")
    print(f"🔐 State: {state}")
    print(f"🔐 Error: {error}")
    
    if error:
        print(f"❌ Error OAuth: {error}")
        return RedirectResponse(url=f"/api/auth/login?error=OAuth_error_{error}")
    
    if not code:
        print("❌ No se recibió código de autorización")
        return RedirectResponse(url="/api/auth/login?error=No_authorization_code")
    
    # ✅ OAuth exitoso - Redirigir directamente al dashboard
    print("✅ OAuth exitoso - Redirigiendo al dashboard")
    return RedirectResponse(url="/dashboard?oauth=success")

# Endpoint OAuth más corto - ClickUp puede guardar este
@app.get("/oauth")
async def oauth_short_callback(code: str = None, state: str = None, error: str = None):
    """Callback OAuth CORTO - ClickUp puede guardar /oauth fácilmente"""
    print(f"🔐 OAuth SHORT Callback - Code: {code[:20] if code else 'None'}...")
    print(f"🔐 State: {state}")
    print(f"🔐 Error: {error}")
    
    if error:
        print(f"❌ Error OAuth: {error}")
        return RedirectResponse(url=f"/api/auth/login?error=OAuth_error_{error}")
    
    if not code:
        print("❌ No se recibió código de autorización")
        return RedirectResponse(url="/api/auth/login?error=No_authorization_code")
    
    # ✅ OAuth exitoso - Redirigir directamente al dashboard
    print("✅ OAuth SHORT exitoso - Redirigiendo al dashboard")
    return RedirectResponse(url="/dashboard?oauth=success")

# Ruta del dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Dashboard principal"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ClickUp Project Manager</title>
        </head>
        <body>
            <h1>ClickUp Project Manager</h1>
            <p>Dashboard en construcción...</p>
            <a href="/api/auth/login">Iniciar Sesión</a>
        </body>
        </html>
        """)

# Incluir solo las rutas de autenticación
app.include_router(auth.router, prefix="/api")

# Ruta de salud
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

# Manejo de errores 404
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Manejo de errores 404"""
    if request.url.path.startswith("/api/"):
        return {"error": "Endpoint no encontrado", "path": request.url.path}
    else:
        return RedirectResponse(url="/api/auth/login")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando ClickUp Project Manager...")
    print(f"🌐 Servidor: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 Documentación: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🔐 Autenticación: http://{settings.HOST}:{settings.PORT}/api/auth/login")
    uvicorn.run(
        "main_simple:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

