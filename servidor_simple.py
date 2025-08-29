#!/usr/bin/env python3
"""
Servidor HTTP simple para servir el dashboard con campo de teléfono
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Configuración del servidor
PORT = 8000
DIRECTORY = "static"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Agregar headers CORS para permitir acceso desde cualquier origen
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        # Manejar preflight CORS
        self.send_response(200)
        self.end_headers()

def main():
    print("🚀 Iniciando servidor HTTP simple...")
    print(f"📁 Directorio: {os.path.abspath(DIRECTORY)}")
    print(f"🌐 Puerto: {PORT}")
    print(f"🔗 URL: http://localhost:{PORT}")
    
    # Verificar que el directorio existe
    if not os.path.exists(DIRECTORY):
        print(f"❌ Error: El directorio '{DIRECTORY}' no existe")
        return
    
    # Verificar que el archivo dashboard.html existe
    dashboard_path = os.path.join(DIRECTORY, "dashboard.html")
    if not os.path.exists(dashboard_path):
        print(f"❌ Error: El archivo '{dashboard_path}' no existe")
        return
    
    print(f"✅ Archivo dashboard.html encontrado: {dashboard_path}")
    
    try:
        # Cambiar al directorio de archivos estáticos
        os.chdir(DIRECTORY)
        
        # Crear y configurar el servidor
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"✅ Servidor iniciado en http://localhost:{PORT}")
            print("📱 El campo de teléfono está implementado en el dashboard")
            print("🔄 Presiona Ctrl+C para detener el servidor")
            
            # Abrir el navegador automáticamente
            try:
                webbrowser.open(f"http://localhost:{PORT}/dashboard.html")
                print("🌐 Navegador abierto automáticamente")
            except:
                print("💡 Abre manualmente: http://localhost:8000/dashboard.html")
            
            # Mantener el servidor corriendo
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

