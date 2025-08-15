"""
ClickUp Project Manager - Agente Inteligente
Módulo principal de la aplicación
"""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from api.routes import tasks, workspaces, lists, users, automation, reports, integrations, spaces, webhooks, dashboard, search
from core.config import settings
from core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejar eventos de inicio y cierre de la aplicación"""
    # Startup
    await init_db()
    
    # Inicializar motor de búsqueda RAG
    try:
        from core.search_engine import search_engine
        await search_engine.initialize()
        print("✅ Motor de búsqueda RAG inicializado")
    except Exception as e:
        print(f"⚠️ Error inicializando motor de búsqueda: {e}")
    
    yield
    # Shutdown (si es necesario)

app = FastAPI(
    title="ClickUp Project Manager",
    description="Agente Inteligente para gestión de tareas con ClickUp API",
    version="1.0.0",
    lifespan=lifespan
)

# Agregar middleware de seguridad HTTPS en producción
import os
if os.getenv("RAILWAY_ENVIRONMENT_NAME"):  # Detectar Railway
    print("🚂 Detectado Railway - Configurando middleware de seguridad HTTPS")
    
    # Middleware para hosts confiables
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["clickuptaskmanager-production.up.railway.app", "*.up.railway.app"]
    )
    
    # Middleware para forzar HTTPS (solo en Railway)
    # app.add_middleware(HTTPSRedirectMiddleware)  # Comentado por ahora para evitar loops
    
    # Middleware personalizado para headers de seguridad
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "upgrade-insecure-requests"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

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

# Incluir rutas
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(workspaces.router, prefix="/api/v1/workspaces", tags=["workspaces"])
app.include_router(lists.router, prefix="/api/v1/lists", tags=["lists"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(automation.router, prefix="/api/v1/automation", tags=["automation"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["integrations"])
app.include_router(spaces.router, prefix="/api/v1/spaces", tags=["spaces"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])

# Autenticación opcional (comentada para uso básico)
# try:
#     from api.routes import auth
#     app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
# except ImportError:
#     print("⚠️ Sistema de autenticación no disponible")

from fastapi.responses import FileResponse

@app.get("/")
async def root():
    """Servir la interfaz web"""
    return FileResponse("static/index.html")

@app.get("/api")
async def api_root():
    """Endpoint raíz de la API"""
    return {
        "message": "ClickUp Project Manager - Agente Inteligente",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "ui": "/"
    }

@app.get("/health")
async def health_check():
    """Verificar el estado de la aplicación"""
    return {"status": "healthy"}



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
