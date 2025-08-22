"""
ClickUp Project Manager - Servidor Simplificado
Versión sin motor de búsqueda RAG para evitar problemas de inicialización
"""

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import os

from api.routes import tasks, workspaces, lists, users, automation, reports, integrations, spaces, webhooks, dashboard, search, auth
from core.config import settings
from core.database import init_db

app = FastAPI(
    title="ClickUp Project Manager - Simplificado",
    description="Intelligent Agent for task management with ClickUp API (Simplified Version)",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static", check_dir=False), name="static")

# Custom static file handler
@app.get("/static/{file_path:path}")
async def get_static_file(file_path: str):
    """Serve static files"""
    file_path_full = os.path.join("static", file_path)
    if not os.path.exists(file_path_full):
        raise HTTPException(status_code=404, detail="File not found")
    
    response = FileResponse(file_path_full)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    return response

# Serve CSS and JS files from root
@app.get("/styles.css")
async def get_css():
    """Serve CSS file"""
    response = FileResponse("styles.css", media_type="text/css")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    return response

@app.get("/script.js")
async def get_js():
    """Serve JavaScript file"""
    response = FileResponse("script.js", media_type="application/javascript")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    return response

# Include API routes
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
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/")
async def root():
    """Serve dashboard as main page"""
    response = FileResponse("static/dashboard.html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    return response

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "ClickUp Project Manager funcionando correctamente",
        "mode": "servidor_simplificado",
        "database": "PostgreSQL (conectado)",
        "apis": "Todas las rutas incluidas"
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint"""
    return {
        "message": "¡Servidor simplificado funcionando!",
        "timestamp": "2025-08-22",
        "mode": "servidor_simplificado",
        "features": ["APIs completas", "Dashboard", "CSS/JS", "Sin motor RAG"]
    }

if __name__ == "__main__":
    print("🚀 Iniciando servidor simplificado...")
    print("📍 Host: 127.0.0.1")
    print("🔌 Puerto: 8000")
    print("🗄️ Inicializando base de datos...")
    
    # Initialize database
    init_db()
    print("✅ Base de datos inicializada")
    
    print("🌐 Iniciando servidor web...")
    uvicorn.run(
        "main_simple:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )
