#!/usr/bin/env python3
"""
Script para monitorear continuamente el deployment de Railway
"""

import requests
import json
import time
from datetime import datetime

def check_endpoint_version():
    """Verificar si el endpoint ya está usando la versión mejorada"""
    try:
        response = requests.post('https://clickuptaskmanager-production.up.railway.app/api/init-db', timeout=15)
        if response.status_code == 200:
            data = response.json()
            # Verificar si es la versión mejorada (debe tener más campos)
            if 'before_tables' in data and 'after_tables' in data:
                return True, data
            else:
                return False, data
        else:
            return False, None
    except Exception as e:
        return False, None

def monitor_railway_deployment():
    """Monitorear el deployment de Railway"""
    print("🚀 MONITOREANDO DEPLOYMENT DE RAILWAY")
    print("=" * 60)
    
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    print(f"🔗 URL: {railway_url}")
    
    check_count = 0
    start_time = datetime.now()
    
    while True:
        check_count += 1
        current_time = datetime.now()
        elapsed = (current_time - start_time).total_seconds() / 60
        
        print(f"\n🕐 Verificación #{check_count} - {current_time.strftime('%H:%M:%S')} (Elapsed: {elapsed:.1f} min)")
        
        # Verificar si el endpoint ya está usando la versión mejorada
        is_updated, response_data = check_endpoint_version()
        
        if is_updated:
            print("🎉 ¡DEPLOYMENT COMPLETADO!")
            print("✅ El endpoint ya está usando la versión mejorada")
            print("\n📊 INFORMACIÓN DETALLADA:")
            print(json.dumps(response_data, indent=2))
            
            # Verificar si la base de datos se inicializó correctamente
            if response_data.get('notification_type_exists'):
                print("\n✅ ¡PROBLEMA RESUELTO!")
                print("   La columna notification_type ya existe")
                print("   El dashboard debería funcionar correctamente")
            else:
                print("\n❌ PROBLEMA PERSISTE")
                print("   La columna notification_type aún no existe")
                print("   Necesitamos investigar más")
            
            break
        else:
            print("⏳ Deployment aún en progreso...")
            if response_data:
                print(f"   Respuesta actual: {response_data.get('message', 'N/A')}")
            
            # Verificar si hay algún cambio en el sistema
            try:
                debug_response = requests.get(f"{railway_url}/debug", timeout=10)
                if debug_response.status_code == 200:
                    debug_data = debug_response.json()
                    print(f"   🌍 ENVIRONMENT: {debug_data.get('configuration', {}).get('ENVIRONMENT', 'N/A')}")
                    print(f"   🗄️  Base de datos: {debug_data.get('database', {}).get('database_status', 'N/A')}")
            except:
                pass
            
            print(f"   ⏰ Esperando 30 segundos...")
            time.sleep(30)
            
            # Si han pasado más de 10 minutos, sugerir verificar manualmente
            if elapsed > 10:
                print(f"\n⚠️ Han pasado {elapsed:.1f} minutos")
                print("💡 Considera verificar manualmente en Railway si el deployment está tardando mucho")
                print("   - Ve a Railway Dashboard")
                print("   - Ve a tu proyecto")
                print("   - Verifica el estado del deployment")
                print("   - Revisa los logs si hay errores")

def main():
    """Función principal"""
    print(f"🕐 Iniciando monitoreo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("💡 Este script monitoreará continuamente hasta que Railway aplique los cambios")
    print("   Presiona Ctrl+C para detener el monitoreo")
    
    try:
        monitor_railway_deployment()
    except KeyboardInterrupt:
        print("\n\n⏹️ Monitoreo detenido por el usuario")
        print("💡 Puedes ejecutar el script nuevamente más tarde")
    except Exception as e:
        print(f"\n❌ Error durante el monitoreo: {e}")

if __name__ == "__main__":
    main()
