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
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

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
            print("✅ OAuth ROOT exitoso - Redirigiendo al callback de auth")
            # ✅ OAuth exitoso - Redirigir al endpoint de auth que maneja el OAuth correctamente
            return RedirectResponse(url=f"/api/auth/callback?code={code}&state={state}")
        
        print("❌ No se recibió código OAuth")
        return RedirectResponse(url="/api/auth/login?error=No_authorization_code")
    
    # Si no hay parámetros OAuth, mostrar página principal
    print("🏠 Acceso normal a página principal")
    return RedirectResponse(url="/api/auth/login")

# Callback de OAuth desde ClickUp - ENDPOINT PRINCIPAL
@app.get("/callback")
async def oauth_callback(code: str = None, state: str = None, error: str = None):
    """Callback de OAuth desde ClickUp - Redirige al endpoint de auth correcto"""
    print(f"🔐 OAuth Callback recibido - Code: {code[:20] if code else 'None'}...")
    print(f"🔐 State: {state}")
    print(f"🔐 Error: {error}")
    
    if error:
        print(f"❌ Error OAuth: {error}")
        return RedirectResponse(url=f"/api/auth/login?error=OAuth_error_{error}")
    
    if not code:
        print("❌ No se recibió código de autorización")
        return RedirectResponse(url="/api/auth/login?error=No_authorization_code")
    
    # ✅ OAuth exitoso - Redirigir al callback de auth que maneja correctamente el OAuth
    print("✅ OAuth exitoso - Redirigiendo al callback de auth")
    return RedirectResponse(url=f"/api/auth/callback?code={code}&state={state}")

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
    
    # ✅ OAuth exitoso - Redirigir al callback de auth que maneja correctamente el OAuth
    print("✅ OAuth SHORT exitoso - Redirigiendo al callback de auth")
    return RedirectResponse(url=f"/api/auth/callback?code={code}&state={state}")

# Ruta del dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(token: str = None, oauth: str = None, error: str = None):
    """Dashboard principal - Maneja redirecciones OAuth"""
    print(f"🏠 Dashboard accedido - Token: {token[:20] if token else 'None'}..., OAuth: {oauth}, Error: {error}")
    
    if error:
        print(f"❌ Error en dashboard: {error}")
        return RedirectResponse(url=f"/api/auth/login?error={error}")
    
    try:
        # Leer el archivo del dashboard completo (incluye gráficas y JS actualizado)
        with open("static/dashboard.html", "r", encoding="utf-8") as f:
            dashboard_content = f.read()
        print("✅ Dashboard cargado exitosamente (dashboard.html)")
        return HTMLResponse(content=dashboard_content)
        
    except FileNotFoundError:
        print("❌ Archivo index.html no encontrado")
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
        """, status_code=200)
    except Exception as e:
        print(f"❌ Error cargando dashboard: {e}")
        return RedirectResponse(url="/api/auth/login?error=Error_cargando_dashboard")

# Incluir rutas de API
app.include_router(auth.router, prefix="/api")

# Importar y agregar routers de API
from api.routes import dashboard, tasks
app.include_router(dashboard.router, prefix="/api/v1/dashboard")
app.include_router(tasks.router, prefix="/api/v1")

# Endpoint para lista de usuarios y tareas
@app.get("/users-tasks", response_class=HTMLResponse)
async def users_tasks():
    """Página de tabla de usuarios y tareas"""
    print("📋 Accedido endpoint users-tasks")
    try:
        with open("static/users_tasks_table.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        print("❌ Archivo users_tasks_table.html no encontrado")
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Lista de Tareas - ClickUp Project Manager</title>
            <link rel="stylesheet" href="/static/styles.css">
        </head>
        <body>
            <div class="container">
                <h1>Lista de Usuarios y Tareas</h1>
                <p>Página en construcción...</p>
                <a href="/dashboard">Volver al Dashboard</a>
            </div>
        </body>
        </html>
        """, status_code=200)
    except Exception as e:
        print(f"❌ Error cargando users-tasks: {e}")
        return RedirectResponse(url="/dashboard?error=Error_cargando_lista_tareas")

# Endpoint para Kanban Board
@app.get("/kanban", response_class=HTMLResponse)
async def kanban_board():
    """Página del Kanban Board con drag and drop"""
    print("📋 Accedido endpoint kanban")
    try:
        with open("static/kanban_board.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        print("❌ Archivo kanban_board.html no encontrado")
        return RedirectResponse(url="/dashboard?error=Kanban_no_disponible")
    except Exception as e:
        print(f"❌ Error cargando kanban: {e}")
        return RedirectResponse(url="/dashboard?error=Error_cargando_kanban")

# Endpoint para ejecutar migraciones de base de datos
@app.post("/api/migrate-db")
async def migrate_database():
    """Ejecutar migraciones de base de datos"""
    try:
        from core.database import engine
        from models import Base
        
        print("🔄 Ejecutando migraciones de base de datos...")
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        
        print("✅ Migraciones ejecutadas exitosamente")
        
        return {
            "status": "success",
            "message": "Migraciones de base de datos ejecutadas exitosamente",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error ejecutando migraciones: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Endpoint para inicializar base de datos
@app.post("/api/init-db")
async def init_database():
    """Inicializar base de datos con esquema completo"""
    try:
        from core.database import engine
        from models import Base
        
        print("🔄 Inicializando base de datos...")
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        
        print("✅ Base de datos inicializada exitosamente")
        
        return {
            "status": "success",
            "message": "Base de datos inicializada exitosamente",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

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
        return JSONResponse(content={"error": "Endpoint no encontrado", "path": request.url.path}, status_code=404)
    return RedirectResponse(url="/api/auth/login")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando ClickUp Project Manager...")
    print(f"🌐 Servidor: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 Documentación: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🔐 Autenticación: http://{settings.HOST}:{settings.PORT}/api/auth/login")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

