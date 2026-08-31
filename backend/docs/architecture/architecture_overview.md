# Architecture Overview

## Introducción

Marcha es un sistema de gestión integral para restaurantes diseñado bajo una arquitectura cliente-servidor de operación local.

El objetivo arquitectónico principal es garantizar que las funciones esenciales del restaurante puedan ejecutarse sin depender de una conexión permanente a Internet.

Marcha coordina:

- salón;
- pedidos;
- producción;
- caja;
- administración;
- reportes;
- backups;
- sincronización en tiempo real.

---

## Principios arquitectónicos

La arquitectura se basa en los siguientes principios:

- operación local y offline-first;
- servidor dentro del establecimiento;
- clientes web ligeros;
- separación entre frontend y backend;
- reglas de negocio centralizadas;
- persistencia relacional;
- sincronización en tiempo real;
- despliegue reproducible;
- aislamiento lógico por restaurante;
- backups integrados;
- licenciamiento offline.

---

## Arquitectura general

La arquitectura de producción puede representarse así:

```text
         Tablets / teléfonos / PCs
                    │
                    │ HTTP / WebSocket
                    ▼
              Red LAN / Wi-Fi
                    │
                    ▼
                Nginx :80
             ┌──────┴──────┐
             │             │
             ▼             ▼
        React SPA       /api + /ws
                           │
                           ▼
                       FastAPI
                       Backend
                       │   │
              ┌────────┘   └────────┐
              │                     │
              ▼                     ▼
         PostgreSQL               Redis
              │                     │
              │                     │
              └─────── dominio ─────┘
```

---

## Modelo de despliegue

Marcha se instala en un equipo que funciona como servidor local del restaurante.

Los clientes acceden mediante navegador web desde:

- computadoras;
- tablets;
- teléfonos móviles.

Los dispositivos deben estar conectados a la misma red local.

El sistema no requiere instalar una aplicación nativa en cada dispositivo cliente.

---

## Offline-first

La operación principal de Marcha no depende de Internet.

Las siguientes funciones pueden ejecutarse exclusivamente dentro de la red local:

- autenticación;
- mesas;
- pedidos;
- cocina;
- producción;
- pagos;
- caja;
- administración;
- reportes;
- backups locales.

Algunas capacidades opcionales pueden requerir conectividad externa.

Ejemplo:

```text
envío de backups por correo electrónico
```

La pérdida de Internet no debe impedir el funcionamiento operativo del restaurante.

---

## Frontend

El frontend está desarrollado mediante:

```text
React
TypeScript
Vite
```

Es una Single Page Application.

Su responsabilidad es:

- mostrar información;
- permitir interacción;
- mantener estado visual;
- comunicarse con el backend;
- reaccionar a eventos WebSocket.

El frontend no implementa la autoridad final sobre las reglas de negocio.

---

## Backend

El backend utiliza:

```text
Python
FastAPI
SQLAlchemy
Pydantic
Alembic
```

Es responsable de:

- autenticación;
- autorización;
- reglas de negocio;
- acceso a datos;
- transacciones;
- validaciones;
- emisión de eventos;
- backups;
- tareas programadas;
- licenciamiento.

---

## Arquitectura interna del backend

El flujo habitual es:

```text
Router
   ↓
Dependency Injection
   ↓
Service
   ↓
SQLAlchemy
   ↓
PostgreSQL
```

Las reglas de negocio se implementan principalmente en Services.

Los Routers permanecen enfocados en HTTP.

No existe actualmente una capa Repository obligatoria.

---

## Base de datos

Marcha utiliza PostgreSQL como base de datos de producción.

PostgreSQL almacena información como:

- restaurantes;
- usuarios;
- mesas;
- productos;
- categorías;
- estaciones;
- órdenes;
- items;
- pagos;
- cajas;
- movimientos;
- configuración;
- eventos.

El esquema se administra mediante Alembic.

---

## Evolución del esquema

Toda modificación del esquema se realiza mediante migraciones.

Flujo:

```text
Models
   ↓
Alembic revision
   ↓
revisión
   ↓
migration
   ↓
alembic upgrade head
```

`Base.metadata.create_all()` no se utiliza para evolucionar el esquema de producción.

---

## Multi-tenancy

El modelo de datos soporta múltiples restaurantes mediante:

```text
restaurant_id
```

Las entidades que pertenecen a un restaurante se encuentran asociadas explícitamente a dicho identificador.

Ejemplo conceptual:

```text
Restaurant
   ├── Users
   ├── Tables
   ├── Products
   ├── Orders
   ├── Payments
   └── Cash Registers
```

Las consultas del backend deben respetar siempre esta pertenencia.

`restaurant_id` constituye una frontera lógica y de seguridad.

---

## Roles

Marcha define distintos perfiles operativos.

Actualmente:

```text
ADMIN
WAITER
KITCHEN
CASHIER
```

Cada rol accede a funcionalidades relacionadas con su trabajo.

### ADMIN

Administra:

- productos;
- categorías;
- usuarios;
- estaciones;
- mesas;
- configuración;
- reportes;
- backups.

### WAITER

Gestiona:

- mesas;
- pedidos;
- productos;
- entrega de items.

### KITCHEN

Gestiona:

- estaciones;
- producción;
- cambios de estado de items.

### CASHIER

Gestiona:

- pagos;
- caja;
- movimientos;
- cierre de órdenes.

---

## Órdenes

La orden es una de las entidades principales del dominio.

Flujo general:

```text
OPEN
 ↓
SENT
 ↓
IN_PROGRESS
 ↓
READY
 ↓
CLOSED
```

También existe:

```text
CANCELLED
```

Las reglas de transición se controlan en el backend.

---

## Items de orden

Cada producto agregado a una orden posee su propio estado.

Flujo habitual:

```text
PENDING
   ↓
SENT
   ↓
IN_PROGRESS
   ↓
READY
   ↓
DELIVERED
```

También puede existir:

```text
CANCELLED
```

Esta granularidad permite que distintos productos del mismo pedido evolucionen de forma independiente.

---

## Producción

Los productos pueden asociarse a estaciones de producción.

Ejemplo:

```text
Pedido
├── Hamburguesa → Cocina
├── Refresco    → Barra
└── Postre      → Cocina
```

Cada estación visualiza únicamente los items que le corresponden.

Las estaciones pueden desactivarse sin eliminarse físicamente.

---

## Caja y pagos

Los pagos se asocian a órdenes.

Métodos actuales:

```text
CASH
CARD
TRANSFER
```

La caja controla:

- importe inicial;
- ventas;
- efectivo;
- movimientos;
- efectivo esperado;
- efectivo contado;
- diferencia.

La lógica monetaria crítica se ejecuta en backend.

---

## Comunicación en tiempo real

Marcha utiliza:

```text
Redis
+
WebSockets
```

para sincronizar clientes.

Ejemplo:

```text
Waiter
   ↓
envía pedido
   ↓
Backend
   ↓
PostgreSQL
   ↓
evento
   ↓
Redis
   ↓
WebSocket
   ↓
Kitchen
```

Los eventos pueden distribuirse por:

- rol;
- estación;
- audiencia general.

---

## Filosofía de eventos

Los eventos representan cambios ocurridos en el sistema.

El frontend no debería depender necesariamente del evento como única fuente del estado completo.

Patrón preferido:

```text
evento
   ↓
cliente detecta cambio
   ↓
HTTP GET
   ↓
estado actual
```

Esto reduce el riesgo de inconsistencias.

---

## Nginx

Nginx constituye el único punto HTTP expuesto en producción.

Gestiona:

```text
/       → frontend React
/api/   → FastAPI
/ws     → WebSocket
```

El puerto interno de FastAPI no necesita exponerse directamente a la LAN.

---

## Docker

Los componentes principales de producción se ejecutan mediante Docker.

Servicios principales:

```text
db
backend
redis
frontend
```

Todos se gestionan mediante:

```text
docker-compose.prod.yml
```

---

## Systemd

Systemd administra el ciclo de vida lógico del stack.

Servicio principal:

```text
pos-restaurant.service
```

Systemd no considera que Marcha está operativo únicamente porque los contenedores hayan sido creados.

El proceso de arranque verifica que el backend quede saludable.

---

## Arranque de producción

Flujo simplificado:

```text
systemd
   ↓
start_stack.sh
   ↓
Docker Compose
   ↓
PostgreSQL / Redis / Frontend / Backend
   ↓
Backend entrypoint
```

El backend ejecuta:

```text
espera PostgreSQL
   ↓
restauración pendiente si existe
   ↓
Alembic
   ↓
validación de licencia
   ↓
seed
   ↓
Uvicorn
```

Solo después de responder correctamente en:

```text
/health
```

se considera que el backend está disponible.

---

## Scripts operativos

Marcha incluye scripts para administrar el ciclo de vida del producto.

```text
install.sh
start_server.sh
stop_server.sh
update.sh
uninstall.sh
```

Cada uno tiene una responsabilidad específica.

### install.sh

- prepara el sistema;
- instala dependencias;
- configura Docker;
- genera configuración;
- construye contenedores;
- registra servicios;
- configura red local.

### start_server.sh

- inicia Marcha;
- verifica backend;
- verifica frontend;
- informa errores.

### stop_server.sh

- detiene servicios;
- baja el stack Docker;
- conserva datos.

### update.sh

- realiza backup técnico;
- actualiza código;
- reconstruye imágenes;
- reinicia servicios;
- verifica disponibilidad.

### uninstall.sh

- detiene Marcha;
- elimina servicios;
- restaura configuración de red;
- conserva datos, backups, configuración y licencia.

---

## Backups

Marcha administra backups internamente.

Puede realizar:

- backups manuales;
- automáticos;
- diarios;
- semanales;
- mensuales;
- pre-restore;
- retención;
- restauración;
- descarga;
- envío por correo.

Los backups se almacenan fuera del volumen PostgreSQL.

Esto permite conservarlos incluso si el volumen de base de datos es eliminado.

---

## Actualizaciones

Antes de actualizar, el sistema genera un backup técnico.

Flujo:

```text
verificar repositorio
   ↓
backup pre-update
   ↓
git pull
   ↓
build
   ↓
restart
   ↓
health check
```

Las migraciones se ejecutan únicamente desde el entrypoint del backend.

El updater no duplica esa responsabilidad.

---

## Licenciamiento

Marcha utiliza un sistema de licencia offline.

La licencia:

```text
license.json
```

se almacena fuera del repositorio en:

```text
/var/lib/pos-restaurant/license.json
```

La licencia se encuentra firmada digitalmente.

El backend contiene únicamente la clave pública necesaria para verificarla.

---

## Fingerprint de máquina

La licencia está vinculada a una identidad derivada del host.

Actualmente intervienen:

```text
/etc/machine-id
/sys/class/dmi/id/product_uuid
```

Estos valores se normalizan y se procesan mediante SHA-256.

La identidad se recalcula desde la máquina.

No se confía en un archivo local editable como fuente del fingerprint.

---

## Firma digital

Las licencias utilizan Ed25519.

Arquitectura:

```text
Herramienta privada
   ↓
Private Key
   ↓
firma license.json
```

En el cliente:

```text
license.json
+
Public Key
   ↓
Backend
   ↓
verificación
```

La clave privada nunca se distribuye con Marcha.

---

## Comportamiento ante licencia inválida

Si la licencia:

- no existe;
- está modificada;
- tiene firma inválida;
- pertenece a otra máquina;
- ha expirado cuando corresponda;

el backend no inicia.

El stack se considera fallido y systemd refleja dicho estado.

---

## Seguridad

La arquitectura incorpora varias capas de seguridad.

Entre ellas:

- autenticación;
- JWT;
- autorización por roles;
- aislamiento por `restaurant_id`;
- validaciones backend;
- secretos mediante variables de entorno;
- cifrado de credenciales sensibles;
- licencia firmada;
- backups;
- acceso limitado al entorno LAN.

La interfaz frontend no se considera frontera de seguridad.

---

## SMTP

Marcha puede utilizar SMTP para envío de backups.

Las credenciales sensibles no se almacenan en texto plano.

La contraseña SMTP se cifra mediante Fernet utilizando:

```text
ENCRYPTION_KEY
```

La clave debe conservarse junto con la configuración de la instalación.

---

## Configuración

La configuración sensible del backend se almacena fuera del código fuente.

Ejemplo:

```text
backend/.env
```

Puede contener:

```text
DATABASE_URL
SECRET_KEY
ENCRYPTION_KEY
POSTGRES_PASSWORD
ADMIN_SEED_PASSWORD
```

Este archivo no debe versionarse.

---

## Entornos

Marcha distingue entre desarrollo y producción.

### Desarrollo

Puede utilizar:

```text
Vite dev server
FastAPI local
Docker para infraestructura
```

La validación de licencia puede omitirse.

### Producción

Utiliza:

```text
Docker Compose
Nginx
Systemd
PostgreSQL
Redis
Licensing obligatorio
```

---

## Arquitectura de red

El servidor puede anunciarse mediante mDNS como:

```text
pos.local
```

También puede accederse mediante IP local.

Ejemplo:

```text
http://192.168.x.x
```

El uso de IP constituye un mecanismo válido cuando el dispositivo cliente no resuelve mDNS.

---

## Dependencias externas

La operación principal de Marcha busca minimizar dependencias externas.

No requiere:

- cloud obligatorio;
- base de datos remota;
- servicio externo de autenticación;
- servidor de licencias online.

Las integraciones externas deben ser complementarias y no impedir la operación principal del restaurante.

---

## Escalabilidad

La arquitectura actual prioriza:

```text
simplicidad
+
confiabilidad
+
operación local
```

sobre escalabilidad distribuida innecesaria.

Marcha puede soportar múltiples clientes conectados al mismo servidor mediante:

```text
HTTP
WebSockets
Redis
PostgreSQL
```

No se introducen componentes distribuidos adicionales mientras no exista una necesidad real.

---

## Decisiones arquitectónicas

Las decisiones importantes se documentan en:

```text
architecture_decisions.md
```

Ejemplos:

- offline-first;
- PostgreSQL;
- Alembic;
- ausencia de Repository obligatorio;
- multi-tenancy;
- WebSockets;
- Docker;
- systemd;
- backups;
- licenciamiento.

El objetivo es conservar el contexto y evitar que decisiones históricas importantes sean modificadas sin comprender sus motivos.

---

## Documentación relacionada

La arquitectura se complementa con:

```text
backend_structure.md
backend_standards.md
frontend_structure.md
frontend_standards.md
architecture_decisions.md
```

Cada documento responde a una pregunta distinta.

### `architecture_overview.md`

> ¿Cómo funciona Marcha como sistema completo?

### `backend_structure.md`

> ¿Cómo está organizado el backend?

### `backend_standards.md`

> ¿Qué reglas debe seguir el código backend?

### `frontend_structure.md`

> ¿Cómo está organizado el frontend?

### `frontend_standards.md`

> ¿Qué reglas debe seguir el código frontend?

### `architecture_decisions.md`

> ¿Por qué se tomaron determinadas decisiones?

---

## Visión resumida

Marcha puede resumirse arquitectónicamente de esta forma:

```text
┌───────────────────────────────────────────────┐
│                  CLIENTES                     │
│                                               │
│   PC        Tablet        Teléfono            │
└───────────────────────┬───────────────────────┘
                        │
                 LAN / Wi-Fi
                        │
                        ▼
┌───────────────────────────────────────────────┐
│                    NGINX                      │
│                                               │
│   React SPA        /api         /ws            │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│                   FASTAPI                     │
│                                               │
│ Routers → Services → Domain                   │
│                    │                          │
│           Events / Scheduler / Licensing      │
└──────────────┬─────────────────┬──────────────┘
               │                 │
               ▼                 ▼
        ┌────────────┐       ┌─────────┐
        │ PostgreSQL │       │  Redis  │
        └────────────┘       └─────────┘
```

---

## Principio final

La arquitectura de Marcha busca que la complejidad técnica esté al servicio de una operación simple.

El objetivo no es construir una infraestructura sofisticada por sí misma.

El objetivo es que, durante un turno real de restaurante:

```text
el mozo tome pedidos,
la cocina los reciba,
la caja pueda cobrar,
los dispositivos se mantengan sincronizados
y el sistema siga funcionando aunque Internet desaparezca.
```

Toda decisión arquitectónica futura debería evaluarse en función de ese principio.