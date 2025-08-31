#!/usr/bin/env python3
"""
Verificar variables de entorno después del deploy
"""

import os
import sys

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import settings

def check_post_deploy():
    """Verificar configuración después del deploy"""
    
    print("🔍 VERIFICACIÓN POST-DEPLOY - VARIABLES DE ENTORNO")
    print("=" * 70)
    
    # Variables críticas de WhatsApp
    print("\n📱 CONFIGURACIÓN DE WHATSAPP:")
    print("-" * 40)
    
    print(f"✅ WHATSAPP_ENABLED: {settings.WHATSAPP_ENABLED}")
    print(f"✅ WHATSAPP_NOTIFICATIONS_ENABLED: {settings.WHATSAPP_NOTIFICATIONS_ENABLED}")
    print(f"✅ WHATSAPP_TASK_CREATED: {settings.WHATSAPP_TASK_CREATED}")
    
    print(f"\n🔧 CONFIGURACIÓN TÉCNICA:")
    print("-" * 40)
    print(f"✅ WHATSAPP_EVOLUTION_URL: {settings.WHATSAPP_EVOLUTION_URL}")
    print(f"✅ WHATSAPP_EVOLUTION_API_KEY: {settings.WHATSAPP_EVOLUTION_API_KEY}")
    print(f"✅ WHATSAPP_INSTANCE_NAME: {settings.WHATSAPP_INSTANCE_NAME}")
    
    print(f"\n🎮 CONFIGURACIÓN DEL SIMULADOR:")
    print("-" * 40)
    print(f"⚠️  WHATSAPP_SIMULATOR_ENABLED: {settings.WHATSAPP_SIMULATOR_ENABLED}")
    
    # Verificar valores de entorno directamente
    print(f"\n🔍 VALORES DIRECTOS DE ENTORNO:")
    print("-" * 40)
    
    env_vars = [
        "WHATSAPP_SIMULATOR_ENABLED",
        "WHATSAPP_EVOLUTION_URL",
        "WHATSAPP_EVOLUTION_API_KEY",
        "WHATSAPP_INSTANCE_NAME"
    ]
    
    for var in env_vars:
        value = os.getenv(var, "NO DEFINIDA")
        print(f"📋 {var}: {value}")
    
    # Análisis del estado actual
    print(f"\n🎯 ANÁLISIS DEL ESTADO ACTUAL:")
    print("-" * 40)
    
    # Verificar simulador
    if settings.WHATSAPP_SIMULATOR_ENABLED:
        print("❌ PROBLEMA: El simulador sigue ACTIVADO")
        print("💡 Las notificaciones van al simulador, no a WhatsApp real")
    else:
        print("✅ EXCELENTE: El simulador está DESACTIVADO")
        print("💡 Las notificaciones irán a WhatsApp real")
    
    # Verificar URL
    if "localhost" in settings.WHATSAPP_EVOLUTION_URL:
        print("❌ PROBLEMA: URL sigue apuntando a localhost")
        print(f"💡 Actual: {settings.WHATSAPP_EVOLUTION_URL}")
        print("💡 Debería ser: https://evolution-api-production-9d5d.up.railway.app")
    else:
        print("✅ EXCELENTE: URL apunta a Railway correctamente")
        print(f"💡 Actual: {settings.WHATSAPP_EVOLUTION_URL}")
    
    # Verificar instancia
    if settings.WHATSAPP_INSTANCE_NAME != "clickup-v23":
        print("❌ PROBLEMA: Instancia incorrecta")
        print(f"💡 Actual: {settings.WHATSAPP_INSTANCE_NAME}")
        print("💡 Debería ser: clickup-v23")
    else:
        print("✅ EXCELENTE: Instancia configurada correctamente")
        print(f"💡 Actual: {settings.WHATSAPP_INSTANCE_NAME}")
    
    # Verificar API Key
    if settings.WHATSAPP_EVOLUTION_API_KEY != "clickup-evolution-v223":
        print("❌ PROBLEMA: API Key incorrecta")
        print(f"💡 Actual: {settings.WHATSAPP_EVOLUTION_API_KEY}")
        print("💡 Debería ser: clickup-evolution-v223")
    else:
        print("✅ EXCELENTE: API Key configurada correctamente")
        print(f"💡 Actual: {settings.WHATSAPP_EVOLUTION_API_KEY}")
    
    # Resumen final
    print(f"\n🎯 RESUMEN FINAL:")
    print("-" * 40)
    
    problems = []
    if settings.WHATSAPP_SIMULATOR_ENABLED:
        problems.append("Simulador activado")
    if "localhost" in settings.WHATSAPP_EVOLUTION_URL:
        problems.append("URL incorrecta")
    if settings.WHATSAPP_INSTANCE_NAME != "clickup-v23":
        problems.append("Instancia incorrecta")
    if settings.WHATSAPP_EVOLUTION_API_KEY != "clickup-evolution-v223":
        problems.append("API Key incorrecta")
    
    if not problems:
        print("🎉 ¡PERFECTO! Todas las configuraciones están correctas")
        print("✅ Las notificaciones de WhatsApp deberían funcionar correctamente")
        print("✅ La tarea 'Dodgers' recibirá notificación si la recreas")
    else:
        print(f"⚠️  PROBLEMAS DETECTADOS: {len(problems)}")
        for problem in problems:
            print(f"   ❌ {problem}")
        print("🔧 Necesitas configurar estas variables en Railway")

if __name__ == "__main__":
    check_post_deploy()

