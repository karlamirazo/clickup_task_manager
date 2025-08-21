"""
ClickUp Project Manager - Intelligent Agent
Main application module
"""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import os

from api.routes import tasks, workspaces, lists, users, automation, reports, integrations, spaces, webhooks, dashboard, search, auth
from core.config import settings
from core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events"""
    # Startup
    init_db()
    
    # Initialize RAG search engine
    try:
        from core.search_engine import search_engine
        await search_engine.initialize()
        print("SUCCESS: RAG search engine initialized")
    except Exception as e:
        print(f"ERROR: Error initializing search engine: {e}")
    
    yield
    # Shutdown (if needed)

app = FastAPI(
    title="ClickUp Project Manager",
    description="Intelligent Agent for task management with ClickUp API",
    version="1.0.0",
    lifespan=lifespan
)

# Add HTTPS security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Only add UTF-8 encoding headers for HTML responses
    if "text/html" in response.headers.get("Content-Type", ""):
        response.headers["Content-Type"] = "text/html; charset=utf-8"
    
    # Only add security headers in production (Railway)
    if "railway.app" in str(request.url):
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "upgrade-insecure-requests"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        print("✅ HTTPS security headers applied")
    
    return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files with NO CACHE
app.mount("/static", StaticFiles(directory="static", check_dir=False), name="static")

# Custom static file handler with NO CACHE
@app.get("/static/{file_path:path}")
async def get_static_file(file_path: str):
    """Serve static files with NO CACHE headers"""
    file_path_full = os.path.join("static", file_path)
    if not os.path.exists(file_path_full):
        raise HTTPException(status_code=404, detail="File not found")
    
    response = FileResponse(file_path_full)
    
    # AGGRESSIVE NO CACHE HEADERS
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Last-Modified"] = "Thu, 01 Jan 1970 00:00:00 GMT"
    response.headers["ETag"] = f'"{hash(file_path)}"'
    
    return response

# Serve CSS and JS files from root
@app.get("/styles.css")
async def get_css():
    """Serve CSS file with AGGRESSIVE NO CACHE"""
    response = FileResponse("styles.css", media_type="text/css")
    
    # AGGRESSIVE NO CACHE HEADERS
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Last-Modified"] = "Thu, 01 Jan 1970 00:00:00 GMT"
    response.headers["ETag"] = f'"{hash("styles.css")}"'
    
    return response

@app.get("/script.js")
async def get_js():
    """Serve JavaScript file with AGGRESSIVE NO CACHE"""
    response = FileResponse("script.js", media_type="application/javascript")
    
    # AGGRESSIVE NO CACHE HEADERS
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Last-Modified"] = "Thu, 01 Jan 1970 00:00:00 GMT"
    response.headers["ETag"] = f'"{hash("script.js")}"'
    
    return response

# Include routes
# Adjustment: expose task routes under /api/v1/tasks to align with frontend
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

# Optional authentication (commented for basic use)
# try:
#     from api.routes import auth
#     app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
# except ImportError:
#     print("‚ö†Ô∏è Authentication system not available")

import datetime

@app.get("/")
async def root():
    """Serve dashboard as main page with AGGRESSIVE NO CACHE"""
    response = FileResponse("static/dashboard.html")
    
    # AGGRESSIVE NO CACHE HEADERS - EVEN MORE AGGRESSIVE
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"
    response.headers["Last-Modified"] = "Thu, 01 Jan 1970 00:00:00 GMT"
    response.headers["ETag"] = f'"{hash("dashboard.html")}"'
    response.headers["Vary"] = "*"
    response.headers["Surrogate-Control"] = "no-store"
    
    return response

@app.get("/index", response_class=HTMLResponse)
async def read_index():
    """Serve original index page"""
    response = FileResponse("static/index.html")
    
    # AGGRESSIVE NO CACHE HEADERS
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Last-Modified"] = "Thu, 01 Jan 1970 00:00:00 GMT"
    response.headers["ETag"] = f'"{hash("index.html")}"'
    
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard():
    """Dashboard of notifications"""
    with open("static/dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/users-tasks", response_class=HTMLResponse)
async def read_users_tasks_table():
    """Tabla profesional de usuarios y tareas"""
    response = FileResponse("static/users_tasks_table.html")
    
    # AGGRESSIVE NO CACHE HEADERS
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Last-Modified"] = "Thu, 01 Jan 1970 00:00:00 GMT"
    response.headers["ETag"] = f'"{hash("users_tasks_table.html")}"'
    
    return response

@app.get("/test-users-tasks", response_class=HTMLResponse)
async def read_test_users_tasks():
    """Página de prueba para la tabla de usuarios y tareas"""
    response = FileResponse("static/test_users_tasks.html")
    
    # AGGRESSIVE NO CACHE HEADERS
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Last-Modified"] = "Thu, 01 Jan 1970 00:00:00 GMT"
    response.headers["ETag"] = f'"{hash("test_users_tasks.html")}"'
    
    return response

@app.get("/debug-table", response_class=HTMLResponse)
async def read_debug_table():
    """Página de debugging para la tabla de usuarios y tareas"""
    response = FileResponse("static/debug_table.html")
    
    # AGGRESSIVE NO CACHE HEADERS
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Last-Modified"] = "Thu, 01 Jan 1970 00:00:00 GMT"
    response.headers["ETag"] = f'"{hash("debug_table.html")}"'
    
    return response

@app.get("/tasks-dashboard", response_class=HTMLResponse)
async def read_tasks_dashboard():
    """Dashboard of tasks"""
    with open("static/tasks_dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/api")
async def api_root():
    """Root endpoint of the API with debug information"""
    import os
    from core.database import engine
    
    try:
        # Basic configuration information
        config_status = {
            "CLICKUP_API_TOKEN": "‚úÖ Configured" if os.getenv("CLICKUP_API_TOKEN") else "‚ùå Not configured",
            "DATABASE_URL": "‚úÖ Configured" if os.getenv("DATABASE_URL") else "‚ùå Not configured",
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "development")
        }
        
        # Database information
        db_status = "‚ùå Not available"
        db_type = "Unknown"
        
        try:
            if engine:
                db_type = "PostgreSQL" if "postgresql" in str(engine.url) else "SQLite"
                db_status = "‚úÖ Connected"
        except Exception as e:
            db_status = f"‚ùå Error: {str(e)}"
        
        return {
            "message": "ClickUp Project Manager - Intelligent Agent",
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
            "message": "ClickUp Project Manager - Intelligent Agent",
            "version": "1.0.0",
            "status": "error",
            "error": str(e)
        }

@app.get("/debug")
async def debug_info():
    """Independent debug endpoint to check server status"""
    import os
    from core.database import engine
    
    try:
        # Check configuration
        config_info = {
            "CLICKUP_API_TOKEN": "‚úÖ Configured" if os.getenv("CLICKUP_API_TOKEN") else "‚ùå Not configured",
            "DATABASE_URL": "‚úÖ Configured" if os.getenv("DATABASE_URL") else "‚ùå Not configured",
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "development")
        }
        
        # Check database
        db_info = {}
        try:
            if engine:
                db_info["database_type"] = "PostgreSQL" if "postgresql" in str(engine.url) else "SQLite"
                db_info["database_status"] = "‚úÖ Connected"
            else:
                db_info["database_status"] = "‚ùå Not available"
        except Exception as e:
            db_info["database_status"] = f"‚ùå Error: {str(e)}"
        
        # Check ClickUp client
        clickup_info = {}
        try:
            from core.clickup_client import ClickUpClient
            client = ClickUpClient()
            clickup_info["client_status"] = "‚úÖ Available"
            clickup_info["token_configured"] = "‚úÖ Yes" if client.api_token else "‚ùå No"
        except Exception as e:
            clickup_info["client_status"] = f"‚ùå Error: {str(e)}"
        
        # ===== LOGGING AUTOMATICO CON LANGGRAPH =====
        try:
            import sys
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from langgraph_tools.simple_error_logging import log_error_with_graph
            
            log_error_with_graph({
                "error_description": "Debug endpoint accessed - System status check",
                "solution_description": "Manual check of server status",
                "context_info": f"Endpoint: GET /debug, Config: {config_info}, DB: {db_info}, ClickUp: {clickup_info}",
                "deployment_id": "railway-production",
                "environment": "production",
                "severity": "info",
                "status": "resolved"
            })
            logging_status = "‚úÖ Logging system active"
        except Exception as logging_error:
            logging_status = f"‚ùå Logging error: {str(logging_error)}"
        
        return {
            "status": "success",
            "timestamp": str(datetime.datetime.now()),
            "configuration": config_info,
            "database": db_info,
            "clickup_client": clickup_info,
            "logging_system": logging_status
        }
        
    except Exception as e:
        # ===== LOGGING AUTOMATICO CON LANGGRAPH PARA ERRORES =====
        try:
            import sys
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from langgraph_tools.simple_error_logging import log_error_with_graph
            
            log_error_with_graph({
                "error_description": f"Error in debug endpoint: {str(e)}",
                "solution_description": "Check server configuration and dependencies",
                "context_info": f"Endpoint: GET /debug, Error: {str(e)}",
                "deployment_id": "railway-production",
                "environment": "production",
                "severity": "high",
                "status": "pending"
            })
        except Exception as logging_error:
            print(f"‚ö†Ô∏è Automatic logging error: {logging_error}")
        
        return {
            "status": "error",
            "error": str(e),
            "timestamp": str(datetime.datetime.now())
        }

@app.get("/health")
async def health_check():
    """Check application status with NO CACHE"""
    from fastapi.responses import JSONResponse
    
    response = JSONResponse(content={"status": "healthy"})
    
    # AGGRESSIVE NO CACHE HEADERS
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response

@app.post("/api/v1/tasks/clear-all")
async def clear_all_tasks():
    """Clear all tasks from local database"""
    try:
        from core.database import SessionLocal
        from models.task import Task
        
        db = SessionLocal()
        try:
            # Delete all tasks
            deleted_count = db.query(Task).delete()
            db.commit()
            
            return {
                "status": "success",
                "message": f"Cleared {deleted_count} tasks from local database",
                "deleted_count": deleted_count
            }
        finally:
            db.close()
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error clearing tasks: {str(e)}"
        }

@app.get("/test-logging")
async def test_logging_system():
    """Endpoint to test the LangGraph logging system"""
    try:
        # Check if LangGraph is available
        try:
            import langgraph
            langgraph_available = True
            langgraph_version = langgraph.__version__
        except ImportError:
            langgraph_available = False
            langgraph_version = "Not available"
        
        # Check if logging module is available
        try:
            import sys
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from langgraph_tools.simple_error_logging import log_error_with_graph
            logging_module_available = True
        except Exception as e:
            logging_module_available = False
            logging_error = str(e)
        
        # If everything is available, test logging
        if langgraph_available and logging_module_available:
            test_result = log_error_with_graph({
                "error_description": "Test of logging system from /test-logging endpoint",
                "solution_description": "Verify that logging works correctly in Railway with PostgreSQL",
                "context_info": "Endpoint: GET /test-logging, Timestamp: " + str(datetime.datetime.now()),
                "deployment_id": "railway-production",
                "environment": "production",
                "severity": "info",
                "status": "resolved"
            })
            
            return {
                "status": "success",
                "message": "Logging system tested successfully",
                "langgraph_available": langgraph_available,
                "langgraph_version": langgraph_version,
                "logging_module_available": logging_module_available,
                "logging_result": test_result,
                "timestamp": str(datetime.datetime.now())
            }
        else:
            return {
                "status": "error",
                "message": "Dependencies not available",
                "langgraph_available": langgraph_available,
                "langgraph_version": langgraph_version,
                "logging_module_available": logging_module_available,
                "logging_error": logging_error if not logging_module_available else None,
                "timestamp": str(datetime.datetime.now())
            }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error testing logging system: {str(e)}",
            "timestamp": str(datetime.datetime.now())
        }

@app.get("/test-simple")
async def test_simple_endpoint():
    """Simple endpoint to verify deployment"""
    return {
        "status": "success",
        "message": "Simple endpoint working correctly",
        "timestamp": str(datetime.datetime.now()),
        "deployment_version": "2025-08-18-13:10"
    }



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False  # Forzar sin auto-reload
    )
