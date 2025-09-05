#!/usr/bin/env python3
"""
Verificar qué tareas están en Railway
"""

import requests
import json

def check_railway_tasks():
    """Verificar tareas en Railway"""
    
    print("🔍 VERIFICANDO TAREAS EN RAILWAY")
    print("=" * 60)
    
    # URL del endpoint
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    try:
        # Obtener todas las tareas
        print(f"📡 URL: {base_url}/api/v1/tasks/")
        print(f"\n🔄 Obteniendo tareas...")
        
        response = requests.get(
            f"{base_url}/api/v1/tasks/",
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Respuesta exitosa!")
            try:
                result = response.json()
                print(f"📋 Tipo de respuesta: {type(result)}")
                print(f"📋 Respuesta completa: {json.dumps(result, indent=2)}")
                
                # Verificar si es una lista o un objeto
                if isinstance(result, list):
                    tasks = result
                elif isinstance(result, dict):
                    tasks = result.get("items", [])
                else:
                    tasks = []
                
                print(f"\n📋 Total de tareas: {len(tasks)}")
                print("-" * 50)
                
                for i, task in enumerate(tasks[:10], 1):  # Mostrar solo las primeras 10
                    print(f"📝 TAREA {i}:")
                    print(f"   🆔 ID Local: {task.get('id')}")
                    print(f"   🏷️ Nombre: {task.get('name')}")
                    print(f"   📱 ClickUp ID: {task.get('clickup_id')}")
                    print(f"   🎯 Estado: {task.get('status')}")
                    print(f"   ⚡ Prioridad: {task.get('priority')}")
                    print("-" * 30)
                
                if len(tasks) > 10:
                    print(f"... y {len(tasks) - 10} tareas más")
                    
            except json.JSONDecodeError:
                print("❌ Respuesta no es JSON válido")
                print(f"📋 Respuesta texto: {response.text}")
        else:
            print(f"❌ Error en la respuesta")
            print(f"📋 Respuesta texto: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        print(f"🔍 Tipo de error: {type(e).__name__}")

if __name__ == "__main__":
    check_railway_tasks()
