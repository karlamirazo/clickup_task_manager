#!/usr/bin/env python3
"""
Script de diagnóstico completo para Evolution API
Verifica conectividad, configuración y estado de WhatsApp
"""

import os
import sys
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional

# Agregar el directorio raiz al path para importar módulos del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.config import settings
    from integrations.evolution_api.config import get_evolution_config, is_production_ready
    from integrations.whatsapp.client import WhatsAppClient, WhatsAppNotificationService
    from integrations.whatsapp.simulator import WhatsAppSimulator
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("💡 Asegúrate de estar en el directorio del proyecto")
    sys.exit(1)

def print_banner():
    """Mostrar banner del diagnóstico"""
    print("=" * 80)
    print("🔍 DIAGNÓSTICO DE EVOLUTION API")
    print("   ClickUp Project Manager - Verificación de WhatsApp")
    print("=" * 80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print("-" * 80)

def check_basic_configuration():
    """Verificar configuración básica"""
    print("🔧 VERIFICANDO CONFIGURACIÓN BÁSICA")
    print("-" * 50)
    
    config_checks = [
        ("WHATSAPP_ENABLED", settings.WHATSAPP_ENABLED, "False"),
        ("WHATSAPP_NOTIFICATIONS_ENABLED", settings.WHATSAPP_NOTIFICATIONS_ENABLED, "False"),
        ("WHATSAPP_EVOLUTION_URL", settings.WHATSAPP_EVOLUTION_URL, "http://localhost:8080"),
        ("WHATSAPP_EVOLUTION_API_KEY", settings.WHATSAPP_EVOLUTION_API_KEY, ""),
        ("WHATSAPP_INSTANCE_NAME", settings.WHATSAPP_INSTANCE_NAME, "clickup-manager"),
        ("WHATSAPP_WEBHOOK_URL", settings.WHATSAPP_WEBHOOK_URL, ""),
        ("WHATSAPP_SIMULATOR_ENABLED", settings.WHATSAPP_SIMULATOR_ENABLED, "True")
    ]
    
    config_status = {}
    all_ok = True
    
    for setting_name, value, default in config_checks:
        if value and str(value) != default and str(value) != "":
            print(f"   ✅ {setting_name}: {value}")
            config_status[setting_name] = "configured"
        else:
            print(f"   ⚠️  {setting_name}: {default} (default/not set)")
            config_status[setting_name] = "default"
            if setting_name in ["WHATSAPP_EVOLUTION_URL", "WHATSAPP_INSTANCE_NAME"]:
                all_ok = False
    
    print(f"\n📊 Estado general: {'✅ Configurado' if all_ok else '⚠️ Configuración incompleta'}")
    return config_status, all_ok

def check_evolution_config():
    """Verificar configuración de Evolution API"""
    print("\n⚙️ VERIFICANDO CONFIGURACIÓN DE EVOLUTION")
    print("-" * 50)
    
    try:
        config = get_evolution_config()
        production_ready = is_production_ready()
        
        print(f"   📡 Base URL: {config.base_url}")
        print(f"   🔑 API Key: {'✅ Configurado' if config.api_key else '❌ No configurado'}")
        print(f"   📱 Instance: {config.instance_name}")
        print(f"   🔗 Webhook URL: {config.webhook_url}")
        print(f"   🚀 Production Mode: {config.production_mode}")
        print(f"   📝 Log Messages: {config.log_all_messages}")
        print(f"   ⚡ Rate Limiting: {config.rate_limit_enabled}")
        print(f"   📞 Phone Validation: {config.validate_phone_numbers}")
        
        print(f"\n🎯 Production Ready: {'✅ Sí' if production_ready else '❌ No'}")
        
        # Verificar tipos de notificación habilitados
        enabled_notifications = [k for k, v in config.notification_types.items() if v]
        print(f"\n📢 Notificaciones habilitadas ({len(enabled_notifications)}):")
        for notif_type in enabled_notifications:
            print(f"   ✅ {notif_type}")
        
        disabled_notifications = [k for k, v in config.notification_types.items() if not v]
        if disabled_notifications:
            print(f"\n🔇 Notificaciones deshabilitadas ({len(disabled_notifications)}):")
            for notif_type in disabled_notifications:
                print(f"   ❌ {notif_type}")
        
        return production_ready
        
    except Exception as e:
        print(f"❌ Error verificando configuración de Evolution: {e}")
        return False

async def test_evolution_api_connectivity():
    """Probar conectividad con Evolution API"""
    print("\n🌐 PROBANDO CONECTIVIDAD CON EVOLUTION API")
    print("-" * 50)
    
    try:
        client = WhatsAppClient()
        
        # Test 1: Información de la instancia
        print("🔍 Test 1: Información de la instancia")
        async with client:
            info_response = await client.get_instance_info()
            if info_response.success:
                print("   ✅ Conexión exitosa - Instancia accesible")
                if info_response.data:
                    print(f"   📊 Datos: {json.dumps(info_response.data, indent=2)[:200]}...")
            else:
                print(f"   ❌ Error: {info_response.message}")
                if info_response.error:
                    print(f"   🔍 Detalles: {info_response.error}")
        
        # Test 2: Estado de la instancia
        print("\n🔍 Test 2: Estado de la instancia")
        async with client:
            status_response = await client.get_instance_status()
            if status_response.success:
                print("   ✅ Estado obtenido exitosamente")
                if status_response.data:
                    state = status_response.data.get('instance', {}).get('state', 'unknown')
                    print(f"   📱 Estado: {state}")
            else:
                print(f"   ❌ Error obteniendo estado: {status_response.message}")
        
        # Test 3: QR Code (si no está conectado)
        print("\n🔍 Test 3: Código QR")
        async with client:
            qr_response = await client.get_qr_code()
            if qr_response.success:
                print("   ✅ QR Code disponible")
                if qr_response.data and 'qrcode' in qr_response.data:
                    print("   📱 Para conectar WhatsApp, escanea el QR desde la app")
                    # Guardar QR en archivo para mostrar después
                    with open("qr_code.txt", "w") as f:
                        f.write(qr_response.data.get('qrcode', ''))
                    print("   💾 QR guardado en qr_code.txt")
            else:
                print(f"   ⚠️  QR no disponible: {qr_response.message}")
                if "already connected" in qr_response.message.lower():
                    print("   📱 La instancia ya está conectada")
        
        return True
        
    except Exception as e:
        print(f"❌ Error de conectividad: {e}")
        return False

async def test_whatsapp_notification_service():
    """Probar servicio de notificaciones"""
    print("\n📱 PROBANDO SERVICIO DE NOTIFICACIONES")
    print("-" * 50)
    
    try:
        service = WhatsAppNotificationService()
        
        print(f"   🔧 Servicio habilitado: {service.enabled}")
        print(f"   🎭 Simulador disponible: {service.simulator is not None}")
        
        # Si el simulador está habilitado, probarlo
        if service.simulator:
            print("\n🧪 Test con simulador:")
            test_response = await service.send_task_notification(
                phone_number="5551234567",
                task_title="Prueba de Diagnóstico",
                task_description="Este es un mensaje de prueba del sistema de diagnóstico",
                notification_type="created"
            )
            
            if test_response.success:
                print(f"   ✅ Simulador: {test_response.message}")
            else:
                print(f"   ❌ Error en simulador: {test_response.error}")
        
        # Si está en modo producción, hacer test básico
        if service.enabled and not settings.WHATSAPP_SIMULATOR_ENABLED:
            print("\n🚀 Test en modo producción:")
            print("   ⚠️  Para evitar enviar mensajes reales, se omite el test")
            print("   💡 Use --test-real para enviar un mensaje de prueba real")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando servicio: {e}")
        return False

async def test_phone_number_validation():
    """Probar validación de números de teléfono"""
    print("\n📞 PROBANDO VALIDACIÓN DE NÚMEROS")
    print("-" * 50)
    
    test_numbers = [
        "5551234567",        # Nacional México
        "+525551234567",     # Internacional México
        "1234567890",        # Sin código de país
        "+1234567890",       # Formato internacional
        "55 1234 5678",      # Con espacios
        "55-1234-5678",      # Con guiones
        "(55) 1234-5678",    # Con paréntesis
    ]
    
    try:
        service = WhatsAppNotificationService()
        
        for number in test_numbers:
            cleaned = service._clean_phone_number(number)
            print(f"   📱 {number:<20} → {cleaned}")
        
        print("\n✅ Validación de números funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en validación: {e}")
        return False

def check_whatsapp_simulator():
    """Verificar simulador de WhatsApp"""
    print("\n🎭 VERIFICANDO SIMULADOR DE WHATSAPP")
    print("-" * 50)
    
    try:
        if not settings.WHATSAPP_SIMULATOR_ENABLED:
            print("   ⚠️  Simulador deshabilitado en configuración")
            return False
        
        simulator = WhatsAppSimulator()
        
        print(f"   ✅ Simulador disponible")
        print(f"   ⏱️  Delay configurado: {settings.WHATSAPP_SIMULATOR_DELAY}s")
        print(f"   📊 Respuestas exitosas: simuladas al 100%")
        
        # Test básico del simulador
        test_result = asyncio.run(simulator.send_text_message(
            "+5251234567", 
            "Test de diagnóstico"
        ))
        
        if test_result.get("success", True):
            print(f"   ✅ Test básico exitoso: {test_result.get('message', 'OK')}")
        else:
            print(f"   ❌ Test básico falló: {test_result.get('error', 'Error desconocido')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando simulador: {e}")
        return False

def check_docker_evolution_api():
    """Verificar si Evolution API está corriendo en Docker"""
    print("\n🐳 VERIFICANDO EVOLUTION API EN DOCKER")
    print("-" * 50)
    
    try:
        import subprocess
        
        # Verificar si Docker está instalado
        try:
            subprocess.run(["docker", "--version"], 
                         capture_output=True, check=True)
            print("   ✅ Docker está instalado")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("   ❌ Docker no está instalado o no está accesible")
            return False
        
        # Verificar contenedores de Evolution API
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=evolution", "--format", "table {{.Names}}\t{{.Status}}"],
                capture_output=True, text=True, check=True
            )
            
            if result.stdout.strip():
                print("   📦 Contenedores de Evolution API encontrados:")
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        print(f"      {line}")
            else:
                print("   ⚠️  No se encontraron contenedores de Evolution API corriendo")
        
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Error verificando contenedores: {e}")
        
        # Verificar archivos Docker en el proyecto
        docker_files = [
            "docker-compose.evolution.yml",
            "evolution-api/docker-compose.yaml",
            "docker-compose-whatsapp.yml"
        ]
        
        print("\n   📄 Archivos Docker en el proyecto:")
        for file_path in docker_files:
            if os.path.exists(file_path):
                print(f"      ✅ {file_path}")
            else:
                print(f"      ❌ {file_path} (no encontrado)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando Docker: {e}")
        return False

async def generate_diagnostic_report(results: Dict[str, Any]):
    """Generar reporte de diagnóstico"""
    print("\n📋 GENERANDO REPORTE DE DIAGNÓSTICO")
    print("=" * 80)
    
    timestamp = datetime.now()
    
    report = {
        "timestamp": timestamp.isoformat(),
        "environment": settings.ENVIRONMENT,
        "evolution_api_diagnostic": {
            "configuration_status": results.get("config_status", {}),
            "connectivity_test": results.get("connectivity", False),
            "notification_service": results.get("notifications", False),
            "phone_validation": results.get("phone_validation", False),
            "simulator_status": results.get("simulator", False),
            "docker_status": results.get("docker", False)
        },
        "summary": {
            "total_tests": len([k for k in results.keys() if k != "config_status"]),
            "passed_tests": len([v for k, v in results.items() if k != "config_status" and v]),
            "overall_status": "healthy" if all(results.values()) else "issues_detected"
        },
        "recommendations": []
    }
    
    # Generar recomendaciones
    if not results.get("connectivity", False):
        report["recommendations"].append({
            "priority": "high",
            "issue": "Evolution API no accesible",
            "solution": "Verificar que Evolution API esté corriendo y la URL sea correcta"
        })
    
    if not results.get("notifications", False):
        report["recommendations"].append({
            "priority": "medium",
            "issue": "Servicio de notificaciones con problemas",
            "solution": "Revisar configuración de WhatsApp y credenciales"
        })
    
    if not results.get("simulator", False) and settings.WHATSAPP_SIMULATOR_ENABLED:
        report["recommendations"].append({
            "priority": "low",
            "issue": "Simulador no funciona correctamente",
            "solution": "Verificar configuración del simulador en settings"
        })
    
    # Guardar reporte
    report_file = f"evolution_api_diagnostic_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        os.makedirs("logs", exist_ok=True)
        report_path = f"logs/{report_file}"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Reporte guardado: {report_path}")
        
    except Exception as e:
        print(f"⚠️  No se pudo guardar el reporte: {e}")
    
    # Mostrar resumen
    print(f"\n🎯 RESUMEN DEL DIAGNÓSTICO")
    print(f"   📊 Tests ejecutados: {report['summary']['total_tests']}")
    print(f"   ✅ Tests exitosos: {report['summary']['passed_tests']}")
    print(f"   📈 Estado general: {report['summary']['overall_status']}")
    
    if report["recommendations"]:
        print(f"\n💡 RECOMENDACIONES:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"   {i}. [{rec['priority'].upper()}] {rec['issue']}")
            print(f"      💡 {rec['solution']}")
    else:
        print(f"\n🎉 ¡Todo funcionando correctamente!")
    
    return report

async def run_quick_connectivity_test():
    """Test rápido de conectividad"""
    print("⚡ TEST RÁPIDO DE CONECTIVIDAD")
    print("-" * 40)
    
    try:
        async with aiohttp.ClientSession() as session:
            url = settings.WHATSAPP_EVOLUTION_URL
            
            # Test básico de conectividad
            try:
                async with session.get(f"{url}/instance", timeout=5) as response:
                    if response.status == 200:
                        print(f"✅ Evolution API responde en {url}")
                        return True
                    else:
                        print(f"⚠️  Evolution API responde con código {response.status}")
                        return False
            except asyncio.TimeoutError:
                print(f"❌ Timeout conectando a {url}")
                return False
            except Exception as e:
                print(f"❌ Error: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Error en test de conectividad: {e}")
        return False

async def main():
    """Función principal de diagnóstico"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Diagnóstico completo de Evolution API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Diagnóstico completo
  python scripts/diagnose_evolution_api.py
  
  # Solo test rápido
  python scripts/diagnose_evolution_api.py --quick
  
  # Test con mensaje real (cuidado!)
  python scripts/diagnose_evolution_api.py --test-real
        """
    )
    
    parser.add_argument("--quick", action="store_true",
                       help="Solo hacer test rápido de conectividad")
    parser.add_argument("--test-real", action="store_true",
                       help="Enviar mensaje de prueba real (usar con precaución)")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Test rápido
    if args.quick:
        connectivity_ok = await run_quick_connectivity_test()
        if connectivity_ok:
            print("\n🎉 Test rápido exitoso - Evolution API está accesible")
        else:
            print("\n❌ Test rápido falló - Revisar configuración")
        return
    
    # Diagnóstico completo
    results = {}
    
    # 1. Configuración básica
    config_status, config_ok = check_basic_configuration()
    results["config_status"] = config_status
    results["config_ok"] = config_ok
    
    # 2. Configuración de Evolution
    evolution_ok = check_evolution_config()
    results["evolution_config"] = evolution_ok
    
    # 3. Conectividad
    connectivity_ok = await test_evolution_api_connectivity()
    results["connectivity"] = connectivity_ok
    
    # 4. Servicio de notificaciones
    notifications_ok = await test_whatsapp_notification_service()
    results["notifications"] = notifications_ok
    
    # 5. Validación de números
    phone_validation_ok = await test_phone_number_validation()
    results["phone_validation"] = phone_validation_ok
    
    # 6. Simulador
    simulator_ok = check_whatsapp_simulator()
    results["simulator"] = simulator_ok
    
    # 7. Docker
    docker_ok = check_docker_evolution_api()
    results["docker"] = docker_ok
    
    # 8. Test real (opcional)
    if args.test_real:
        print("\n🚨 ENVIANDO MENSAJE DE PRUEBA REAL")
        print("-" * 50)
        print("⚠️  ¡ESTO ENVIARÁ UN MENSAJE REAL!")
        
        phone = input("📱 Ingresa el número de teléfono (con código de país): ")
        if phone:
            service = WhatsAppNotificationService()
            test_response = await service.send_task_notification(
                phone_number=phone,
                task_title="🧪 Test de Evolution API",
                task_description="Este es un mensaje de prueba del sistema de diagnóstico",
                notification_type="created"
            )
            
            if test_response.success:
                print(f"   ✅ Mensaje enviado: {test_response.message}")
            else:
                print(f"   ❌ Error enviando mensaje: {test_response.error}")
    
    # Generar reporte
    await generate_diagnostic_report(results)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Diagnóstico cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el diagnóstico: {e}")
        sys.exit(1)
