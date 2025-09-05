#!/usr/bin/env python3
"""
Script para actualizar configuración a Evolution API v2.2.3
Ejecutar cuando tengas la nueva URL de Railway
"""

import subprocess
import sys

def update_railway_config():
    """Actualizar variables de Railway para usar Evolution API v2.2.3"""
    
    # URL que obtendrás de Railway (REEMPLAZA CON LA TUYA)
    new_evolution_url = "TU_NUEVA_URL_AQUI"  # Ej: https://evolution-v223-production.up.railway.app
    new_api_key = "clickup-whatsapp-v223"
    
    print("🔧 ACTUALIZANDO CONFIGURACIÓN PARA EVOLUTION API v2.2.3")
    print("=" * 60)
    
    updates = [
        ("WHATSAPP_EVOLUTION_URL", new_evolution_url),
        ("WHATSAPP_EVOLUTION_API_KEY", new_api_key),
        ("WHATSAPP_INSTANCE_NAME", "clickup-main"),  # Nombre limpio para nueva instancia
        ("WHATSAPP_SIMULATOR_ENABLED", "false")      # Usar WhatsApp real
    ]
    
    for var_name, var_value in updates:
        try:
            cmd = f'railway variables --set "{var_name}={var_value}"'
            print(f"📝 Actualizando {var_name}...")
            subprocess.run(cmd, shell=True, check=True)
            print(f"✅ {var_name} = {var_value}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error actualizando {var_name}: {e}")
    
    print("\n🎯 SIGUIENTE PASO:")
    print("1. Ve al nuevo manager: " + new_evolution_url + "/manager")
    print("2. Login con API Key: " + new_api_key)
    print("3. Crea instancia: clickup-main")
    print("4. ¡Escanea el QR!")

if __name__ == "__main__":
    print("⚠️  ANTES DE EJECUTAR:")
    print("1. Reemplaza 'TU_NUEVA_URL_AQUI' con tu URL real de Railway")
    print("2. Asegúrate de que el deploy esté completo")
    print("\n¿Continuar? (y/n)")
    
    response = input().lower()
    if response == 'y':
        update_railway_config()
    else:
        print("Cancelado. Edita el script cuando tengas la URL lista.")
