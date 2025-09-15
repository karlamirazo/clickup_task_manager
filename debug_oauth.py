
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
async def debug_root(request: Request):
    """Endpoint de debug para ver qué recibe"""
    params = dict(request.query_params)
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head><title>Debug OAuth</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h1>🔍 Debug OAuth Callback</h1>
        <h2>Parámetros recibidos:</h2>
        <ul>
            {''.join([f'<li><strong>{k}:</strong> {v}</li>' for k, v in params.items()])}
        </ul>
        <h2>URL completa:</h2>
        <p>{request.url}</p>
        <h2>Headers:</h2>
        <ul>
            {''.join([f'<li><strong>{k}:</strong> {v}</li>' for k, v in request.headers.items()])}
        </ul>
    </body>
    </html>
    """)
