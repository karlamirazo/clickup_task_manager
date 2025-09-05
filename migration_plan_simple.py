#!/usr/bin/env python3
"""
Plan de migración seguro simplificado
Solo verificación y preparación - SIN cambios que afecten funcionalidad
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

class SafeMigrationSimple:
    """Migración segura del proyecto - Solo verificación"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_before_migration"
        
    def create_backup(self) -> bool:
        """Crea backup completo del proyecto"""
        print("Creando backup del proyecto...")
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            
            # Excluir directorios que no necesitamos en el backup
            exclude_dirs = {'__pycache__', '.git', 'node_modules', 'backup_before_migration', 'logs', '.venv', 'venv'}
            
            def ignore_func(dir, files):
                return [f for f in files if f in exclude_dirs or f.startswith('.')]
            
            shutil.copytree(self.project_root, self.backup_dir, ignore=ignore_func)
            print(f"Backup creado en: {self.backup_dir}")
            return True
            
        except Exception as e:
            print(f"Error creando backup: {e}")
            return False
    
    def verify_backup(self) -> bool:
        """Verifica que el backup se creó correctamente"""
        print("Verificando backup...")
        
        critical_files = [
            "main.py",
            "core/config.py",
            "core/database.py",
            "models/task.py",
            "api/routes/tasks.py"
        ]
        
        for file_path in critical_files:
            backup_file = self.backup_dir / file_path
            if not backup_file.exists():
                print(f"Archivo critico no encontrado en backup: {file_path}")
                return False
        
        print("Backup verificado correctamente")
        return True
    
    def create_new_structure(self) -> bool:
        """Crea la nueva estructura de directorios SIN mover archivos"""
        print("Creando nueva estructura de directorios...")
        
        try:
            # Crear directorios principales
            new_dirs = [
                "app",
                "auth", 
                "integrations/clickup",
                "integrations/whatsapp",
                "integrations/evolution_api",
                "monitoring/railway",
                "monitoring/health",
                "search",
                "notifications/email",
                "notifications/whatsapp",
                "scripts/clickup",
                "scripts/whatsapp", 
                "scripts/railway",
                "scripts/database"
            ]
            
            for dir_name in new_dirs:
                new_dir = self.project_root / dir_name
                new_dir.mkdir(parents=True, exist_ok=True)
                # Crear __init__.py
                (new_dir / "__init__.py").touch()
            
            print("Nueva estructura creada (sin mover archivos)")
            return True
            
        except Exception as e:
            print(f"Error creando estructura: {e}")
            return False
    
    def test_current_imports(self) -> bool:
        """Prueba que los imports actuales funcionen"""
        print("Probando imports actuales...")
        
        try:
            # Probar imports críticos
            critical_imports = [
                "core.config",
                "core.database",
                "core.clickup_client", 
                "models.task",
                "models.user"
            ]
            
            for module in critical_imports:
                try:
                    __import__(module)
                    print(f"  OK: {module}")
                except Exception as e:
                    print(f"  ERROR: {module} - {e}")
                    return False
            
            print("Todos los imports criticos funcionan correctamente")
            return True
            
        except Exception as e:
            print(f"Error probando imports: {e}")
            return False
    
    def generate_migration_plan(self) -> Dict[str, Any]:
        """Genera un plan detallado de migración"""
        print("Generando plan de migración...")
        
        # Mapeo de archivos a nuevas ubicaciones
        file_mapping = {
            # Core files - NO MOVER
            "main.py": "app/main.py",
            "core/config.py": "core/config.py",  # Mantener en core
            "core/database.py": "core/database.py",  # Mantener en core
            
            # Auth
            "core/auth.py": "auth/auth.py",
            
            # API Routes - Mantener estructura actual
            "api/routes/tasks.py": "api/routes/tasks.py",
            "api/routes/workspaces.py": "api/routes/workspaces.py",
            "api/routes/users.py": "api/routes/users.py",
            
            # Models - Mantener estructura actual
            "models/task.py": "models/task.py",
            "models/user.py": "models/user.py",
            "models/workspace.py": "models/workspace.py",
            
            # ClickUp Integration
            "core/clickup_client.py": "integrations/clickup/client.py",
            "core/clickup_webhook_manager.py": "integrations/clickup/webhook_manager.py",
            "core/advanced_sync.py": "integrations/clickup/sync.py",
            
            # WhatsApp Integration
            "core/whatsapp_client.py": "integrations/whatsapp/client.py",
            "core/whatsapp_integrator.py": "integrations/whatsapp/integrator.py",
            "core/robust_whatsapp_service.py": "integrations/whatsapp/service.py",
            
            # Railway Monitoring
            "core/railway_log_monitor.py": "monitoring/railway/log_monitor.py",
            "core/railway_alerts.py": "monitoring/railway/alerts.py",
            
            # Search
            "core/search_engine.py": "search/engine.py",
            
            # Notifications
            "core/notification_scheduler.py": "notifications/scheduler.py",
            "utils/notifications.py": "notifications/manager.py",
            "utils/advanced_notifications.py": "notifications/advanced_manager.py",
        }
        
        return {
            "total_files": len(file_mapping),
            "file_mapping": file_mapping,
            "status": "ready"
        }
    
    def execute_verification_only(self) -> bool:
        """Ejecuta solo la verificación - SIN cambios"""
        print("=== MIGRACION SEGURA - SOLO VERIFICACION ===")
        print("=" * 60)
        
        # Paso 1: Crear backup
        if not self.create_backup():
            print("ERROR: No se pudo crear backup. Abortando.")
            return False
        
        if not self.verify_backup():
            print("ERROR: Backup no verificado. Abortando.")
            return False
        
        # Paso 2: Crear nueva estructura (solo directorios)
        if not self.create_new_structure():
            print("ERROR: No se pudo crear nueva estructura. Abortando.")
            return False
        
        # Paso 3: Probar imports actuales
        if not self.test_current_imports():
            print("ERROR: Imports actuales no funcionan. Abortando.")
            return False
        
        # Paso 4: Generar plan de migración
        plan = self.generate_migration_plan()
        
        print("\n" + "=" * 60)
        print("VERIFICACION COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print(f"Backup creado: {self.backup_dir}")
        print(f"Archivos mapeados: {plan['total_files']}")
        print("Nueva estructura creada (sin mover archivos)")
        print("Imports actuales funcionan correctamente")
        
        print("\nPROXIMOS PASOS:")
        print("1. Revisar la nueva estructura creada")
        print("2. Verificar que el backup es completo")
        print("3. Si todo esta bien, proceder con migracion fisica")
        print("4. Si hay problemas, restaurar desde backup")
        
        return True

def main():
    """Funcion principal"""
    print("MIGRACION SEGURA - ClickUp Project Manager")
    print("=" * 60)
    
    # Obtener directorio del proyecto
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"Directorio del proyecto: {project_root}")
    
    # Crear migrador
    migrator = SafeMigrationSimple(project_root)
    
    # Ejecutar solo verificacion
    success = migrator.execute_verification_only()
    
    if success:
        print("\nVERIFICACION COMPLETADA EXITOSAMENTE")
        print("El proyecto esta listo para la migracion")
    else:
        print("\nLA VERIFICACION FALLO")
        print("Revisa los errores antes de proceder")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
