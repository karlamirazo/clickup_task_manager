#!/usr/bin/env python3
"""
Diagnosticar fallo del deploy en Railway
"""

import requests
import json

def diagnose_railway_deploy():
    """Diagnosticar fallo del deploy"""
    print("🔍 DIAGNOSTICANDO FALLO DEL DEPLOY EN RAILWAY")
    print("=" * 60)
    
    railway_url = "https://clickuptaskmanager-production.up.railway.app"
    
    # Probar diferentes endpoints
    print("1. Probando endpoints básicos...")
    endpoints = [
        "/",
        "/health", 
        "/docs",
        "/api/auth/login",
        "/api/auth/clickup"
    ]
    
    for endpoint in endpoints:
        url = f"{railway_url}{endpoint}"
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', 'N/A')
                print(f"   Content-Type: {content_type}")
                
                if endpoint == "/health":
                    try:
                        data = response.json()
                        print(f"   Health data: {data}")
                    except:
                        print(f"   Health response: {response.text[:100]}...")
            elif response.status_code == 404:
                print(f"   ❌ No encontrado - posible problema de routing")
            elif response.status_code == 500:
                print(f"   ❌ Error interno del servidor")
            else:
                print(f"   ⚠️  Status inesperado: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"❌ {endpoint}: Timeout - Railway no responde")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint}: Error de conexión - Railway no disponible")
        except Exception as e:
            print(f"❌ {endpoint}: Error: {e}")
    
    print(f"\n2. Verificando configuración de Railway...")
    print("📋 Posibles causas del fallo:")
    print("   - Railway no está usando main_simple.py")
    print("   - Variables de entorno no configuradas")
    print("   - Error en requirements.txt")
    print("   - Error en la base de datos")
    print("   - Puerto no configurado correctamente")
    
    print(f"\n3. Verificando logs de Railway...")
    print("📋 Para ver los logs:")
    print("   1. Ve a: https://railway.app/dashboard")
    print("   2. Busca tu proyecto 'clickuptaskmanager'")
    print("   3. Haz clic en el servicio")
    print("   4. Ve a la pestaña 'Deployments'")
    print("   5. Haz clic en el último deploy")
    print("   6. Revisa los logs para errores")
    
    print(f"\n4. Verificando configuración...")
    print("📋 Verifica que en Railway tengas:")
    print("   - Start Command: python main_simple.py")
    print("   - Health Check Path: /health")
    print("   - Variables de entorno configuradas")
    print("   - Puerto: 8000 (o el que use Railway)")

def check_railway_config():
    """Verificar configuración de Railway"""
    print(f"\n🔧 VERIFICANDO CONFIGURACIÓN DE RAILWAY")
    print("=" * 50)
    
    print("📋 Checklist de configuración:")
    print("✅ railway.json creado")
    print("✅ Procfile creado") 
    print("✅ main_simple.py en la raíz")
    print("✅ requirements.txt actualizado")
    print("✅ .env.production con JWT secret")
    
    print(f"\n📋 Variables de entorno requeridas:")
    print("   CLICKUP_OAUTH_CLIENT_ID=7US6KJX26FOROTI3ZSOZYCAXBCG7W386")
    print("   CLICKUP_OAUTH_CLIENT_SECRET=H4M3AVO1L6OG7RDH8XMPUK756PB0X2R28E5KTIJBV8PDQNSORKRSAXI7ZGI5MCXC")
    print("   CLICKUP_OAUTH_REDIRECT_URI=https://clickuptaskmanager-production.up.railway.app/api/auth/callback")
    print("   JWT_SECRET_KEY=dRq6HQ2oaXdvOMEMC3ir722xw3vZ-R594oONCchHeShZ2qSvKTdTf8h-c6oT5JFyDrsQi5F_1DPkt28ArGrP_g")
    print("   ALLOWED_ORIGINS=https://clickuptaskmanager-production.up.railway.app")

def suggest_fixes():
    """Sugerir soluciones"""
    print(f"\n🛠️  SOLUCIONES POSIBLES:")
    print("=" * 30)
    
    print("1. **Verificar que Railway esté usando main_simple.py**")
    print("   - Ve a Settings > Start Command")
    print("   - Debe ser: python main_simple.py")
    
    print("\n2. **Verificar variables de entorno**")
    print("   - Ve a Variables")
    print("   - Asegúrate de que todas estén configuradas")
    
    print("\n3. **Verificar logs de Railway**")
    print("   - Revisa los logs del último deploy")
    print("   - Busca errores específicos")
    
    print("\n4. **Redesplegar manualmente**")
    print("   - Ve a Deployments")
    print("   - Haz clic en 'Redeploy'")
    
    print("\n5. **Verificar base de datos**")
    print("   - Asegúrate de que PostgreSQL esté configurado")
    print("   - Verifica la conexión")

def main():
    """Función principal"""
    print("🔍 DIAGNÓSTICO DE FALLO DE DEPLOY EN RAILWAY")
    print("=" * 70)
    
    # Diagnosticar deploy
    diagnose_railway_deploy()
    
    # Verificar configuración
    check_railway_config()
    
    # Sugerir soluciones
    suggest_fixes()
    
    print(f"\n" + "=" * 70)
    print("📋 PRÓXIMOS PASOS:")
    print("1. Revisa los logs de Railway")
    print("2. Verifica la configuración")
    print("3. Redespliega si es necesario")
    print("4. Comparte los logs si necesitas ayuda")

if __name__ == "__main__":
    main()

