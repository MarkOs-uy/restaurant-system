# Development Setup

## Objetivo

Este documento describe cómo preparar un entorno de desarrollo para Marcha.

Su propósito es permitir que un nuevo desarrollador pueda:

- clonar el proyecto;
- configurar backend y frontend;
- levantar la infraestructura;
- ejecutar migraciones;
- iniciar el sistema;
- correr tests;
- trabajar sin afectar instalaciones de producción.

---

## Requisitos generales

Entorno recomendado:

```text
Windows + Docker Desktop
o
Linux + Docker Engine
```

Herramientas principales:

```text
Git
Docker
Docker Compose
Python
Node.js
npm
PostgreSQL client tools opcionales
```

El desarrollo puede realizarse con backend y frontend ejecutándose localmente mientras los servicios de infraestructura se ejecutan mediante Docker.

---

# Estructura general del proyecto

Ejemplo:

```text
marcha/
├── backend/
├── frontend/
├── scripts/
├── docs/
├── docker-compose.yml
├── docker-compose.prod.yml
└── README.md
```

---

# Clonar el proyecto

```bash
git clone <repository-url>
cd marcha
```

---

# Configuración backend

Entrar en:

```bash
cd backend
```

Crear entorno virtual:

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux

```bash
source venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

# Variables de entorno

El backend utiliza un archivo:

```text
backend/.env
```

Este archivo no debe versionarse.

Ejemplo conceptual:

```text
DATABASE_URL=postgresql+psycopg2://admin:password@localhost:5432/restaurant
SECRET_KEY=...
ENCRYPTION_KEY=...
ENVIRONMENT=development
```

Las credenciales concretas dependen del entorno local.

---

# Base de datos

Marcha utiliza PostgreSQL.

Durante desarrollo puede levantarse mediante Docker:

```bash
docker compose up -d db
```

Si el backend se ejecuta desde el host, `DATABASE_URL` debe utilizar un hostname accesible desde el host.

Ejemplo:

```text
localhost
```

No debe utilizarse:

```text
db
```

salvo que el backend también se ejecute dentro de Docker Compose.

---

# Diferencia host vs Docker

Dentro de Docker Compose:

```text
backend
   ↓
db:5432
```

Desde el sistema host:

```text
backend local
   ↓
localhost:<puerto-publicado>
```

Por lo tanto, una URL como:

```text
postgresql://...@db:5432/...
```

solo funciona cuando el proceso que la utiliza participa en la red Docker correspondiente.

---

# Migraciones

Marcha utiliza Alembic como única autoridad para evolucionar el esquema.

Aplicar migraciones:

```bash
alembic upgrade head
```

Crear una nueva migración:

```bash
alembic revision --autogenerate -m "descripcion"
```

Revisar siempre el archivo generado antes de aplicarlo.

---

# Migraciones y Models

Flujo recomendado:

```text
Modificar Model
   ↓
alembic revision --autogenerate
   ↓
revisar migration
   ↓
alembic upgrade head
   ↓
probar
```

No debe utilizarse:

```python
Base.metadata.create_all()
```

para evolucionar una base de datos de desarrollo o producción existente.

Su uso puede existir únicamente en contextos controlados como tests aislados.

---

# Iniciar backend

Con el entorno virtual activo:

```bash
uvicorn app.main:app --reload
```

El backend queda disponible normalmente en:

```text
http://localhost:8000
```

Documentación FastAPI:

```text
http://localhost:8000/docs
```

---

# Health Check

El backend proporciona un endpoint de health.

Ejemplo:

```text
GET /health
```

Debe utilizarse para verificar que la aplicación inició correctamente.

---

# Licenciamiento en desarrollo

El entorno de desarrollo utiliza:

```text
ENVIRONMENT=development
```

En este modo, la validación de licencia de producción puede omitirse.

La licencia nunca debe deshabilitarse automáticamente en producción.

---

# Frontend

Entrar en:

```bash
cd frontend
```

Instalar dependencias:

```bash
npm install
```

Cuando exista `package-lock.json`, en instalaciones reproducibles puede utilizarse:

```bash
npm ci
```

---

# Iniciar frontend

```bash
npm run dev
```

Vite mostrará la URL disponible.

Ejemplo:

```text
http://localhost:5173
```

---

# Frontend y backend

Durante desarrollo el frontend debe comunicarse con el backend utilizando la configuración definida por el proyecto.

Las llamadas deben pasar por:

```typescript
apiFetch(...)
```

No deben introducirse URLs absolutas dispersas dentro de Pages o Components.

---

# Build frontend

Antes de considerar terminado un cambio importante:

```bash
npm run build
```

Esto es obligatorio especialmente cuando el desarrollo se realiza sobre Windows.

El build puede detectar problemas que Windows no muestra durante desarrollo.

Ejemplos:

```text
casing incorrecto
imports inexistentes
exports duplicados
errores TypeScript
variables sin usar
```

---

# Diferencias de casing

Linux distingue:

```text
WebSocketEvents.ts
```

de:

```text
webSocketEvents.ts
```

Windows puede no hacerlo.

Por ello:

> El nombre utilizado en un import debe coincidir exactamente con el nombre físico del archivo.

---

# Redis

Marcha utiliza Redis para eventos en tiempo real.

Puede iniciarse mediante:

```bash
docker compose up -d redis
```

El backend debe utilizar la dirección correspondiente al entorno donde está ejecutándose.

---

# Docker Compose completo

Cuando se desea ejecutar todo el stack mediante Docker:

```bash
docker compose up -d
```

Ver estado:

```bash
docker compose ps
```

Ver logs:

```bash
docker compose logs -f
```

Backend:

```bash
docker compose logs -f backend
```

---

# Detener entorno Docker

```bash
docker compose down
```

Esto no debe confundirse con:

```bash
docker compose down -v
```

`-v` elimina volúmenes y puede destruir la base de datos local.

Debe utilizarse únicamente cuando se desea explícitamente reiniciar la persistencia.

---

# Desarrollo con backend local

Una configuración habitual es:

```text
Frontend
→ npm run dev

Backend
→ uvicorn ... --reload

PostgreSQL
→ Docker

Redis
→ Docker
```

Ventajas:

- recarga rápida;
- debugging sencillo;
- infraestructura reproducible.

---

# Desarrollo completamente Dockerizado

También puede ejecutarse:

```text
Frontend
Backend
PostgreSQL
Redis
```

mediante Docker Compose.

Esta modalidad es útil para:

- probar comportamiento más cercano a producción;
- validar networking;
- evitar diferencias de dependencias locales.

---

# Seed

Marcha posee un proceso de seed para crear información inicial cuando corresponde.

El seed debe ser:

- idempotente;
- seguro de ejecutar nuevamente;
- compatible con una base ya inicializada.

No debe dependerse del seed para modificar datos de producción existentes de forma arbitraria.

---

# Testing backend

Los tests se encuentran en:

```text
backend/tests/
```

Ejemplo:

```text
tests/
├── conftest.py
└── unit/
    ├── factories.py
    ├── test_order_service.py
    ├── test_cash_register_service.py
    ├── test_auth_and_permissions.py
    └── test_backup_service.py
```

Ejecutar toda la suite:

```bash
pytest
```

Modo verbose:

```bash
pytest -v
```

Un archivo concreto:

```bash
pytest tests/unit/test_order_service.py -v
```

Desde Docker:

```bash
docker compose exec backend pytest -v
```

---

# Base de datos de tests

Los tests unitarios actuales utilizan:

```text
SQLite in-memory
```

Cada test recibe una base aislada.

Ventajas:

- no modifica PostgreSQL;
- no depende del contenedor `db`;
- ejecución rápida;
- aislamiento por test.

Los tests que requieran comportamiento específico de PostgreSQL deberán utilizar una estrategia de integración separada.

---

# Fixtures

Las fixtures comunes se encuentran en:

```text
tests/conftest.py
```

Ejemplos:

```text
db
restaurant
user
table
product
order
```

Pytest descubre este archivo automáticamente.

No es necesario importarlo desde cada test.

---

# Factories de tests

Las funciones para crear entidades específicas se encuentran en:

```text
tests/unit/factories.py
```

Ejemplos:

```text
crear_pago
crear_movimiento_caja
crear_orden
crear_item
```

Se utilizan para reducir boilerplate sin ocultar excesivamente la construcción de datos.

---

# Archivos temporales

Los tests que escriben archivos deben utilizar recursos temporales de pytest.

Ejemplo:

```python
tmp_path
```

Nunca deben escribir accidentalmente en:

```text
/backups
```

o en directorios reales de una instalación.

---

# Mocks

Los servicios externos o procesos del sistema pueden mockearse cuando el objetivo del test no es verificar la herramienta externa.

Ejemplo:

```text
pg_dump
```

No es necesario probar que PostgreSQL sabe ejecutar `pg_dump`.

Debe probarse:

- cómo se invoca;
- cómo se maneja un error;
- qué hace Marcha ante ese error.

---

# Flujo de trabajo recomendado

Antes de comenzar:

```bash
git pull
```

Crear o seleccionar rama según la política vigente.

Durante desarrollo:

```text
modificar
↓
probar manualmente
↓
ejecutar tests relevantes
↓
npm run build si hay frontend
↓
revisar git diff
```

Antes de commit:

```bash
git status
git diff
```

---

# Archivos locales

Archivos de trabajo local que no formen parte del producto deben mantenerse fuera de Git mediante:

```text
.gitignore
```

Ejemplos actuales:

```text
PROJECT_SUMMARY.md
analyze_project.py
```

Si un archivo ya fue versionado antes de incluirlo en `.gitignore`, debe eliminarse del índice mediante:

```bash
git rm --cached <archivo>
```

---

# Secretos

Nunca deben committearse:

```text
.env
private keys
passwords
tokens
production license files
SMTP credentials
database dumps
```

La clave privada utilizada para emitir licencias se mantiene fuera del repositorio distribuido.

---

# Producción

El entorno de desarrollo no debe utilizarse como sustituto de una instalación productiva.

Antes de liberar una versión debe probarse también:

```text
Docker production build
installation
migration
startup
health checks
update
backup
restore
licensing
```

---

# Documentación relacionada

```text
architecture_overview.md
backend_structure.md
frontend_structure.md
backend_standards.md
frontend_standards.md
testing_strategy.md
```

---

# Principio final

El entorno de desarrollo debe permitir:

```text
clonar
↓
configurar
↓
levantar infraestructura
↓
migrar
↓
ejecutar
↓
testear
```

sin depender de conocimiento no documentado del desarrollador original.

Si para iniciar Marcha un nuevo programador necesita preguntar qué comando secreto debe ejecutar, falta documentación.