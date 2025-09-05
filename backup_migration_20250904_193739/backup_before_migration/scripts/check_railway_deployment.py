#!/usr/bin/env python3
"""
Script para verificar el estado del deployment en Railway
"""

import requests
import json
import time
from datetime import datetime

def check_deployment_status():
    """Verificar el estado del deployment"""
    print("ğŸš‚ Verificando estado del deployment en Railway")
    print("=" * 60)
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Lista de endpoints para verificar
    endpoints = [
        ("Health Check", "/health"),
        ("API Status", "/api"),
        ("Debug Info", "/debug"),
        ("Test Simple", "/test-simple"),
        ("Test Logging", "/test-logging"),
        ("Tasks Debug", "/api/v1/tasks/debug-code"),
        ("Workspaces", "/api/v1/workspaces"),
        ("Static CSS", "/static/styles.css"),
        ("Static JS", "/static/script.js"),
        ("Main Page", "/")
    ]
    
    results = {}
    
    for name, endpoint in endpoints:
        try:
            print(f"ğŸ”� Verificando {name} ({endpoint})...")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"   âœ… {name}: OK (Status: {response.status_code})")
                results[name] = {
                    "status": "success",
                    "status_code": response.status_code,
                    "size": len(response.content),
                    "content_type": response.headers.get("Content-Type", "unknown")
                }
            else:
                print(f"   â�Œ {name}: Error (Status: {response.status_code})")
                print(f"   ğŸ“„ Respuesta: {response.text[:100]}")
                results[name] = {
                    "status": "error",
                    "status_code": response.status_code,
                    "error": response.text[:200]
                }
                
        except Exception as e:
            print(f"   â�Œ {name}: Error de conexion - {e}")
            results[name] = {
                "status": "error",
                "error": str(e)
            }
        
        # Pequena pausa entre requests
        time.sleep(1)
    
    return results

def analyze_deployment_status(results):
    """Analizar el estado del deployment"""
    print("\n" + "=" * 60)
    print("ğŸ“Š ANALISIS DEL DEPLOYMENT")
    print("=" * 60)
    
    # Contar resultados
    success_count = sum(1 for r in results.values() if r.get("status") == "success")
    error_count = sum(1 for r in results.values() if r.get("status") == "error")
    total_count = len(results)
    
    print(f"\nğŸ“ˆ ESTADISTICAS:")
    print(f"   âœ… Exitosos: {success_count}/{total_count}")
    print(f"   â�Œ Errores: {error_count}/{total_count}")
    print(f"   ğŸ“Š Tasa de exito: {(success_count/total_count)*100:.1f}%")
    
    # Analisis por categorias
    print(f"\nğŸ”� ANALISIS POR CATEGORIAS:")
    
    # Endpoints basicos
    basic_endpoints = ["Health Check", "API Status", "Debug Info"]
    basic_success = sum(1 for name in basic_endpoints if results.get(name, {}).get("status") == "success")
    print(f"   ğŸŒ� Endpoints basicos: {basic_success}/{len(basic_endpoints)} funcionando")
    
    # Endpoints de prueba
    test_endpoints = ["Test Simple", "Test Logging"]
    test_success = sum(1 for name in test_endpoints if results.get(name, {}).get("status") == "success")
    print(f"   ğŸ§ª Endpoints de prueba: {test_success}/{len(test_endpoints)} funcionando")
    
    # Endpoints de API
    api_endpoints = ["Tasks Debug", "Workspaces"]
    api_success = sum(1 for name in api_endpoints if results.get(name, {}).get("status") == "success")
    print(f"   ğŸ”Œ Endpoints de API: {api_success}/{len(api_endpoints)} funcionando")
    
    # Archivos estaticos
    static_endpoints = ["Static CSS", "Static JS", "Main Page"]
    static_success = sum(1 for name in static_endpoints if results.get(name, {}).get("status") == "success")
    print(f"   ğŸ“� Archivos estaticos: {static_success}/{len(static_endpoints)} funcionando")
    
    # Diagnostico del problema
    print(f"\nğŸ”� DIAGNOSTICO:")
    
    if test_success == 0:
        print("   âš ï¸� PROBLEMA: Los endpoints de prueba no estan funcionando")
        print("   ğŸ’¡ POSIBLE CAUSA: Deployment no completado o codigo no actualizado")
        print("   ğŸ”§ SOLUCION: Verificar logs de Railway o forzar nuevo deployment")
    
    if basic_success < len(basic_endpoints):
        print("   â�Œ PROBLEMA CRITICO: Endpoints basicos no funcionando")
        print("   ğŸ’¡ POSIBLE CAUSA: Aplicacion no iniciada correctamente")
        print("   ğŸ”§ SOLUCION: Revisar logs de Railway inmediatamente")
    
    if static_success < len(static_endpoints):
        print("   âš ï¸� PROBLEMA: Archivos estaticos no accesibles")
        print("   ğŸ’¡ POSIBLE CAUSA: Configuracion de archivos estaticos incorrecta")
    
    if api_success < len(api_endpoints):
        print("   âš ï¸� PROBLEMA: Algunos endpoints de API no funcionando")
        print("   ğŸ’¡ POSIBLE CAUSA: Problemas de configuracion o dependencias")
    
    # Estado general
    overall_score = (success_count / total_count) * 100
    
    print(f"\nğŸ�¯ ESTADO GENERAL:")
    if overall_score >= 90:
        print("   ğŸ�‰ EXCELENTE: Deployment funcionando perfectamente")
    elif overall_score >= 70:
        print("   âœ… BUENO: Deployment funcionando con algunos problemas menores")
    elif overall_score >= 50:
        print("   âš ï¸� ACEPTABLE: Deployment funcionando con problemas significativos")
    else:
        print("   â�Œ CRITICO: Deployment con problemas graves")
    
    print(f"   ğŸ“Š Puntuacion: {overall_score:.1f}%")
    
    return overall_score

def main():
    """Funcion principal"""
    print("ğŸš‚ VERIFICACION COMPLETA DEL DEPLOYMENT EN RAILWAY")
    print("=" * 60)
    
    # Verificar estado del deployment
    results = check_deployment_status()
    
    # Analizar resultados
    score = analyze_deployment_status(results)
    
    print(f"\nğŸ•� Verificacion completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Recomendaciones
    print(f"\nğŸ’¡ RECOMENDACIONES:")
    if score < 70:
        print("   1. ğŸ”� Revisar logs de Railway en el dashboard")
        print("   2. ğŸ”„ Forzar nuevo deployment desde Railway")
        print("   3. âš™ï¸� Verificar variables de entorno en Railway")
        print("   4. ğŸ“¦ Verificar que requirements.txt este actualizado")
    else:
        print("   1. âœ… El deployment esta funcionando correctamente")
        print("   2. ğŸ”� Los problemas menores no afectan la funcionalidad principal")
        print("   3. ğŸ“Š La aplicacion esta lista para uso en produccion")

if __name__ == "__main__":
    main()
