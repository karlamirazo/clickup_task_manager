# 🚀 Sistema de Monitoreo de Railway - Guía Completa

**ClickUp Project Manager - Railway Monitoring System**

---

## 📋 Índice

1. [Descripción General](#descripción-general)
2. [Características Principales](#características-principales)
3. [Instalación y Configuración](#instalación-y-configuración)
4. [Uso del Sistema](#uso-del-sistema)
5. [Dashboard Web](#dashboard-web)
6. [API de Monitoreo](#api-de-monitoreo)
7. [Sistema de Alertas](#sistema-de-alertas)
8. [Ejemplos de Uso](#ejemplos-de-uso)
9. [Solución de Problemas](#solución-de-problemas)
10. [Mantenimiento](#mantenimiento)

---

## 🎯 Descripción General

El **Sistema de Monitoreo de Railway** es una solución integral para supervisar la salud, performance y estabilidad de tu aplicación desplegada en Railway. Proporciona monitoreo en tiempo real, alertas automáticas y un dashboard web interactivo.

### ¿Qué monitorea?

- ✅ **Tiempo de respuesta** del sistema
- ✅ **Tasa de errores** por hora  
- ✅ **Uso de CPU y memoria**
- ✅ **Estado de la base de datos**
- ✅ **Conectividad general**
- ✅ **Logs del sistema**
- ✅ **Métricas de performance**

### ¿Cómo te avisa?

- 📧 **Email** (SMTP configurado)
- 📱 **WhatsApp** (Evolution API)
- 📊 **Dashboard web** en tiempo real
- 📝 **Logs estructurados**
- 🔔 **Integración con LangGraph**

---

## ⭐ Características Principales

### 🔍 Monitoreo Inteligente
- **Health checks** automáticos cada 30 segundos
- **Detección de patrones** de errores
- **Análisis de tendencias** de performance
- **Alertas predictivas** basadas en thresholds

### 🚨 Sistema de Alertas Avanzado
- **4 niveles de alerta**: INFO, WARNING, ERROR, CRITICAL
- **6 tipos de problemas**: Sistema caído, errores altos, respuesta lenta, DB error, CPU/memoria altos
- **Cooldown automático** para evitar spam de notificaciones
- **Resolución automática** de alertas cuando se soluciona el problema

### 📊 Dashboard Interactivo
- **Métricas en tiempo real** con gráficos
- **Estado visual** del sistema
- **Logs recientes** con filtros
- **Controles del sistema** desde la web
- **Responsive design** para móviles

### 🔧 API REST Completa
- **15+ endpoints** para gestión del monitoreo
- **Exportación de datos** en JSON/CSV
- **Control remoto** del sistema
- **Métricas históricas** personalizables

---

## 🛠️ Instalación y Configuración

### Prerequisitos

```bash
# Verificar Python 3.8+
python --version

# Instalar dependencias
pip install -r requirements.txt
```

### Dependencias Principales

```txt
aiohttp>=3.8.0      # Cliente HTTP asíncrono
psutil>=5.9.0       # Métricas del sistema  
fastapi>=0.68.0     # API REST
pydantic>=1.8.0     # Validación de datos
chart.js            # Gráficos del dashboard
```

### Variables de Entorno

Configura estas variables en Railway:

```env
# Sistema de monitoreo
RAILWAY_MONITORING_ENABLED=True
RAILWAY_MONITORING_INTERVAL=30
RAILWAY_ALERT_ERROR_THRESHOLD=5
RAILWAY_ALERT_RESPONSE_THRESHOLD=5.0

# Notificaciones por email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password
SMTP_FROM=tu_email@gmail.com

# Notificaciones por WhatsApp
WHATSAPP_ENABLED=True
WHATSAPP_NOTIFICATIONS_ENABLED=True
WHATSAPP_EVOLUTION_URL=tu_evolution_api_url

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/railway_monitor.log
```

### Configuración en Railway

1. **Variables de entorno**: Configura las variables arriba en tu proyecto Railway
2. **Reiniciar servicio**: Railway aplicará automáticamente los cambios
3. **Verificar**: Accede a `/railway-monitor` para ver el dashboard

---

## 🚀 Uso del Sistema

### 1. Inicio Rápido

```bash
# Verificar que todo esté configurado
python scripts/start_railway_monitoring.py --check-only

# Monitoreo por 1 hora
python scripts/start_railway_monitoring.py --duration 1

# Monitoreo continuo (Ctrl+C para detener)
python scripts/start_railway_monitoring.py
```

### 2. Opciones Avanzadas

```bash
# Intervalo de 15 segundos
python scripts/start_railway_monitoring.py --interval 15

# Sin alertas automáticas
python scripts/start_railway_monitoring.py --no-alerts

# Thresholds personalizados
python scripts/start_railway_monitoring.py \
  --error-threshold 10 \
  --response-threshold 3.0

# Probar notificaciones
python scripts/start_railway_monitoring.py --test-notifications

# Ver información del sistema
python scripts/start_railway_monitoring.py --info
```

### 3. Acceso al Dashboard

Una vez iniciado tu aplicación, puedes acceder al dashboard en:

```
https://tu-app.up.railway.app/railway-monitor
```

---

## 📊 Dashboard Web

### Secciones Principales

#### 🎛️ **Header del Sistema**
- Estado actual (🟢 Operativo, 🟡 Degradado, 🔴 Error)
- Timestamp de última actualización
- Enlaces rápidos a métricas

#### 📈 **Métricas Principales**
- **Tiempo de Respuesta**: ms promedio
- **Errores por Hora**: conteo de errores
- **Uso de CPU**: porcentaje actual
- **Uso de Memoria**: porcentaje actual

#### 📊 **Gráficos Interactivos**
- **Performance Chart**: Líneas de tiempo de métricas (24h)
- **Alerts Chart**: Distribución de tipos de alertas

#### 🔔 **Alertas Activas**
- Lista de problemas actuales
- Nivel de severidad con colores
- Timestamp y detalles técnicos

#### 🎮 **Controles del Sistema**
- 🔄 **Actualizar Datos**: Refresh manual
- 📥 **Exportar Logs**: Descarga en JSON
- 📱 **Probar Alertas**: Test de notificaciones
- ▶️ **Iniciar/Detener**: Control del monitoreo

#### 📝 **Logs Recientes**
- Últimas 100 entradas de logs
- Filtros por nivel (INFO, WARNING, ERROR)
- Formato legible con timestamps

### Características del Dashboard

- ✅ **Actualización automática** cada 30 segundos
- ✅ **Responsive design** para móviles
- ✅ **Tema moderno** con colores consistentes
- ✅ **Gráficos interactivos** con Chart.js
- ✅ **Indicadores visuales** de estado
- ✅ **Controles en tiempo real**

---

## 🔌 API de Monitoreo

### Endpoints Principales

#### Status del Sistema
```http
GET /api/v1/railway/status
```
Respuesta:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "system_status": "healthy",
  "railway_url": "https://tu-app.up.railway.app",
  "monitoring_active": true,
  "active_alerts_count": 0,
  "environment": "production",
  "version": "1.0.0"
}
```

#### Métricas Actuales
```http
GET /api/v1/railway/metrics
```
Respuesta:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "response_time": 234.5,
  "error_rate": 2,
  "cpu_usage": 45.2,
  "memory_usage": 67.8,
  "active_alerts": 1,
  "system_status": "healthy"
}
```

#### Historial de Métricas
```http
GET /api/v1/railway/metrics/history?hours=24
```

#### Alertas del Sistema
```http
GET /api/v1/railway/alerts?active_only=true
```

#### Logs Recientes
```http
GET /api/v1/railway/logs?limit=100&level=ERROR
```

### Control del Monitoreo

#### Iniciar Monitoreo
```http
POST /api/v1/railway/monitoring/start
Content-Type: application/json

{
  "interval": 30,
  "duration_hours": 2,
  "enable_alerts": true,
  "alert_threshold_errors": 5,
  "alert_threshold_response_time": 5.0
}
```

#### Detener Monitoreo
```http
POST /api/v1/railway/monitoring/stop
```

#### Estado del Monitoreo
```http
GET /api/v1/railway/monitoring/status
```

### Alertas Personalizadas

#### Crear Alerta
```http
POST /api/v1/railway/alerts
Content-Type: application/json

{
  "level": "warning",
  "title": "Problema Personalizado",
  "message": "Descripción del problema",
  "details": {
    "custom_field": "custom_value"
  }
}
```

### Utilidades

#### Probar Notificaciones
```http
POST /api/v1/railway/test/notifications
```

#### Exportar Logs
```http
GET /api/v1/railway/export/logs?date=2024-01-15&format=json
```

#### Health Check
```http
GET /api/v1/railway/health
```

---

## 🚨 Sistema de Alertas

### Niveles de Alerta

| Nivel | Color | Descripción | Notificación |
|-------|--------|-------------|--------------|
| **INFO** | 🔵 Azul | Informativo | No |
| **WARNING** | 🟡 Amarillo | Atención requerida | Email |
| **ERROR** | 🟠 Naranja | Problema serio | Email + WhatsApp |
| **CRITICAL** | 🔴 Rojo | Sistema en riesgo | Email + WhatsApp + Log |

### Tipos de Alertas

#### 🚨 **CRITICAL - Sistema No Responde**
- **Trigger**: Endpoint principal no responde
- **Threshold**: 3 fallos consecutivos
- **Acción**: Notificación inmediata

#### ❌ **ERROR - Tasa Alta de Errores**
- **Trigger**: >5 errores por hora (configurable)
- **Threshold**: Basado en `alert_threshold_errors`
- **Acción**: Análisis de patrones de errores

#### ⚠️ **WARNING - Respuesta Lenta**
- **Trigger**: Tiempo >5 segundos (configurable)
- **Threshold**: Basado en `alert_threshold_response_time`
- **Acción**: Monitoreo de performance

#### 🗄️ **ERROR - Error de Base de Datos**
- **Trigger**: Endpoints de DB fallan
- **Threshold**: 2+ endpoints con error
- **Acción**: Verificación de conectividad

#### 🔥 **WARNING - CPU Alto**
- **Trigger**: CPU >85%
- **Threshold**: Sostenido por 2+ mediciones
- **Acción**: Monitoreo de recursos

#### 💾 **WARNING - Memoria Alta**
- **Trigger**: Memoria >90%
- **Threshold**: Sostenido por 2+ mediciones
- **Acción**: Monitoreo de memoria

### Configuración de Alertas

#### Thresholds por Defecto
```python
thresholds = {
    "error_rate_per_hour": 5,
    "response_time_seconds": 5.0,
    "cpu_percent": 85.0,
    "memory_percent": 90.0,
    "consecutive_failures": 3
}
```

#### Cooldown de Notificaciones
- **Tiempo**: 15 minutos entre notificaciones del mismo tipo
- **Propósito**: Evitar spam de alertas
- **Excepción**: Alertas CRITICAL siempre se envían

#### Resolución Automática
- Las alertas se resuelven automáticamente cuando la condición mejora
- Se envía notificación de resolución para alertas CRITICAL y ERROR
- Se registra el tiempo de duración del problema

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Monitoreo Básico (1 hora)

```bash
# Terminal 1: Iniciar monitoreo
python scripts/start_railway_monitoring.py --duration 1

# Terminal 2: Ver logs en tiempo real
tail -f logs/railway_monitor.log

# Browser: Ver dashboard
open https://tu-app.up.railway.app/railway-monitor
```

**Resultado esperado:**
- ✅ Monitoreo activo por 1 hora
- ✅ Logs guardados en `logs/railway_monitor_YYYYMMDD.json`
- ✅ Reporte final en `logs/railway_monitor_report_YYYYMMDD_HHMMSS.json`

### Ejemplo 2: Monitoreo de Alta Frecuencia

```bash
# Verificaciones cada 10 segundos con alertas estrictas
python scripts/start_railway_monitoring.py \
  --interval 10 \
  --error-threshold 3 \
  --response-threshold 2.0
```

**Uso recomendado:**
- 🎯 Durante deployments críticos
- 🎯 Después de cambios importantes
- 🎯 Períodos de alto tráfico

### Ejemplo 3: Solo Monitoreo (Sin Alertas)

```bash
# Monitoreo silencioso para recolección de datos
python scripts/start_railway_monitoring.py \
  --no-alerts \
  --duration 24
```

**Uso recomendado:**
- 📊 Análisis de performance
- 📊 Recolección de métricas base
- 📊 Testing de nuevas features

### Ejemplo 4: Verificación Rápida del Sistema

```bash
# Solo verificar que todo esté funcionando
python scripts/start_railway_monitoring.py --check-only
```

**Output esperado:**
```
🔍 Verificando dependencias...
   ✅ aiohttp
   ✅ psutil
   ✅ fastapi
✅ Todas las dependencias están instaladas

🔧 Verificando configuración...
   ✅ ENVIRONMENT: production
   ✅ WHATSAPP_ENABLED: True
   ✅ SMTP_HOST: smtp.gmail.com
✅ Configuración verificada

🌐 Probando conectividad...
   ✅ Railway responde: HTTP 200
✅ Verificación del sistema completada
```

### Ejemplo 5: Usar la API desde Python

```python
import asyncio
import aiohttp

async def get_system_metrics():
    """Obtener métricas del sistema"""
    async with aiohttp.ClientSession() as session:
        url = "https://tu-app.up.railway.app/api/v1/railway/metrics"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                print(f"CPU: {data['cpu_usage']}%")
                print(f"Memoria: {data['memory_usage']}%")
                print(f"Respuesta: {data['response_time']}ms")
                print(f"Errores: {data['error_rate']}/hora")
            else:
                print(f"Error: {response.status}")

# Ejecutar
asyncio.run(get_system_metrics())
```

### Ejemplo 6: Crear Alerta Personalizada

```python
import asyncio
import aiohttp

async def create_custom_alert():
    """Crear alerta personalizada"""
    alert_data = {
        "level": "warning",
        "title": "🔧 Mantenimiento Programado",
        "message": "El sistema entrará en mantenimiento en 30 minutos",
        "details": {
            "maintenance_start": "2024-01-15T14:00:00Z",
            "duration": "30 minutes",
            "affected_services": ["database", "api"]
        }
    }
    
    async with aiohttp.ClientSession() as session:
        url = "https://tu-app.up.railway.app/api/v1/railway/alerts"
        async with session.post(url, json=alert_data) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Alerta creada: {result['message']}")
            else:
                print(f"❌ Error: {response.status}")

# Ejecutar
asyncio.run(create_custom_alert())
```

---

## 🔧 Solución de Problemas

### Problemas Comunes

#### 1. **Error: ModuleNotFoundError**

```bash
❌ Error importando módulos: No module named 'aiohttp'
```

**Solución:**
```bash
pip install -r requirements.txt
# o específicamente:
pip install aiohttp psutil fastapi pydantic
```

#### 2. **Error de conectividad a Railway**

```bash
❌ Error de conectividad: Cannot connect to host
```

**Posibles causas:**
- Railway app no está desplegada
- URL incorrecta en configuración
- Firewall bloqueando conexiones

**Solución:**
```bash
# Verificar que la app esté funcionando
curl https://tu-app.up.railway.app/debug

# Verificar variables de entorno
python -c "from core.config import settings; print(settings.ENVIRONMENT)"
```

#### 3. **Notificaciones no se envían**

```bash
❌ Error enviando email: Authentication failed
```

**Solución para email:**
```bash
# Verificar configuración SMTP
python -c "
from core.config import settings
print(f'SMTP_HOST: {settings.SMTP_HOST}')
print(f'SMTP_USER: {settings.SMTP_USER}')
print(f'SMTP_PASSWORD: {len(settings.SMTP_PASSWORD)} caracteres')
"

# Probar notificaciones
python scripts/start_railway_monitoring.py --test-notifications
```

**Solución para WhatsApp:**
- Verificar que Evolution API esté funcionando
- Verificar `WHATSAPP_ENABLED=True`
- Verificar `WHATSAPP_NOTIFICATIONS_ENABLED=True`

#### 4. **Dashboard no carga**

```bash
❌ 404 Not Found: /railway-monitor
```

**Solución:**
```bash
# Verificar que el archivo existe
ls -la static/railway_dashboard.html

# Verificar que la ruta esté registrada en main.py
grep -n "railway-monitor" main.py

# Reiniciar la aplicación
# (en Railway se hace automáticamente al hacer deploy)
```

#### 5. **Logs no se guardan**

```bash
❌ Error procesando logs: Permission denied
```

**Solución:**
```bash
# Crear directorio de logs
mkdir -p logs

# Verificar permisos
ls -la logs/

# En Railway, los logs se guardan en memoria, usar la API para exportar
curl https://tu-app.up.railway.app/api/v1/railway/export/logs
```

### Debugging Avanzado

#### Verificar Estado del Monitor

```python
# En una consola Python
from core.railway_log_monitor import RailwayLogMonitor
monitor = RailwayLogMonitor()
print(f"Monitoring active: {monitor.monitoring_active}")
print(f"Log buffer size: {len(monitor.log_buffer)}")
```

#### Verificar Estado de Alertas

```python
from core.railway_alerts import alerts_manager
print(f"Active alerts: {len(alerts_manager.get_active_alerts())}")
print(f"Alert history: {len(alerts_manager.get_alert_history(24))}")
```

#### Ver Logs Detallados

```bash
# Logs del sistema
tail -f logs/railway_monitor.log

# Logs de la aplicación principal
tail -f logs/app.log

# En Railway, usar Railway CLI
railway logs
```

---

## 🔄 Mantenimiento

### Tareas de Mantenimiento Regular

#### Diario
- ✅ Verificar que el dashboard está accesible
- ✅ Revisar alertas activas
- ✅ Verificar últimas métricas

#### Semanal  
- ✅ Exportar y revisar logs de la semana
- ✅ Verificar uso de recursos (CPU/memoria tendencias)
- ✅ Probar sistema de notificaciones
- ✅ Limpiar logs antiguos (si aplicable)

#### Mensual
- ✅ Revisar y ajustar thresholds de alertas
- ✅ Analizar patrones de errores históricos
- ✅ Optimizar configuración basada en datos recolectados
- ✅ Actualizar documentación si hay cambios

### Scripts de Mantenimiento

#### Verificación de Salud Semanal
```bash
#!/bin/bash
# weekly_health_check.sh

echo "🏥 Verificación de salud semanal - $(date)"

# Verificar sistema
python scripts/start_railway_monitoring.py --check-only

# Probar notificaciones
python scripts/start_railway_monitoring.py --test-notifications

# Exportar métricas de la semana
curl "https://tu-app.up.railway.app/api/v1/railway/metrics/history?hours=168" \
  -o "reports/weekly_metrics_$(date +%Y%m%d).json"

echo "✅ Verificación completada"
```

#### Limpieza de Logs
```bash
#!/bin/bash
# cleanup_logs.sh

echo "🧹 Limpiando logs antiguos..."

# Mantener solo logs de los últimos 30 días
find logs/ -name "*.json" -mtime +30 -delete
find logs/ -name "*.log" -mtime +30 -delete

echo "✅ Limpieza completada"
```

### Actualizaciones del Sistema

#### Actualizar Dependencias
```bash
# Actualizar requirements.txt
pip list --outdated
pip install --upgrade aiohttp psutil fastapi pydantic

# Generar nuevo requirements.txt
pip freeze > requirements.txt
```

#### Backup de Configuración
```bash
# Backup de configuración actual
cp railway.env.example railway.env.backup.$(date +%Y%m%d)
cp core/config.py core/config.py.backup.$(date +%Y%m%d)
```

### Monitoreo del Monitoreo

Para asegurar que el sistema de monitoreo esté siempre funcionando:

#### Cron Job (si tienes acceso a cron)
```cron
# Verificar cada hora que el monitoreo esté activo
0 * * * * curl -f https://tu-app.up.railway.app/api/v1/railway/health || echo "Monitor down!" | mail admin@tu-dominio.com
```

#### Health Check Externo
Usar servicios como UptimeRobot o Pingdom para monitorear:
- `https://tu-app.up.railway.app/api/v1/railway/health`
- `https://tu-app.up.railway.app/railway-monitor`

---

## 📞 Soporte y Contacto

### Recursos de Ayuda

1. **Documentación técnica**: Este archivo
2. **Logs del sistema**: `logs/railway_monitor.log`
3. **Dashboard de estado**: `/railway-monitor`
4. **API de diagnóstico**: `/api/v1/railway/health`

### Información para Soporte

Cuando contactes soporte, incluye:

```bash
# Información del sistema
python --version
pip list | grep -E "(aiohttp|psutil|fastapi|pydantic)"

# Estado de la configuración
python -c "
from core.config import settings
print(f'Environment: {settings.ENVIRONMENT}')
print(f'Version: {settings.VERSION}')
print(f'Railway URL: Railway app URL')
"

# Últimos logs (últimas 20 líneas)
tail -20 logs/railway_monitor.log

# Estado actual del sistema
curl https://tu-app.up.railway.app/api/v1/railway/status
```

---

## 🎉 ¡Felicitaciones!

Has configurado exitosamente el **Sistema de Monitoreo de Railway** para tu aplicación ClickUp Project Manager. 

### ¿Qué sigue?

1. **Personaliza los thresholds** según tus necesidades
2. **Configura las notificaciones** para tu equipo
3. **Monitorea regularmente** el dashboard
4. **Ajusta la configuración** basándose en los datos recolectados

### Recursos Adicionales

- 📚 [Documentación de Railway](https://docs.railway.app/)
- 📚 [FastAPI Documentation](https://fastapi.tiangolo.com/)
- 📚 [Chart.js Documentation](https://www.chartjs.org/)

---

**¡Tu sistema ahora está completamente monitoreado! 🚀**

*Última actualización: Enero 2024*
