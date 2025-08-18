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
    print("🚂 Verificando estado del deployment en Railway")
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
            print(f"🔍 Verificando {name} ({endpoint})...")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ {name}: OK (Status: {response.status_code})")
                results[name] = {
                    "status": "success",
                    "status_code": response.status_code,
                    "size": len(response.content),
                    "content_type": response.headers.get("Content-Type", "unknown")
                }
            else:
                print(f"   ❌ {name}: Error (Status: {response.status_code})")
                print(f"   📄 Respuesta: {response.text[:100]}")
                results[name] = {
                    "status": "error",
                    "status_code": response.status_code,
                    "error": response.text[:200]
                }
                
        except Exception as e:
            print(f"   ❌ {name}: Error de conexión - {e}")
            results[name] = {
                "status": "error",
                "error": str(e)
            }
        
        # Pequeña pausa entre requests
        time.sleep(1)
    
    return results

def analyze_deployment_status(results):
    """Analizar el estado del deployment"""
    print("\n" + "=" * 60)
    print("📊 ANÁLISIS DEL DEPLOYMENT")
    print("=" * 60)
    
    # Contar resultados
    success_count = sum(1 for r in results.values() if r.get("status") == "success")
    error_count = sum(1 for r in results.values() if r.get("status") == "error")
    total_count = len(results)
    
    print(f"\n📈 ESTADÍSTICAS:")
    print(f"   ✅ Exitosos: {success_count}/{total_count}")
    print(f"   ❌ Errores: {error_count}/{total_count}")
    print(f"   📊 Tasa de éxito: {(success_count/total_count)*100:.1f}%")
    
    # Análisis por categorías
    print(f"\n🔍 ANÁLISIS POR CATEGORÍAS:")
    
    # Endpoints básicos
    basic_endpoints = ["Health Check", "API Status", "Debug Info"]
    basic_success = sum(1 for name in basic_endpoints if results.get(name, {}).get("status") == "success")
    print(f"   🌐 Endpoints básicos: {basic_success}/{len(basic_endpoints)} funcionando")
    
    # Endpoints de prueba
    test_endpoints = ["Test Simple", "Test Logging"]
    test_success = sum(1 for name in test_endpoints if results.get(name, {}).get("status") == "success")
    print(f"   🧪 Endpoints de prueba: {test_success}/{len(test_endpoints)} funcionando")
    
    # Endpoints de API
    api_endpoints = ["Tasks Debug", "Workspaces"]
    api_success = sum(1 for name in api_endpoints if results.get(name, {}).get("status") == "success")
    print(f"   🔌 Endpoints de API: {api_success}/{len(api_endpoints)} funcionando")
    
    # Archivos estáticos
    static_endpoints = ["Static CSS", "Static JS", "Main Page"]
    static_success = sum(1 for name in static_endpoints if results.get(name, {}).get("status") == "success")
    print(f"   📁 Archivos estáticos: {static_success}/{len(static_endpoints)} funcionando")
    
    # Diagnóstico del problema
    print(f"\n🔍 DIAGNÓSTICO:")
    
    if test_success == 0:
        print("   ⚠️ PROBLEMA: Los endpoints de prueba no están funcionando")
        print("   💡 POSIBLE CAUSA: Deployment no completado o código no actualizado")
        print("   🔧 SOLUCIÓN: Verificar logs de Railway o forzar nuevo deployment")
    
    if basic_success < len(basic_endpoints):
        print("   ❌ PROBLEMA CRÍTICO: Endpoints básicos no funcionando")
        print("   💡 POSIBLE CAUSA: Aplicación no iniciada correctamente")
        print("   🔧 SOLUCIÓN: Revisar logs de Railway inmediatamente")
    
    if static_success < len(static_endpoints):
        print("   ⚠️ PROBLEMA: Archivos estáticos no accesibles")
        print("   💡 POSIBLE CAUSA: Configuración de archivos estáticos incorrecta")
    
    if api_success < len(api_endpoints):
        print("   ⚠️ PROBLEMA: Algunos endpoints de API no funcionando")
        print("   💡 POSIBLE CAUSA: Problemas de configuración o dependencias")
    
    # Estado general
    overall_score = (success_count / total_count) * 100
    
    print(f"\n🎯 ESTADO GENERAL:")
    if overall_score >= 90:
        print("   🎉 EXCELENTE: Deployment funcionando perfectamente")
    elif overall_score >= 70:
        print("   ✅ BUENO: Deployment funcionando con algunos problemas menores")
    elif overall_score >= 50:
        print("   ⚠️ ACEPTABLE: Deployment funcionando con problemas significativos")
    else:
        print("   ❌ CRÍTICO: Deployment con problemas graves")
    
    print(f"   📊 Puntuación: {overall_score:.1f}%")
    
    return overall_score

def main():
    """Función principal"""
    print("🚂 VERIFICACIÓN COMPLETA DEL DEPLOYMENT EN RAILWAY")
    print("=" * 60)
    
    # Verificar estado del deployment
    results = check_deployment_status()
    
    # Analizar resultados
    score = analyze_deployment_status(results)
    
    print(f"\n🕐 Verificación completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES:")
    if score < 70:
        print("   1. 🔍 Revisar logs de Railway en el dashboard")
        print("   2. 🔄 Forzar nuevo deployment desde Railway")
        print("   3. ⚙️ Verificar variables de entorno en Railway")
        print("   4. 📦 Verificar que requirements.txt esté actualizado")
    else:
        print("   1. ✅ El deployment está funcionando correctamente")
        print("   2. 🔍 Los problemas menores no afectan la funcionalidad principal")
        print("   3. 📊 La aplicación está lista para uso en producción")

if __name__ == "__main__":
    main()
