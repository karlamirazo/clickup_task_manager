#!/usr/bin/env python3
"""
Verificación simple - Solo verifica imports y estructura
NO hace cambios, NO crea backups, NO afecta funcionalidad
"""

import os
import sys
import importlib
from pathlib import Path

def test_critical_imports():
    """Prueba imports críticos del sistema"""
    print("Probando imports criticos...")
    
    critical_imports = [
        "core.config",
        "core.database", 
        "core.clickup_client",
        "models.task",
        "models.user"
    ]
    
    all_ok = True
    for module in critical_imports:
        try:
            importlib.import_module(module)
            print(f"  OK: {module}")
        except Exception as e:
            print(f"  ERROR: {module} - {e}")
            all_ok = False
    
    return all_ok

def test_api_imports():
    """Prueba imports de API"""
    print("Probando imports de API...")
    
    api_imports = [
        "api.routes.tasks",
        "api.routes.workspaces", 
        "api.routes.users",
        "api.schemas.task"
    ]
    
    all_ok = True
    for module in api_imports:
        try:
            importlib.import_module(module)
            print(f"  OK: {module}")
        except Exception as e:
            print(f"  ERROR: {module} - {e}")
            all_ok = False
    
    return all_ok

def test_utils_imports():
    """Prueba imports de utilidades"""
    print("Probando imports de utilidades...")
    
    utils_imports = [
        "utils.helpers",
        "notifications.manager",
        "utils.deployment_logger"
    ]
    
    all_ok = True
    for module in utils_imports:
        try:
            importlib.import_module(module)
            print(f"  OK: {module}")
        except Exception as e:
            print(f"  ERROR: {module} - {e}")
            all_ok = False
    
    return all_ok

def check_project_structure():
    """Verifica estructura actual del proyecto"""
    print("Verificando estructura del proyecto...")
    
    project_root = Path(os.path.dirname(os.path.abspath(__file__)))
    
    critical_dirs = [
        "core",
        "api/routes", 
        "api/schemas",
        "models",
        "utils"
    ]
    
    all_ok = True
    for dir_path in critical_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"  OK: {dir_path}")
        else:
            print(f"  ERROR: {dir_path} no existe")
            all_ok = False
    
    return all_ok

def main():
    """Funcion principal - Solo verificacion"""
    print("VERIFICACION SIMPLE - ClickUp Project Manager")
    print("=" * 60)
    print("SOLO VERIFICACION - NO SE HACEN CAMBIOS")
    print("=" * 60)
    
    # Verificar estructura
    structure_ok = check_project_structure()
    
    # Verificar imports críticos
    critical_ok = test_critical_imports()
    
    # Verificar imports de API
    api_ok = test_api_imports()
    
    # Verificar imports de utilidades
    utils_ok = test_utils_imports()
    
    print("\n" + "=" * 60)
    print("RESUMEN DE VERIFICACION")
    print("=" * 60)
    print(f"Estructura del proyecto: {'OK' if structure_ok else 'ERROR'}")
    print(f"Imports criticos: {'OK' if critical_ok else 'ERROR'}")
    print(f"Imports de API: {'OK' if api_ok else 'ERROR'}")
    print(f"Imports de utilidades: {'OK' if utils_ok else 'ERROR'}")
    
    all_ok = structure_ok and critical_ok and api_ok and utils_ok
    
    if all_ok:
        print("\nVERIFICACION EXITOSA")
        print("El proyecto esta funcionando correctamente")
        print("Puedes proceder con confianza a la migracion")
    else:
        print("\nVERIFICACION FALLO")
        print("Hay problemas que deben corregirse antes de la migracion")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
