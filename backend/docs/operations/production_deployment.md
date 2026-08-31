# Production Deployment

## Objetivo

Este documento describe la arquitectura y el procedimiento general utilizado para desplegar Marcha en producción.

Debe leerse junto con:

```text
installation.md
update.md
backup_restore.md
licensing.md
troubleshooting.md
```

---

# Principios de producción

Marcha está diseñado para operar:

- dentro de la red local del restaurante;
- sin dependencia permanente de Internet;
- sobre un servidor Linux;
- mediante contenedores Docker;
- con PostgreSQL como base de datos;
- con Nginx como punto de acceso;
- con systemd administrando el ciclo de vida del sistema.

La operación principal debe continuar aunque el establecimiento pierda conexión a Internet.

---

# Arquitectura de producción

```text
      Tablets / teléfonos / PCs
                 │
                 │ LAN / Wi-Fi
                 ▼
              Nginx :80
          ┌──────┴──────┐
          │             │
          ▼             ▼
      React SPA      /api + /ws
                         │
                         ▼
                     FastAPI
                     Backend
                     │     │
              ┌──────┘     └──────┐
              ▼                   ▼
         PostgreSQL              Redis
```

---

# Componentes principales

La instalación productiva utiliza al menos:

```text
frontend
backend
db
redis
```

gestionados mediante:

```text
docker-compose.prod.yml
```

---

# Nginx

Nginx constituye el único punto HTTP que necesita exponerse a la red local.

Gestiona:

```text
/       → frontend React
/api/   → backend FastAPI
/ws     → WebSocket backend
```

El backend no necesita exponer directamente su puerto interno a la LAN.

---

# Backend

El backend utiliza:

```text
FastAPI
SQLAlchemy
Alembic
PostgreSQL
Redis
```

Durante el arranque ejecuta las tareas necesarias antes de iniciar Uvicorn.

Flujo conceptual:

```text
esperar PostgreSQL
        ↓
restauración pendiente si existe
        ↓
alembic upgrade head
        ↓
validar licencia
        ↓
seed
        ↓
Uvicorn
```

---

# Frontend

El frontend React se compila mediante Vite.

Flujo:

```text
source
   ↓
npm run build
   ↓
dist
   ↓
imagen Docker
   ↓
Nginx
```

Los cambios realizados en el código fuente no aparecen automáticamente en producción.

Debe reconstruirse la imagen frontend.

---

# PostgreSQL

PostgreSQL constituye la fuente principal de persistencia.

Los datos deben almacenarse en un volumen Docker persistente.

Detener o recrear contenedores no debe destruir la base de datos.

---

# Redis

Redis se utiliza para distribución de eventos en tiempo real.

No constituye la fuente definitiva de estado.

Si Redis se reinicia, el estado persistente continúa almacenado en PostgreSQL.

---

# Docker Compose

El stack productivo se administra mediante:

```bash
docker compose -f docker-compose.prod.yml ...
```

Ejemplos:

```bash
docker compose -f docker-compose.prod.yml ps
```

```bash
docker compose -f docker-compose.prod.yml logs backend
```

---

# Systemd

Marcha registra:

```text
pos-restaurant.service
```

como servicio principal.

Además puede utilizar:

```text
pos-zeroconf.service
```

para publicación del nombre local mediante mDNS.

---

# pos-restaurant.service

El servicio principal utiliza:

```text
Type=oneshot
RemainAfterExit=yes
```

y ejecuta:

```text
scripts/start_stack.sh
```

La unidad no debe considerarse correctamente iniciada mientras el backend no supere su health check.

---

# start_stack.sh

`start_stack.sh` es responsable de:

1. comprobar la existencia de la licencia;
2. levantar Docker Compose;
3. esperar al backend;
4. detectar fallos o reinicios;
5. verificar `/health`;
6. detener el stack si el backend no inicia correctamente.

Esto evita que systemd marque Marcha como operativo cuando el backend está fallando.

---

# Health Check

El backend proporciona:

```text
GET /health
```

El stack solo debe considerarse disponible cuando dicho endpoint responde correctamente.

---

# Licencia

La licencia productiva se encuentra fuera del repositorio.

Ruta:

```text
/var/lib/pos-restaurant/license.json
```

El contenedor backend la monta en modo solo lectura.

La ausencia o invalidez de la licencia impide iniciar el backend.

Ver:

```text
licensing.md
```

---

# Persistencia fuera del código

Los siguientes elementos deben sobrevivir a actualizaciones del repositorio:

```text
base de datos PostgreSQL
backups
backend/.env
license.json
install.conf
```

El código fuente puede actualizarse.

Los datos operativos no deben depender del estado del repositorio Git.

---

# Variables de entorno

La configuración sensible se mantiene fuera del código.

Ejemplo:

```text
backend/.env
```

Puede contener:

```text
DATABASE_URL
SECRET_KEY
ENCRYPTION_KEY
ADMIN_SEED_PASSWORD
POSTGRES_PASSWORD
ENVIRONMENT=production
```

No debe versionarse.

---

# Red local

Marcha puede ser accesible mediante:

```text
http://pos.local
```

cuando mDNS esté disponible.

También puede accederse directamente mediante:

```text
http://<IP-del-servidor>
```

La dirección IP constituye un mecanismo válido de respaldo.

---

# Puertos

El objetivo es exponer únicamente lo necesario.

Normalmente:

```text
80/tcp
```

para el acceso web.

PostgreSQL, Redis y FastAPI pueden permanecer accesibles únicamente dentro de la red Docker.

---

# Actualizaciones

El procedimiento productivo de actualización se realiza mediante:

```text
update.sh
```

El script genera primero un backup pre-update.

Después:

```text
git pull
build
restart
health check
```

Ver:

```text
update.md
```

---

# Backups

Marcha incluye un sistema interno de backups.

Los backups se almacenan fuera del volumen PostgreSQL.

Ver:

```text
backup_restore.md
```

---

# Desinstalación

La desinstalación normal no destruye:

```text
base de datos
backups
.env
licencia
```

Esto permite reinstalar Marcha preservando la instalación.

No debe utilizarse:

```bash
docker compose down -v
```

salvo que se quiera destruir deliberadamente la base de datos.

---

# Verificación de despliegue

Una instalación productiva debe comprobar al menos:

```text
Docker activo
contenedores levantados
backend saludable
frontend accesible
login funcionando
WebSocket funcionando
PostgreSQL persistente
licencia válida
backup disponible
```

---

# Criterio de éxito

El despliegue se considera correctamente realizado cuando desde un dispositivo de la LAN puede completarse el flujo:

```text
login
↓
abrir caja
↓
abrir mesa
↓
crear pedido
↓
enviar a producción
↓
preparar
↓
entregar
↓
cobrar
↓
cerrar orden
```

sin necesidad de ejecutar comandos técnicos adicionales.