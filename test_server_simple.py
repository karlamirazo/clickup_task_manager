#!/usr/bin/env python3
"""
Servidor de prueba simple para identificar problemas
"""

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse

# Crear aplicación simple
app = FastAPI(title="Test Server")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Página principal de prueba"""
    return FileResponse("static/index.html")

@app.get("/health")
async def health():
    """Endpoint de salud"""
    return {"status": "ok", "message": "Servidor funcionando"}

@app.get("/test")
async def test():
    """Endpoint de prueba"""
    return {"message": "Test endpoint funcionando"}

if __name__ == "__main__":
    print("🚀 Iniciando servidor de prueba simple...")
    print("🌐 Host: 0.0.0.0")
    print("🔌 Puerto: 8000")
    
    try:
        uvicorn.run(
            "test_server_simple:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        import traceback
        traceback.print_exc()
