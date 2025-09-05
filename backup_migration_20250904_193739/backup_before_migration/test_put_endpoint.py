#!/usr/bin/env python3
"""
Test directo del endpoint PUT para diagnosticar problemas de sincronización
"""

import requests
import json

def test_put_endpoint():
    """Probar el endpoint PUT directamente"""
    
    print("🔍 TEST DIRECTO DEL ENDPOINT PUT")
    print("=" * 60)
    
    # URL del endpoint
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    task_id = "34"  # ID de la tarea simulador
    
    # Datos de actualización
    update_data = {
        "name": "simulador 4",
        "description": "Test directo del endpoint PUT",
        "status": "complete",
        "priority": 1,
        "due_date": "2025-09-04"
    }
    
    print(f"📡 URL: {base_url}/api/v1/tasks/{task_id}")
    print(f"📋 Datos de actualización: {json.dumps(update_data, indent=2)}")
    
    try:
        # Hacer la petición PUT
        print(f"\n🔄 Enviando petición PUT...")
        response = requests.put(
            f"{base_url}/api/v1/tasks/{task_id}",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Respuesta exitosa!")
            try:
                result = response.json()
                print(f"📋 Respuesta JSON: {json.dumps(result, indent=2)}")
                
                # Verificar si se actualizó correctamente
                if result.get("name") == "simulador 4":
                    print("✅ Nombre actualizado correctamente")
                else:
                    print(f"❌ Nombre NO se actualizó: {result.get('name')}")
                
                if result.get("status") == "complete":
                    print("✅ Estado actualizado correctamente")
                else:
                    print(f"❌ Estado NO se actualizó: {result.get('status')}")
                    
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
    test_put_endpoint()

