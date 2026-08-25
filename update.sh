#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="docker-compose.prod.yml"
SERVICE_NAME="pos-restaurant"
ZEROCONF_SERVICE="pos-zeroconf"
BACKUP_DIR="${APP_DIR}/backups/manual-updates"
PRE_UPDATE_BACKUPS_MAX=10

if [ -t 1 ]; then
  RED=$'\033[31m'
  GREEN=$'\033[32m'
  YELLOW=$'\033[33m'
  BLUE=$'\033[34m'
  BOLD=$'\033[1m'
  RESET=$'\033[0m'
else
  RED=""
  GREEN=""
  YELLOW=""
  BLUE=""
  BOLD=""
  RESET=""
fi

section() {
  printf "\n%s==> %s%s\n" "$BLUE" "$1" "$RESET"
}

success() {
  printf "%s[OK]%s %s\n" "$GREEN" "$RESET" "$1"
}

warn() {
  printf "%s[AVISO]%s %s\n" "$YELLOW" "$RESET" "$1"
}

fail() {
  printf "%s[ERROR]%s %s\n" "$RED" "$RESET" "$1" >&2
  exit 1
}

run_privileged() {
  if [ "$EUID" -eq 0 ]; then
    "$@"
  else
    sudo "$@"
  fi
}

compose() {
  docker compose -f "$COMPOSE_FILE" "$@"
}

service_exists() {
  command -v systemctl >/dev/null 2>&1 && systemctl cat "$1" >/dev/null 2>&1
}

wait_for_backend() {
  local ready=0

  for _ in {1..45}; do
    if compose exec -T backend python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" >/dev/null 2>&1; then
      ready=1
      break
    fi
    sleep 2
  done

  [ "$ready" -eq 1 ] || fail "El backend no quedo listo despues de actualizar. Revisa: docker compose -f ${COMPOSE_FILE} logs backend"
}

wait_for_frontend() {
  local ready=0

  for _ in {1..30}; do
    if curl -fsS \
      http://127.0.0.1/ \
      >/dev/null 2>&1
    then
      ready=1
      break
    fi

    sleep 1
  done

  [ "$ready" -eq 1 ] || \
    fail "El frontend no quedo listo despues de actualizar. Revisa: docker compose -f ${COMPOSE_FILE} logs frontend"
}

make_database_backup() {
  if ! compose exec -T db sh -c \
    'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
    >/dev/null 2>&1
  then
    fail "La base de datos no esta disponible. No se actualizara sin backup previo."
  fi

  mkdir -p "$BACKUP_DIR"

  local backup_file
  backup_file="${BACKUP_DIR}/pre-update-$(date +%Y%m%d-%H%M%S).sql.gz"

  if compose exec -T db sh -c \
    'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' \
    | gzip > "$backup_file"
  then
    success "Backup previo creado: ${backup_file}"
    cleanup_update_backups
  else
    rm -f "$backup_file"

    fail "No se pudo crear el backup previo. La actualizacion fue cancelada."
  fi
}

cleanup_update_backups() {
  [ -d "$BACKUP_DIR" ] || return

  mapfile -t backups < <(
    find "$BACKUP_DIR" \
      -maxdepth 1 \
      -type f \
      -name 'pre-update-*.sql.gz' \
      -printf '%T@ %p\n' \
      | sort -rn \
      | cut -d' ' -f2-
  )

  if [ "${#backups[@]}" -le "$PRE_UPDATE_BACKUPS_MAX" ]; then
    return
  fi

  for backup in "${backups[@]:$PRE_UPDATE_BACKUPS_MAX}"; do
    rm -f -- "$backup"
  done
}

printf "%sPOS Restaurant - actualizador%s\n" "$BOLD" "$RESET"

cd "$APP_DIR"

command -v git >/dev/null 2>&1 || fail "git no esta instalado."
command -v docker >/dev/null 2>&1 || fail "Docker no esta instalado."
docker compose version >/dev/null 2>&1 || fail "Docker Compose no esta disponible."
[ -d "${APP_DIR}/.git" ] || fail "Este directorio no parece ser un repositorio git: ${APP_DIR}"
[ -f "${APP_DIR}/${COMPOSE_FILE}" ] || fail "No encontre ${COMPOSE_FILE}"

section "Verificando Docker"
if command -v systemctl >/dev/null 2>&1; then
  run_privileged systemctl start docker || true
fi

for _ in {1..30}; do
  if docker info >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

docker info >/dev/null 2>&1 || fail "Docker no respondio despues de 30 segundos."
success "Docker esta listo"

section "Revisando estado local"
if [ -n "$(git status --porcelain)" ]; then
  fail "Hay cambios locales sin confirmar. Guarda esos cambios antes de actualizar para no pisar trabajo."
fi

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
CURRENT_COMMIT="$(git rev-parse --short HEAD)"
success "Repositorio limpio en rama ${CURRENT_BRANCH} (${CURRENT_COMMIT})"

section "Preparando backup"
make_database_backup

section "Descargando cambios"
git fetch origin "$CURRENT_BRANCH"
git pull --ff-only origin "$CURRENT_BRANCH"
NEW_COMMIT="$(git rev-parse --short HEAD)"
success "Codigo actualizado: ${CURRENT_COMMIT} -> ${NEW_COMMIT}"

section "Deteniendo servicios"
if service_exists "$ZEROCONF_SERVICE"; then
  run_privileged systemctl stop "$ZEROCONF_SERVICE" || true
fi
if service_exists "$SERVICE_NAME"; then
  run_privileged systemctl stop "$SERVICE_NAME" || true
fi
compose down --remove-orphans
success "Servicios detenidos"

section "Reconstruyendo contenedores"
compose build
success "Imagenes reconstruidas"


section "Iniciando servicios"
if service_exists "$SERVICE_NAME"; then
  run_privileged systemctl start "$SERVICE_NAME"
else
  compose up -d
fi
if service_exists "$ZEROCONF_SERVICE"; then
  run_privileged systemctl start "$ZEROCONF_SERVICE"
fi
success "Servicios iniciados"


section "Verificando servicios"
wait_for_backend
success "Backend responde en /health"
wait_for_frontend
success "Frontend responde en puerto 80"

printf "\n%sActualizacion completada.%s\n" "$GREEN" "$RESET"
printf "Version instalada: %s\n" "$NEW_COMMIT"
printf "Acceso local: http://pos.local\n"

if [ -t 0 ]; then
  printf "Presiona Enter para cerrar esta ventana."
  read -r _
fi
