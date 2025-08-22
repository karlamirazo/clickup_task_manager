"""
Servidor de prueba simple para verificar funcionalidad
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Test Server", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Test server working!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/test")
async def test_api():
    return {"message": "API endpoint working!"}

if __name__ == "__main__":
    print("🚀 Starting test server...")
    uvicorn.run(app, host="127.0.0.1", port=8080)

