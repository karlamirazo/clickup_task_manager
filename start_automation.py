#!/usr/bin/env python3
"""
Script para activar el sistema de automatización de notificaciones
"""

import asyncio
import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from notifications.automated_manager import AutomatedNotificationManager
from core.config import settings

async def start_automation():
    """Inicia el sistema de automatización de notificaciones"""
    print("🚀 INICIANDO SISTEMA DE AUTOMATIZACIÓN DE NOTIFICACIONES")
    print("=" * 60)
    
    try:
        # Crear el gestor de notificaciones
        manager = AutomatedNotificationManager()
        
        print(f"✅ Configuración cargada:")
        print(f"   - WhatsApp habilitado: {settings.WHATSAPP_ENABLED}")
        print(f"   - Notificaciones habilitadas: {settings.WHATSAPP_NOTIFICATIONS_ENABLED}")
        print(f"   - Automatización habilitada: {settings.AUTOMATION_ENABLED}")
        print(f"   - Intervalo de verificación: {settings.AUTOMATION_INTERVAL} segundos")
        print()
        
        # Iniciar el sistema de automatización
        print("🔄 Iniciando verificación automática de tareas...")
        await manager.start_automation()
        
        print("✅ Sistema de automatización iniciado correctamente")
        print("📱 Las notificaciones de WhatsApp se enviarán automáticamente")
        print("⏰ Verificando tareas cada 5 minutos...")
        print()
        print("💡 Para detener el sistema, presiona Ctrl+C")
        
        # Mantener el sistema ejecutándose
        while True:
            await asyncio.sleep(60)  # Verificar cada minuto
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sistema de automatización...")
        await manager.stop_automation()
        print("✅ Sistema detenido correctamente")
    except Exception as e:
        print(f"❌ Error iniciando automatización: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(start_automation())
