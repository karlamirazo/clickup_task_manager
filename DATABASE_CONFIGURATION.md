# 🗄️ Configuración de Base de Datos - ClickUp Project Manager

## 📋 **Resumen**

Este proyecto **SOLO** usa **PostgreSQL** como base de datos principal. Los archivos SQLite que existían eran residuales de desarrollo anterior y han sido eliminados.

## 🎯 **Configuración Principal**

### **Base de Datos por Defecto: PostgreSQL**

```bash
# Configuración principal en core/config.py
DATABASE_URL=postgresql://postgres:admin123@localhost:5432/clickup_project_manager

# Variables específicas de PostgreSQL
POSTGRES_ENABLED=True
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=clickup_project_manager
POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin123
```

## 🔧 **Configuración por Entorno**

### **1. Desarrollo Local**
```bash
# En tu archivo .env
DATABASE_URL=postgresql://postgres:admin123@localhost:5432/clickup_project_manager
```

### **2. Railway (Producción)**
```bash
# Railway configura automáticamente DATABASE_URL
# No necesitas configurar nada manualmente
```

### **3. Docker (Opcional)**
```bash
# Usar el script de configuración
./docker_postgres_setup.ps1
```

## 🚫 **¿Por qué NO SQLite?**

1. **Inconsistencia**: El proyecto está diseñado para PostgreSQL
2. **Funcionalidades**: PostgreSQL ofrece mejor rendimiento y características
3. **Despliegue**: Railway usa PostgreSQL por defecto
4. **Escalabilidad**: PostgreSQL es más robusto para producción

## 🛠️ **Inicialización de Base de Datos**

### **Comando de Inicialización**
```bash
python -c "from core.database import init_db; import asyncio; asyncio.run(init_db())"
```

### **Verificación de Conexión**
```bash
python -c "from core.database import engine; print('✅ Base de datos conectada:', engine.url)"
```

## 📁 **Archivos Eliminados**

Los siguientes archivos SQLite han sido eliminados del proyecto:
- ❌ `clickup_manager.db`
- ❌ `clickup_tasks.db`
- ❌ `clickup_project_manager.db`
- ❌ `clickup_manager_backup.db`
- ❌ `clickup_manager_backup_20250809_210854.db`

## 🔍 **Verificación de Estado**

### **Comando de Verificación**
```bash
# Verificar que no hay archivos SQLite
dir *.db

# Verificar configuración actual
python -c "from core.config import settings; print('DATABASE_URL:', settings.DATABASE_URL)"
```

## 📚 **Dependencias Requeridas**

### **PostgreSQL Driver**
```bash
pip install psycopg2-binary
```

### **Verificar en requirements.txt**
```
psycopg2-binary>=2.9.0
```

## ⚠️ **Solución de Problemas**

### **Error: "No module named 'psycopg2'"**
```bash
pip install psycopg2-binary
```

### **Error de Conexión a PostgreSQL**
1. Verificar que PostgreSQL esté ejecutándose
2. Verificar credenciales en `.env`
3. Verificar que la base de datos exista

### **Error de Permisos**
```sql
-- En PostgreSQL
GRANT ALL PRIVILEGES ON DATABASE clickup_project_manager TO postgres;
```

## 🎉 **Estado Actual**

✅ **Base de datos unificada**: Solo PostgreSQL  
✅ **Configuración limpia**: Sin archivos SQLite residuales  
✅ **Documentación actualizada**: Configuración clara y consistente  
✅ **Gitignore configurado**: Previene archivos de base de datos en el repositorio  

---

**Nota**: Si necesitas usar SQLite para desarrollo local específico, puedes cambiar temporalmente `DATABASE_URL` en tu archivo `.env`, pero recuerda que no es la configuración recomendada para este proyecto.
