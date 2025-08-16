#!/usr/bin/env python3
"""
Script para probar la conexión con Railway
"""

import requests
import json

def test_railway_endpoints():
    """Probar endpoints de Railway"""
    
    # Reemplaza con tu URL real de Railway
    base_url = "https://tu-app.up.railway.app"  # CAMBIA ESTO
    
    print("🧪 PROBANDO ENDPOINTS DE RAILWAY")
    print("=" * 50)
    
    endpoints = [
        "/health",
        "/api/v1/tasks/debug-server",
        "/api/v1/tasks/debug-db",
        "/api/v1/tasks/debug-models",
        "/api/v1/tasks/test"
    ]
    
    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"\n🔍 Probando: {endpoint}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"   📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Respuesta: {json.dumps(data, indent=2, ensure_ascii=False)}")
                except:
                    print(f"   📝 Respuesta: {response.text[:200]}...")
            else:
                print(f"   ❌ Error: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   💥 Error de conexión: {e}")
        except Exception as e:
            print(f"   🚨 Error inesperado: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 PRUEBAS COMPLETADAS")

if __name__ == "__main__":
    print("⚠️  IMPORTANTE: Cambia la URL base_url en el script")
    print("   con tu URL real de Railway antes de ejecutar")
    print()
    
    # Preguntar si quiere continuar
    response = input("¿Quieres continuar con la URL por defecto? (s/n): ")
    if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        test_railway_endpoints()
    else:
        print("Por favor, edita el script y cambia la URL base_url")
