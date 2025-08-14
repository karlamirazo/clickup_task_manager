#!/usr/bin/env python3
import sqlite3
import os

# Verificar si el archivo de BD existe
db_path = 'clickup_manager.db'
if not os.path.exists(db_path):
    print(f"❌ Base de datos no encontrada: {db_path}")
    exit(1)

print(f"✅ Base de datos encontrada: {db_path}")
print(f"   Tamaño: {os.path.getsize(db_path)} bytes")

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar tablas disponibles
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"\nTablas disponibles ({len(tables)}):")
for table in tables:
    print(f"  - {table[0]}")

# Verificar estructura de cada tabla
for table in tables:
    table_name = table[0]
    print(f"\n📋 Estructura de tabla '{table_name}':")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Contar registros
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"  Registros: {count}")

conn.close()
