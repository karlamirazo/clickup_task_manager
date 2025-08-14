#!/usr/bin/env python3
import sqlite3
import json

# Conectar a la base de datos
conn = sqlite3.connect('clickup_manager.db')
cursor = conn.cursor()

# Obtener el reporte más reciente
cursor.execute("SELECT id, name, report_type, workspace_id, data, status FROM reports ORDER BY id DESC LIMIT 1")
report = cursor.fetchone()

if report:
    report_id, name, report_type, workspace_id, data, status = report
    print(f"📊 Reporte más reciente:")
    print(f"  ID: {report_id}")
    print(f"  Nombre: {name}")
    print(f"  Tipo: {report_type}")
    print(f"  Workspace: {workspace_id}")
    print(f"  Estado: {status}")
    
    if data:
        try:
            data_dict = json.loads(data)
            print(f"  Datos:")
            for key, value in data_dict.items():
                print(f"    {key}: {value}")
        except:
            print(f"  Datos: {data}")
    else:
        print(f"  Datos: None")
else:
    print("No se encontraron reportes")

conn.close()
