# Marcha

Sistema integral de gestión para restaurantes, diseñado para operar dentro de la red local del establecimiento y con mínima dependencia de Internet.

Marcha centraliza las principales operaciones del restaurante:

- mesas;
- pedidos;
- producción;
- cocina;
- caja;
- pagos;
- usuarios;
- productos;
- reportes;
- backups;
- licenciamiento.

El sistema utiliza una arquitectura cliente-servidor y puede ser utilizado desde PCs, tablets y teléfonos conectados a la misma red local.

---

## Principios del producto

Marcha fue diseñado priorizando:

- operación local;
- funcionamiento sin Internet permanente;
- simplicidad de uso;
- sincronización en tiempo real;
- separación por roles;
- persistencia confiable;
- despliegue reproducible;
- recuperación mediante backups.

> El objetivo es que el restaurante pueda completar un turno operativo sin depender de servicios externos.

---

## Stack tecnológico

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Alembic

### Frontend

- React
- TypeScript
- Vite

### Infraestructura

- PostgreSQL
- Redis
- Docker
- Docker Compose
- Nginx
- systemd

---

## Arquitectura general

```text
      Tablets / teléfonos / PCs
                 │
                 │ LAN / Wi-Fi
                 ▼
              Nginx
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

# Desarrollo

## Requisitos

- Docker
- Docker Compose
- Python
- Node.js
- npm

---

## Levantar infraestructura

```bash
docker compose up --build
```

---

## Backend

Crear:

```text
backend/.env
```

a partir de:

```text
backend/.env.example
```

Variables importantes:

```text
SECRET_KEY
CORS_ORIGINS
DATABASE_URL
ENVIRONMENT
ENCRYPTION_KEY
```

Aplicar migraciones:

```bash
docker compose exec backend alembic upgrade head
```

El seed se ejecuta automáticamente cuando corresponde.

---

## Frontend

Opcionalmente crear:

```text
frontend/.env
```

desde:

```text
frontend/.env.example
```

Variables principales:

```text
VITE_API_URL
VITE_WS_URL
```

Valores productivos habituales:

```text
VITE_API_URL=/api
```

y WebSocket utilizando el host actual.

---

## Ejecutar tests

Toda la suite backend:

```bash
docker compose exec backend pytest -v
```

Solo unit tests:

```bash
docker compose exec backend pytest tests/unit -v
```

Ejemplo:

```bash
docker compose exec backend pytest tests/unit/test_order_service.py -v
```

---

## Build frontend

Antes de considerar terminado un cambio frontend:

```bash
cd frontend
npm run build
```

Esto permite detectar problemas que pueden pasar inadvertidos durante desarrollo, especialmente diferencias de casing entre Windows y Linux.

---

# Producción

El despliegue productivo utiliza:

```text
docker-compose.prod.yml
```

La instalación está automatizada mediante scripts operativos.

Principales:

```text
install.sh
start_server.sh
stop_server.sh
update.sh
uninstall.sh
scripts/start_stack.sh
```

No se recomienda administrar manualmente producción mediante comandos Docker aislados cuando existe un script específico para la operación.

---

# Persistencia

Los datos importantes deben sobrevivir a:

- reinicios;
- recreación de contenedores;
- actualizaciones;
- desinstalación normal;
- reinstalación.

Esto incluye principalmente:

```text
PostgreSQL
backups
backend/.env
license.json
```

---

# Licenciamiento

La versión productiva utiliza licencia offline vinculada a la máquina.

La licencia se almacena en:

```text
/var/lib/pos-restaurant/license.json
```

La validación utiliza firma digital Ed25519.

La clave privada de emisión no forma parte del proyecto distribuido.

---

# Backups

Marcha dispone de:

- backups manuales;
- backups automáticos;
- diarios;
- semanales;
- mensuales;
- políticas de retención;
- restore;
- pre-restore;
- backups pre-update.

Los backups no deben considerarse completamente validados hasta comprobar una restauración.

---

# Roles

Roles actuales:

```text
ADMIN
WAITER
KITCHEN
CASHIER
```

Cada rol tiene responsabilidades operativas diferentes.

La interfaz puede ocultar acciones según rol, pero la autorización definitiva siempre se valida en backend.

---

# Estados principales

## Order

```text
OPEN
SENT
IN_PROGRESS
READY
CLOSED
CANCELLED
```

## OrderItem

```text
PENDING
SENT
IN_PROGRESS
READY
DELIVERED
CANCELLED
```

Las reglas completas se encuentran documentadas en:

```text
docs/architecture/domain_rules.md
```

---

# Documentación

La documentación del proyecto se encuentra en:

```text
docs/
```

---

## Architecture

```text
docs/architecture/
├── architecture_overview.md
├── architecture_decisions.md
├── backend_structure.md
├── frontend_structure.md
├── data_model.md
├── domain_rules.md
└── realtime_events.md
```

### `architecture_overview.md`

Visión general del sistema.

### `architecture_decisions.md`

Decisiones arquitectónicas y motivos.

### `backend_structure.md`

Organización del backend.

### `frontend_structure.md`

Organización del frontend.

### `data_model.md`

Entidades y relaciones principales.

### `domain_rules.md`

Reglas funcionales y transiciones permitidas.

### `realtime_events.md`

Eventos y sincronización mediante WebSockets.

---

## Development

```text
docs/development/
├── backend_standards.md
├── frontend_standards.md
├── development_setup.md
└── testing_strategy.md
```

### `backend_standards.md`

Convenciones de desarrollo backend.

### `frontend_standards.md`

Convenciones de desarrollo frontend.

### `development_setup.md`

Preparación del entorno de desarrollo.

### `testing_strategy.md`

Estrategia y prioridades de testing.

---

## Operations

```text
docs/operations/
├── production_deployment.md
├── installation.md
├── update.md
├── backup_restore.md
├── licensing.md
└── troubleshooting.md
```

### `production_deployment.md`

Arquitectura de producción.

### `installation.md`

Instalación productiva.

### `update.md`

Procedimiento seguro de actualización.

### `backup_restore.md`

Backup y recuperación.

### `licensing.md`

Licenciamiento offline.

### `troubleshooting.md`

Diagnóstico de problemas frecuentes.

---

## Product

```text
docs/product/
├── product_overview.md
├── functional_scope.md
├── roadmap.md
└── known_limitations.md
```

### `product_overview.md`

Descripción general del producto.

### `functional_scope.md`

Alcance funcional actual.

### `roadmap.md`

Evolución prevista.

### `known_limitations.md`

Limitaciones conocidas y alcance no implementado.

---

# Flujo operativo principal

```text
Abrir caja
    ↓
Abrir mesa
    ↓
Agregar productos
    ↓
Enviar a producción
    ↓
Preparar
    ↓
Marcar READY
    ↓
Entregar
    ↓
Registrar pago
    ↓
Cerrar orden
    ↓
Cerrar caja
```

Este flujo constituye el núcleo funcional del producto.

---

# Testing

La estrategia de testing prioriza riesgo.

Prioridades principales:

```text
P0
→ dinero
→ caja
→ órdenes
→ pagos
→ estados

P1
→ autenticación
→ permisos
→ multi-tenancy
→ backups
→ licenciamiento
```

La cobertura porcentual no es el objetivo principal.

El objetivo es proteger las operaciones cuyo fallo tendría mayor impacto.

---

# Seguridad

Principios principales:

- autenticación mediante JWT;
- autorización por roles;
- separación por `restaurant_id`;
- reglas críticas validadas en backend;
- secretos fuera del código;
- credenciales sensibles cifradas;
- licencia firmada digitalmente.

El frontend nunca se considera frontera de seguridad.

---

# Multi-tenancy

Las entidades operativas pertenecen a un restaurante mediante:

```text
restaurant_id
```

Todas las operaciones deben respetar esa pertenencia.

Conocer el ID de un recurso no autoriza a acceder a él.

---

# Fuente de verdad

Para el esquema físico:

```text
SQLAlchemy Models
+
Alembic migrations
```

Para reglas de negocio:

```text
Domain Services
```

Para estado persistente:

```text
PostgreSQL
```

Para sincronización:

```text
WebSocket notifica
HTTP confirma
```

---

# Filosofía de desarrollo

Marcha prioriza soluciones:

```text
claras
predecibles
mantenibles
simples
```

sobre abstracciones innecesarias.

No se introduce complejidad únicamente porque una arquitectura más sofisticada sea técnicamente posible.

---

# Estado del proyecto

Marcha dispone actualmente de un flujo funcional completo que ha sido probado en aspectos como:

- instalación desde cero;
- migraciones;
- autenticación;
- pedidos;
- producción;
- caja;
- WebSockets;
- backups;
- actualización;
- desinstalación;
- reinstalación;
- persistencia;
- licenciamiento offline.

La etapa siguiente se centra principalmente en validación mediante uso real en restaurantes.

---

# Proyecto

**Marcha**

Sistema integral de gestión para restaurantes.