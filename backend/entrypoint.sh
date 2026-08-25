#!/usr/bin/env bash
set -euo pipefail

echo "Esperando a Postgres..."

until pg_isready \
  -h db \
  -U "${POSTGRES_USER:-pos_user}" \
  -d "${POSTGRES_DB:-restaurant}" \
  >/dev/null 2>&1
do
  sleep 2
done

echo "Postgres listo"


if [ -f /backups/restore.pending ]; then
  BACKUP="$(cat /backups/restore.pending)"

  echo "========================================="
  echo " Restaurando base de datos"
  echo " Backup: $BACKUP"
  echo "========================================="

  python -m app.restore_pending

  echo "========================================="
  echo " Restauracion finalizada"
  echo "========================================="
fi


echo "Corriendo migraciones..."
alembic upgrade head


echo "Corriendo seed..."
python -m app.seed


echo "Iniciando backend..."
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000