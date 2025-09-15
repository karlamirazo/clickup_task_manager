#!/usr/bin/env python3
"""
Diagnosticar problema de OAuth con ClickUp
"""

import requests
import json
from urllib.parse import urlparse, parse_qs

def diagnose_oauth_issue():
    """Diagnosticar problema de OAuth"""
    print("🔍 DIAGNOSTICANDO PROBLEMA DE OAUTH")
    print("=" * 50)
    
    try:
        # 1. Verificar configuración actual
        print("1. Verificando configuración...")
        
        # Leer .env
        try:
            with open('.env', 'r') as f:
                env_content = f.read()
                print("✅ Archivo .env encontrado")
                
                # Buscar configuración OAuth
                if 'CLICKUP_OAUTH_CLIENT_ID' in env_content:
                    print("✅ CLICKUP_OAUTH_CLIENT_ID configurado")
                else:
                    print("❌ CLICKUP_OAUTH_CLIENT_ID no encontrado")
                    
                if 'CLICKUP_OAUTH_REDIRECT_URI' in env_content:
                    print("✅ CLICKUP_OAUTH_REDIRECT_URI configurado")
                else:
                    print("❌ CLICKUP_OAUTH_REDIRECT_URI no encontrado")
                    
        except FileNotFoundError:
            print("❌ Archivo .env no encontrado")
            return
            
        # 2. Probar URL de OAuth
        print("\n2. Probando URL de OAuth...")
        oauth_response = requests.get("http://127.0.0.1:8000/api/auth/clickup", allow_redirects=False)
        
        if oauth_response.status_code == 307:
            redirect_url = oauth_response.headers.get('Location', '')
            print(f"✅ URL de OAuth generada: {redirect_url}")
            
            # Analizar URL
            parsed_url = urlparse(redirect_url)
            query_params = parse_qs(parsed_url.query)
            
            print("\n📊 Parámetros de la URL:")
            for key, value in query_params.items():
                print(f"  {key}: {value[0] if value else 'N/A'}")
                
            # Verificar si es la URL correcta de ClickUp
            if 'app.clickup.com' in redirect_url:
                print("✅ URL de ClickUp correcta")
            else:
                print("❌ URL de ClickUp incorrecta")
                
        else:
            print(f"❌ Error en OAuth: {oauth_response.status_code}")
            return
            
        # 3. Verificar configuración de ClickUp
        print("\n3. Verificando configuración de ClickUp...")
        print("📋 Verifica que en ClickUp tengas:")
        print("   - Client ID: 7US6KJX26FOROTI3ZSOZYCAXBCG7W386")
        print("   - Redirect URI: http://127.0.0.1:8000")
        print("   - Permisos: read:user, read:workspace, read:task, write:task")
        
        # 4. Probar callback manual
        print("\n4. Probando callback manual...")
        test_callback = requests.get("http://127.0.0.1:8000/api/auth/callback?code=test_code&state=test_state", allow_redirects=False)
        
        if test_callback.status_code == 307:
            print("✅ Callback funcionando")
            redirect_url = test_callback.headers.get('Location', '')
            print(f"📊 Redirect: {redirect_url}")
        else:
            print(f"❌ Error en callback: {test_callback.status_code}")
            
        # 5. Verificar logs del servidor
        print("\n5. Verificando logs del servidor...")
        print("📋 Revisa los logs del servidor para ver si hay errores")
        print("   Busca mensajes como:")
        print("   - 'Error de conexión en OAuth'")
        print("   - 'State inválido o expirado'")
        print("   - 'Error de conexión con ClickUp'")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_clickup_oauth_flow():
    """Probar flujo OAuth completo con ClickUp"""
    print("\n🧪 PROBANDO FLUJO OAUTH COMPLETO")
    print("=" * 50)
    
    try:
        # 1. Obtener URL de OAuth
        print("1. Obteniendo URL de OAuth...")
        oauth_response = requests.get("http://127.0.0.1:8000/api/auth/clickup", allow_redirects=False)
        
        if oauth_response.status_code == 307:
            redirect_url = oauth_response.headers.get('Location', '')
            print(f"✅ URL de OAuth: {redirect_url}")
            
            # 2. Simular flujo completo
            print("\n2. Simulando flujo completo...")
            print("📋 Pasos a seguir:")
            print("   1. Ve a la URL de OAuth en tu navegador")
            print("   2. Inicia sesión en ClickUp")
            print("   3. Acepta los permisos")
            print("   4. ClickUp te redirigirá a: http://127.0.0.1:8000")
            print("   5. El servidor debería procesar el callback")
            print("   6. Te redirigirá al dashboard")
            
            # 3. Verificar que el servidor esté escuchando
            print("\n3. Verificando que el servidor esté escuchando...")
            try:
                response = requests.get("http://127.0.0.1:8000/api/auth/login")
                if response.status_code == 200:
                    print("✅ Servidor funcionando")
                else:
                    print(f"❌ Error en servidor: {response.status_code}")
            except Exception as e:
                print(f"❌ Error conectando al servidor: {e}")
                
        else:
            print(f"❌ Error obteniendo URL de OAuth: {oauth_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🔍 DIAGNÓSTICO DE OAUTH CON CLICKUP")
    print("=" * 60)
    
    # Diagnóstico
    diagnose_oauth_issue()
    
    # Prueba de flujo
    test_clickup_oauth_flow()
    
    print("\n" + "=" * 60)
    print("📋 PRÓXIMOS PASOS:")
    print("1. Verifica la configuración en ClickUp")
    print("2. Prueba el flujo OAuth en el navegador")
    print("3. Revisa los logs del servidor")
    print("4. Si hay errores, compártelos conmigo")

if __name__ == "__main__":
    main()

