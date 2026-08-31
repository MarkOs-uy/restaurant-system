# Installation

## Objetivo

Este documento describe el procedimiento de instalación productiva de Marcha.

El proceso está diseñado para automatizar la mayor parte de la configuración del servidor.

---

# Requisitos

Servidor recomendado:

```text
Debian
Ubuntu
```

Debe disponer de:

- acceso administrativo;
- conexión de red local;
- espacio suficiente en disco;
- acceso temporal a Internet cuando sea necesario instalar dependencias o descargar imágenes/código.

La operación posterior de Marcha no requiere Internet de forma permanente.

---

# Archivos principales

La instalación utiliza principalmente:

```text
install.sh
docker-compose.prod.yml
scripts/start_stack.sh
```

---

# Ejecutar como administrador

La instalación requiere privilegios administrativos.

Ejemplo:

```bash
sudo ./install.sh
```

---

# Licencia antes de instalar

Antes de realizar cambios en el sistema, `install.sh` comprueba la existencia de:

```text
/var/lib/pos-restaurant/license.json
```

Si la licencia no existe, el script:

1. genera el fingerprint de la máquina;
2. muestra el código completo;
3. muestra una versión agrupada para facilitar su lectura;
4. termina sin continuar la instalación.

Ejemplo conceptual:

```text
Fingerprint:

1234567890abcdef...

12345678-90abcdef-...
```

---

# Generación de licencia

El fingerprint debe utilizarse desde la herramienta privada de emisión de licencias.

La clave privada nunca debe copiarse al servidor del cliente.

Una vez generado el archivo:

```text
license.json
```

debe colocarse en:

```text
/var/lib/pos-restaurant/license.json
```

Luego puede ejecutarse nuevamente:

```bash
sudo ./install.sh
```

---

# Importancia del orden

La licencia se comprueba antes de:

- crear `.env`;
- generar contraseñas;
- modificar hostname;
- instalar componentes;
- levantar Docker.

Esto evita instalaciones parciales.

---

# Dependencias

El instalador prepara las dependencias necesarias.

Entre ellas:

```text
Docker
Docker Compose
Avahi / mDNS cuando corresponde
herramientas auxiliares
```

---

# Configuración persistente

El instalador utiliza:

```text
/var/lib/pos-restaurant/
```

para información persistente de instalación.

Ejemplos:

```text
license.json
install.conf
```

---

# Configuración original del sistema

Durante la primera instalación se conserva información necesaria para restaurar posteriormente:

```text
hostname anterior
configuración relacionada con Avahi
```

Esta información se guarda únicamente si todavía no existe una instalación previa registrada.

Una reinstalación no debe sobrescribir los datos originales con valores ya modificados por Marcha.

---

# Hostname y mDNS

Marcha puede configurar un nombre local:

```text
pos.local
```

Esto facilita el acceso desde dispositivos del restaurante.

El nombre depende de soporte mDNS en el cliente.

Siempre debe continuar siendo posible acceder mediante IP.

---

# Configuración .env

Si no existe, el instalador genera:

```text
backend/.env
```

Incluyendo valores aleatorios para secretos relevantes.

Ejemplos:

```text
POSTGRES_PASSWORD
SECRET_KEY
ENCRYPTION_KEY
ADMIN_SEED_PASSWORD
ENVIRONMENT=production
```

El archivo no debe regenerarse automáticamente en una reinstalación si ya existe.

---

# Importancia de ENCRYPTION_KEY

`ENCRYPTION_KEY` puede utilizarse para descifrar credenciales persistidas, como la contraseña SMTP.

Perder dicha clave puede hacer que esos valores ya no puedan recuperarse.

Debe preservarse junto con la instalación.

---

# Construcción de contenedores

El instalador ejecuta el build del entorno productivo.

Conceptualmente:

```bash
docker compose -f docker-compose.prod.yml build
```

seguido de:

```bash
docker compose -f docker-compose.prod.yml up -d
```

---

# PostgreSQL

El instalador espera hasta que PostgreSQL esté disponible antes de depender del backend.

El backend aplica:

```bash
alembic upgrade head
```

durante su proceso de inicio.

---

# Seed

El backend ejecuta el seed inicial cuando corresponde.

El seed debe poder ejecutarse más de una vez sin duplicar información crítica.

---

# Registro de systemd

La instalación registra:

```text
pos-restaurant.service
```

y, cuando corresponde:

```text
pos-zeroconf.service
```

Después ejecuta:

```bash
systemctl daemon-reload
```

y habilita los servicios necesarios.

---

# Verificación de backend

La instalación no debe considerarse terminada hasta que:

```text
GET /health
```

responda correctamente.

Si el backend falla:

- se muestran logs;
- el stack se detiene;
- la instalación informa el error.

---

# Acceso inicial

Al finalizar se informa:

```text
URL local
IP del servidor
usuario inicial
contraseña inicial cuando fue generada
```

La contraseña inicial debe guardarse en un lugar seguro.

---

# Reinstalación

Una reinstalación sobre la misma máquina debe preservar:

```text
PostgreSQL
backups
.env
license.json
```

El fingerprint de la máquina permanece válido mientras la identidad del host no cambie.

---

# Desinstalación y reinstalación

El flujo soportado es:

```text
install
↓
uso
↓
uninstall
↓
reinstall
```

sin pérdida intencional de datos.

---

# No usar down -v

Nunca ejecutar:

```bash
docker compose -f docker-compose.prod.yml down -v
```

como procedimiento normal.

La opción:

```text
-v
```

elimina volúmenes y puede destruir PostgreSQL.

---

# Verificación final

Después de instalar:

```bash
systemctl status pos-restaurant
```

```bash
docker compose -f docker-compose.prod.yml ps
```

Luego comprobar desde un navegador:

```text
http://pos.local
```

o:

```text
http://<IP-servidor>
```

---

# Checklist de instalación

```text
[ ] licencia instalada
[ ] Docker funcionando
[ ] .env creado
[ ] PostgreSQL funcionando
[ ] Alembic aplicado
[ ] backend saludable
[ ] frontend accesible
[ ] systemd habilitado
[ ] login exitoso
[ ] WebSocket operativo
[ ] datos persistentes
```