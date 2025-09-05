#!/usr/bin/env python3
"""
Monitor del deploy de Railway en tiempo real
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

async def monitor_railway_deploy():
    """Monitorear el deploy en Railway"""
    
    print("🚀 MONITOREANDO DEPLOY DE RAILWAY")
    print("=" * 50)
    
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    
    print(f"🔗 URL: {railway_url}")
    print(f"🕐 Iniciado: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    checks = [
        {
            "name": "Sistema Principal",
            "url": "/debug",
            "description": "Endpoint de debug principal"
        },
        {
            "name": "API de Monitoreo",
            "url": "/api/v1/railway/status", 
            "description": "Nuevo sistema de monitoreo"
        },
        {
            "name": "Dashboard Monitoreo",
            "url": "/railway-monitor",
            "description": "Dashboard web de monitoreo"
        },
        {
            "name": "API Métricas",
            "url": "/api/v1/railway/metrics",
            "description": "Endpoint de métricas"
        }
    ]
    
    max_checks = 10
    check_count = 0
    
    while check_count < max_checks:
        check_count += 1
        current_time = datetime.now().strftime('%H:%M:%S')
        
        print(f"🔍 Check #{check_count}/10 - {current_time}")
        print("-" * 30)
        
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                
                for check in checks:
                    url = f"{railway_url}{check['url']}"
                    
                    try:
                        async with session.get(url) as resp:
                            status = resp.status
                            
                            if status == 200:
                                print(f"   ✅ {check['name']}: OK ({status})")
                                
                                # Para algunos endpoints, mostrar datos
                                if 'api' in check['url']:
                                    try:
                                        data = await resp.json()
                                        if 'timestamp' in data:
                                            print(f"      📊 Timestamp: {data['timestamp']}")
                                        if 'system_status' in data:
                                            print(f"      🎯 Status: {data['system_status']}")
                                    except:
                                        pass
                                        
                            elif status == 404:
                                print(f"   ⏳ {check['name']}: No disponible aún ({status})")
                            elif status >= 500:
                                print(f"   ❌ {check['name']}: Error del servidor ({status})")
                            else:
                                print(f"   ⚠️  {check['name']}: Estado {status}")
                                
                    except asyncio.TimeoutError:
                        print(f"   ⏰ {check['name']}: Timeout")
                    except Exception as e:
                        print(f"   ❌ {check['name']}: Error - {str(e)[:50]}")
                
        except Exception as e:
            print(f"❌ Error general: {e}")
        
        print()
        
        # Verificar si el deploy está completo
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{railway_url}/api/v1/railway/status") as resp:
                    if resp.status == 200:
                        print("🎉 ¡DEPLOY COMPLETADO EXITOSAMENTE!")
                        print("✅ Nuevo sistema de monitoreo está funcionando")
                        print(f"🔗 Dashboard disponible: {railway_url}/railway-monitor")
                        return True
        except:
            pass
        
        if check_count < max_checks:
            print(f"⏳ Esperando 30 segundos para el próximo check...")
            print()
            await asyncio.sleep(30)
    
    print("⏰ Monitoreo completado")
    print("💡 El deploy puede tomar unos minutos más en completarse")
    return False

async def show_final_status():
    """Mostrar estado final después del monitoreo"""
    
    print("\n🎯 ESTADO FINAL DEL DEPLOY")
    print("=" * 40)
    
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Verificar sistema principal
            async with session.get(f"{railway_url}/debug") as resp:
                if resp.status == 200:
                    print("✅ Sistema principal: FUNCIONANDO")
                else:
                    print("❌ Sistema principal: CON PROBLEMAS")
            
            # Verificar nuevos endpoints
            async with session.get(f"{railway_url}/api/v1/railway/status") as resp:
                if resp.status == 200:
                    print("✅ API de monitoreo: DESPLEGADA")
                    data = await resp.json()
                    print(f"   📊 Version: {data.get('version', 'N/A')}")
                    print(f"   🌍 Environment: {data.get('environment', 'N/A')}")
                else:
                    print("⏳ API de monitoreo: AÚN NO DISPONIBLE")
            
            # Verificar dashboard
            async with session.get(f"{railway_url}/railway-monitor") as resp:
                if resp.status == 200:
                    print("✅ Dashboard: DISPONIBLE")
                    print(f"   🔗 {railway_url}/railway-monitor")
                else:
                    print("⏳ Dashboard: AÚN NO DISPONIBLE")
                    
    except Exception as e:
        print(f"❌ Error verificando estado: {e}")
    
    print("\n💡 ENLACES ÚTILES:")
    print(f"   🏠 App principal: {railway_url}")
    print(f"   📊 Dashboard monitoreo: {railway_url}/railway-monitor") 
    print(f"   🔍 Debug: {railway_url}/debug")
    print(f"   📈 API status: {railway_url}/api/v1/railway/status")

async def main():
    """Función principal"""
    
    print("🚀 RAILWAY DEPLOYMENT MONITOR")
    print("=" * 50)
    print("Monitoreando el deploy de los nuevos cambios...")
    print()
    
    # Monitorear deploy
    completed = await monitor_railway_deploy()
    
    # Mostrar estado final
    await show_final_status()
    
    if completed:
        print("\n🎊 ¡Deploy completado exitosamente!")
    else:
        print("\n⏳ Deploy aún en progreso - verifica en unos minutos")

if __name__ == "__main__":
    asyncio.run(main())

