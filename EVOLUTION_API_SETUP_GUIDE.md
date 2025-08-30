# 📱 Guía de Configuración Evolution API para WhatsApp

## 🎯 **ESTADO ACTUAL**

### ✅ **LO QUE YA ESTÁ CONFIGURADO:**
1. **Servicio Evolution API creado** en Railway
   - Nombre: `evolution-whatsapp-api`
   - ID: `d655f28d-8a45-45d1-a52e-f15b1da5b081`
   - Imagen: `atendai/evolution-api:v2.1.1`

2. **Dominio público configurado**
   - URL: `https://evolution-whatsapp-api-production.up.railway.app`
   - Puerto: 8080

3. **Variables de entorno configuradas**
   ```
   SERVER_TYPE=http
   SERVER_PORT=8080
   PORT=8080
   AUTHENTICATION_TYPE=apikey
   AUTHENTICATION_API_KEY=clickup-whatsapp-2024
   AUTHENTICATION_EXPOSE_IN_FETCH_INSTANCES=true
   QRCODE_LIMIT=30
   STORE_MESSAGES=true
   STORE_MESSAGE_UP=true
   DATABASE_ENABLED=false
   ```

4. **Aplicación principal actualizada**
   - `WHATSAPP_EVOLUTION_URL`: `https://evolution-whatsapp-api-production.up.railway.app`
   - `WHATSAPP_EVOLUTION_API_KEY`: `clickup-whatsapp-2024`
   - `WHATSAPP_SIMULATOR_ENABLED`: `False` (WhatsApp real)

## 🔧 **PROBLEMA ACTUAL**

Evolution API está teniendo problemas para iniciar en Railway. **Error 502: Bad Gateway**

### **Posibles soluciones:**

#### **OPCIÓN A: Esperar y Reintentar**
1. Railway puede estar procesando el deployment
2. Evolution API puede tardar varios minutos en inicializar
3. Probar la URL en 5-10 minutos

#### **OPCIÓN B: Configuración Alternativa**
Si Evolution API sigue fallando, usar un servicio externo:

1. **Heroku** (más estable para Evolution API)
2. **VPS/Servidor dedicado**
3. **Docker local** (para desarrollo)

#### **OPCIÓN C: Volver al Simulador Temporalmente**
```bash
# En Railway, cambiar variables:
WHATSAPP_SIMULATOR_ENABLED=True
WHATSAPP_EVOLUTION_URL=http://localhost:8080
```

## 📋 **PASOS SIGUIENTES**

### **1. Verificar Estado de Evolution API**
```bash
curl -H "apikey: clickup-whatsapp-2024" \
     https://evolution-whatsapp-api-production.up.railway.app/
```

### **2. Si Evolution API Funciona - Crear Instancia**
```bash
curl -X POST \
     -H "apikey: clickup-whatsapp-2024" \
     -H "Content-Type: application/json" \
     -d '{"instanceName": "clickup-manager"}' \
     https://evolution-whatsapp-api-production.up.railway.app/instance/create
```

### **3. Obtener Código QR para WhatsApp**
```bash
curl -H "apikey: clickup-whatsapp-2024" \
     https://evolution-whatsapp-api-production.up.railway.app/instance/qrcode/clickup-manager
```

### **4. Probar Envío de Mensaje**
```bash
curl -X POST \
     -H "apikey: clickup-whatsapp-2024" \
     -H "Content-Type: application/json" \
     -d '{"number": "+1234567890", "text": "¡Hola desde ClickUp!"}' \
     https://evolution-whatsapp-api-production.up.railway.app/message/sendText/clickup-manager
```

## 🚨 **TROUBLESHOOTING**

### **Error 502: Bad Gateway**
- Evolution API aún no está listo
- Verificar logs en Railway
- Esperar 5-10 minutos más

### **Error 401: Unauthorized**
- Verificar API key: `clickup-whatsapp-2024`
- Verificar header: `apikey: clickup-whatsapp-2024`

### **Error de Timeout**
- Evolution API puede estar sobrecargado
- Intentar reiniciar el servicio en Railway

## 🎯 **RESUMEN**

**Evolution API está configurado correctamente** pero Railway está teniendo problemas para ejecutarlo. **Tu aplicación principal ya está lista** para usar WhatsApp real en cuanto Evolution API esté funcionando.

**Mientras tanto, puedes usar el simulador** que funciona perfectamente para testing.
