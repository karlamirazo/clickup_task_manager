#!/usr/bin/env python3
"""
Servidor de prueba para verificar que el CSS se cargue correctamente
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

# Crear aplicación
app = FastAPI(title="Test Server CSS Fix")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos en la raíz
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/api/health")
async def health():
    """Endpoint de salud"""
    return {"status": "ok", "message": "Servidor funcionando"}

@app.get("/api/test")
async def test():
    """Endpoint de prueba"""
    return {"message": "Test endpoint funcionando"}

@app.get("/api/tasks")
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

@app.get("/api/workspaces")
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

@app.get("/api/dashboard/health")
async def dashboard_health():
    """Endpoint de salud del dashboard"""
    return {"status": "ok", "message": "Dashboard funcionando"}

if __name__ == "__main__":
    print("🚀 Iniciando servidor de prueba para CSS...")
    print("🌐 Host: 0.0.0.0")
    print("🔌 Puerto: 8000")
    print("📁 Archivos estáticos montados en /")
    
    try:
        uvicorn.run(
            "test_server_css_fix:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        import traceback
        traceback.print_exc()
