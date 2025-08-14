# 🐘 Instalación de PostgreSQL en Windows

## 📥 Descarga e Instalación

### Opción 1: Instalador Oficial (Recomendado)
1. **Descargar PostgreSQL:**
   - Ve a: https://www.postgresql.org/download/windows/
   - Haz clic en "Download the installer"
   - Selecciona la versión más reciente (15.x o 16.x)

2. **Ejecutar el instalador:**
   - Ejecuta el archivo `.exe` descargado
   - Acepta los términos de licencia
   - Selecciona el directorio de instalación (por defecto: `C:\Program Files\PostgreSQL\15\`)

3. **Configuración de la instalación:**
   - **Data Directory:** `C:\Program Files\PostgreSQL\15\data` (por defecto)
   - **Password:** `postgres` (¡IMPORTANTE! Usa esta contraseña)
   - **Port:** `5432` (por defecto)
   - **Locale:** `Default locale`

4. **Componentes a instalar:**
   - ✅ PostgreSQL Server
   - ✅ pgAdmin 4 (interfaz gráfica)
   - ✅ Command Line Tools
   - ✅ Stack Builder (opcional)

5. **Finalizar instalación:**
   - Espera a que se complete la instalación
   - **NO** ejecutes Stack Builder al finalizar

### Opción 2: Chocolatey (Desarrolladores)
```powershell
# Instalar Chocolatey primero si no lo tienes
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Instalar PostgreSQL
choco install postgresql
```

## 🔧 Configuración Post-Instalación

### 1. Verificar la instalación
```powershell
# Verificar que PostgreSQL esté ejecutándose
Get-Service postgresql*

# Verificar la versión
psql --version
```

### 2. Configurar variables de entorno
- Busca "Variables de entorno" en Windows
- En "Variables del sistema", agrega:
  - `PG_HOME`: `C:\Program Files\PostgreSQL\15`
  - `PATH`: Agrega `%PG_HOME%\bin`

### 3. Verificar conexión
```powershell
# Conectar a PostgreSQL
psql -U postgres -h localhost
# Contraseña: postgres

# Dentro de psql, verificar la base de datos
\l
\q
```

## 🚀 Ejecutar la Migración

### 1. Instalar dependencias Python
```powershell
pip install psycopg2-binary
```

### 2. Ejecutar el script de migración
```powershell
python migrate_to_postgres.py
```

### 3. Verificar la migración
```powershell
# Conectar a la nueva base de datos
psql -U postgres -h localhost -d clickup_manager

# Ver tablas
\dt

# Ver datos de ejemplo
SELECT * FROM users LIMIT 5;
SELECT * FROM tasks LIMIT 5;
```

## 🛠️ Solución de Problemas

### Error: "psql no se reconoce"
- **Solución:** Agregar `C:\Program Files\PostgreSQL\15\bin` al PATH
- **Alternativa:** Usar la ruta completa: `"C:\Program Files\PostgreSQL\15\bin\psql.exe"`

### Error: "Connection refused"
- **Solución:** Verificar que el servicio esté ejecutándose
- **Comando:** `Get-Service postgresql*`

### Error: "Authentication failed"
- **Solución:** Usar contraseña `postgres`
- **Alternativa:** Cambiar contraseña en pgAdmin

### Error: "Port already in use"
- **Solución:** Cambiar puerto en `postgresql.conf`
- **Ubicación:** `C:\Program Files\PostgreSQL\15\data\postgresql.conf`

## 📊 pgAdmin 4 (Interfaz Gráfica)

### Acceder a pgAdmin
1. Busca "pgAdmin 4" en el menú de inicio
2. Abre la aplicación
3. **Primera vez:** Establece una contraseña maestra
4. **Conectar al servidor:**
   - Host: `localhost`
   - Port: `5432`
   - Username: `postgres`
   - Password: `postgres`

### Crear base de datos manualmente
1. Click derecho en "Databases"
2. "Create" → "Database"
3. Nombre: `clickup_manager`
4. Owner: `postgres`

## 🔒 Seguridad

### Cambiar contraseña por defecto
```sql
-- Conectar como postgres
psql -U postgres -h localhost

-- Cambiar contraseña
ALTER USER postgres PASSWORD 'tu_nueva_contraseña_segura';

-- Crear usuario específico para la aplicación
CREATE USER clickup_app WITH PASSWORD 'contraseña_app';
GRANT ALL PRIVILEGES ON DATABASE clickup_manager TO clickup_app;
```

### Configurar firewall
- Permitir conexiones al puerto 5432
- Restringir acceso solo a localhost en desarrollo

## 📈 Rendimiento

### Configuración recomendada para desarrollo
```sql
-- En postgresql.conf
shared_buffers = 128MB
effective_cache_size = 512MB
work_mem = 4MB
maintenance_work_mem = 64MB
```

### Monitoreo
```sql
-- Ver conexiones activas
SELECT * FROM pg_stat_activity;

-- Ver estadísticas de tablas
SELECT * FROM pg_stat_user_tables;
```

## 🎯 Próximos Pasos

1. ✅ Instalar PostgreSQL
2. ✅ Ejecutar script de migración
3. ✅ Verificar datos migrados
4. ✅ Probar aplicación con PostgreSQL
5. ✅ Configurar respaldos automáticos
6. ✅ Optimizar consultas si es necesario

---

**¿Necesitas ayuda con algún paso específico?** 
Consulta la documentación oficial: https://www.postgresql.org/docs/
