#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Probando conexión a la base de datos...")
    
    # Importar configuración
    from core.config import settings
    print(f"✅ Configuración cargada: {settings.DATABASE_URL}")
    
    # Importar base de datos
    from core.database import init_db, get_db
    print("✅ Módulo de base de datos importado")
    
    # Inicializar base de datos
    print("🔄 Inicializando base de datos...")
    init_db()
    print("✅ Base de datos inicializada")
    
    # Probar conexión
    print("🔄 Probando conexión...")
    db = next(get_db())
    
    # Hacer una consulta simple
    from sqlalchemy import text
    result = db.execute(text("SELECT COUNT(*) FROM tasks"))
    task_count = result.scalar()
    print(f"✅ Conexión exitosa: {task_count} tareas en la base de datos")
    
    # Cerrar conexión
    db.close()
    print("✅ Conexión cerrada correctamente")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
