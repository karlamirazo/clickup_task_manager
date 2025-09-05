#!/usr/bin/env python3
"""
Configuración completa de integración WhatsApp con ClickUp
Incluye opciones para Evolution API real y simulador para pruebas
"""

import os
import sys
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

def print_header(title):
    """Imprime un encabezado"""
    print(f"\n{'='*70}")
    print(f"🚀 {title}")
    print(f"{'='*70}")

def print_step(step, description):
    """Imprime un paso de configuración"""
    print(f"\n🔧 PASO {step}: {description}")
    print(f"{'─'*50}")

def print_success(message):
    """Imprime un mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message):
    """Imprime un mensaje de error"""
    print(f"❌ {message}")

def print_info(message):
    """Imprime un mensaje informativo"""
    print(f"ℹ️ {message}")

def print_warning(message):
    """Imprime un mensaje de advertencia"""
    print(f"⚠️ {message}")

def check_docker():
    """Verifica si Docker está disponible"""
    print_step(1, "Verificando Docker")
    
    try:
        import subprocess
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_success(f"Docker está disponible: {result.stdout.strip()}")
            return True
        else:
            print_error("Docker no está disponible")
            return False
    except Exception as e:
        print_error(f"No se pudo verificar Docker: {e}")
        return False

def check_docker_running():
    """Verifica si Docker está ejecutándose"""
    try:
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
        if result.returncode == 0:
            print_success("Docker está ejecutándose")
            return True
        else:
            print_warning("Docker no está ejecutándose")
            return False
    except Exception:
        print_warning("No se pudo verificar si Docker está ejecutándose")
        return False

def start_evolution_api():
    """Inicia Evolution API con Docker"""
    print_step(2, "Iniciando Evolution API")
    
    if not check_docker_running():
        print_info("Docker no está ejecutándose. Intentando iniciar Docker Desktop...")
        try:
            subprocess.run(['docker-desktop'], start_new_session=True)
            print_info("Docker Desktop iniciado. Esperando que esté listo...")
            time.sleep(30)  # Esperar a que Docker esté listo
        except Exception as e:
            print_error(f"No se pudo iniciar Docker Desktop: {e}")
            return False
    
    print_info("Iniciando Evolution API con Docker Compose...")
    try:
        result = subprocess.run(
            ['docker-compose', '-f', 'docker-compose-whatsapp.yml', 'up', '-d'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("Evolution API iniciado exitosamente")
            print_info("Esperando que los servicios estén listos...")
            time.sleep(20)  # Esperar a que los servicios estén listos
            return True
        else:
            print_error(f"Error iniciando Evolution API: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"Error ejecutando Docker Compose: {e}")
        return False

def check_evolution_api():
    """Verifica si Evolution API está ejecutándose"""
    print_step(3, "Verificando Evolution API")
    
    try:
        response = requests.get("http://localhost:8080/instance/fetchInstances", timeout=10)
        if response.status_code == 200:
            print_success("Evolution API está ejecutándose en http://localhost:8080")
            return True
        else:
            print_info(f"Evolution API responde con código: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_info("Evolution API no está ejecutándose")
        return False
    except Exception as e:
        print_error(f"Error verificando Evolution API: {e}")
        return False

def create_whatsapp_instance():
    """Crea una instancia de WhatsApp"""
    print_step(4, "Creando instancia de WhatsApp")
    
    url = "http://localhost:8080/instance/create"
    headers = {
        "Content-Type": "application/json",
        "apikey": "clickup_whatsapp_key_2024"
    }
    
    data = {
        "instanceName": "clickup-manager",
        "token": "clickup_token_2024",
        "qrcode": True,
        "number": "55123456789"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        if response.status_code == 200:
            result = response.json()
            print_success("Instancia de WhatsApp creada exitosamente")
            print_info(f"Resultado: {json.dumps(result, indent=2)}")
            return True
        else:
            print_error(f"Error creando instancia: {response.status_code}")
            print_info(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error en la petición: {e}")
        return False

def get_qr_code():
    """Obtiene el código QR para conectar WhatsApp"""
    print_step(5, "Obteniendo código QR")
    
    url = "http://localhost:8080/instance/qrcode/clickup-manager"
    headers = {
        "apikey": "clickup_whatsapp_key_2024"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            result = response.json()
            print_success("Código QR obtenido exitosamente")
            
            # Guardar el código QR en un archivo
            if 'qrcode' in result:
                qr_data = result['qrcode']
                if qr_data.startswith('data:image'):
                    # Es un código QR en base64
                    print_info("Código QR generado. Escanea este código con tu WhatsApp:")
                    print_info("El código QR se ha guardado en 'whatsapp_qr.html'")
                    
                    # Crear archivo HTML para mostrar el QR
                    html_content = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>WhatsApp QR Code - ClickUp Integration</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; text-align: center; padding: 20px; background: #f5f5f5; }}
                            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                            .qr-container {{ margin: 20px auto; max-width: 400px; }}
                            .instructions {{ background: #e8f4fd; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: left; }}
                            .warning {{ background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107; }}
                            h1 {{ color: #25d366; }}
                            .step {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>📱 Código QR de WhatsApp</h1>
                            <p><strong>Integración con ClickUp Project Manager</strong></p>
                            
                            <div class="qr-container">
                                <img src="{qr_data}" alt="WhatsApp QR Code" style="max-width: 100%; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                            </div>
                            
                            <div class="instructions">
                                <h3>📋 Instrucciones paso a paso:</h3>
                                <div class="step">1. 📱 Abre WhatsApp en tu teléfono</div>
                                <div class="step">2. ⚙️ Ve a <strong>Configuración</strong> > <strong>Dispositivos vinculados</strong></div>
                                <div class="step">3. 🔗 Toca <strong>Vincular un dispositivo</strong></div>
                                <div class="step">4. 📷 Escanea este código QR</div>
                                <div class="step">5. ✅ Confirma la vinculación</div>
                            </div>
                            
                            <div class="warning">
                                <strong>⚠️ Importante:</strong>
                                <ul style="margin: 10px 0; padding-left: 20px;">
                                    <li>No compartas este código QR con nadie</li>
                                    <li>El código expira en 5 minutos</li>
                                    <li>Mantén tu teléfono conectado a internet</li>
                                </ul>
                            </div>
                            
                            <p><em>Una vez conectado, podrás recibir notificaciones automáticas de ClickUp</em></p>
                        </div>
                    </body>
                    </html>
                    """
                    
                    with open('whatsapp_qr.html', 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    return True
                else:
                    print_info(f"QR recibido: {qr_data}")
                    return True
            else:
                print_info(f"Respuesta completa: {json.dumps(result, indent=2)}")
                return True
        else:
            print_error(f"Error obteniendo QR: {response.status_code}")
            print_info(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error en la petición: {e}")
        return False

def check_instance_status():
    """Verifica el estado de la instancia"""
    print_step(6, "Verificando estado de la instancia")
    
    url = "http://localhost:8080/instance/status/clickup-manager"
    headers = {
        "apikey": "clickup_whatsapp_key_2024"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            result = response.json()
            print_success("Estado de instancia obtenido")
            print_info(f"Estado: {json.dumps(result, indent=2)}")
            
            # Verificar si está conectado
            if 'status' in result and result['status'] == 'open':
                print_success("¡WhatsApp está conectado!")
                return True
            else:
                print_info("WhatsApp aún no está conectado")
                return False
        else:
            print_error(f"Error verificando estado: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error en la petición: {e}")
        return False

def test_send_message():
    """Prueba enviar un mensaje de WhatsApp"""
    print_step(7, "Probando envío de mensaje")
    
    url = "http://localhost:8080/message/sendText/clickup-manager"
    headers = {
        "Content-Type": "application/json",
        "apikey": "clickup_whatsapp_key_2024"
    }
    
    data = {
        "number": "55123456789",
        "text": "🧪 Mensaje de prueba desde ClickUp Project Manager - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        if response.status_code == 200:
            result = response.json()
            print_success("Mensaje enviado exitosamente")
            print_info(f"Resultado: {json.dumps(result, indent=2)}")
            return True
        else:
            print_error(f"Error enviando mensaje: {response.status_code}")
            print_info(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error en la petición: {e}")
        return False

def setup_simulator():
    """Configura el simulador de WhatsApp"""
    print_step(8, "Configurando simulador de WhatsApp")
    
    try:
        from whatsapp_simulator import whatsapp_simulator, notification_simulator
        
        # Conectar simulador
        result = whatsapp_simulator.connect()
        if result.success:
            print_success("Simulador de WhatsApp configurado exitosamente")
            print_info("Puedes usar el simulador para pruebas mientras configuras Evolution API")
            return True
        else:
            print_error("Error configurando simulador")
            return False
    except ImportError:
        print_error("No se pudo importar el simulador de WhatsApp")
        return False
    except Exception as e:
        print_error(f"Error configurando simulador: {e}")
        return False

def show_next_steps():
    """Muestra los siguientes pasos"""
    print_step(9, "Próximos pasos")
    
    print_info("Para completar la configuración:")
    print("1. 📱 Escanea el código QR con tu WhatsApp")
    print("2. 🔄 Ejecuta este script nuevamente para verificar la conexión")
    print("3. 🧪 Ejecuta: python test_whatsapp_integration.py")
    print("4. 🚀 Inicia tu aplicación ClickUp: python main.py")
    print("5. 🔗 Configura webhooks en ClickUp apuntando a tu servidor")
    
    print("\n📋 Configuración de webhooks en ClickUp:")
    print("- URL: http://tu-servidor:8000/api/v1/whatsapp/webhook/clickup")
    print("- Eventos: taskCreated, taskUpdated, taskCompleted")
    
    print("\n📱 Campos personalizados en ClickUp:")
    print("- Crear campo 'WhatsApp' de tipo Text")
    print("- Agregar números de teléfono en formato: 55123456789")
    
    print("\n💡 Alternativa para pruebas:")
    print("- Usa el simulador: python whatsapp_simulator.py")
    print("- Modifica core/config.py para usar el simulador")

def main():
    """Función principal"""
    print_header("Configuración Completa de Integración WhatsApp con ClickUp")
    
    # Verificar Docker
    if not check_docker():
        print_error("Docker no está disponible. Por favor instala Docker Desktop.")
        return
    
    # Intentar iniciar Evolution API
    if not start_evolution_api():
        print_warning("No se pudo iniciar Evolution API. Configurando simulador...")
        if setup_simulator():
            show_next_steps()
        return
    
    # Verificar Evolution API
    if not check_evolution_api():
        print_warning("Evolution API no está respondiendo. Configurando simulador...")
        if setup_simulator():
            show_next_steps()
        return
    
    # Crear instancia
    if not create_whatsapp_instance():
        print_error("No se pudo crear la instancia de WhatsApp")
        return
    
    # Obtener QR
    if not get_qr_code():
        print_error("No se pudo obtener el código QR")
        return
    
    # Verificar estado
    if not check_instance_status():
        print_info("La instancia no está conectada. Escanea el código QR.")
        show_next_steps()
        return
    
    # Probar envío
    if test_send_message():
        print_success("¡Integración configurada exitosamente!")
        print_info("Puedes ejecutar las pruebas: python test_whatsapp_integration.py")
    else:
        print_error("Error en la prueba de envío")
        show_next_steps()

if __name__ == "__main__":
    main()
