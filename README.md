Restaurant System

Levantar el proyecto:

```bash
docker compose up --build
```

Migraciones:

```bash
docker compose exec backend alembic upgrade head
```

Seed:

Se ejecuta automaticamente.

Configuracion:

Crear `backend/.env` desde `backend/.env.example`.
Opcionalmente crear `frontend/.env` desde `frontend/.env.example`.

Variables importantes:

- `SECRET_KEY`: clave para firmar JWT.
- `CORS_ORIGINS`: origenes permitidos separados por coma.
- `VITE_API_URL`: base HTTP del frontend. Por defecto `/api`.
- `VITE_WS_URL`: base WebSocket del frontend. Por defecto usa el host actual.

Stack:

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker

![Backend tests](https://github.com/MarkOs-uy/restaurant-system/actions/workflows/backend-tests.yml/badge.svg)