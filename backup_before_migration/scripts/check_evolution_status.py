#!/usr/bin/env python3
"""
Script rápido para verificar el estado de Evolution API
"""

import os
import sys
import asyncio
import aiohttp
import json
from datetime import datetime

# Agregar el directorio raiz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.config import settings
except ImportError:
    print("❌ Error: No se pueden importar las configuraciones")
    print("💡 Ejecuta desde el directorio raíz del proyecto")
    sys.exit(1)

async def quick_evolution_check():
    """Verificación rápida de Evolution API"""
    
    print("🔍 VERIFICACIÓN RÁPIDA DE EVOLUTION API")
    print("=" * 50)
    print(f"🕐 {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Configuración
    print("📋 CONFIGURACIÓN:")
    print(f"   URL: {settings.WHATSAPP_EVOLUTION_URL}")
    print(f"   Instancia: {settings.WHATSAPP_INSTANCE_NAME}")
    print(f"   API Key: {'✅ Configurado' if settings.WHATSAPP_EVOLUTION_API_KEY else '❌ No configurado'}")
    print(f"   WhatsApp habilitado: {settings.WHATSAPP_ENABLED}")
    print()
    
    # Test de conectividad básica
    print("🌐 TEST DE CONECTIVIDAD:")
    
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        headers = {}
        
        if settings.WHATSAPP_EVOLUTION_API_KEY:
            headers['apikey'] = settings.WHATSAPP_EVOLUTION_API_KEY
        
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            
            # Test 1: Endpoint raíz
            try:
                url = settings.WHATSAPP_EVOLUTION_URL
                async with session.get(url) as response:
                    print(f"   📡 Conexión base: {response.status} ({url})")
            except Exception as e:
                print(f"   ❌ Error conexión base: {e}")
            
            # Test 2: Endpoint de instancia
            try:
                instance_url = f"{settings.WHATSAPP_EVOLUTION_URL}/instance"
                async with session.get(instance_url) as response:
                    print(f"   📱 Endpoint instancias: {response.status}")
                    if response.status == 200:
                        data = await response.text()
                        print(f"   📊 Respuesta: {data[:100]}...")
            except Exception as e:
                print(f"   ❌ Error endpoint instancias: {e}")
            
            # Test 3: Estado específico de nuestra instancia
            try:
                status_url = f"{settings.WHATSAPP_EVOLUTION_URL}/instance/status/{settings.WHATSAPP_INSTANCE_NAME}"
                async with session.get(status_url) as response:
                    print(f"   🔍 Estado instancia '{settings.WHATSAPP_INSTANCE_NAME}': {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        instance_state = data.get('instance', {}).get('state', 'unknown')
                        print(f"   📱 Estado WhatsApp: {instance_state}")
                        
                        if instance_state == 'open':
                            print("   ✅ WhatsApp CONECTADO y listo")
                        elif instance_state == 'close':
                            print("   ⚠️  WhatsApp DESCONECTADO - necesita escanear QR")
                        else:
                            print(f"   ❓ Estado desconocido: {instance_state}")
                            
                    elif response.status == 404:
                        print("   ❌ Instancia no encontrada - necesita ser creada")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Error: {error_text[:100]}...")
            except Exception as e:
                print(f"   ❌ Error estado instancia: {e}")
    
    except Exception as e:
        print(f"❌ Error general: {e}")
    
    print()
    
    # Verificar si el simulador está habilitado
    print("🎭 SIMULADOR:")
    if settings.WHATSAPP_SIMULATOR_ENABLED:
        print("   ✅ Simulador HABILITADO - mensajes simulados")
        print("   💡 Los mensajes no se envían realmente")
    else:
        print("   🚀 Simulador DESHABILITADO - modo producción")
        print("   ⚠️  Los mensajes se envían realmente")
    
    print()
    
    # Recomendaciones rápidas
    print("💡 RECOMENDACIONES RÁPIDAS:")
    
    if not settings.WHATSAPP_ENABLED:
        print("   🔧 Habilitar WhatsApp: WHATSAPP_ENABLED=True")
    
    if not settings.WHATSAPP_EVOLUTION_API_KEY:
        print("   🔑 Configurar API Key: WHATSAPP_EVOLUTION_API_KEY=tu_api_key")
    
    if settings.WHATSAPP_EVOLUTION_URL == "http://localhost:8080":
        print("   🌐 Verificar URL de Evolution API si no es local")
    
    print("   📖 Para diagnóstico completo: python scripts/diagnose_evolution_api.py")
    
    print()
    print("=" * 50)

def check_docker_containers():
    """Verificar contenedores Docker de Evolution"""
    print("🐳 CONTENEDORES DOCKER:")
    
    try:
        import subprocess
        
        # Verificar contenedores corriendo
        result = subprocess.run(
            ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            evolution_containers = [line for line in lines if 'evolution' in line.lower()]
            
            if evolution_containers:
                print("   📦 Contenedores Evolution encontrados:")
                for container in evolution_containers:
                    print(f"      {container}")
            else:
                print("   ⚠️  No hay contenedores Evolution corriendo")
                print("   💡 Intentar: docker-compose -f docker-compose.evolution.yml up -d")
        else:
            print("   ❌ Error ejecutando docker ps")
            
    except FileNotFoundError:
        print("   ❌ Docker no está instalado o no está en PATH")
    except Exception as e:
        print(f"   ❌ Error verificando Docker: {e}")
    
    print()

async def main():
    """Función principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "--with-docker":
        check_docker_containers()
    
    await quick_evolution_check()
    
    # Ofrecer comandos útiles
    print("🛠️  COMANDOS ÚTILES:")
    print("   🔍 Diagnóstico completo:")
    print("      python scripts/diagnose_evolution_api.py")
    print()
    print("   🚀 Iniciar Evolution API (Docker):")
    print("      docker-compose -f docker-compose.evolution.yml up -d")
    print()
    print("   📱 Ver logs de Evolution:")
    print("      docker-compose -f docker-compose.evolution.yml logs -f")
    print()
    print("   ⏹️  Detener Evolution API:")
    print("      docker-compose -f docker-compose.evolution.yml down")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Verificación cancelada")
    except Exception as e:
        print(f"\n❌ Error: {e}")
