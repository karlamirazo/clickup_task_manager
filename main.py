"""
ClickUp Project Manager - Agente Inteligente
Módulo principal de la aplicación
"""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

from api.routes import tasks, workspaces, lists, users, automation, reports, integrations, spaces, webhooks, dashboard, search, auth
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

# Agregar headers de seguridad HTTPS
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Solo agregar headers de seguridad en producción (Railway)
    if "railway.app" in str(request.url):
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "upgrade-insecure-requests"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        print("🔒 Headers de seguridad HTTPS aplicados")
    
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
# Ajuste: exponer rutas de tareas bajo /api/v1/tasks para alinear con el frontend
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

# Autenticación opcional (comentada para uso básico)
# try:
#     from api.routes import auth
#     app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
# except ImportError:
#     print("⚠️ Sistema de autenticación no disponible")

from fastapi.responses import FileResponse
import datetime

@app.get("/")
async def root():
    """Servir la interfaz web"""
    return FileResponse("static/index.html")

@app.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard():
    """Dashboard de notificaciones"""
    with open("static/dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/tasks-dashboard", response_class=HTMLResponse)
async def read_tasks_dashboard():
    """Dashboard de tareas"""
    with open("static/tasks_dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/api")
async def api_root():
    """Endpoint raíz de la API con información de debug"""
    import os
    from core.database import engine
    
    try:
        # Información básica de configuración
        config_status = {
            "CLICKUP_API_TOKEN": "✅ Configurado" if os.getenv("CLICKUP_API_TOKEN") else "❌ No configurado",
            "DATABASE_URL": "✅ Configurado" if os.getenv("DATABASE_URL") else "❌ No configurado",
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "development")
        }
        
        # Información de la base de datos
        db_status = "❌ No disponible"
        db_type = "Desconocido"
        
        try:
            if engine:
                db_type = "PostgreSQL" if "postgresql" in str(engine.url) else "SQLite"
                db_status = "✅ Conectado"
        except Exception as e:
            db_status = f"❌ Error: {str(e)}"
        
        return {
            "message": "ClickUp Project Manager - Agente Inteligente",
            "version": "1.0.0",
            "status": "running",
            "debug_info": {
                "configuration": config_status,
                "database": {
                    "type": db_type,
                    "status": db_status
                }
            }
        }
    except Exception as e:
        return {
            "message": "ClickUp Project Manager - Agente Inteligente",
            "version": "1.0.0",
            "status": "error",
            "error": str(e)
        }

@app.get("/debug")
async def debug_info():
    """Endpoint de debug independiente para verificar el estado del servidor"""
    import os
    from core.database import engine
    
    try:
        # Verificar configuración
        config_info = {
            "CLICKUP_API_TOKEN": "✅ Configurado" if os.getenv("CLICKUP_API_TOKEN") else "❌ No configurado",
            "DATABASE_URL": "✅ Configurado" if os.getenv("DATABASE_URL") else "❌ No configurado",
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "development")
        }
        
        # Verificar base de datos
        db_info = {}
        try:
            if engine:
                db_info["database_type"] = "PostgreSQL" if "postgresql" in str(engine.url) else "SQLite"
                db_info["database_status"] = "✅ Conectado"
            else:
                db_info["database_status"] = "❌ No disponible"
        except Exception as e:
            db_info["database_status"] = f"❌ Error: {str(e)}"
        
        # Verificar ClickUp client
        clickup_info = {}
        try:
            from core.clickup_client import ClickUpClient
            client = ClickUpClient()
            clickup_info["client_status"] = "✅ Disponible"
            clickup_info["token_configured"] = "✅ Sí" if client.api_token else "❌ No"
        except Exception as e:
            clickup_info["client_status"] = f"❌ Error: {str(e)}"
        
        # ===== LOGGING AUTOMÁTICO CON LANGGRAPH =====
        try:
            import sys
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from langgraph_tools.simple_error_logging import log_error_with_graph
            
            log_error_with_graph({
                "error_description": "Endpoint de debug accedido - Verificación del sistema",
                "solution_description": "Verificación manual del estado del servidor",
                "context_info": f"Endpoint: GET /debug, Config: {config_info}, DB: {db_info}, ClickUp: {clickup_info}",
                "deployment_id": "railway-production",
                "environment": "production",
                "severity": "info",
                "status": "resolved"
            })
            logging_status = "✅ Sistema de logging activo"
        except Exception as logging_error:
            logging_status = f"❌ Error en logging: {str(logging_error)}"
        
        return {
            "status": "success",
            "timestamp": str(datetime.datetime.now()),
            "configuration": config_info,
            "database": db_info,
            "clickup_client": clickup_info,
            "logging_system": logging_status
        }
        
    except Exception as e:
        # ===== LOGGING AUTOMÁTICO CON LANGGRAPH PARA ERRORES =====
        try:
            import sys
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from langgraph_tools.simple_error_logging import log_error_with_graph
            
            log_error_with_graph({
                "error_description": f"Error en endpoint de debug: {str(e)}",
                "solution_description": "Verificar configuración del servidor y dependencias",
                "context_info": f"Endpoint: GET /debug, Error: {str(e)}",
                "deployment_id": "railway-production",
                "environment": "production",
                "severity": "high",
                "status": "pending"
            })
        except Exception as logging_error:
            print(f"⚠️ Error en logging automático: {logging_error}")
        
        return {
            "status": "error",
            "error": str(e),
            "timestamp": str(datetime.datetime.now())
        }

@app.get("/health")
async def health_check():
    """Verificar el estado de la aplicación"""
    return {"status": "healthy"}

@app.get("/test-logging")
async def test_logging_system():
    """Endpoint para probar el sistema de logging de LangGraph"""
    try:
        # Verificar si LangGraph está disponible
        try:
            import langgraph
            langgraph_available = True
            langgraph_version = langgraph.__version__
        except ImportError:
            langgraph_available = False
            langgraph_version = "No disponible"
        
        # Verificar si el módulo de logging está disponible
        try:
            import sys
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from langgraph_tools.simple_error_logging import log_error_with_graph
            logging_module_available = True
        except Exception as e:
            logging_module_available = False
            logging_error = str(e)
        
        # Si todo está disponible, probar logging
        if langgraph_available and logging_module_available:
            test_result = log_error_with_graph({
                "error_description": "Prueba del sistema de logging desde endpoint /test-logging",
                "solution_description": "Verificar que el logging funciona correctamente en Railway con PostgreSQL",
                "context_info": "Endpoint: GET /test-logging, Timestamp: " + str(datetime.datetime.now()),
                "deployment_id": "railway-production",
                "environment": "production",
                "severity": "info",
                "status": "resolved"
            })
            
            return {
                "status": "success",
                "message": "Sistema de logging probado exitosamente",
                "langgraph_available": langgraph_available,
                "langgraph_version": langgraph_version,
                "logging_module_available": logging_module_available,
                "logging_result": test_result,
                "timestamp": str(datetime.datetime.now())
            }
        else:
            return {
                "status": "error",
                "message": "Dependencias no disponibles",
                "langgraph_available": langgraph_available,
                "langgraph_version": langgraph_version,
                "logging_module_available": logging_module_available,
                "logging_error": logging_error if not logging_module_available else None,
                "timestamp": str(datetime.datetime.now())
            }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error probando sistema de logging: {str(e)}",
            "timestamp": str(datetime.datetime.now())
        }

@app.get("/test-simple")
async def test_simple_endpoint():
    """Endpoint simple para verificar que el deployment funciona"""
    return {
        "status": "success",
        "message": "Endpoint simple funcionando correctamente",
        "timestamp": str(datetime.datetime.now()),
        "deployment_version": "2025-08-18-13:10"
    }



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
