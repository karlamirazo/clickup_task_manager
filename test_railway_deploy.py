#!/usr/bin/env python3
"""
Script para probar la conexion con Railway
"""

import requests
import json

def test_railway_endpoints():
    """Test endpoints de Railway"""
    
    # Reemplaza con tu URL real de Railway
    base_url = "https://tu-app.up.railway.app"  # CAMBIA ESTO
    
    print("ğŸ§ª PROBANDO ENDPOINTS DE RAILWAY")
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
        print(f"\nğŸ”� Probando: {endpoint}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"   ğŸ“¡ Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   âœ… Respuesta: {json.dumps(data, indent=2, ensure_ascii=False)}")
                except:
                    print(f"   ğŸ“� Respuesta: {response.text[:200]}...")
            else:
                print(f"   â�Œ Error: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ğŸ’¥ Error de conexion: {e}")
        except Exception as e:
            print(f"   ğŸš¨ Error inesperado: {e}")
    
    print("\n" + "=" * 50)
    print("ğŸ�� PRUEBAS COMPLETADAS")

if __name__ == "__main__":
    print("âš ï¸�  IMPORTANTE: Cambia la URL base_url en el script")
    print("   con tu URL real de Railway antes de ejecutar")
    print()
    
    # Preguntar si quiere continuar
    response = input("Â¿Quieres continuar con la URL por defecto? (s/n): ")
    if response.lower() in ['s', 'si', 'si', 'y', 'yes']:
        test_railway_endpoints()
    else:
        print("Por favor, edita el script y cambia la URL base_url")
