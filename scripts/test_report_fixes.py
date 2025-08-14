#!/usr/bin/env python3
"""
Script de prueba para verificar los fixes del reporte visual
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

async def test_api_endpoint(session, endpoint, method="GET", data=None):
    """Probar un endpoint de la API"""
    url = f"{API_BASE}{endpoint}"
    try:
        if method == "GET":
            async with session.get(url) as response:
                return response.status, await response.json() if response.status != 204 else {}
        elif method == "POST":
            async with session.post(url, json=data) as response:
                return response.status, await response.json() if response.status != 204 else {}
    except Exception as e:
        return 0, {"error": str(e)}

async def test_users_endpoint():
    """Probar el endpoint de usuarios"""
    print("🔍 Probando endpoint de usuarios...")
    
    async with aiohttp.ClientSession() as session:
        # Probar obtener usuarios de un workspace específico
        status, data = await test_api_endpoint(session, "/users/?workspace_id=9014943317")
        
        print(f"   Status: {status}")
        if status == 200:
            users = data.get("users", [])
            print(f"   Usuarios encontrados: {len(users)}")
            for user in users[:3]:  # Mostrar solo los primeros 3
                name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                if not name:
                    name = user.get('username', user.get('email', 'N/A'))
                print(f"   - {name} (ID: {user.get('clickup_id')})")
        else:
            print(f"   Error: {data}")

async def test_tasks_with_assignees():
    """Probar que las tareas incluyan información de asignados"""
    print("\n🔍 Probando tareas con información de asignados...")
    
    async with aiohttp.ClientSession() as session:
        # Obtener todas las tareas
        status, data = await test_api_endpoint(session, "/tasks/?include_closed=true&limit=10")
        
        print(f"   Status: {status}")
        if status == 200:
            tasks = data.get("tasks", [])
            print(f"   Tareas encontradas: {len(tasks)}")
            
            for task in tasks[:5]:  # Mostrar solo las primeras 5
                name = task.get("name", "Sin nombre")
                priority = task.get("priority", "Sin prioridad")
                assignee_name = task.get("assignee_name", "Sin asignar")
                assignee_id = task.get("assignee_id", "N/A")
                
                print(f"   - {name}")
                print(f"     Prioridad: {priority}")
                print(f"     Asignado: {assignee_name} (ID: {assignee_id})")
                print()
        else:
            print(f"   Error: {data}")

async def test_priority_formatting():
    """Probar que las prioridades se formateen correctamente"""
    print("\n🔍 Probando formateo de prioridades...")
    
    # Simular diferentes tipos de prioridad
    test_priorities = [1, 2, 3, 4, "1", "2", "3", "4", None, "urgent", "high", "normal", "low"]
    
    for priority in test_priorities:
        priority_str = str(priority) if priority is not None else "None"
        print(f"   Prioridad: {priority_str} -> {format_priority(priority)}")

def format_priority(priority):
    """Función de formateo de prioridad (copiada del frontend)"""
    if priority is None:
        return "Sin prioridad"
    
    # Convertir a string si es número
    priority_str = str(priority)
    if priority_str == '1':
        return 'Urgente'
    elif priority_str == '2':
        return 'Alta'
    elif priority_str == '3':
        return 'Normal'
    elif priority_str == '4':
        return 'Baja'
    else:
        return 'Sin prioridad'

async def test_report_generation():
    """Probar la generación de reportes"""
    print("\n🔍 Probando generación de reportes...")
    
    async with aiohttp.ClientSession() as session:
        # Crear un reporte
        report_data = {
            "name": "Reporte de Prueba",
            "report_type": "task_summary",
            "workspace_id": "9014943317",
            "description": "Reporte de prueba para verificar funcionalidad"
        }
        
        status, data = await test_api_endpoint(session, "/reports/", method="POST", data=report_data)
        
        print(f"   Status creación: {status}")
        if status == 201:
            report_id = data.get("id")
            print(f"   Reporte creado con ID: {report_id}")
            
            # Generar el reporte
            status2, data2 = await test_api_endpoint(session, f"/reports/{report_id}/generate", method="POST")
            print(f"   Status generación: {status2}")
            
            if status2 == 200:
                print("   ✅ Reporte generado exitosamente")
                print(f"   Total tareas: {data2.get('total_tasks', 0)}")
                print(f"   Completadas: {data2.get('completed_tasks', 0)}")
                print(f"   Pendientes: {data2.get('pending_tasks', 0)}")
                
                # Mostrar distribuciones
                if 'status_distribution' in data2:
                    print(f"   Estados: {data2['status_distribution']}")
                if 'priority_distribution' in data2:
                    print(f"   Prioridades: {data2['priority_distribution']}")
                if 'assignee_distribution' in data2:
                    print(f"   Asignados: {data2['assignee_distribution']}")
            else:
                print(f"   Error generando reporte: {data2}")
        else:
            print(f"   Error creando reporte: {data}")

async def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de fixes del reporte visual")
    print("=" * 50)
    
    # Verificar que el servidor esté corriendo
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status != 200:
                    print("❌ El servidor no está respondiendo correctamente")
                    return
    except Exception as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        return
    
    print("✅ Servidor respondiendo correctamente")
    
    # Ejecutar pruebas
    await test_users_endpoint()
    await test_tasks_with_assignees()
    await test_report_generation()
    
    print("\n" + "=" * 50)
    print("🏁 Pruebas completadas")

if __name__ == "__main__":
    asyncio.run(main())
