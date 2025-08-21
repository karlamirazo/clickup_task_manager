# ClickUp Project Manager - Agente Inteligente

Un mÃ³dulo completo de gestiÃ³n de tareas con la API de ClickUp que incluye automatizaciÃ³n, reportes e integraciones.

## ğŸš€ CaracterÃ­sticas

### GestiÃ³n de Tareas
- âœ… Crear, actualizar y eliminar tareas
- âœ… GestiÃ³n de espacios de trabajo, listas y usuarios
- âœ… BÃºsqueda y filtrado avanzado
- âœ… Operaciones masivas (bulk operations)
- âœ… SincronizaciÃ³n bidireccional con ClickUp

### AutomatizaciÃ³n
- âœ… Reglas de automatizaciÃ³n personalizables
- âœ… Triggers basados en eventos de tareas
- âœ… Acciones automÃ¡ticas (asignaciones, fechas lÃ­mite, etiquetas)
- âœ… EjecuciÃ³n manual y programada
- âœ… Monitoreo de ejecuciones y errores

### Reportes
- âœ… Resumen de tareas por estado y prioridad
- âœ… AnÃ¡lisis de rendimiento de usuarios
- âœ… LÃ­nea de tiempo de tareas
- âœ… Vista general del workspace
- âœ… Reportes personalizables con filtros
- âœ… ExportaciÃ³n en formato JSON

### Integraciones
- âœ… CRMs (Salesforce, HubSpot, Pipedrive)
- âœ… Bases de datos (PostgreSQL, MySQL, MongoDB)
- âœ… Herramientas de productividad (Slack, Teams, Google Workspace)
- âœ… GestiÃ³n de proyectos (Jira, Asana, Trello)
- âœ… Pruebas de conexiÃ³n y sincronizaciÃ³n

## ğŸ�—ï¸� Arquitectura

```
ClickUp Project Manager/
â”œâ”€â”€ api/                    # API REST con FastAPI
â”‚   â”œâ”€â”€ routes/            # Endpoints de la API
â”‚   â””â”€â”€ schemas/           # Esquemas Pydantic
â”œâ”€â”€ core/                  # ConfiguraciÃ³n y utilidades
â”‚   â”œâ”€â”€ config.py         # ConfiguraciÃ³n de la aplicaciÃ³n
â”‚   â”œâ”€â”€ database.py       # ConfiguraciÃ³n de base de datos
â”‚   â””â”€â”€ clickup_client.py # Cliente de ClickUp API
â”œâ”€â”€ models/               # Modelos de SQLAlchemy
â”œâ”€â”€ utils/                # Utilidades y helpers
â”œâ”€â”€ data/                 # Datos y reportes generados
â”œâ”€â”€ logs/                 # Archivos de log
â”œâ”€â”€ static/               # Archivos estÃ¡ticos
â”œâ”€â”€ templates/            # Plantillas HTML
â””â”€â”€ tests/                # Tests unitarios y de integraciÃ³n
```

## ğŸ› ï¸� TecnologÃ­as

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producciÃ³n)
- **API**: ClickUp API v2
- **AutenticaciÃ³n**: JWT
- **DocumentaciÃ³n**: OpenAPI/Swagger
- **Tests**: pytest, pytest-asyncio

## ğŸ“¦ InstalaciÃ³n

### Prerrequisitos

- Python 3.8+
- pip
- ClickUp API Token

### Pasos de instalaciÃ³n

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

6. **Ejecutar la aplicaciÃ³n**
```bash
python main.py
```

La aplicaciÃ³n estarÃ¡ disponible en `http://localhost:8000`

## ğŸ”§ ConfiguraciÃ³n

### Variables de entorno principales

```env
# ClickUp API
CLICKUP_API_TOKEN=your_clickup_api_token_here

# Base de datos
DATABASE_URL=sqlite:///./clickup_manager.db

# ConfiguraciÃ³n de la aplicaciÃ³n
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### Obtener API Token de ClickUp

1. Ve a [ClickUp Settings](https://app.clickup.com/settings)
2. Navega a "Apps" â†’ "API Token"
3. Crea un nuevo token con los permisos necesarios
4. Copia el token a tu archivo `.env`

## ğŸ“š Uso de la API

### AutenticaciÃ³n

La API utiliza autenticaciÃ³n basada en tokens. Incluye tu API token de ClickUp en el header:

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
  "description": "DescripciÃ³n de la tarea",
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

# Obtener workspace especÃ­fico
GET /api/v1/workspaces/{workspace_id}

# Sincronizar workspace
POST /api/v1/workspaces/{workspace_id}/sync
```

#### Automatizaciones
```bash
# Crear automatizaciÃ³n
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

# Ejecutar automatizaciÃ³n
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
# Crear integraciÃ³n
POST /api/v1/integrations/
{
  "name": "IntegraciÃ³n Salesforce",
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

# Probar integraciÃ³n
POST /api/v1/integrations/{integration_id}/test
{
  "test_type": "connection"
}
```

## ğŸ”„ Automatizaciones

### Tipos de triggers disponibles

- `task_created`: Cuando se crea una nueva tarea
- `task_updated`: Cuando se actualiza una tarea
- `task_completed`: Cuando se completa una tarea
- `due_date_approaching`: Cuando se acerca la fecha lÃ­mite
- `priority_changed`: Cuando cambia la prioridad

### Tipos de acciones disponibles

- `assign_user`: Asignar usuario a la tarea
- `set_priority`: Cambiar prioridad
- `add_tags`: Agregar etiquetas
- `set_due_date`: Establecer fecha lÃ­mite
- `send_notification`: Enviar notificaciÃ³n
- `create_subtask`: Crear subtarea

### Ejemplo de automatizaciÃ³n

```json
{
  "name": "GestiÃ³n automÃ¡tica de tareas urgentes",
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
      "tags": ["urgente", "automÃ¡tico"]
    },
    {
      "type": "set_due_date",
      "days_from_now": 1
    }
  ]
}
```

## ğŸ“Š Reportes

### Tipos de reportes disponibles

1. **Resumen de Tareas**: EstadÃ­sticas por estado, prioridad y asignaciÃ³n
2. **Rendimiento de Usuarios**: AnÃ¡lisis de productividad por usuario
3. **LÃ­nea de Tiempo**: AnÃ¡lisis temporal de tareas
4. **Vista General del Workspace**: MÃ©tricas completas del workspace
5. **AnÃ¡lisis Personalizado**: Reportes con filtros especÃ­ficos

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
    "best_performer": "Juan PÃ©rez",
    "avg_completion_rate": 85.2
  },
  "data": {
    "user_performance": [
      {
        "user_name": "Juan PÃ©rez",
        "total_tasks": 25,
        "completed_tasks": 23,
        "completion_rate": 92.0
      }
    ]
  }
}
```

## ğŸ”Œ Integraciones

### CRMs soportados

- **Salesforce**: SincronizaciÃ³n de leads y oportunidades
- **HubSpot**: GestiÃ³n de contactos y deals
- **Pipedrive**: Pipeline de ventas

### Bases de datos

- **PostgreSQL**: Almacenamiento de datos histÃ³ricos
- **MySQL**: SincronizaciÃ³n de mÃ©tricas
- **MongoDB**: Almacenamiento de documentos

### Herramientas de productividad

- **Slack**: Notificaciones automÃ¡ticas
- **Microsoft Teams**: IntegraciÃ³n con canales
- **Google Workspace**: SincronizaciÃ³n con Calendar y Drive

## ğŸ§ª Testing

### Ejecutar tests

```bash
# Tests unitarios
pytest tests/unit/

# Tests de integraciÃ³n
pytest tests/integration/

# Todos los tests
pytest tests/

# Con cobertura
pytest --cov=. tests/
```

### Estructura de tests

```
tests/
â”œâ”€â”€ unit/                 # Tests unitarios
â”‚   â”œâ”€â”€ test_models.py
â”‚   â”œâ”€â”€ test_schemas.py
â”‚   â””â”€â”€ test_utils.py
â”œâ”€â”€ integration/          # Tests de integraciÃ³n
â”‚   â”œâ”€â”€ test_api.py
â”‚   â””â”€â”€ test_clickup_client.py
â””â”€â”€ conftest.py          # ConfiguraciÃ³n de tests
```

## ğŸ“ˆ Monitoreo y Logs

### ConfiguraciÃ³n de logs

```python
# En core/config.py
LOG_LEVEL = "INFO"
LOG_FILE = "logs/app.log"
```

### Niveles de log

- `DEBUG`: InformaciÃ³n detallada para desarrollo
- `INFO`: InformaciÃ³n general de la aplicaciÃ³n
- `WARNING`: Advertencias que no impiden la ejecuciÃ³n
- `ERROR`: Errores que afectan la funcionalidad
- `CRITICAL`: Errores crÃ­ticos que pueden detener la aplicaciÃ³n

## ğŸš€ Despliegue

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

## ğŸ¤� ContribuciÃ³n

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## ğŸ“„ Licencia

Este proyecto estÃ¡ bajo la Licencia MIT. Ver el archivo `LICENSE` para mÃ¡s detalles.

## ğŸ†˜ Soporte

- **DocumentaciÃ³n**: [Wiki del proyecto](link-to-wiki)
- **Issues**: [GitHub Issues](link-to-issues)
- **Email**: support@clickup-manager.com

## ğŸ”® Roadmap

### PrÃ³ximas caracterÃ­sticas

- [ ] Dashboard web con grÃ¡ficos interactivos
- [ ] Notificaciones push en tiempo real
- [ ] IntegraciÃ³n con mÃ¡s CRMs
- [ ] API GraphQL
- [ ] Mobile app
- [ ] Machine Learning para predicciones
- [ ] Workflows visuales para automatizaciones
- [ ] ExportaciÃ³n a Excel/PDF
- [ ] IntegraciÃ³n con calendarios
- [ ] Sistema de permisos granular

### Mejoras tÃ©cnicas

- [ ] Cache distribuido con Redis
- [ ] Background jobs con Celery
- [ ] MÃ©tricas con Prometheus
- [ ] Logs centralizados
- [ ] CI/CD pipeline
- [ ] Tests de carga
- [ ] DocumentaciÃ³n automÃ¡tica
- [ ] Monitoreo de performance

---

**ClickUp Project Manager** - Potenciando la productividad con automatizaciÃ³n inteligente ğŸš€
