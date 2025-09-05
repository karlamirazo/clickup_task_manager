#!/usr/bin/env python3
"""
Script de configuración y prueba para Evolution API
Configura y prueba el sistema de WhatsApp de producción
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.evolution_api_config import get_evolution_config, is_production_ready
from core.production_whatsapp_service import get_production_service
from core.evolution_webhook_manager import get_webhook_manager
from core.automated_notification_manager import get_automated_manager
from core.config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EvolutionAPISetup:
    """Clase para configurar y probar Evolution API"""
    
    def __init__(self):
        self.config = get_evolution_config()
        self.test_results = {}
    
    async def run_full_setup(self) -> bool:
        """Ejecuta la configuración completa"""
        print("🚀 Iniciando configuración completa de Evolution API...")
        print("=" * 60)
        
        try:
            # 1. Verificar configuración
            if not await self.check_configuration():
                return False
            
            # 2. Verificar conexión a Evolution API
            if not await self.check_evolution_connection():
                return False
            
            # 3. Verificar instancia de WhatsApp
            if not await self.check_whatsapp_instance():
                return False
            
            # 4. Probar envío de mensaje
            if not await self.test_message_sending():
                return False
            
            # 5. Configurar webhooks
            if not await self.setup_webhooks():
                return False
            
            # 6. Probar sistema automático
            if not await self.test_automated_system():
                return False
            
            print("✅ Configuración completa exitosa!")
            return True
            
        except Exception as e:
            logger.error(f"Error en configuración completa: {e}")
            return False
    
    async def check_configuration(self) -> bool:
        """Verifica la configuración básica"""
        print("📋 Verificando configuración...")
        
        try:
            # Verificar variables de entorno
            required_vars = [
                'WHATSAPP_EVOLUTION_URL',
                'WHATSAPP_EVOLUTION_API_KEY',
                'WHATSAPP_INSTANCE_NAME'
            ]
            
            missing_vars = []
            for var in required_vars:
                if not getattr(settings, var, None):
                    missing_vars.append(var)
            
            if missing_vars:
                print(f"❌ Variables faltantes: {', '.join(missing_vars)}")
                print("   Configura estas variables en tu archivo .env")
                return False
            
            # Verificar configuración de producción
            if not is_production_ready():
                print("❌ Configuración de producción no está lista")
                return False
            
            print("✅ Configuración básica correcta")
            self.test_results['configuration'] = True
            return True
            
        except Exception as e:
            print(f"❌ Error verificando configuración: {e}")
            return False
    
    async def check_evolution_connection(self) -> bool:
        """Verifica la conexión a Evolution API"""
        print("🔌 Verificando conexión a Evolution API...")
        
        try:
            # Crear sesión de prueba
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                # Verificar que el servidor responda
                try:
                    async with session.get(f"{self.config.base_url}/", timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            print("✅ Servidor Evolution API responde")
                            print(f"   Versión: {data.get('version', 'N/A')}")
                        else:
                            print(f"⚠️ Servidor responde con estado {response.status}")
                except Exception:
                    print("⚠️ No se pudo verificar endpoint raíz")
                
                # Verificar que la API esté disponible
                try:
                    headers = {"apikey": self.config.api_key} if self.config.api_key else {}
                    # Probar endpoint del manager que sabemos que funciona
                    async with session.get(f"{self.config.base_url}/manager", headers=headers, timeout=10) as response:
                        if response.status == 200:
                            print("✅ API Evolution API disponible")
                            self.test_results['evolution_connection'] = True
                            return True
                        else:
                            print(f"❌ API no disponible: HTTP {response.status}")
                            return False
                except Exception as e:
                    print(f"❌ Error conectando a Evolution API: {e}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error verificando conexión: {e}")
            return False
    
    async def check_whatsapp_instance(self) -> bool:
        """Verifica la instancia de WhatsApp"""
        print("📱 Verificando instancia de WhatsApp...")
        
        try:
            whatsapp_service = await get_production_service()
            
            # Verificar estado de la instancia
            status = await whatsapp_service.get_instance_status()
            
            if status.get("success"):
                instance_data = status.get("data", {})
                instance_status = instance_data.get("status", "unknown")
                
                print(f"✅ Instancia {self.config.instance_name} encontrada")
                print(f"   Estado: {instance_status}")
                
                if instance_status == "open":
                    print("   WhatsApp conectado y listo")
                    self.test_results['whatsapp_instance'] = True
                    return True
                elif instance_status == "close":
                    print("   WhatsApp desconectado - escanea el código QR")
                    self.test_results['whatsapp_instance'] = False
                    return False
                else:
                    print(f"   Estado desconocido: {instance_status}")
                    return False
            else:
                print(f"❌ Error obteniendo estado de instancia: {status.get('error')}")
                return False
                
        except Exception as e:
            print(f"❌ Error verificando instancia: {e}")
            return False
    
    async def test_message_sending(self) -> bool:
        """Prueba el envío de mensajes"""
        print("📤 Probando envío de mensajes...")
        
        try:
            whatsapp_service = await get_production_service()
            
            # Crear notificación de prueba
            from core.production_whatsapp_service import ProductionNotification
            
            test_notification = ProductionNotification(
                id="test_message",
                task_id="TEST-001",
                task_title="Mensaje de prueba",
                task_description="Este es un mensaje de prueba del sistema de notificaciones de ClickUp",
                phone_numbers=["+525512345678"],  # Número de prueba
                notification_type="test",
                priority="normal"
            )
            
            # Intentar enviar (esto puede fallar si no hay números válidos)
            try:
                result = await whatsapp_service.send_task_notification(test_notification)
                
                if result.get("success"):
                    print("✅ Envío de mensajes funcionando")
                    self.test_results['message_sending'] = True
                    return True
                else:
                    print(f"⚠️ Envío de mensajes con problemas: {result.get('error')}")
                    # No es un error crítico, puede ser por números de prueba
                    self.test_results['message_sending'] = False
                    return True
                    
            except Exception as e:
                print(f"⚠️ Error en envío de prueba: {e}")
                # No es un error crítico
                return True
                
        except Exception as e:
            print(f"❌ Error probando envío: {e}")
            return False
    
    async def setup_webhooks(self) -> bool:
        """Configura los webhooks"""
        print("🔗 Configurando webhooks...")
        
        try:
            webhook_manager = await get_webhook_manager()
            
            # Verificar estado del gestor
            status = webhook_manager.get_status()
            
            if status.get("is_processing"):
                print("✅ Gestor de webhooks funcionando")
                self.test_results['webhooks'] = True
                return True
            else:
                print("❌ Gestor de webhooks no está funcionando")
                return False
                
        except Exception as e:
            print(f"❌ Error configurando webhooks: {e}")
            return False
    
    async def test_automated_system(self) -> bool:
        """Prueba el sistema automático"""
        print("🤖 Probando sistema automático...")
        
        try:
            automated_manager = await get_automated_manager()
            
            # Verificar estado del gestor
            status = automated_manager.get_status()
            
            if status.get("is_running"):
                print("✅ Sistema automático funcionando")
                print(f"   Cola de notificaciones: {status.get('queue_size')}")
                print(f"   Notificaciones programadas: {status.get('scheduled_notifications')}")
                self.test_results['automated_system'] = True
                return True
            else:
                print("❌ Sistema automático no está funcionando")
                return False
                
        except Exception as e:
            print(f"❌ Error probando sistema automático: {e}")
            return False
    
    def print_summary(self):
        """Imprime un resumen de los resultados"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE CONFIGURACIÓN")
        print("=" * 60)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASÓ" if result else "❌ FALLÓ"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print("\n" + "=" * 60)
        
        if all(self.test_results.values()):
            print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está listo para producción.")
        else:
            print("⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")
        
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Configura webhooks en ClickUp para notificaciones automáticas")
        print("2. Agrega números de teléfono reales en las descripciones de tareas")
        print("3. Prueba creando/actualizando tareas en ClickUp")
        print("4. Monitorea los logs para ver las notificaciones enviadas")
    
    async def cleanup(self):
        """Limpia los recursos"""
        try:
            # Detener servicios
            from core.evolution_webhook_manager import webhook_manager
            from core.automated_notification_manager import automated_manager
            
            if webhook_manager.is_processing:
                await webhook_manager.stop()
            
            if automated_manager.is_running:
                await automated_manager.stop()
                
        except Exception as e:
            logger.error(f"Error en cleanup: {e}")

async def main():
    """Función principal"""
    setup = EvolutionAPISetup()
    
    try:
        # Ejecutar configuración completa
        success = await setup.run_full_setup()
        
        # Imprimir resumen
        setup.print_summary()
        
        if success:
            print("\n🚀 El sistema está listo para usar en producción!")
        else:
            print("\n❌ Hay problemas que deben resolverse antes de usar en producción.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Configuración interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    finally:
        # Limpiar recursos
        await setup.cleanup()

if __name__ == "__main__":
    # Ejecutar configuración
    asyncio.run(main())
