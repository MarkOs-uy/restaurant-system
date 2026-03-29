#!/bin/bash

echo "Esperando a Postgres..."

until pg_isready -h db -U admin
do
  sleep 2
done

echo "Postgres listo ✅"

echo "Corriendo migrations..."
alembic upgrade head

echo "Corriendo seed..."
python -m app.seed

echo "Iniciando backend..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
