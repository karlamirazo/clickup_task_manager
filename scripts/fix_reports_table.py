#!/usr/bin/env python3
"""
Script para arreglar la tabla de reportes
"""

import sys
import os
sys.path.insert(0, os.getcwd())

from core.database import engine, Base
from models.report import Report
from sqlalchemy import text

def fix_reports_table():
    """Arreglar la tabla de reportes"""
    
    print("üîß Arreglando tabla de reportes...")
    
    try:
        # Delete la tabla existente
        Report.__table__.drop(engine, checkfirst=True)
        print("‚úÖ Tabla de reportes eliminada")
        
        # Create la tabla con el nuevo esquema
        Report.__table__.create(engine, checkfirst=True)
        print("‚úÖ Tabla de reportes recreada con esquema actualizado")
        
        # Verificar que la tabla existe
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='reports'"))
            if result.fetchone():
                print("‚úÖ Tabla de reportes verificada")
            else:
                print("‚ùå Error: La tabla no se creo correctamente")
                
    except Exception as e:
        print(f"‚ùå Error arreglando tabla: {e}")

if __name__ == "__main__":
    fix_reports_table()
