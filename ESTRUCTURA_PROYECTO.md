# 📁 Estructura del Proyecto ClickUp Project Manager

## 🏗️ Organización por Funcionalidad

El proyecto ha sido reorganizado para mejorar la mantenibilidad y escalabilidad, agrupando los archivos por funcionalidad específica.

### 📂 Estructura de Directorios

```
ClickUp_Project_Manager/
├── app/                   # 🚀 Aplicación principal
│   └── main.py           # Punto de entrada de FastAPI
├── auth/                  # 🔐 Sistema de autenticación
│   └── auth.py           # Módulo de autenticación y autorización
├── integrations/          # 🔌 Integraciones externas
│   ├── clickup/          # ClickUp API
│   │   ├── client.py     # Cliente principal de ClickUp
│   │   ├── sync.py       # Sincronización avanzada
│   │   └── webhook_manager.py
│   ├── whatsapp/         # WhatsApp Evolution API
│   │   ├── client.py     # Cliente WhatsApp
│   │   ├── integrator.py # Integrador principal
│   │   ├── service.py    # Servicios WhatsApp
│   │   └── simulator.py  # Simulador para desarrollo
│   └── evolution_api/    # Configuración Evolution API
│       ├── config.py
│       └── webhook_manager.py
├── monitoring/            # 📊 Monitoreo y alertas
│   ├── railway/          # Monitoreo de Railway
│   │   ├── alerts.py     # Sistema de alertas
│   │   └── log_monitor.py # Monitoreo de logs
│   └── health/           # Health checks
│       └── __init__.py
├── search/               # 🔍 Motor de búsqueda
│   ├── __init__.py
│   └── engine.py         # Motor de búsqueda semántica
├── notifications/        # 📧 Sistema de notificaciones
│   ├── manager.py        # Gestor principal
│   ├── advanced_manager.py # Gestor avanzado
│   ├── automated_manager.py # Gestor automatizado
│   ├── scheduler.py      # Programador de notificaciones
│   ├── email/           # Plantillas de email
│   │   └── templates.py
│   └── whatsapp/        # Notificaciones WhatsApp
│       └── __init__.py
├── scripts/             # 📜 Scripts organizados por categoría
│   ├── clickup/         # Scripts ClickUp
│   ├── whatsapp/        # Scripts WhatsApp
│   ├── railway/         # Scripts Railway
│   └── database/        # Scripts de base de datos
├── api/                 # 🌐 API REST con FastAPI
│   ├── routes/          # Endpoints de la API
│   │   ├── tasks.py     # Gestión de tareas
│   │   ├── users.py     # Gestión de usuarios
│   │   ├── workspaces.py # Gestión de workspaces
│   │   ├── auth.py      # Autenticación
│   │   ├── webhooks.py  # Webhooks
│   │   └── whatsapp.py  # Endpoints WhatsApp
│   └── schemas/         # Esquemas Pydantic
├── core/                # ⚙️ Núcleo del sistema
│   ├── config.py        # Configuración de la aplicación
│   ├── database.py      # Configuración de base de datos
│   └── phone_extractor.py # Extracción de números de teléfono
├── models/              # 🗄️ Modelos de SQLAlchemy
│   ├── task.py          # Modelo de tareas
│   ├── user.py          # Modelo de usuarios
│   ├── workspace.py     # Modelo de workspaces
│   └── notification_log.py # Log de notificaciones
├── utils/               # 🛠️ Utilidades y helpers
│   ├── helpers.py       # Funciones auxiliares
│   └── deployment_logger.py # Logger de despliegues
└── langgraph_tools/     # 🤖 Herramientas LangGraph
    ├── sync_workflow.py # Flujo de sincronización
    ├── rag_search_workflow.py # Flujo de búsqueda RAG
    └── error_logging_workflow.py # Flujo de logging de errores
```

## 🔄 Cambios Principales

### 1. **Aplicación Principal**
- `main.py` → `app/main.py`
- Punto de entrada centralizado en `app/`

### 2. **Integraciones Separadas**
- ClickUp: `integrations/clickup/`
- WhatsApp: `integrations/whatsapp/`
- Evolution API: `integrations/evolution_api/`

### 3. **Monitoreo Dedicado**
- Railway: `monitoring/railway/`
- Health checks: `monitoring/health/`

### 4. **Sistema de Notificaciones**
- Gestores: `notifications/`
- Plantillas: `notifications/email/`
- WhatsApp: `notifications/whatsapp/`

### 5. **Scripts Organizados**
- Por categoría: `scripts/clickup/`, `scripts/whatsapp/`, etc.

## 🚀 Comandos de Ejecución

### Desarrollo Local
```bash
uvicorn app.main:app --reload
```

### Producción
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Railway
```bash
# Procfile actualizado
web: uvicorn app.main:app
```

## 📋 Imports Actualizados

### Antes
```python
from core.clickup_client import ClickUpClient
from utils.notifications import NotificationManager
from core.search_engine import SearchEngine
```

### Después
```python
from integrations.clickup.client import ClickUpClient
from notifications.manager import NotificationManager
from search.engine import SearchEngine
```

## 🔧 Configuración

### Variables de Entorno
- `DATABASE_URL`: Base de datos PostgreSQL
- `CLICKUP_API_TOKEN`: Token de ClickUp
- `WHATSAPP_API_URL`: URL de Evolution API
- `RAILWAY_API_TOKEN`: Token de Railway

### Archivos de Configuración
- `core/config.py`: Configuración principal
- `env.example`: Variables de entorno de ejemplo
- `Procfile`: Configuración de Railway

## 📚 Documentación Adicional

- `README.md`: Documentación principal
- `ESTRUCTURA_PROYECTO.md`: Este archivo
- `migration_summary.md`: Resumen de la migración
- `dependency_analysis.md`: Análisis de dependencias

## 🛡️ Backups

- `backup_before_migration/`: Backup antes de la migración
- `backup_migration_20250904_193739/`: Backup durante la migración

## ✅ Verificación

Para verificar que todo funciona correctamente:

```bash
python verify_final.py
```

Este script verifica:
- Estructura de directorios
- Imports críticos
- Imports de API
- Imports de utilidades
