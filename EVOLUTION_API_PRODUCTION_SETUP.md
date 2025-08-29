# 🚀 Configuración de WhatsApp Real con Evolution API

## 📋 Resumen

Este sistema permite enviar notificaciones reales de WhatsApp desde ClickUp usando Evolution API. Las notificaciones se envían automáticamente cuando se crean, actualizan o completan tareas, y los números de teléfono se extraen automáticamente desde las descripciones de las tareas.

## ✨ Características Principales

- ✅ **WhatsApp Real**: Usa Evolution API para envío real de mensajes
- ✅ **Extracción Automática**: Los números se extraen desde descripciones de tareas
- ✅ **Notificaciones Automáticas**: Se envían automáticamente según eventos de ClickUp
- ✅ **Sistema de Fallback**: Puede usar simulador como respaldo
- ✅ **Rate Limiting**: Control de velocidad para evitar spam
- ✅ **Webhooks**: Manejo de eventos de WhatsApp y ClickUp
- ✅ **Modo Producción**: Configuración optimizada para uso real

## 🏗️ Arquitectura del Sistema

```
ClickUp → Webhooks → Sistema Automático → Evolution API → WhatsApp
   ↓           ↓           ↓              ↓           ↓
Tareas    Eventos    Notificaciones   Mensajes   Usuarios Reales
```

## 📦 Componentes Principales

1. **`core/evolution_api_config.py`** - Configuración específica de Evolution API
2. **`core/production_whatsapp_service.py`** - Servicio de WhatsApp de producción
3. **`core/evolution_webhook_manager.py`** - Gestor de webhooks de WhatsApp
4. **`core/automated_notification_manager.py`** - Sistema de notificaciones automáticas
5. **`setup_evolution_api.py`** - Script de configuración y prueba

## 🚀 Instalación y Configuración

### 1. Instalar Evolution API

```bash
# Clonar Evolution API
git clone https://github.com/EvolutionAPI/evolution-api.git
cd evolution-api

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env
```

### 2. Configurar Evolution API

Editar `.env` en Evolution API:

```env
# Configuración básica
SERVER_URL=http://localhost:8080
CORS_ORIGIN=*
API_KEY=tu_api_key_secreta

# Configuración de WhatsApp
WHATSAPP_DEFAULT_ANSWER=Hola! Soy el bot de ClickUp
WHATSAPP_GROUP_LIMIT=256
WHATSAPP_PAIR_LIMIT=1
```

### 3. Iniciar Evolution API

```bash
# Desarrollo
npm run start:dev

# Producción
npm run start:prod
```

### 4. Configurar el Sistema Principal

```bash
# Copiar archivo de configuración
cp env.production .env

# Editar configuración
nano .env
```

### 5. Configurar Variables de Entorno

```env
# WhatsApp Evolution API
WHATSAPP_EVOLUTION_URL=http://localhost:8080
WHATSAPP_EVOLUTION_API_KEY=tu_api_key_secreta
WHATSAPP_INSTANCE_NAME=clickup-manager
WHATSAPP_WEBHOOK_URL=https://tu-dominio.com/api/webhooks/whatsapp

# ClickUp
CLICKUP_API_TOKEN=tu_token_clickup
CLICKUP_WORKSPACE_ID=tu_workspace_id
```

## 🔧 Configuración Detallada

### Configuración de Evolution API

1. **Crear Instancia**: 
   - POST `/instance/create`
   - Nombre: `clickup-manager`
   - Token: Tu API key

2. **Conectar WhatsApp**:
   - GET `/instance/qrcode/clickup-manager`
   - Escanear código QR con tu WhatsApp

3. **Verificar Estado**:
   - GET `/instance/status/clickup-manager`
   - Debe mostrar `"status": "open"`

### Configuración de ClickUp

1. **Crear Webhook**:
   - Ir a Settings → Apps → Webhooks
   - URL: `https://tu-dominio.com/api/webhooks/clickup`
   - Eventos: `taskCreated`, `taskUpdated`, `taskCompleted`

2. **Configurar Campos Personalizados** (opcional):
   - Crear campo "WhatsApp" tipo texto
   - O usar campos existentes como "Description"

## 🧪 Pruebas y Verificación

### Ejecutar Script de Configuración

```bash
python setup_evolution_api.py
```

Este script verifica:
- ✅ Configuración básica
- ✅ Conexión a Evolution API
- ✅ Estado de instancia de WhatsApp
- ✅ Envío de mensajes
- ✅ Configuración de webhooks
- ✅ Sistema automático

### Pruebas Manuales

1. **Crear Tarea de Prueba**:
   ```
   Título: Prueba WhatsApp
   Descripción: Contacto: +525512345678
   ```

2. **Verificar Notificación**:
   - Debe recibirse en WhatsApp
   - Formato: Mensaje estructurado con emojis

3. **Verificar Logs**:
   ```bash
   tail -f logs/production.log
   ```

## 📱 Formato de Mensajes

### Plantillas Disponibles

- **Tarea Creada**: 🆕 Nueva tarea creada: {title}
- **Tarea Actualizada**: ✏️ Tarea actualizada: {title}
- **Tarea Completada**: ✅ Tarea completada: {title}
- **Vence Pronto**: ⏰ Tarea vence pronto: {title} - Vence: {due_date}
- **Tarea Vencida**: 🚨 Tarea vencida: {title} - Vencida desde: {due_date}

### Variables Disponibles

- `{title}` - Título de la tarea
- `{description}` - Descripción (truncada a 200 caracteres)
- `{due_date}` - Fecha de vencimiento
- `{assignee}` - Usuario asignado
- `{priority}` - Prioridad de la tarea
- `{task_id}` - ID de la tarea

## 🔍 Extracción de Números de Teléfono

### Campos Revisados

1. **Descripción de la tarea**
2. **Campos personalizados**
3. **Comentarios**

### Formatos Soportados

- **Internacional**: `+52 55 1234 5678`
- **México**: `55 1234 5678`
- **Con paréntesis**: `+52 (55) 1234-5678`
- **WhatsApp**: `wa.me/525512345678`
- **Con etiquetas**: `WhatsApp: +525512345678`

### Validación

- ✅ Mínimo 10 dígitos
- ✅ Código de país requerido (52 para México)
- ✅ Eliminación de duplicados
- ✅ Formateo automático

## 🚨 Solución de Problemas

### Problemas Comunes

1. **Evolution API no responde**:
   ```bash
   # Verificar que esté corriendo
   curl http://localhost:8080/health
   
   # Verificar logs
   tail -f evolution-api/logs/app.log
   ```

2. **WhatsApp no conecta**:
   - Verificar código QR
   - Reiniciar instancia
   - Verificar conexión a internet

3. **Notificaciones no se envían**:
   - Verificar números de teléfono
   - Verificar configuración de Evolution API
   - Revisar logs del sistema

4. **Rate Limiting**:
   - Ajustar `max_messages_per_minute` en configuración
   - Verificar límites de Evolution API

### Logs y Debugging

```bash
# Logs del sistema principal
tail -f logs/production.log

# Logs de Evolution API
tail -f evolution-api/logs/app.log

# Estado del sistema
curl http://localhost:8000/api/status/whatsapp
```

## 📊 Monitoreo y Métricas

### Endpoints de Estado

- **Estado General**: `GET /api/status/whatsapp`
- **Estado de Evolution API**: `GET /api/status/evolution`
- **Estado de Webhooks**: `GET /api/status/webhooks`
- **Estado Automático**: `GET /api/status/automated`

### Métricas Disponibles

- Mensajes enviados por minuto/hora
- Tasa de éxito/fallo
- Estado de conexión
- Cola de notificaciones
- Notificaciones programadas

## 🔒 Seguridad

### Recomendaciones

1. **API Keys**: Usar claves largas y complejas
2. **Webhooks**: Verificar secretos de webhook
3. **CORS**: Restringir orígenes permitidos
4. **Rate Limiting**: Habilitar control de velocidad
5. **Logs**: Monitorear actividad sospechosa

### Variables Sensibles

```env
# Cambiar en producción
JWT_SECRET_KEY=clave_muy_larga_y_compleja
SECRET_KEY=otra_clave_muy_larga_y_compleja
WHATSAPP_EVOLUTION_API_KEY=tu_api_key_real
```

## 🚀 Despliegue en Producción

### Railway (Recomendado)

1. **Configurar Variables de Entorno**:
   - Usar Railway Dashboard
   - Configurar todas las variables del `.env`

2. **Configurar Evolution API**:
   - Desplegar en servidor separado
   - Configurar dominio público
   - Actualizar `WHATSAPP_EVOLUTION_URL`

3. **Configurar Webhooks**:
   - Actualizar URLs en ClickUp
   - Verificar HTTPS

### Docker

```bash
# Evolution API
docker run -d \
  --name evolution-api \
  -p 8080:8080 \
  -v evolution-data:/app/instances \
  evolution-api:latest

# Sistema principal
docker run -d \
  --name clickup-manager \
  -p 8000:8000 \
  --env-file .env \
  clickup-manager:latest
```

## 📚 Recursos Adicionales

- [Evolution API Documentation](https://doc.evolution-api.com/)
- [ClickUp API Reference](https://clickup.com/api)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)

## 🆘 Soporte

Para problemas o preguntas:
1. Revisar logs del sistema
2. Verificar configuración
3. Probar con script de configuración
4. Consultar documentación de Evolution API

---

**¡El sistema está listo para enviar notificaciones reales de WhatsApp desde ClickUp!** 🎉
