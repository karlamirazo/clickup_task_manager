#!/usr/bin/env python3
"""
Script para inicializar la base de datos
"""

import sys
import os
import asyncio
sys.path.insert(0, os.getcwd())

from core.database import init_db, engine
from sqlalchemy import text

async def force_init_db():
    """Forzar la inicialización de la base de datos"""
    print("🔧 Inicializando base de datos...")
    
    try:
        # Verificar si el archivo de BD existe
        db_path = 'clickup_manager.db'
        if os.path.exists(db_path):
            print(f"📁 Base de datos existente: {db_path}")
            print(f"   Tamaño actual: {os.path.getsize(db_path)} bytes")
        
        # Inicializar la base de datos
        await init_db()
        
        # Verificar que se crearon las tablas
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            
            print(f"\n✅ Base de datos inicializada correctamente")
            print(f"📋 Tablas creadas ({len(tables)}):")
            for table in tables:
                print(f"   - {table}")
            
            # Verificar tamaño del archivo
            if os.path.exists(db_path):
                print(f"\n📊 Tamaño final: {os.path.getsize(db_path)} bytes")
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(force_init_db())
