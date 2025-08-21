#!/usr/bin/env python3
"""
Servidor de prueba muy simple para verificar CSS
"""

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

# Crear aplicación
app = FastAPI(title="Test Server Simple CSS")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Página principal"""
    return FileResponse("static/index_test.html")

@app.get("/styles.css")
async def get_css():
    """CSS directamente"""
    return FileResponse("static/styles.css")

@app.get("/api/health")
async def health():
    """Endpoint de salud"""
    return {"status": "ok", "message": "Servidor funcionando"}

@app.get("/api/tasks")
async def get_tasks():
    """Tareas de prueba"""
    return [
        {"id": 1, "name": "Tarea de Prueba 1", "status": "to do", "priority": 3, "description": "Esta es una tarea de prueba"},
        {"id": 2, "name": "Tarea de Prueba 2", "status": "complete", "priority": 2, "description": "Esta es otra tarea de prueba"}
    ]

@app.get("/api/workspaces")
async def get_workspaces():
    """Workspaces de prueba"""
    return {"workspaces": [{"id": "9014943317", "name": "Workspace de Prueba", "clickup_id": "9014943317"}]}

if __name__ == "__main__":
    print("🚀 Iniciando servidor simple para CSS...")
    print("🌐 Host: 0.0.0.0")
    print("🔌 Puerto: 8000")
    
    try:
        uvicorn.run(
            "test_server_simple_css:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        import traceback
        traceback.print_exc()
