#!/usr/bin/env python3
"""
Test script to simulate task creation with custom fields from the frontend
"""

import requests
import json

# URL del servidor
base_url = "http://localhost:3000"

# Datos de prueba para crear una tarea
task_data = {
    "name": "Tarea de prueba",
    "description": "Descripción de prueba",
    "workspace_id": "9014943317",
    "list_id": "901411770471",
    "status": "to_do",
    "priority": 3,
    "assignee_id": None,
    "custom_fields": {}
}

print("🔍 Probando creación de tarea...")
print(f"📝 Datos a enviar: {json.dumps(task_data, indent=2)}")

try:
    # Intentar crear la tarea
    response = requests.post(
        f"{base_url}/api/v1/tasks/",
        json=task_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"📡 Status Code: {response.status_code}")
    print(f"📡 Response Headers: {dict(response.headers)}")
    
    if response.status_code == 201:
        print("✅ Tarea creada exitosamente!")
        print(f"📝 Respuesta: {response.json()}")
    else:
        print(f"❌ Error {response.status_code}")
        print(f"📝 Respuesta: {response.text}")
        
        # Si es un error 422, mostrar detalles de validación
        if response.status_code == 422:
            try:
                error_details = response.json()
                print(f"🔍 Detalles del error de validación:")
                print(json.dumps(error_details, indent=2))
            except:
                print("⚠️ No se pudieron parsear los detalles del error")
                
except Exception as e:
    print(f"💥 Error de conexión: {e}")
