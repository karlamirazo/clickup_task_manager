#!/usr/bin/env python3
"""
Script para actualizar las configuraciones de WhatsApp en Railway
"""

import subprocess
import sys

def update_railway_whatsapp_config():
    """Actualizar configuraciones de WhatsApp en Railway"""
    
    print("🔧 ACTUALIZANDO CONFIGURACIONES DE WHATSAPP EN RAILWAY")
    print("=" * 60)
    
    # Configuraciones correctas para WhatsApp
    whatsapp_configs = [
        ("WHATSAPP_ENABLED", "True"),
        ("WHATSAPP_EVOLUTION_URL", "https://evolution-api-production-9d5d.up.railway.app"),
        ("WHATSAPP_EVOLUTION_API_KEY", "clickup-evolution-v223"),
        ("WHATSAPP_INSTANCE_NAME", "clickup-v23"),
        ("WHATSAPP_WEBHOOK_URL", "https://clickuptaskmanager-production.up.railway.app/api/webhooks/whatsapp"),
        ("WHATSAPP_NOTIFICATIONS_ENABLED", "True"),
        ("WHATSAPP_SIMULATOR_ENABLED", "False"),
        ("WHATSAPP_TASK_CREATED", "True"),
        ("WHATSAPP_TASK_UPDATED", "True"),
        ("WHATSAPP_TASK_COMPLETED", "True"),
        ("WHATSAPP_TASK_DUE_SOON", "True"),
        ("WHATSAPP_TASK_OVERDUE", "True"),
    ]
    
    print("📋 Configuraciones a actualizar:")
    for var_name, var_value in whatsapp_configs:
        print(f"   {var_name} = {var_value}")
    
    print(f"\n🚀 Actualizando variables en Railway...")
    
    success_count = 0
    error_count = 0
    
    for var_name, var_value in whatsapp_configs:
        try:
            # Comando para actualizar variable en Railway
            cmd = f'railway variables --set "{var_name}={var_value}"'
            print(f"📝 Actualizando {var_name}...")
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {var_name} = {var_value}")
                success_count += 1
            else:
                print(f"❌ Error actualizando {var_name}: {result.stderr}")
                error_count += 1
                
        except Exception as e:
            print(f"❌ Excepción actualizando {var_name}: {e}")
            error_count += 1
    
    print(f"\n📊 RESUMEN:")
    print(f"   ✅ Exitosos: {success_count}")
    print(f"   ❌ Errores: {error_count}")
    
    if error_count == 0:
        print(f"\n🎉 ¡Todas las configuraciones actualizadas exitosamente!")
        print(f"🚀 Railway debería reiniciar automáticamente con las nuevas configuraciones")
        print(f"\n🎯 PRÓXIMOS PASOS:")
        print(f"1. Esperar que Railway reinicie la aplicación")
        print(f"2. Probar crear una nueva tarea")
        print(f"3. Verificar que llegue la notificación de WhatsApp")
    else:
        print(f"\n⚠️  Algunas configuraciones fallaron")
        print(f"🔍 Verificar que Railway CLI esté instalado y configurado")
        print(f"💡 Comando para instalar: npm install -g @railway/cli")
        print(f"💡 Comando para login: railway login")
    
    return error_count == 0

def check_railway_cli():
    """Verificar si Railway CLI está instalado"""
    try:
        result = subprocess.run("railway --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Railway CLI instalado: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Railway CLI no encontrado")
            return False
    except Exception as e:
        print(f"❌ Error verificando Railway CLI: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 ACTUALIZADOR DE CONFIGURACIONES WHATSAPP EN RAILWAY")
    print("=" * 60)
    
    # Verificar Railway CLI
    if not check_railway_cli():
        print(f"\n❌ Railway CLI no está instalado")
        print(f"📥 Instalar con: npm install -g @railway/cli")
        print(f"🔑 Login con: railway login")
        return False
    
    # Actualizar configuraciones
    success = update_railway_whatsapp_config()
    
    return success

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
