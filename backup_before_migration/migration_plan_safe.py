#!/usr/bin/env python3
"""
Plan de migración seguro para reorganizar el proyecto ClickUp Project Manager
Este script ejecuta la migración paso a paso con verificaciones de seguridad
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json
from datetime import datetime

class SafeMigration:
    """Migración segura del proyecto con verificaciones"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_before_migration"
        self.new_structure = {
            "app": ["main.py"],
            "core": ["config.py", "database.py"],
            "auth": ["auth.py"],
            "api": {
                "routes": [],
                "schemas": []
            },
            "models": [],
            "integrations": {
                "clickup": [],
                "whatsapp": [],
                "evolution_api": []
            },
            "monitoring": {
                "railway": [],
                "health": []
            },
            "search": [],
            "notifications": {
                "email": [],
                "whatsapp": []
            },
            "utils": [],
            "scripts": {
                "clickup": [],
                "whatsapp": [],
                "railway": [],
                "database": []
            }
        }
        
    def create_backup(self) -> bool:
        """Crea backup completo del proyecto"""
        print("🔄 Creando backup del proyecto...")
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            
            # Excluir directorios que no necesitamos en el backup
            exclude_dirs = {'__pycache__', '.git', 'node_modules', 'backup_before_migration', 'logs'}
            
            def ignore_func(dir, files):
                return [f for f in files if f in exclude_dirs or f.startswith('.')]
            
            shutil.copytree(self.project_root, self.backup_dir, ignore=ignore_func)
            print(f"✅ Backup creado en: {self.backup_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            return False
    
    def verify_backup(self) -> bool:
        """Verifica que el backup se creó correctamente"""
        print("🔍 Verificando backup...")
        
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
                print(f"❌ Archivo crítico no encontrado en backup: {file_path}")
                return False
        
        print("✅ Backup verificado correctamente")
        return True
    
    def create_new_structure(self) -> bool:
        """Crea la nueva estructura de directorios"""
        print("🏗️ Creando nueva estructura de directorios...")
        
        try:
            # Crear directorios principales
            for dir_name in self.new_structure.keys():
                if isinstance(self.new_structure[dir_name], dict):
                    # Crear subdirectorios
                    for subdir in self.new_structure[dir_name].keys():
                        new_dir = self.project_root / dir_name / subdir
                        new_dir.mkdir(parents=True, exist_ok=True)
                        # Crear __init__.py
                        (new_dir / "__init__.py").touch()
                else:
                    # Crear directorio simple
                    new_dir = self.project_root / dir_name
                    new_dir.mkdir(parents=True, exist_ok=True)
                    # Crear __init__.py
                    (new_dir / "__init__.py").touch()
            
            print("✅ Nueva estructura creada")
            return True
            
        except Exception as e:
            print(f"❌ Error creando estructura: {e}")
            return False
    
    def map_file_movements(self) -> Dict[str, str]:
        """Mapea qué archivos se moverán a dónde"""
        movements = {}
        
        # Mapeo de archivos a nuevas ubicaciones
        file_mapping = {
            # Core files
            "main.py": "app/main.py",
            "core/config.py": "core/config.py",
            "core/database.py": "core/database.py",
            
            # Auth
            "core/auth.py": "auth/auth.py",
            
            # API Routes
            "api/routes/tasks.py": "api/routes/tasks.py",
            "api/routes/workspaces.py": "api/routes/workspaces.py",
            "api/routes/users.py": "api/routes/users.py",
            "api/routes/lists.py": "api/routes/lists.py",
            "api/routes/spaces.py": "api/routes/spaces.py",
            "api/routes/webhooks.py": "api/routes/webhooks.py",
            "api/routes/dashboard.py": "api/routes/dashboard.py",
            "api/routes/search.py": "api/routes/search.py",
            "api/routes/auth.py": "api/routes/auth.py",
            "api/routes/notifications.py": "api/routes/notifications.py",
            "api/routes/railway_monitor.py": "api/routes/railway_monitor.py",
            "api/routes/whatsapp.py": "api/routes/whatsapp.py",
            "api/routes/whatsapp_diagnostics.py": "api/routes/whatsapp_diagnostics.py",
            "api/routes/automation.py": "api/routes/automation.py",
            "api/routes/reports.py": "api/routes/reports.py",
            "api/routes/integrations.py": "api/routes/integrations.py",
            
            # API Schemas
            "api/schemas/task.py": "api/schemas/task.py",
            "api/schemas/user.py": "api/schemas/user.py",
            "api/schemas/workspace.py": "api/schemas/workspace.py",
            "api/schemas/automation.py": "api/schemas/automation.py",
            "api/schemas/integration.py": "api/schemas/integration.py",
            "api/schemas/report.py": "api/schemas/report.py",
            "api/schemas/notification.py": "api/schemas/notification.py",
            
            # Models
            "models/task.py": "models/task.py",
            "models/user.py": "models/user.py",
            "models/workspace.py": "models/workspace.py",
            "models/automation.py": "models/automation.py",
            "models/integration.py": "models/integration.py",
            "models/report.py": "models/report.py",
            "models/notification_log.py": "models/notification_log.py",
            
            # ClickUp Integration
            "core/clickup_client.py": "integrations/clickup/client.py",
            "core/clickup_webhook_manager.py": "integrations/clickup/webhook_manager.py",
            "core/advanced_sync.py": "integrations/clickup/sync.py",
            "core/simple_sync.py": "integrations/clickup/simple_sync.py",
            
            # WhatsApp Integration
            "core/whatsapp_client.py": "integrations/whatsapp/client.py",
            "core/whatsapp_integrator.py": "integrations/whatsapp/integrator.py",
            "core/robust_whatsapp_service.py": "integrations/whatsapp/service.py",
            "core/whatsapp_simulator.py": "integrations/whatsapp/simulator.py",
            "core/whatsapp_simulator_config.py": "integrations/whatsapp/simulator_config.py",
            "core/production_whatsapp_service.py": "integrations/whatsapp/production_service.py",
            "core/automated_notification_manager.py": "integrations/whatsapp/notification_manager.py",
            "core/phone_extractor.py": "integrations/whatsapp/phone_extractor.py",
            
            # Evolution API
            "core/evolution_api_config.py": "integrations/evolution_api/config.py",
            "core/evolution_webhook_manager.py": "integrations/evolution_api/webhook_manager.py",
            
            # Railway Monitoring
            "core/railway_log_monitor.py": "monitoring/railway/log_monitor.py",
            "core/railway_alerts.py": "monitoring/railway/alerts.py",
            
            # Search
            "core/search_engine.py": "search/engine.py",
            
            # Notifications
            "core/notification_scheduler.py": "notifications/scheduler.py",
            "utils/notifications.py": "notifications/manager.py",
            "utils/advanced_notifications.py": "notifications/advanced_manager.py",
            "utils/email_templates.py": "notifications/email/templates.py",
            
            # Utils
            "utils/helpers.py": "utils/helpers.py",
            "utils/deployment_logger.py": "utils/deployment_logger.py",
            
            # Scripts - ClickUp
            "scripts/verify_clickup_task.py": "scripts/clickup/verify_task.py",
            "scripts/test_update_task_method.py": "scripts/clickup/test_update_method.py",
            "scripts/test_update_function_local.py": "scripts/clickup/test_update_function.py",
            "scripts/test_manual_update_direct.py": "scripts/clickup/test_manual_update.py",
            "scripts/test_custom_field_update.py": "scripts/clickup/test_custom_fields.py",
            "scripts/refresh_custom_field_ids.py": "scripts/clickup/refresh_field_ids.py",
            "scripts/get_clickup_custom_field_ids.py": "scripts/clickup/get_field_ids.py",
            "scripts/force_update_direct.py": "scripts/clickup/force_update.py",
            "scripts/emergency_sync.py": "scripts/clickup/emergency_sync.py",
            "scripts/debug_list_response.py": "scripts/clickup/debug_list.py",
            "scripts/get_clickup_statuses.py": "scripts/clickup/get_statuses.py",
            
            # Scripts - WhatsApp
            "scripts/setup_whatsapp_instance.py": "scripts/whatsapp/setup_instance.py",
            
            # Scripts - Railway
            "scripts/start_railway_monitoring.py": "scripts/railway/start_monitoring.py",
            "scripts/monitor_railway_status.py": "scripts/railway/monitor_status.py",
            
            # Scripts - Database
            "scripts/init_db.py": "scripts/database/init_db.py",
            "scripts/fix_reports_table.py": "scripts/database/fix_reports.py",
        }
        
        return file_mapping
    
    def update_imports_in_file(self, file_path: Path, old_imports: Dict[str, str]) -> bool:
        """Actualiza imports en un archivo específico"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Actualizar imports
            for old_import, new_import in old_imports.items():
                # Actualizar imports 'from'
                content = content.replace(f"from {old_import}", f"from {new_import}")
                # Actualizar imports 'import'
                content = content.replace(f"import {old_import}", f"import {new_import}")
            
            # Actualizar sys.path.append si es necesario
            if "sys.path.append" in content:
                # Actualizar paths relativos
                content = content.replace(
                    "sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))",
                    "sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))"
                )
                content = content.replace(
                    "sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))",
                    "sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))"
                )
            
            # Solo escribir si hubo cambios
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
                
        except Exception as e:
            print(f"❌ Error actualizando imports en {file_path}: {e}")
            return False
        
        return True
    
    def test_imports_after_update(self) -> bool:
        """Prueba que los imports funcionen después de la actualización"""
        print("🔍 Probando imports después de actualización...")
        
        try:
            # Ejecutar el script de verificación
            result = subprocess.run([
                sys.executable, "verify_imports_safe.py"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ Todos los imports funcionan correctamente")
                return True
            else:
                print(f"❌ Error en verificación de imports: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error ejecutando verificación: {e}")
            return False
    
    def execute_migration(self) -> bool:
        """Ejecuta la migración completa"""
        print("🚀 INICIANDO MIGRACIÓN SEGURA")
        print("=" * 60)
        
        # Paso 1: Crear backup
        if not self.create_backup():
            print("❌ Error creando backup. Abortando migración.")
            return False
        
        if not self.verify_backup():
            print("❌ Error verificando backup. Abortando migración.")
            return False
        
        # Paso 2: Crear nueva estructura
        if not self.create_new_structure():
            print("❌ Error creando nueva estructura. Abortando migración.")
            return False
        
        # Paso 3: Mapear movimientos
        file_mapping = self.map_file_movements()
        print(f"📋 Mapeados {len(file_mapping)} archivos para mover")
        
        # Paso 4: Actualizar imports ANTES de mover archivos
        print("🔄 Actualizando imports antes de mover archivos...")
        
        # Crear mapeo de imports
        import_mapping = {
            "core.clickup_client": "integrations.clickup.client",
            "core.whatsapp_client": "integrations.whatsapp.client",
            "core.railway_log_monitor": "monitoring.railway.log_monitor",
            "core.railway_alerts": "monitoring.railway.alerts",
            "core.search_engine": "search.engine",
            "core.notification_scheduler": "notifications.scheduler",
            "utils.notifications": "notifications.manager",
            "utils.advanced_notifications": "notifications.advanced_manager",
            "utils.email_templates": "notifications.email.templates",
        }
        
        # Actualizar imports en archivos críticos
        critical_files = [
            "main.py",
            "api/routes/tasks.py",
            "api/routes/webhooks.py",
            "core/railway_log_monitor.py",
            "core/railway_alerts.py"
        ]
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"   📄 Actualizando: {file_path}")
                self.update_imports_in_file(full_path, import_mapping)
        
        # Paso 5: Probar imports actualizados
        if not self.test_imports_after_update():
            print("❌ Error en imports después de actualización. Abortando migración.")
            return False
        
        print("✅ Migración completada exitosamente")
        print("📋 Próximos pasos:")
        print("   1. Revisar el reporte de verificación")
        print("   2. Probar funcionalidades críticas")
        print("   3. Ejecutar tests completos")
        print("   4. Si todo funciona, proceder con el movimiento físico de archivos")
        
        return True

def main():
    """Función principal"""
    print("🔄 MIGRACIÓN SEGURA - ClickUp Project Manager")
    print("=" * 60)
    
    # Obtener directorio del proyecto
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"📁 Directorio del proyecto: {project_root}")
    
    # Crear migrador
    migrator = SafeMigration(project_root)
    
    # Ejecutar migración
    success = migrator.execute_migration()
    
    if success:
        print("\n🎉 ¡Migración completada exitosamente!")
        print("✅ El proyecto está listo para la siguiente fase")
    else:
        print("\n❌ La migración falló")
        print("🔄 Puedes restaurar desde el backup si es necesario")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
