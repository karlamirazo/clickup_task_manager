#!/usr/bin/env python3
"""
Servidor HTTP mínimo para servir archivos estáticos
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

class CORSHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    # Cambiar al directorio static
    os.chdir('static')
    
    # Configuración del servidor
    port = 8000
    server_address = ('', port)
    
    print(f"🚀 Iniciando servidor en puerto {port}")
    print(f"📁 Directorio: {os.getcwd()}")
    print(f"🌐 URL: http://localhost:{port}")
    print(f"📱 Dashboard: http://localhost:{port}/dashboard.html")
    print("🔄 Presiona Ctrl+C para detener")
    
    try:
        # Crear y ejecutar el servidor
        httpd = HTTPServer(server_address, CORSHTTPRequestHandler)
        print(f"✅ Servidor iniciado en http://localhost:{port}")
        
        # Abrir navegador automáticamente
        import webbrowser
        webbrowser.open(f"http://localhost:{port}/dashboard.html")
        
        # Mantener el servidor corriendo
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

