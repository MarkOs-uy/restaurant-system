Restaurant System

Levantar el proyecto
docker compose up --build

Migraciones
docker compose exec backend alembic upgrade head

Seed
(se ejecuta automáticamente)

Stack

FastAPI
PostgreSQL
SQLAlchemy
Alembic
Docker