#!/usr/bin/env python3
"""
Script para iniciar el sistema de monitoreo de Railway
Incluye configuración automática y verificación de dependencias
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime

# Agregar el directorio raiz al path para importar módulos del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from monitoring.railway.log_monitor import RailwayLogMonitor
    from monitoring.railway.alerts import alerts_manager
    from core.config import settings
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("💡 Asegúrate de estar en el directorio del proyecto y tener las dependencias instaladas")
    sys.exit(1)

def print_banner():
    """Mostrar banner del sistema"""
    print("=" * 80)
    print("🚀 RAILWAY MONITORING SYSTEM")
    print("   ClickUp Project Manager - Sistema de Monitoreo Avanzado")
    print("=" * 80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"🔗 Railway URL: https://clickuptaskmanager-production.up.railway.app")
    print("-" * 80)

def check_dependencies():
    """Verificar dependencias del sistema"""
    print("🔍 Verificando dependencias...")
    
    required_modules = [
        "aiohttp",
        "psutil", 
        "fastapi",
        "pydantic"
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Faltan módulos: {', '.join(missing_modules)}")
        print("💡 Instala las dependencias con: pip install -r requirements.txt")
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True

def check_configuration():
    """Verificar configuración del sistema"""
    print("\n🔧 Verificando configuración...")
    
    config_checks = [
        ("ENVIRONMENT", settings.ENVIRONMENT, "development"),
        ("WHATSAPP_ENABLED", settings.WHATSAPP_ENABLED, "NotSet"),
        ("SMTP_HOST", getattr(settings, 'SMTP_HOST', None), "NotSet"),
        ("LOG_LEVEL", settings.LOG_LEVEL, "INFO")
    ]
    
    for check_name, value, default in config_checks:
        if value and value != "NotSet":
            print(f"   ✅ {check_name}: {value}")
        else:
            print(f"   ⚠️  {check_name}: {default} (default)")
    
    print("✅ Configuración verificada")

async def test_system_connectivity():
    """Probar conectividad del sistema"""
    print("\n🌐 Probando conectividad...")
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            url = "https://clickuptaskmanager-production.up.railway.app/debug"
            print(f"   🔍 Probando: {url}")
            
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    print(f"   ✅ Railway responde: HTTP {response.status}")
                    return True
                else:
                    print(f"   ⚠️  Railway responde con: HTTP {response.status}")
                    return False
                    
    except Exception as e:
        print(f"   ❌ Error de conectividad: {e}")
        return False

async def start_monitoring_system(args):
    """Iniciar sistema de monitoreo"""
    print("\n🚀 Iniciando sistema de monitoreo...")
    
    # Configurar parámetros
    interval = args.interval
    duration_hours = args.duration
    enable_alerts = not args.no_alerts
    
    print(f"   📊 Intervalo: {interval} segundos")
    print(f"   ⏰ Duración: {'Infinito' if not duration_hours else f'{duration_hours} horas'}")
    print(f"   🔔 Alertas: {'Habilitadas' if enable_alerts else 'Deshabilitadas'}")
    
    # Crear monitor
    monitor = RailwayLogMonitor()
    
    # Configurar alertas si están habilitadas
    if enable_alerts:
        if args.error_threshold:
            alerts_manager.thresholds["error_rate_per_hour"] = args.error_threshold
        if args.response_threshold:
            alerts_manager.thresholds["response_time_seconds"] = args.response_threshold
        
        print(f"   🚨 Threshold errores: {alerts_manager.thresholds['error_rate_per_hour']}/hora")
        print(f"   ⚡ Threshold respuesta: {alerts_manager.thresholds['response_time_seconds']}s")
    
    print("\n" + "=" * 80)
    print("🔄 MONITOREO ACTIVO")
    print("   Presiona Ctrl+C para detener el monitoreo")
    print("=" * 80)
    
    try:
        # Iniciar monitoreo
        await monitor.start_monitoring(
            interval=interval,
            duration_hours=duration_hours
        )
        
    except KeyboardInterrupt:
        print("\n⏹️  Monitoreo detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el monitoreo: {e}")
    finally:
        print("✅ Sistema de monitoreo finalizado")

async def test_notifications():
    """Probar sistema de notificaciones"""
    print("\n🧪 Probando sistema de notificaciones...")
    
    try:
        await alerts_manager.test_notifications()
        print("✅ Notificación de prueba enviada correctamente")
        
        # Mostrar canales disponibles
        print("\n📱 Canales de notificación:")
        print(f"   📧 Email: {'✅ Configurado' if settings.SMTP_HOST else '❌ No configurado'}")
        print(f"   📱 WhatsApp: {'✅ Configurado' if settings.WHATSAPP_ENABLED else '❌ No configurado'}")
        
    except Exception as e:
        print(f"❌ Error probando notificaciones: {e}")

def show_monitoring_info():
    """Mostrar información del sistema de monitoreo"""
    print("\n📋 INFORMACIÓN DEL SISTEMA DE MONITOREO")
    print("-" * 50)
    print("🎯 Características principales:")
    print("   • Monitoreo en tiempo real de Railway")
    print("   • Alertas automáticas por email y WhatsApp")
    print("   • Dashboard web interactivo")
    print("   • Exportación de logs y métricas")
    print("   • Integración con sistema de logging")
    
    print("\n🔗 Endpoints disponibles:")
    print("   • Dashboard: /railway-monitor")
    print("   • API Status: /api/v1/railway/status")
    print("   • API Metrics: /api/v1/railway/metrics")
    print("   • API Alerts: /api/v1/railway/alerts")
    
    print("\n📊 Métricas monitoreadas:")
    print("   • Tiempo de respuesta del sistema")
    print("   • Tasa de errores por hora")
    print("   • Uso de CPU y memoria")
    print("   • Estado de la base de datos")
    print("   • Conectividad general")
    
    print("\n🚨 Tipos de alertas:")
    print("   • Sistema no responde (CRITICAL)")
    print("   • Tasa alta de errores (ERROR)")
    print("   • Respuesta lenta (WARNING)")
    print("   • Recursos del sistema altos (WARNING)")

async def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Sistema de Monitoreo de Railway para ClickUp Project Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Monitoreo básico por 1 hora
  python scripts/start_railway_monitoring.py --duration 1
  
  # Monitoreo continuo con intervalo de 15 segundos
  python scripts/start_railway_monitoring.py --interval 15
  
  # Solo verificar sistema (sin monitoreo)
  python scripts/start_railway_monitoring.py --check-only
  
  # Probar notificaciones
  python scripts/start_railway_monitoring.py --test-notifications
        """
    )
    
    parser.add_argument("--interval", type=int, default=30,
                       help="Intervalo entre verificaciones en segundos (default: 30)")
    parser.add_argument("--duration", type=int,
                       help="Duración del monitoreo en horas (default: infinito)")
    parser.add_argument("--no-alerts", action="store_true",
                       help="Deshabilitar sistema de alertas")
    parser.add_argument("--error-threshold", type=int,
                       help="Threshold de errores por hora para alertas (default: 5)")
    parser.add_argument("--response-threshold", type=float,
                       help="Threshold de tiempo de respuesta en segundos (default: 5.0)")
    parser.add_argument("--check-only", action="store_true",
                       help="Solo verificar sistema sin iniciar monitoreo")
    parser.add_argument("--test-notifications", action="store_true",
                       help="Probar sistema de notificaciones")
    parser.add_argument("--info", action="store_true",
                       help="Mostrar información del sistema")
    
    args = parser.parse_args()
    
    # Mostrar banner
    print_banner()
    
    # Mostrar información si se solicita
    if args.info:
        show_monitoring_info()
        return
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar configuración
    check_configuration()
    
    # Probar conectividad
    connectivity_ok = await test_system_connectivity()
    
    if not connectivity_ok:
        print("\n⚠️  Warning: No se pudo conectar al sistema Railway")
        print("   El monitoreo continuará pero las métricas pueden ser limitadas")
    
    # Ejecutar acción solicitada
    if args.test_notifications:
        await test_notifications()
        
    elif args.check_only:
        print("\n✅ Verificación del sistema completada")
        
    else:
        # Iniciar monitoreo
        await start_monitoring_system(args)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Script cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        sys.exit(1)
