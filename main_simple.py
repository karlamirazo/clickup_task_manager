"""
ClickUp Project Manager - VERSION MINIMA PARA PRUEBA
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="ClickUp Project Manager - MINIMO",
    description="Version minima para probar Railway",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Endpoint raiz simple"""
    return {"message": "ClickUp Project Manager - Version minima funcionando"}

@app.get("/health")
async def health_check():
    """Health check simple"""
    return {"status": "healthy", "version": "minima"}

@app.get("/test")
async def test_endpoint():
    """Endpoint de prueba"""
    return {"test": "success", "message": "Railway esta funcionando"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
