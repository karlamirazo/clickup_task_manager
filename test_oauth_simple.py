
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI(title="ClickUp OAuth Test")

@app.get("/")
async def root(request: Request):
    """Maneja todas las rutas"""
    # Verificar si viene de ClickUp OAuth
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")
    
    if code:
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head><title>OAuth Success</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>🎉 OAuth Success!</h1>
            <p>Code: {code[:20]}...</p>
            <p>State: {state}</p>
            <p>✅ ClickUp está redirigiendo correctamente</p>
        </body>
        </html>
        """)
    
    if error:
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head><title>OAuth Error</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>❌ OAuth Error</h1>
            <p>Error: {error}</p>
        </body>
        </html>
        """)
    
    # Página normal
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head><title>ClickUp OAuth Test</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>🔐 ClickUp OAuth Test</h1>
        <p>Si ves esta página, la aplicación está funcionando</p>
        <a href="/test-oauth" style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px;">
            Probar OAuth
        </a>
    </body>
    </html>
    """)

@app.get("/test-oauth")
async def test_oauth():
    """Probar OAuth"""
    client_id = "0J2LPSHXIM5PRB5VDE5CRJY7FJP86L0H"
    redirect_uri = "https://clickuptaskmanager-production.up.railway.app"
    
    auth_url = f"https://app.clickup.com/api/v2/oauth/authorize?" + urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'read:user read:workspace read:task write:task'
    })
    
    return RedirectResponse(url=auth_url)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
