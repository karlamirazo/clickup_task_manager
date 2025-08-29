#!/usr/bin/env python3
"""
Servidor HTTP simple para abrir el dashboard con campo de teléfono
"""

import os
import webbrowser
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

class DashboardHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Agregar headers CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    # Configuración
    port = 8000
    host = 'localhost'
    
    print("🚀 Iniciando servidor para el dashboard...")
    print(f"📁 Directorio actual: {os.getcwd()}")
    print(f"🌐 Puerto: {port}")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('dashboard.html'):
        print("❌ Error: dashboard.html no encontrado en el directorio actual")
        print("💡 Asegúrate de estar en el directorio 'static'")
        return
    
    print("✅ dashboard.html encontrado")
    
    try:
        # Crear servidor
        server_address = ('', port)
        httpd = HTTPServer(server_address, DashboardHandler)
        
        print(f"✅ Servidor iniciado en http://{host}:{port}")
        print("📱 Campo de teléfono implementado en el dashboard")
        print("🔄 Presiona Ctrl+C para detener")
        
        # Abrir navegador después de un momento
        def open_browser():
            time.sleep(1)  # Esperar 1 segundo
            url = f"http://{host}:{port}/dashboard.html"
            print(f"🌐 Abriendo navegador: {url}")
            try:
                webbrowser.open(url)
                print("✅ Navegador abierto automáticamente")
            except Exception as e:
                print(f"⚠️ No se pudo abrir automáticamente: {e}")
                print(f"💡 Abre manualmente: {url}")
        
        # Abrir navegador en un hilo separado
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Mantener servidor corriendo
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

