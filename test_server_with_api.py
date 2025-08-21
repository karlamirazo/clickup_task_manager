#!/usr/bin/env python3
"""
Servidor de prueba con API básica para identificar problemas
"""

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Crear aplicación
app = FastAPI(title="Test Server with API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Página principal"""
    return FileResponse("static/index.html")

@app.get("/health")
async def health():
    """Endpoint de salud"""
    return {"status": "ok", "message": "Servidor funcionando"}

# Endpoint simple de tareas (sin base de datos)
@app.get("/api/v1/tasks/")
async def get_tasks():
    """Endpoint simple de tareas"""
    return [
        {
            "id": 1,
            "name": "Tarea de Prueba 1",
            "status": "to do",
            "priority": 3,
            "description": "Esta es una tarea de prueba"
        },
        {
            "id": 2,
            "name": "Tarea de Prueba 2", 
            "status": "complete",
            "priority": 2,
            "description": "Esta es otra tarea de prueba"
        }
    ]

@app.get("/api/v1/workspaces/")
async def get_workspaces():
    """Endpoint simple de workspaces"""
    return {
        "workspaces": [
            {
                "id": "9014943317",
                "name": "Workspace de Prueba",
                "clickup_id": "9014943317"
            }
        ]
    }

@app.get("/api/v1/dashboard/health")
async def dashboard_health():
    """Endpoint de salud del dashboard"""
    return {"status": "ok", "message": "Dashboard funcionando"}

if __name__ == "__main__":
    print("🚀 Iniciando servidor de prueba con API...")
    print("🌐 Host: 0.0.0.0")
    print("🔌 Puerto: 8000")
    
    try:
        uvicorn.run(
            "test_server_with_api:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        import traceback
        traceback.print_exc()
