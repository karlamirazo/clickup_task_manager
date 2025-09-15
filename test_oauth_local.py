#!/usr/bin/env python3
"""
Script para probar OAuth localmente
"""

import os
import sys
import asyncio
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, HTMLResponse
from urllib.parse import urlencode
import secrets

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar variables de entorno para prueba
os.environ['CLICKUP_OAUTH_CLIENT_ID'] = 'test_client_id'
os.environ['CLICKUP_OAUTH_CLIENT_SECRET'] = 'test_client_secret'
os.environ['CLICKUP_OAUTH_REDIRECT_URI'] = 'http://localhost:8000/api/auth/callback'

# Crear aplicación simple
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "OAuth Test Server", "status": "running"}

@app.get("/debug")
async def debug_endpoint():
    """Endpoint de debug para identificar problemas"""
    try:
        # Verificar importaciones básicas
        import os
        import secrets
        from urllib.parse import urlencode
        from fastapi.responses import HTMLResponse, RedirectResponse
        
        # Verificar variables de entorno
        client_id = os.getenv('CLICKUP_OAUTH_CLIENT_ID', '')
        client_secret = os.getenv('CLICKUP_OAUTH_CLIENT_SECRET', '')
        redirect_uri = os.getenv('CLICKUP_OAUTH_REDIRECT_URI', '')
        
        return {
            "status": "ok",
            "imports": "successful",
            "client_id_present": bool(client_id),
            "client_secret_present": bool(client_secret),
            "redirect_uri_present": bool(redirect_uri),
            "redirect_uri_value": redirect_uri,
            "python_version": "3.11.9"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.get("/api/auth/clickup")
async def clickup_oauth_login():
    """Iniciar proceso de OAuth con ClickUp"""
    try:
        # Obtener configuración de OAuth
        client_id = os.getenv('CLICKUP_OAUTH_CLIENT_ID', '')
        redirect_uri = os.getenv('CLICKUP_OAUTH_REDIRECT_URI', 'http://localhost:8000/api/auth/callback')
        
        print(f"DEBUG: client_id = {client_id}")
        print(f"DEBUG: redirect_uri = {redirect_uri}")
        
        if not client_id:
            return {"error": "OAuth not configured", "client_id": client_id}
        
        # Generar state para seguridad
        state = secrets.token_urlsafe(32)
        print(f"DEBUG: state = {state}")
        
        # Construir URL de autorización
        auth_url = f"https://app.clickup.com/api/v2/oauth/authorize?" + urlencode({
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'state': state,
            'scope': 'read:user read:workspace read:task write:task'
        })
        
        print(f"DEBUG: auth_url = {auth_url}")
        
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        print(f"ERROR: {e}")
        return {"error": str(e), "error_type": type(e).__name__}

@app.get("/api/auth/callback")
async def clickup_oauth_callback(code: str = None, state: str = None, error: str = None):
    """Callback de OAuth de ClickUp"""
    print(f"DEBUG: callback called with code={code}, state={state}, error={error}")
    
    if error:
        return {"error": f"Authorization error: {error}"}
    
    if not code:
        return {"error": "No authorization code received"}
    
    return {
        "message": "OAuth callback successful",
        "code": code[:20] + "..." if code else None,
        "state": state
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting OAuth test server on http://localhost:8000")
    print("📋 Available endpoints:")
    print("   - http://localhost:8000/")
    print("   - http://localhost:8000/debug")
    print("   - http://localhost:8000/api/auth/clickup")
    print("   - http://localhost:8000/api/auth/callback")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


