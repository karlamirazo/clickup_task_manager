#!/usr/bin/env python3
"""
Script para verificar el estado de la aplicación
"""

import requests
import webbrowser

def check_app_status():
    """Verificar si la aplicación está funcionando"""
    print("🔍 VERIFICANDO ESTADO DE LA APLICACIÓN:")
    print("-" * 45)
    
    try:
        response = requests.get("https://clickuptaskmanager-production.up.railway.app", timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Content Length: {len(response.text)} caracteres")
        
        if "ClickUp Task Manager" in response.text:
            print("✅ Aplicación funcionando correctamente")
            print("✅ Página de login cargada")
            return True
        else:
            print("⚠️  Aplicación responde pero contenido inesperado")
            print("📄 Primeros 200 caracteres:")
            print(response.text[:200])
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando a la aplicación: {e}")
        return False

def check_oauth_endpoint():
    """Verificar el endpoint de OAuth"""
    print("\n🔗 VERIFICANDO ENDPOINT OAUTH:")
    print("-" * 35)
    
    try:
        response = requests.get("https://clickuptaskmanager-production.up.railway.app/oauth/clickup", timeout=10)
        print(f"✅ OAuth endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ OAuth endpoint funcionando")
            return True
        else:
            print("⚠️  OAuth endpoint no responde correctamente")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en OAuth endpoint: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE APLICACIÓN CLICKUP")
    print("=" * 60)
    print()
    
    # Verificar aplicación principal
    app_ok = check_app_status()
    
    # Verificar endpoint OAuth
    oauth_ok = check_oauth_endpoint()
    
    print("\n📋 RESUMEN:")
    print("-" * 15)
    print(f"Aplicación principal: {'✅ OK' if app_ok else '❌ ERROR'}")
    print(f"Endpoint OAuth: {'✅ OK' if oauth_ok else '❌ ERROR'}")
    
    if app_ok and oauth_ok:
        print("\n🎉 ¡Aplicación funcionando correctamente!")
        print("💡 El problema está en la configuración de ClickUp")
        print("🔧 Verifica que la URL de redirección sea:")
        print("   https://clickuptaskmanager-production.up.railway.app")
    else:
        print("\n❌ Hay problemas con la aplicación")
        print("💡 Revisa los logs de Railway")
    
    print("\n🌐 Abriendo aplicación en el navegador...")
    try:
        webbrowser.open("https://clickuptaskmanager-production.up.railway.app")
        print("✅ Aplicación abierta en el navegador")
    except Exception as e:
        print(f"❌ Error abriendo navegador: {e}")

if __name__ == "__main__":
    main()
