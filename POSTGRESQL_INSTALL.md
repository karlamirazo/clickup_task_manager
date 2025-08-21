# üêò Instalaci√≥n de PostgreSQL en Windows

## üì• Descarga e Instalaci√≥n

### Opci√≥n 1: Instalador Oficial (Recomendado)
1. **Descargar PostgreSQL:**
   - Ve a: https://www.postgresql.org/download/windows/
   - Haz clic en "Download the installer"
   - Selecciona la versi√≥n m√°s reciente (15.x o 16.x)

2. **Ejecutar el instalador:**
   - Ejecuta el archivo `.exe` descargado
   - Acepta los t√©rminos de licencia
   - Selecciona el directorio de instalaci√≥n (por defecto: `C:\Program Files\PostgreSQL\15\`)

3. **Configuraci√≥n de la instalaci√≥n:**
   - **Data Directory:** `C:\Program Files\PostgreSQL\15\data` (por defecto)
   - **Password:** `postgres` (¬°IMPORTANTE! Usa esta contrase√±a)
   - **Port:** `5432` (por defecto)
   - **Locale:** `Default locale`

4. **Componentes a instalar:**
   - ‚úÖ PostgreSQL Server
   - ‚úÖ pgAdmin 4 (interfaz gr√°fica)
   - ‚úÖ Command Line Tools
   - ‚úÖ Stack Builder (opcional)

5. **Finalizar instalaci√≥n:**
   - Espera a que se complete la instalaci√≥n
   - **NO** ejecutes Stack Builder al finalizar

### Opci√≥n 2: Chocolatey (Desarrolladores)
```powershell
# Instalar Chocolatey primero si no lo tienes
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Instalar PostgreSQL
choco install postgresql
```

## üîß Configuraci√≥n Post-Instalaci√≥n

### 1. Verificar la instalaci√≥n
```powershell
# Verificar que PostgreSQL est√© ejecut√°ndose
Get-Service postgresql*

# Verificar la versi√≥n
psql --version
```

### 2. Configurar variables de entorno
- Busca "Variables de entorno" en Windows
- En "Variables del sistema", agrega:
  - `PG_HOME`: `C:\Program Files\PostgreSQL\15`
  - `PATH`: Agrega `%PG_HOME%\bin`

### 3. Verificar conexi√≥n
```powershell
# Conectar a PostgreSQL
psql -U postgres -h localhost
# Contrase√±a: postgres

# Dentro de psql, verificar la base de datos
\l
\q
```

## üöÄ Ejecutar la Migraci√≥n

### 1. Instalar dependencias Python
```powershell
pip install psycopg2-binary
```

### 2. Ejecutar el script de migraci√≥n
```powershell
python migrate_to_postgres.py
```

### 3. Verificar la migraci√≥n
```powershell
# Conectar a la nueva base de datos
psql -U postgres -h localhost -d clickup_manager

# Ver tablas
\dt

# Ver datos de ejemplo
SELECT * FROM users LIMIT 5;
SELECT * FROM tasks LIMIT 5;
```

## üõ†Ô∏è Soluci√≥n de Problemas

### Error: "psql no se reconoce"
- **Soluci√≥n:** Agregar `C:\Program Files\PostgreSQL\15\bin` al PATH
- **Alternativa:** Usar la ruta completa: `"C:\Program Files\PostgreSQL\15\bin\psql.exe"`

### Error: "Connection refused"
- **Soluci√≥n:** Verificar que el servicio est√© ejecut√°ndose
- **Comando:** `Get-Service postgresql*`

### Error: "Authentication failed"
- **Soluci√≥n:** Usar contrase√±a `postgres`
- **Alternativa:** Cambiar contrase√±a en pgAdmin

### Error: "Port already in use"
- **Soluci√≥n:** Cambiar puerto en `postgresql.conf`
- **Ubicaci√≥n:** `C:\Program Files\PostgreSQL\15\data\postgresql.conf`

## üìä pgAdmin 4 (Interfaz Gr√°fica)

### Acceder a pgAdmin
1. Busca "pgAdmin 4" en el men√∫ de inicio
2. Abre la aplicaci√≥n
3. **Primera vez:** Establece una contrase√±a maestra
4. **Conectar al servidor:**
   - Host: `localhost`
   - Port: `5432`
   - Username: `postgres`
   - Password: `postgres`

### Crear base de datos manualmente
1. Click derecho en "Databases"
2. "Create" ‚Üí "Database"
3. Nombre: `clickup_manager`
4. Owner: `postgres`

## üîí Seguridad

### Cambiar contrase√±a por defecto
```sql
-- Conectar como postgres
psql -U postgres -h localhost

-- Cambiar contrase√±a
ALTER USER postgres PASSWORD 'tu_nueva_contrase√±a_segura';

-- Crear usuario espec√≠fico para la aplicaci√≥n
CREATE USER clickup_app WITH PASSWORD 'contrase√±a_app';
GRANT ALL PRIVILEGES ON DATABASE clickup_manager TO clickup_app;
```

### Configurar firewall
- Permitir conexiones al puerto 5432
- Restringir acceso solo a localhost en desarrollo

## üìà Rendimiento

### Configuraci√≥n recomendada para desarrollo
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

-- Ver estad√≠sticas de tablas
SELECT * FROM pg_stat_user_tables;
```

## üéØ Pr√≥ximos Pasos

1. ‚úÖ Instalar PostgreSQL
2. ‚úÖ Ejecutar script de migraci√≥n
3. ‚úÖ Verificar datos migrados
4. ‚úÖ Probar aplicaci√≥n con PostgreSQL
5. ‚úÖ Configurar respaldos autom√°ticos
6. ‚úÖ Optimizar consultas si es necesario

---

**¬øNecesitas ayuda con alg√∫n paso espec√≠fico?** 
Consulta la documentaci√≥n oficial: https://www.postgresql.org/docs/
