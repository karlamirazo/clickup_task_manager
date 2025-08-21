#!/usr/bin/env python3
import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('clickup_manager.db')
cursor = conn.cursor()

# Verificar tareas
cursor.execute("SELECT clickup_id, name, workspace_id, priority, assignee_id, status FROM tasks")
tasks = cursor.fetchall()

print(f"üìã Tareas en la base de datos ({len(tasks)}):")
for task in tasks:
    clickup_id, name, workspace_id, priority, assignee_id, status = task
    print(f"  - {name}")
    print(f"    ID: {clickup_id}")
    print(f"    Workspace: {workspace_id}")
    print(f"    Prioridad: {priority}")
    print(f"    Asignado: {assignee_id}")
    print(f"    Estado: {status}")
    print()

# Verificar workspaces
cursor.execute("SELECT clickup_id, name FROM workspaces")
workspaces = cursor.fetchall()

print(f"üè¢ Workspaces en la base de datos ({len(workspaces)}):")
for workspace in workspaces:
    clickup_id, name = workspace
    print(f"  - {name} (ID: {clickup_id})")

conn.close()
