#!/usr/bin/env python3
"""
Script para iniciar Evolution API
"""

import subprocess
import os
import time
import requests

def check_docker():
    """Verificar si Docker está funcionando"""
    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def start_evolution_api():
    """Iniciar Evolution API"""
    print("🚀 Iniciando Evolution API...")
    
    evolution_dir = os.path.join(os.getcwd(), "evolution-api")
    
    if not os.path.exists(evolution_dir):
        print("❌ Directorio evolution-api no encontrado")
        return False
    
    try:
        # Cambiar al directorio
        os.chdir(evolution_dir)
        
        # Iniciar servicios
        print("🐳 Iniciando servicios con Docker Compose...")
        result = subprocess.run(["docker-compose", "up", "-d"], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Servicios iniciados")
            return True
        else:
            print(f"❌ Error iniciando servicios: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def wait_for_evolution_api():
    """Esperar a que Evolution API esté disponible"""
    print("⏳ Esperando a que Evolution API esté disponible...")
    
    max_wait = 120  # 2 minutos
    wait_time = 0
    
    while wait_time < max_wait:
        try:
            response = requests.get("http://localhost:8080", timeout=5)
            if response.status_code == 200:
                print("✅ Evolution API está funcionando!")
                return True
        except:
            pass
        
        time.sleep(5)
        wait_time += 5
        
        if wait_time % 15 == 0:
            print(f"⏳ Esperando... ({wait_time}s)")
    
    print("⏰ Tiempo de espera agotado")
    return False

def main():
    """Función principal"""
    print("🔧 Iniciador de Evolution API")
    print("=" * 50)
    
    # Verificar Docker
    print("🔍 Verificando Docker...")
    if not check_docker():
        print("❌ Docker no está funcionando")
        print("💡 Por favor:")
        print("1. Inicia Docker Desktop")
        print("2. Espera a que se inicie completamente")
        print("3. Ejecuta este script nuevamente")
        return
    
    print("✅ Docker está funcionando")
    
    # Iniciar Evolution API
    if start_evolution_api():
        # Esperar a que esté disponible
        if wait_for_evolution_api():
            print("\n🎯 Evolution API iniciado exitosamente!")
            print("📱 Ahora puedes probar enviar mensajes de WhatsApp")
        else:
            print("\n❌ Evolution API no se pudo iniciar correctamente")
    else:
        print("\n❌ Error iniciando Evolution API")

if __name__ == "__main__":
    main()
