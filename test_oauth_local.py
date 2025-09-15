#!/usr/bin/env python3
"""
Probar OAuth localmente antes de desplegar
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from urllib.parse import urlencode
import webbrowser

app = FastAPI(title="OAuth Local Test")

@app.get("/")
async def home(request: Request):
    """Página principal"""
    code = request.query_params.get("code")
    error = request.query_params.get("error")
    
    if code:
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head><title>OAuth Success</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>🎉 ¡OAuth Exitoso!</h1>
            <p>Código: {code[:20]}...</p>
            <p>✅ OAuth funciona correctamente</p>
        </body>
        </html>
        """)
    
    if error:
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head><title>OAuth Error</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>❌ Error OAuth</h1>
            <p>Error: {error}</p>
        </body>
        </html>
        """)
    
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head><title>OAuth Test</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>🔐 OAuth Test</h1>
        <p>Prueba local de OAuth</p>
        <a href="/oauth" style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">
            Probar OAuth
        </a>
    </body>
    </html>
    """)

@app.get("/oauth")
async def start_oauth():
    """Iniciar OAuth"""
    # Usar localhost para prueba local
    redirect_uri = "http://localhost:8000"
    
    auth_url = f"https://app.clickup.com/api/v2/oauth/authorize?" + urlencode({
        'client_id': '0J2LPSHXIM5PRB5VDE5CRJY7FJP86L0H',
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'read:user read:workspace read:task write:task'
    })
    
    return RedirectResponse(url=auth_url)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor local...")
    print("🌐 Ve a: http://localhost:8000")
    print("⚠️  IMPORTANTE: Configura ClickUp con redirect_uri: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)