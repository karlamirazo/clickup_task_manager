"""
ClickUp Project Manager - Iniciador Limpio del Servidor
Limpia todos los procesos y inicia uvicorn correctamente
"""

import os
import subprocess
import time
import signal

def kill_processes_on_port(port):
    """Mata todos los procesos que usen un puerto específico"""
    try:
        # Encontrar procesos usando el puerto (solo LISTENING local)
        result = subprocess.run(
            f'netstat -ano | findstr ":{port}" | findstr "LISTENING"',
            shell=True, capture_output=True, text=True
        )
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'LISTENING' in line and f':{port}' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        print(f"🔄 Terminando proceso PID {pid} en puerto {port}")
                        try:
                            subprocess.run(f'taskkill /PID {pid} /F', shell=True)
                            time.sleep(1)  # Esperar a que se termine
                        except:
                            pass
        else:
            print(f"✅ Puerto {port} ya está libre")
    except Exception as e:
        print(f"⚠️ Error limpiando puerto {port}: {e}")

def check_port_free(port):
    """Verifica si un puerto está libre"""
    try:
        result = subprocess.run(
            f'netstat -ano | findstr ":{port}" | findstr "LISTENING"',
            shell=True, capture_output=True, text=True
        )
        return not result.stdout.strip()
    except:
        return True

def start_server():
    """Inicia el servidor principal"""
    print("🚀 Iniciando ClickUp Project Manager...")
    
    # Limpiar puertos 8000 y 8001
    print("🧹 Limpiando puertos...")
    kill_processes_on_port(8000)
    kill_processes_on_port(8001)
    
    # Esperar un poco más para asegurar que se liberen
    print("⏳ Esperando liberación de puertos...")
    time.sleep(3)
    
    # Verificar que los puertos estén libres
    print("🔍 Verificando puertos...")
    for port in [8000, 8001]:
        if check_port_free(port):
            print(f"✅ Puerto {port} libre")
        else:
            print(f"❌ Puerto {port} aún ocupado")
    
    # Cambiar temporalmente la configuración para usar puerto 8001
    print("🔧 Configurando puerto 8001...")
    try:
        # Crear un archivo de configuración temporal
        with open('temp_config.py', 'w') as f:
            f.write('''
import os
os.environ["PORT"] = "8001"
os.environ["HOST"] = "127.0.0.1"
''')
        
        # Iniciar el servidor con configuración temporal
        print("🚀 Iniciando servidor uvicorn en puerto 8001...")
        subprocess.run(['python', 'main.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        return False
    finally:
        # Limpiar archivo temporal
        if os.path.exists('temp_config.py'):
            os.remove('temp_config.py')
    
    return True

if __name__ == "__main__":
    start_server()
