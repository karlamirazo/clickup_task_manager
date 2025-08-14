# ClickUp Project Manager - Agente Inteligente

Un módulo completo de gestión de tareas con la API de ClickUp que incluye automatización, reportes e integraciones.

## 🚀 Características

### Gestión de Tareas
- ✅ Crear, actualizar y eliminar tareas
- ✅ Gestión de espacios de trabajo, listas y usuarios
- ✅ Búsqueda y filtrado avanzado
- ✅ Operaciones masivas (bulk operations)
- ✅ Sincronización bidireccional con ClickUp

### Automatización
- ✅ Reglas de automatización personalizables
- ✅ Triggers basados en eventos de tareas
- ✅ Acciones automáticas (asignaciones, fechas límite, etiquetas)
- ✅ Ejecución manual y programada
- ✅ Monitoreo de ejecuciones y errores

### Reportes
- ✅ Resumen de tareas por estado y prioridad
- ✅ Análisis de rendimiento de usuarios
- ✅ Línea de tiempo de tareas
- ✅ Vista general del workspace
- ✅ Reportes personalizables con filtros
- ✅ Exportación en formato JSON

### Integraciones
- ✅ CRMs (Salesforce, HubSpot, Pipedrive)
- ✅ Bases de datos (PostgreSQL, MySQL, MongoDB)
- ✅ Herramientas de productividad (Slack, Teams, Google Workspace)
- ✅ Gestión de proyectos (Jira, Asana, Trello)
- ✅ Pruebas de conexión y sincronización

## 🏗️ Arquitectura

```
ClickUp Project Manager/
├── api/                    # API REST con FastAPI
│   ├── routes/            # Endpoints de la API
│   └── schemas/           # Esquemas Pydantic
├── core/                  # Configuración y utilidades
│   ├── config.py         # Configuración de la aplicación
│   ├── database.py       # Configuración de base de datos
│   └── clickup_client.py # Cliente de ClickUp API
├── models/               # Modelos de SQLAlchemy
├── utils/                # Utilidades y helpers
├── data/                 # Datos y reportes generados
├── logs/                 # Archivos de log
├── static/               # Archivos estáticos
├── templates/            # Plantillas HTML
└── tests/                # Tests unitarios y de integración
```

## 🛠️ Tecnologías

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **API**: ClickUp API v2
- **Autenticación**: JWT
- **Documentación**: OpenAPI/Swagger
- **Tests**: pytest, pytest-asyncio

## 📦 Instalación

### Prerrequisitos

- Python 3.8+
- pip
- ClickUp API Token

### Pasos de instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd ClickUp_Project_Manager
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp env.example .env
# Editar .env con tus credenciales de ClickUp
```

5. **Inicializar base de datos**
```bash
python -c "from core.database import init_db; import asyncio; asyncio.run(init_db())"
```

6. **Ejecutar la aplicación**
```bash
python main.py
```

La aplicación estará disponible en `http://localhost:8000`

## 🔧 Configuración

### Variables de entorno principales

```env
# ClickUp API
CLICKUP_API_TOKEN=your_clickup_api_token_here

# Base de datos
DATABASE_URL=sqlite:///./clickup_manager.db

# Configuración de la aplicación
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### Obtener API Token de ClickUp

1. Ve a [ClickUp Settings](https://app.clickup.com/settings)
2. Navega a "Apps" → "API Token"
3. Crea un nuevo token con los permisos necesarios
4. Copia el token a tu archivo `.env`

## 📚 Uso de la API

### Autenticación

La API utiliza autenticación basada en tokens. Incluye tu API token de ClickUp en el header:

```bash
Authorization: your_clickup_api_token_here
```

### Endpoints principales

#### Tareas
```bash
# Crear tarea
POST /api/v1/tasks/
{
  "name": "Nueva tarea",
  "description": "Descripción de la tarea",
  "list_id": "list_id",
  "workspace_id": "workspace_id",
  "assignee_id": "user_id",
  "priority": 3,
  "due_date": "2024-01-15T10:00:00Z"
}

# Obtener tareas
GET /api/v1/tasks/?workspace_id=workspace_id&status=in_progress

# Actualizar tarea
PUT /api/v1/tasks/{task_id}
{
  "status": "complete",
  "priority": 1
}

# Eliminar tarea
DELETE /api/v1/tasks/{task_id}
```

#### Workspaces
```bash
# Obtener workspaces
GET /api/v1/workspaces/

# Obtener workspace específico
GET /api/v1/workspaces/{workspace_id}

# Sincronizar workspace
POST /api/v1/workspaces/{workspace_id}/sync
```

#### Automatizaciones
```bash
# Crear automatización
POST /api/v1/automation/
{
  "name": "Asignar tareas urgentes",
  "trigger_type": "task_created",
  "trigger_conditions": {
    "priority": 1
  },
  "actions": [
    {
      "type": "assign_user",
      "user_id": "default_user_id"
    }
  ],
  "workspace_id": "workspace_id"
}

# Ejecutar automatización
POST /api/v1/automation/{automation_id}/execute
```

#### Reportes
```bash
# Crear reporte
POST /api/v1/reports/
{
  "name": "Reporte mensual",
  "report_type": "task_summary",
  "workspace_id": "workspace_id",
  "date_range": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }
}

# Generar reporte
POST /api/v1/reports/{report_id}/generate
```

#### Integraciones
```bash
# Crear integración
POST /api/v1/integrations/
{
  "name": "Integración Salesforce",
  "integration_type": "crm",
  "provider": "salesforce",
  "config": {
    "instance_url": "https://your-instance.salesforce.com"
  },
  "credentials": {
    "access_token": "your_access_token"
  },
  "workspace_id": "workspace_id"
}

# Probar integración
POST /api/v1/integrations/{integration_id}/test
{
  "test_type": "connection"
}
```

## 🔄 Automatizaciones

### Tipos de triggers disponibles

- `task_created`: Cuando se crea una nueva tarea
- `task_updated`: Cuando se actualiza una tarea
- `task_completed`: Cuando se completa una tarea
- `due_date_approaching`: Cuando se acerca la fecha límite
- `priority_changed`: Cuando cambia la prioridad

### Tipos de acciones disponibles

- `assign_user`: Asignar usuario a la tarea
- `set_priority`: Cambiar prioridad
- `add_tags`: Agregar etiquetas
- `set_due_date`: Establecer fecha límite
- `send_notification`: Enviar notificación
- `create_subtask`: Crear subtarea

### Ejemplo de automatización

```json
{
  "name": "Gestión automática de tareas urgentes",
  "trigger_type": "task_created",
  "trigger_conditions": {
    "priority": 1,
    "workspace_id": "workspace_id"
  },
  "actions": [
    {
      "type": "assign_user",
      "user_id": "manager_id"
    },
    {
      "type": "add_tags",
      "tags": ["urgente", "automático"]
    },
    {
      "type": "set_due_date",
      "days_from_now": 1
    }
  ]
}
```

## 📊 Reportes

### Tipos de reportes disponibles

1. **Resumen de Tareas**: Estadísticas por estado, prioridad y asignación
2. **Rendimiento de Usuarios**: Análisis de productividad por usuario
3. **Línea de Tiempo**: Análisis temporal de tareas
4. **Vista General del Workspace**: Métricas completas del workspace
5. **Análisis Personalizado**: Reportes con filtros específicos

### Ejemplo de reporte de rendimiento

```json
{
  "report_type": "user_performance",
  "parameters": {
    "date_range": "last_month",
    "include_inactive": false
  },
  "summary": {
    "total_users": 5,
    "best_performer": "Juan Pérez",
    "avg_completion_rate": 85.2
  },
  "data": {
    "user_performance": [
      {
        "user_name": "Juan Pérez",
        "total_tasks": 25,
        "completed_tasks": 23,
        "completion_rate": 92.0
      }
    ]
  }
}
```

## 🔌 Integraciones

### CRMs soportados

- **Salesforce**: Sincronización de leads y oportunidades
- **HubSpot**: Gestión de contactos y deals
- **Pipedrive**: Pipeline de ventas

### Bases de datos

- **PostgreSQL**: Almacenamiento de datos históricos
- **MySQL**: Sincronización de métricas
- **MongoDB**: Almacenamiento de documentos

### Herramientas de productividad

- **Slack**: Notificaciones automáticas
- **Microsoft Teams**: Integración con canales
- **Google Workspace**: Sincronización con Calendar y Drive

## 🧪 Testing

### Ejecutar tests

```bash
# Tests unitarios
pytest tests/unit/

# Tests de integración
pytest tests/integration/

# Todos los tests
pytest tests/

# Con cobertura
pytest --cov=. tests/
```

### Estructura de tests

```
tests/
├── unit/                 # Tests unitarios
│   ├── test_models.py
│   ├── test_schemas.py
│   └── test_utils.py
├── integration/          # Tests de integración
│   ├── test_api.py
│   └── test_clickup_client.py
└── conftest.py          # Configuración de tests
```

## 📈 Monitoreo y Logs

### Configuración de logs

```python
# En core/config.py
LOG_LEVEL = "INFO"
LOG_FILE = "logs/app.log"
```

### Niveles de log

- `DEBUG`: Información detallada para desarrollo
- `INFO`: Información general de la aplicación
- `WARNING`: Advertencias que no impiden la ejecución
- `ERROR`: Errores que afectan la funcionalidad
- `CRITICAL`: Errores críticos que pueden detener la aplicación

## 🚀 Despliegue

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/clickup_manager
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: clickup_manager
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
  
  redis:
    image: redis:6-alpine
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

- **Documentación**: [Wiki del proyecto](link-to-wiki)
- **Issues**: [GitHub Issues](link-to-issues)
- **Email**: support@clickup-manager.com

## 🔮 Roadmap

### Próximas características

- [ ] Dashboard web con gráficos interactivos
- [ ] Notificaciones push en tiempo real
- [ ] Integración con más CRMs
- [ ] API GraphQL
- [ ] Mobile app
- [ ] Machine Learning para predicciones
- [ ] Workflows visuales para automatizaciones
- [ ] Exportación a Excel/PDF
- [ ] Integración con calendarios
- [ ] Sistema de permisos granular

### Mejoras técnicas

- [ ] Cache distribuido con Redis
- [ ] Background jobs con Celery
- [ ] Métricas con Prometheus
- [ ] Logs centralizados
- [ ] CI/CD pipeline
- [ ] Tests de carga
- [ ] Documentación automática
- [ ] Monitoreo de performance

---

**ClickUp Project Manager** - Potenciando la productividad con automatización inteligente 🚀
