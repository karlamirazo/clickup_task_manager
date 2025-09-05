#!/usr/bin/env python3
"""
Script para actualizar imports después de la migración
"""

import os
import re
from pathlib import Path

# Mapeo de imports antiguos a nuevos
IMPORT_MAPPINGS = {
    # Core imports
    "from auth.auth import": "from auth.auth import",
    "import auth.auth": "import auth.auth",
    
    # ClickUp integration
    "from integrations.clickup.client import": "from integrations.clickup.client import",
    "import integrations.clickup.client": "import integrations.clickup.client",
    "from integrations.clickup.webhook_manager import": "from integrations.clickup.webhook_manager import",
    "import integrations.clickup.webhook_manager": "import integrations.clickup.webhook_manager",
    "from integrations.clickup.sync import": "from integrations.clickup.sync import",
    "import integrations.clickup.sync": "import integrations.clickup.sync",
    "from integrations.clickup.simple_sync import": "from integrations.clickup.simple_sync import",
    "import integrations.clickup.simple_sync": "import integrations.clickup.simple_sync",
    
    # WhatsApp integration
    "from integrations.whatsapp.client import": "from integrations.whatsapp.client import",
    "import integrations.whatsapp.client": "import integrations.whatsapp.client",
    "from integrations.whatsapp.integrator import": "from integrations.whatsapp.integrator import",
    "import integrations.whatsapp.integrator": "import integrations.whatsapp.integrator",
    "from integrations.whatsapp.service import": "from integrations.whatsapp.service import",
    "import integrations.whatsapp.service": "import integrations.whatsapp.service",
    "from integrations.whatsapp.production_service import": "from integrations.whatsapp.production_service import",
    "import integrations.whatsapp.production_service": "import integrations.whatsapp.production_service",
    "from integrations.whatsapp.simulator import": "from integrations.whatsapp.simulator import",
    "import integrations.whatsapp.simulator": "import integrations.whatsapp.simulator",
    "from integrations.whatsapp.simulator_config import": "from integrations.whatsapp.simulator_config import",
    "import integrations.whatsapp.simulator_config": "import integrations.whatsapp.simulator_config",
    
    # Evolution API integration
    "from integrations.evolution_api.config import": "from integrations.evolution_api.config import",
    "import integrations.evolution_api.config": "import integrations.evolution_api.config",
    "from integrations.evolution_api.webhook_manager import": "from integrations.evolution_api.webhook_manager import",
    "import integrations.evolution_api.webhook_manager": "import integrations.evolution_api.webhook_manager",
    
    # Railway monitoring
    "from monitoring.railway.log_monitor import": "from monitoring.railway.log_monitor import",
    "import monitoring.railway.log_monitor": "import monitoring.railway.log_monitor",
    "from monitoring.railway.alerts import": "from monitoring.railway.alerts import",
    "import monitoring.railway.alerts": "import monitoring.railway.alerts",
    
    # Search
    "from search.engine import": "from search.engine import",
    "import search.engine": "import search.engine",
    
    # Notifications
    "from notifications.scheduler import": "from notifications.scheduler import",
    "import notifications.scheduler": "import notifications.scheduler",
    "from notifications.automated_manager import": "from notifications.automated_manager import",
    "import notifications.automated_manager": "import notifications.automated_manager",
    "from notifications.manager import": "from notifications.manager import",
    "import notifications.manager": "import notifications.manager",
    "from notifications.advanced_manager import": "from notifications.advanced_manager import",
    "import notifications.advanced_manager": "import notifications.advanced_manager",
    "from notifications.email.templates import": "from notifications.email.templates import",
    "import notifications.email.templates": "import notifications.email.templates",
}

def update_file_imports(file_path: Path) -> bool:
    """Actualiza los imports en un archivo"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Aplicar mapeos de imports
        for old_import, new_import in IMPORT_MAPPINGS.items():
            content = content.replace(old_import, new_import)
        
        # Si hubo cambios, escribir el archivo
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"  Actualizado: {file_path}")
            return True
        else:
            print(f"  Sin cambios: {file_path}")
            return False
            
    except Exception as e:
        print(f"  Error en {file_path}: {e}")
        return False

def find_python_files(directory: Path) -> list:
    """Encuentra todos los archivos Python en el directorio"""
    python_files = []
    for file_path in directory.rglob("*.py"):
        # Excluir archivos de backup y cache
        if any(exclude in str(file_path) for exclude in ['__pycache__', 'backup_', '.venv', 'venv']):
            continue
        python_files.append(file_path)
    return python_files

def main():
    """Función principal"""
    print("ACTUALIZANDO IMPORTS DESPUÉS DE MIGRACIÓN")
    print("=" * 60)
    
    project_root = Path(".")
    python_files = find_python_files(project_root)
    
    print(f"Encontrados {len(python_files)} archivos Python")
    print("Actualizando imports...")
    
    updated_count = 0
    for file_path in python_files:
        if update_file_imports(file_path):
            updated_count += 1
    
    print(f"\nActualizados {updated_count} archivos")
    print("Imports actualizados correctamente")

if __name__ == "__main__":
    main()
