# 📱 Integración de WhatsApp con ClickUp Project Manager

Esta integración permite enviar notificaciones automáticas de tareas de ClickUp a través de WhatsApp utilizando la API de Evolution.

## 🚀 Características Principales

- **Notificaciones automáticas** de tareas creadas, actualizadas y completadas
- **Recordatorios automáticos** para tareas que vencen pronto
- **Alertas de tareas vencidas** con notificaciones urgentes
- **Integración con webhooks** de ClickUp para eventos en tiempo real
- **Envío masivo** de notificaciones a múltiples destinatarios
- **Mensajes multimedia** (imágenes, documentos, audio, video)
- **Plantillas personalizables** para diferentes tipos de notificaciones
- **Gestión de contactos** y historial de chat

## 📋 Requisitos Previos

### 1. API de Evolution para WhatsApp
- Instalar y configurar [Evolution API](https://github.com/EvolutionAPI/evolution-api)
- Crear una instancia de WhatsApp
- Obtener la API key de acceso

### 2. Dependencias del Proyecto
```bash
pip install -r requirements.txt
```

### 3. Configuración de Variables de Entorno
Crear o actualizar tu archivo `.env` con las siguientes variables:

```env
# Configuración de WhatsApp Evolution API
WHATSAPP_ENABLED=True
WHATSAPP_EVOLUTION_URL=http://localhost:8080
WHATSAPP_EVOLUTION_API_KEY=your_evolution_api_key_here
WHATSAPP_INSTANCE_NAME=clickup-manager
WHATSAPP_WEBHOOK_URL=http://localhost:8000/api/v1/whatsapp/webhook/clickUp
WHATSAPP_NOTIFICATIONS_ENABLED=True

# Configuración de notificaciones de WhatsApp
WHATSAPP_TASK_CREATED=True
WHATSAPP_TASK_UPDATED=True
WHATSAPP_TASK_COMPLETED=True
WHATSAPP_TASK_DUE_SOON=True
WHATSAPP_TASK_OVERDUE=True

# Campos personalizados de ClickUp para WhatsApp
TASK_WHATSAPP_FIELDS=WhatsApp,Telefono,Phone
```

## 🔧 Instalación y Configuración

### 1. Configurar Evolution API
```bash
# Clonar el repositorio de Evolution API
git clone https://github.com/EvolutionAPI/evolution-api.git
cd evolution-api

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu configuración

# Ejecutar con Docker
docker-compose up -d
```

### 2. Crear Instancia de WhatsApp
```bash
# Crear una nueva instancia
curl -X POST "http://localhost:8080/instance/create" \
  -H "Content-Type: application/json" \
  -H "apikey: YOUR_API_KEY" \
  -d '{
    "instanceName": "clickup-manager",
    "token": "your_token_here",
    "qrcode": true,
    "number": "55123456789"
  }'
```

### 3. Conectar WhatsApp
1. Obtener el código QR:
```bash
curl "http://localhost:8080/instance/qrcode/clickup-manager" \
  -H "apikey: YOUR_API_KEY"
```

2. Escanear el código QR con tu WhatsApp
3. Verificar el estado de conexión:
```bash
curl "http://localhost:8080/instance/status/clickup-manager" \
  -H "apikey: YOUR_API_KEY"
```

## 📱 Uso de la API

### Endpoints Principales

#### Estado y Configuración
- `GET /api/v1/whatsapp/status` - Estado de la integración
- `GET /api/v1/whatsapp/instance/status` - Estado de la instancia
- `GET /api/v1/whatsapp/instance/qr` - Código QR para conectar
- `DELETE /api/v1/whatsapp/instance/logout` - Cerrar sesión

#### Envío de Mensajes
- `POST /api/v1/whatsapp/send/message` - Enviar mensaje de texto
- `POST /api/v1/whatsapp/send/media` - Enviar mensaje multimedia

#### Notificaciones de Tareas
- `POST /api/v1/whatsapp/notify/task` - Notificar tarea específica
- `POST /api/v1/whatsapp/notify/bulk` - Notificaciones masivas

#### Automatización
- `POST /api/v1/whatsapp/automation/reminders` - Recordatorios automáticos
- `POST /api/v1/whatsapp/automation/overdue` - Alertas de tareas vencidas

#### Webhooks
- `POST /api/v1/whatsapp/webhook/clickup` - Procesar webhooks de ClickUp

### Ejemplos de Uso

#### 1. Enviar Mensaje Simple
```python
import requests

url = "http://localhost:8000/api/v1/whatsapp/send/message"
data = {
    "phone_number": "+525512345678",
    "message": "¡Hola! Tienes una nueva tarea asignada.",
    "message_type": "text"
}

response = requests.post(url, json=data)
print(response.json())
```

#### 2. Notificar Tarea de ClickUp
```python
url = "http://localhost:8000/api/v1/whatsapp/notify/task"
data = {
    "task_id": "task_id_from_clickup",
    "phone_numbers": ["+525512345678", "+525598765432"],
    "custom_message": "Nueva tarea urgente asignada"
}

response = requests.post(url, json=data)
print(response.json())
```

#### 3. Enviar Recordatorios Automáticos
```python
url = "http://localhost:8000/api/v1/whatsapp/automation/reminders"
params = {"hours_before": 24}

response = requests.post(url, params=params)
print(response.json())
```

## 🔄 Configuración de Webhooks en ClickUp

### 1. Crear Webhook en ClickUp
1. Ir a **Settings** > **Integrations** > **Webhooks**
2. Hacer clic en **Create Webhook**
3. Configurar:
   - **URL**: `https://tu-dominio.com/api/v1/whatsapp/webhook/clickup`
   - **Events**: Seleccionar eventos deseados (taskCreated, taskUpdated, etc.)
   - **Secret**: Configurar secreto para validación

### 2. Configurar Campos Personalizados
En ClickUp, crear campos personalizados para almacenar números de WhatsApp:
- **Campo**: `WhatsApp` o `Telefono`
- **Tipo**: Text
- **Descripción**: Número de WhatsApp para notificaciones

## 📊 Configuración de Campos Personalizados

### Campos Soportados
La integración busca automáticamente en los siguientes campos:
- `WhatsApp`
- `Telefono`
- `Phone`

### Formato de Números
Los números se formatean automáticamente:
- **Entrada**: `5512345678`, `(55) 1234-5678`, `+55 12 3456 7890`
- **Salida**: `+525512345678` (formato internacional)

## 🧪 Pruebas y Debugging

### Script de Pruebas
Ejecutar el script de pruebas incluido:
```bash
python test_whatsapp_integration.py
```

### Verificar Estado
```bash
# Estado general
curl "http://localhost:8000/api/v1/whatsapp/status"

# Estado de la instancia
curl "http://localhost:8000/api/v1/whatsapp/instance/status"

# Verificación de salud
curl "http://localhost:8000/api/v1/whatsapp/health"
```

### Logs y Monitoreo
- Los logs se guardan en `logs/app.log`
- Nivel de logging configurable via `LOG_LEVEL`
- Errores y eventos importantes se registran automáticamente

## 🚨 Solución de Problemas

### Problemas Comunes

#### 1. Instancia No Conectada
```bash
# Verificar estado
curl "http://localhost:8080/instance/status/clickup-manager"

# Regenerar QR si es necesario
curl "http://localhost:8080/instance/qrcode/clickup-manager"
```

#### 2. Error de Autenticación
- Verificar `WHATSAPP_EVOLUTION_API_KEY` en `.env`
- Confirmar que la API key sea válida
- Verificar permisos de la instancia

#### 3. Mensajes No Enviados
- Verificar formato del número de teléfono
- Confirmar que el destinatario tenga WhatsApp
- Revisar logs para errores específicos

#### 4. Webhooks No Funcionando
- Verificar URL del webhook en ClickUp
- Confirmar que el endpoint sea accesible públicamente
- Revisar configuración de eventos en ClickUp

### Debugging Avanzado
```python
# Habilitar logging detallado
import logging
logging.basicConfig(level=logging.DEBUG)

# Verificar configuración
from core.config import settings
print(f"WhatsApp enabled: {settings.WHATSAPP_ENABLED}")
print(f"Evolution URL: {settings.WHATSAPP_EVOLUTION_URL}")
```

## 🔒 Seguridad y Mejores Prácticas

### 1. Autenticación
- Usar API keys seguras y únicas
- Rotar API keys regularmente
- Limitar acceso por IP si es posible

### 2. Validación de Datos
- Validar números de teléfono antes del envío
- Sanitizar mensajes de entrada
- Implementar rate limiting para evitar spam

### 3. Privacidad
- No almacenar números de teléfono en logs
- Implementar consentimiento para notificaciones
- Cumplir con regulaciones locales de WhatsApp Business

## 📈 Monitoreo y Métricas

### Métricas Recomendadas
- **Tasa de entrega**: Mensajes enviados vs. entregados
- **Tiempo de respuesta**: Latencia de envío
- **Errores**: Tipos y frecuencia de errores
- **Uso**: Número de notificaciones por día/semana

### Alertas
- Configurar alertas para fallos de conexión
- Monitorear tasa de errores
- Alertas para instancias desconectadas

## 🔮 Funcionalidades Futuras

- **Plantillas de mensajes** personalizables
- **Programación de envío** de notificaciones
- **Integración con calendario** para recordatorios
- **Chatbot interactivo** para consultas de tareas
- **Análisis de engagement** de notificaciones
- **Integración con otros canales** (SMS, email)

## 📞 Soporte

### Recursos Útiles
- [Documentación de Evolution API](https://doc.evolution-api.com/)
- [API de ClickUp](https://clickup.com/api)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)

### Reportar Problemas
- Crear issue en el repositorio del proyecto
- Incluir logs y configuración relevante
- Describir pasos para reproducir el problema

---

**¡Con esta integración, tu equipo de ClickUp nunca más se perderá una tarea importante! 📱✨**
