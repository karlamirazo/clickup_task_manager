# 🚀 Deploy Evolution API v2.2.3 en Railway

## 📋 **MÉTODO 1: Deploy desde GitHub con versión específica**

### **Paso 1: Crear nuevo servicio en Railway**

1. **Ve a Railway Dashboard**: https://railway.app/dashboard
2. **New Project** → **Deploy from GitHub repo**
3. **Connect GitHub** (si no está conectado)
4. **Repositorio**: `EvolutionAPI/evolution-api`
5. **Branch**: Seleccionar `v2.2.3` (en el dropdown de branches/tags)

### **Paso 2: Variables de entorno**

```bash
# Variables obligatorias
AUTHENTICATION_API_KEY=clickup-evolution-v223
DATABASE_PROVIDER=postgresql
DATABASE_URL=${{PostgreSQL.DATABASE_URL}}

# Variables de configuración
CONFIG_SESSION_PHONE_CLIENT=Evolution API
CONFIG_SESSION_PHONE_NAME=Chrome
QRCODE_LIMIT=30
QRCODE_COLOR=#198754

# Configuración de logs
LOG_LEVEL=ERROR
LOG_COLOR=true

# Desactivar webhooks innecesarios
WEBHOOK_ENABLED=false
WEBHOOK_EVENTS_MESSAGES_UPSERT=false
WEBHOOK_EVENTS_CONNECTIONS_UPDATE=false

# Cache y rendimiento
CACHE_ENABLED=true
CACHE_TTL=3600
DEL_TEMP_INSTANCES=true
```

### **Paso 3: Conectar PostgreSQL**

1. **Add Service** → **Database** → **PostgreSQL**
2. Railway automáticamente conectará `DATABASE_URL`

## 📋 **MÉTODO 2: Dockerfile personalizado**

Si el método 1 no funciona, crear archivo `Dockerfile.v223`:

```dockerfile
FROM node:18-alpine

# Instalar dependencias del sistema
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    freetype-dev \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    git

# Clonar versión específica
WORKDIR /app
RUN git clone -b v2.2.3 https://github.com/EvolutionAPI/evolution-api.git .

# Instalar dependencias
RUN npm ci --omit=dev

# Variables de entorno
ENV CHROME_BIN=/usr/bin/chromium-browser
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

# Puerto
EXPOSE 8080

# Comando de inicio
CMD ["npm", "start"]
```

## 📋 **MÉTODO 3: Railway CLI**

```bash
# Clonar repo localmente
git clone https://github.com/EvolutionAPI/evolution-api.git
cd evolution-api

# Checkout a versión específica
git checkout v2.2.3

# Deploy a Railway
railway login
railway project create evolution-v223
railway up
```

## 🎯 **CONFIGURACIÓN POST-DEPLOY**

Una vez deployado v2.2.3:

1. **Obtener nueva URL**: `https://evolution-v223-production.up.railway.app`

2. **Actualizar variables ClickUp**:
   ```bash
   railway variables --set "WHATSAPP_EVOLUTION_URL=https://evolution-v223-production.up.railway.app"
   railway variables --set "WHATSAPP_EVOLUTION_API_KEY=clickup-evolution-v223"
   ```

3. **Probar manager**: `https://evolution-v223-production.up.railway.app/manager`

4. **Login**: `clickup-evolution-v223`

5. **Crear instancia**: `clickup-main`

6. **¡Obtener QR funcionando!**

## ✅ **VENTAJAS v2.2.3**

- ✅ **Bug QR corregido**
- ✅ **Mejor manejo de Redis**
- ✅ **Conexiones más estables**
- ✅ **Menos errores internos**
- ✅ **Compatible con tu código actual**
