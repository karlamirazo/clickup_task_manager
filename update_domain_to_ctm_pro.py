#!/usr/bin/env python3
"""
Script para actualizar MASIVAMENTE el dominio antiguo al nuevo dominio ctm-pro.up.railway.app
"""

import os
import re
from datetime import datetime

def print_header():
    """Imprimir cabecera del script"""
    print("=" * 80)
    print("🌐 ACTUALIZACIÓN MASIVA DE DOMINIO A CTM-PRO.UP.RAILWAY.APP")
    print("=" * 80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def update_file_domain(file_path, old_domain, new_domain):
    """Actualizar dominio en un archivo específico"""
    try:
        # Leer contenido actual
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar si contiene el dominio antiguo
        if old_domain in content:
            # Reemplazar todas las ocurrencias
            updated_content = content.replace(old_domain, new_domain)
            
            # Escribir archivo actualizado
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            return True
        
        return False
        
    except Exception as e:
        print(f"   ❌ Error procesando {file_path}: {e}")
        return False

def get_files_to_update():
    """Obtener lista de archivos importantes a actualizar"""
    important_files = [
        # Archivos de configuración principales
        'core/config.py',
        'api/routes/simple_auth.py',
        'api/routes/simple_auth_fixed.py',
        
        # Archivos de entorno
        'env.production',
        'env.oauth.simple',
        '.env',
        
        # Scripts principales (no backups)
        'setup_oauth.py',
        'fix_oauth_redirect_final.py',
        'fix_url_corta.py',
        
        # Archivos de deploy
        'deploy_now.bat',
        'deploy_fix.bat',
        'final_deploy.bat',
        
        # Scripts de configuración activos
        'configure_oauth_production.py',
        'setup_railway_oauth_final.py',
        
        # Dashboards y monitoreo activos
        'static/railway_dashboard.html',
        'api/routes/railway_monitor.py',
        'scripts/railway/monitor_railway_status.py',
        'monitoring/railway/log_monitor.py',
        
        # Documentación
        'WHATSAPP_FIX_SUMMARY.md',
        'README.md'
    ]
    
    # Filtrar solo archivos que existen
    existing_files = []
    for file_path in important_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
    
    return existing_files

def main():
    """Función principal"""
    print_header()
    
    # Dominios
    old_domain = "clickuptaskmanager-production.up.railway.app"
    new_domain = "ctm-pro.up.railway.app"
    
    print(f"🔄 CAMBIANDO DOMINIO:")
    print(f"   Anterior: {old_domain}")
    print(f"   Nuevo: {new_domain}")
    print()
    
    # Obtener archivos a actualizar
    files_to_update = get_files_to_update()
    
    print(f"📁 ARCHIVOS A PROCESAR: {len(files_to_update)}")
    print("-" * 60)
    
    updated_count = 0
    
    for file_path in files_to_update:
        print(f"📄 Procesando: {file_path}")
        
        if update_file_domain(file_path, old_domain, new_domain):
            print(f"   ✅ Actualizado")
            updated_count += 1
        else:
            print(f"   ℹ️ No necesita cambios")
    
    print()
    print("-" * 60)
    print(f"✅ ARCHIVOS ACTUALIZADOS: {updated_count}")
    print(f"📁 ARCHIVOS PROCESADOS: {len(files_to_update)}")
    
    print("\n🎯 NUEVA URL DE OAUTH PARA CLICKUP:")
    print(f"   📍 https://{new_domain}/callback")
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. 🔧 Hacer commit y push de estos cambios")
    print("2. 🌐 Actualizar ClickUp con la nueva URL:")
    print(f"   https://{new_domain}/callback")
    print("3. 🚀 Probar el OAuth con el nuevo dominio")
    
    print("\n" + "=" * 80)
    print("✅ ACTUALIZACIÓN DE DOMINIO COMPLETADA")
    print("=" * 80)

if __name__ == "__main__":
    main()
