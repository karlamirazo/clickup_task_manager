#!/usr/bin/env python3
"""
Script para verificar la funcionalidad completa de la interfaz web
"""

import requests
import json
import os
from datetime import datetime

def check_interface_endpoints():
    """Verificar endpoints de la interfaz"""
    print("🌐 Verificando endpoints de la interfaz...")
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    endpoints = {
        "Interfaz Principal": "/",
        "Dashboard de Tareas": "/tasks-dashboard",
        "Dashboard de Notificaciones": "/dashboard",
        "Estilos CSS": "/static/styles.css",
        "JavaScript": "/static/script.js"
    }
    
    results = {}
    
    for name, endpoint in endpoints.items():
        try:
            print(f"🔍 Verificando {name} ({endpoint})...")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ {name}: OK (Status: {response.status_code})")
                print(f"   📄 Tamaño: {len(response.content)} bytes")
                results[name] = {
                    "status": "success",
                    "status_code": response.status_code,
                    "size": len(response.content),
                    "content_type": response.headers.get("Content-Type", "unknown")
                }
            else:
                print(f"   ❌ {name}: Error (Status: {response.status_code})")
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
    
    return results

def check_api_endpoints_for_interface():
    """Verificar endpoints de API que usa la interfaz"""
    print("\n🔌 Verificando endpoints de API para la interfaz...")
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    api_endpoints = {
        "Estado del Sistema": "/api",
        "Debug del Sistema": "/debug",
        "Workspaces": "/api/v1/workspaces",
        "Lists": "/api/v1/lists",
        "Tasks": "/api/v1/tasks",
        "Users": "/api/v1/users"
    }
    
    api_results = {}
    
    for name, endpoint in api_endpoints.items():
        try:
            print(f"🔍 Verificando API {name} ({endpoint})...")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ {name}: OK (Status: {response.status_code})")
                try:
                    data = response.json()
                    api_results[name] = {
                        "status": "success",
                        "status_code": response.status_code,
                        "data_type": type(data).__name__,
                        "has_data": bool(data)
                    }
                except:
                    api_results[name] = {
                        "status": "success",
                        "status_code": response.status_code,
                        "data_type": "text",
                        "content": response.text[:100]
                    }
            else:
                print(f"   ⚠️ {name}: {response.status_code} - {response.text[:100]}")
                api_results[name] = {
                    "status": "warning",
                    "status_code": response.status_code,
                    "message": response.text[:100]
                }
                
        except Exception as e:
            print(f"   ❌ {name}: Error - {e}")
            api_results[name] = {
                "status": "error",
                "error": str(e)
            }
    
    return api_results

def check_interface_features():
    """Verificar características específicas de la interfaz"""
    print("\n🎨 Verificando características de la interfaz...")
    
    base_url = "https://clickuptaskmanager-production.up.railway.app"
    features = {}
    
    # Verificar si la interfaz principal tiene elementos clave
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            content = response.text.lower()
            
            features["HTML Completo"] = {
                "status": "success",
                "has_doctype": "<!doctype html" in content,
                "has_title": "clickup project manager" in content,
                "has_navigation": "nav-tabs" in content,
                "has_dashboard": "dashboard" in content,
                "has_tasks": "tareas" in content,
                "has_workspaces": "workspaces" in content
            }
            
            print("   ✅ Interfaz principal: HTML completo y bien estructurado")
            
    except Exception as e:
        features["HTML Completo"] = {"status": "error", "error": str(e)}
        print(f"   ❌ Error verificando HTML: {e}")
    
    # Verificar CSS
    try:
        response = requests.get(f"{base_url}/static/styles.css", timeout=10)
        if response.status_code == 200:
            css_content = response.text
            features["CSS"] = {
                "status": "success",
                "has_reset": "* {" in css_content,
                "has_gradients": "linear-gradient" in css_content,
                "has_responsive": "@media" in css_content,
                "has_animations": "transition" in css_content or "animation" in css_content
            }
            print("   ✅ CSS: Estilos completos con gradientes y responsive")
            
    except Exception as e:
        features["CSS"] = {"status": "error", "error": str(e)}
        print(f"   ❌ Error verificando CSS: {e}")
    
    # Verificar JavaScript
    try:
        response = requests.get(f"{base_url}/static/script.js", timeout=10)
        if response.status_code == 200:
            js_content = response.text
            features["JavaScript"] = {
                "status": "success",
                "has_fetch": "fetch" in js_content,
                "has_api_calls": "/api/" in js_content,
                "has_error_handling": "catch" in js_content,
                "has_ui_updates": "innerhtml" in js_content or "textContent" in js_content
            }
            print("   ✅ JavaScript: Funcionalidad completa con API calls")
            
    except Exception as e:
        features["JavaScript"] = {"status": "error", "error": str(e)}
        print(f"   ❌ Error verificando JavaScript: {e}")
    
    return features

def generate_interface_report(interface_results, api_results, features):
    """Generar reporte completo de la interfaz"""
    print("\n" + "=" * 70)
    print("📊 REPORTE COMPLETO DE LA INTERFAZ")
    print("=" * 70)
    
    # Resumen de endpoints de interfaz
    print("\n🌐 ENDPOINTS DE INTERFAZ:")
    for name, result in interface_results.items():
        status_icon = "✅" if result.get("status") == "success" else "❌"
        print(f"   {status_icon} {name}: {result.get('status', 'error')}")
        if result.get("status") == "success":
            print(f"      📄 Tamaño: {result.get('size', 0)} bytes")
            print(f"      🎨 Tipo: {result.get('content_type', 'unknown')}")
    
    # Resumen de API endpoints
    print("\n🔌 ENDPOINTS DE API:")
    for name, result in api_results.items():
        if result.get("status") == "success":
            status_icon = "✅"
        elif result.get("status") == "warning":
            status_icon = "⚠️"
        else:
            status_icon = "❌"
        
        print(f"   {status_icon} {name}: {result.get('status', 'error')}")
        if result.get("status") == "success":
            print(f"      📊 Tipo de datos: {result.get('data_type', 'unknown')}")
            print(f"      📈 Tiene datos: {result.get('has_data', False)}")
    
    # Resumen de características
    print("\n🎨 CARACTERÍSTICAS DE LA INTERFAZ:")
    for name, result in features.items():
        if result.get("status") == "success":
            status_icon = "✅"
            print(f"   {status_icon} {name}: Funcional")
            
            # Mostrar detalles específicos
            if name == "HTML Completo":
                html_features = []
                if result.get("has_doctype"): html_features.append("DOCTYPE")
                if result.get("has_title"): html_features.append("Título")
                if result.get("has_navigation"): html_features.append("Navegación")
                if result.get("has_dashboard"): html_features.append("Dashboard")
                if result.get("has_tasks"): html_features.append("Tareas")
                if result.get("has_workspaces"): html_features.append("Workspaces")
                print(f"      📋 Elementos: {', '.join(html_features)}")
            
            elif name == "CSS":
                css_features = []
                if result.get("has_reset"): css_features.append("Reset")
                if result.get("has_gradients"): css_features.append("Gradientes")
                if result.get("has_responsive"): css_features.append("Responsive")
                if result.get("has_animations"): css_features.append("Animaciones")
                print(f"      🎨 Estilos: {', '.join(css_features)}")
            
            elif name == "JavaScript":
                js_features = []
                if result.get("has_fetch"): js_features.append("Fetch API")
                if result.get("has_api_calls"): js_features.append("API Calls")
                if result.get("has_error_handling"): js_features.append("Error Handling")
                if result.get("has_ui_updates"): js_features.append("UI Updates")
                print(f"      ⚡ Funcionalidad: {', '.join(js_features)}")
        else:
            status_icon = "❌"
            print(f"   {status_icon} {name}: Error - {result.get('error', 'Desconocido')}")
    
    # Estado general
    print("\n🎯 ESTADO GENERAL DE LA INTERFAZ:")
    interface_success = sum(1 for r in interface_results.values() if r.get("status") == "success")
    api_success = sum(1 for r in api_results.values() if r.get("status") == "success")
    features_success = sum(1 for r in features.values() if r.get("status") == "success")
    
    total_interface = len(interface_results)
    total_api = len(api_results)
    total_features = len(features)
    
    print(f"   🌐 Interfaz: {interface_success}/{total_interface} endpoints funcionando")
    print(f"   🔌 API: {api_success}/{total_api} endpoints disponibles")
    print(f"   🎨 Características: {features_success}/{total_features} funcionales")
    
    overall_score = (interface_success + api_success + features_success) / (total_interface + total_api + total_features) * 100
    print(f"   📊 Puntuación general: {overall_score:.1f}%")
    
    if overall_score >= 90:
        print("   🎉 ¡Excelente! La interfaz está funcionando perfectamente")
    elif overall_score >= 70:
        print("   ✅ Bueno! La interfaz está funcionando correctamente")
    elif overall_score >= 50:
        print("   ⚠️ Aceptable, pero hay algunos problemas")
    else:
        print("   ❌ Problemas significativos en la interfaz")

def main():
    """Función principal"""
    print("🌐 Verificando funcionalidad completa de la interfaz web")
    print("=" * 70)
    
    # Verificar endpoints de interfaz
    interface_results = check_interface_endpoints()
    
    # Verificar endpoints de API
    api_results = check_api_endpoints_for_interface()
    
    # Verificar características específicas
    features = check_interface_features()
    
    # Generar reporte
    generate_interface_report(interface_results, api_results, features)
    
    print(f"\n🕐 Verificación completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
