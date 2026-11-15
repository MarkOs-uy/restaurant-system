#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

COMPOSE_FILE="docker-compose.prod.yml"

SERVICE_NAME="pos-restaurant"
ZEROCONF_SERVICE="pos-zeroconf"

BACKUP_DIR="${APP_DIR}/backups/manual-updates"
PRE_UPDATE_BACKUPS_MAX=10

MONITOR_DIR="${APP_DIR}/monitor-marcha"
MONITOR_VENV="${MONITOR_DIR}/venv"
MONITOR_REQUIREMENTS="${MONITOR_DIR}/requirements.txt"


# -----------------------------------------------------------------------------
# Colores
# -----------------------------------------------------------------------------

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


# -----------------------------------------------------------------------------
# Helpers de salida
# -----------------------------------------------------------------------------

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


# -----------------------------------------------------------------------------
# Ejecutar comando con privilegios cuando sea necesario
# -----------------------------------------------------------------------------

run_privileged() {
  if [ "$EUID" -eq 0 ]; then
    "$@"
  else
    sudo "$@"
  fi
}


# -----------------------------------------------------------------------------
# Docker Compose
# -----------------------------------------------------------------------------

compose() {
  docker compose -f "$COMPOSE_FILE" "$@"
}


# -----------------------------------------------------------------------------
# Comprobar existencia de servicio systemd
# -----------------------------------------------------------------------------

service_exists() {
  command -v systemctl >/dev/null 2>&1 \
    && systemctl cat "$1" >/dev/null 2>&1
}


# -----------------------------------------------------------------------------
# Detectar usuario de escritorio.
#
# Casos:
# - update.sh ejecutado normalmente por el usuario -> id -un
# - update.sh ejecutado con sudo -> SUDO_USER
# - ejecutado directamente como root -> intenta logname
# -----------------------------------------------------------------------------

get_desktop_user() {
  local target_user=""

  if [ -n "${SUDO_USER:-}" ] \
    && [ "${SUDO_USER}" != "root" ]
  then
    target_user="$SUDO_USER"

  elif [ "$EUID" -ne 0 ]; then
    target_user="$(
      id -un
    )"

  else
    target_user="$(
      logname 2>/dev/null || true
    )"
  fi

  printf "%s" "$target_user"
}


# -----------------------------------------------------------------------------
# Instalar / actualizar Marcha Monitor.
#
# El monitor vive fuera de Docker y tiene su propio entorno virtual.
#
# Esta función también cubre instalaciones antiguas que reciben el monitor
# por primera vez mediante git pull y, por lo tanto, nunca ejecutaron la
# versión nueva de install.sh.
# -----------------------------------------------------------------------------

update_monitor() {

  if [ ! -d "$MONITOR_DIR" ]; then
    warn "No existe ${MONITOR_DIR}; se omite Marcha Monitor."
    return 0
  fi


  if [ ! -f "${MONITOR_DIR}/marcha_monitor.py" ]; then
    warn "No encontre marcha_monitor.py; se omite Marcha Monitor."
    return 0
  fi


  if [ ! -f "$MONITOR_REQUIREMENTS" ]; then
    warn "No encontre ${MONITOR_REQUIREMENTS}; se omite Marcha Monitor."
    return 0
  fi


  command -v python3 >/dev/null 2>&1 \
    || fail "Python 3 no esta instalado; no puedo configurar Marcha Monitor."


  # ---------------------------------------------------------------------------
  # Dependencias del sistema necesarias para Tkinter y entornos virtuales.
  # Solo ejecutamos apt si realmente falta alguno de los paquetes.
  # ---------------------------------------------------------------------------

  local install_system_dependencies=0


  if ! dpkg -s python3-tk >/dev/null 2>&1; then
    install_system_dependencies=1
  fi


  if ! dpkg -s python3-venv >/dev/null 2>&1; then
    install_system_dependencies=1
  fi


  if [ "$install_system_dependencies" -eq 1 ]; then

    printf "Instalando dependencias del sistema para Marcha Monitor...\n"

    run_privileged \
      apt-get update -qq

    run_privileged \
      apt-get install -y \
      python3-tk \
      python3-venv

  fi


  # ---------------------------------------------------------------------------
  # Crear entorno virtual si todavía no existe.
  # ---------------------------------------------------------------------------

  if [ ! -x "${MONITOR_VENV}/bin/python" ]; then

    printf "Creando entorno virtual de Marcha Monitor...\n"

    run_privileged \
      python3 -m venv \
      "$MONITOR_VENV"

  fi


  # ---------------------------------------------------------------------------
  # Actualizar dependencias Python del monitor.
  #
  # Se ejecuta con privilegios porque el venv puede haber sido creado por
  # install.sh como root.
  # ---------------------------------------------------------------------------

  printf "Actualizando dependencias de Marcha Monitor...\n"

  run_privileged \
    "${MONITOR_VENV}/bin/python" \
    -m pip \
    install \
    --upgrade \
    pip \
    >/dev/null


  run_privileged \
    "${MONITOR_VENV}/bin/python" \
    -m pip \
    install \
    -r "$MONITOR_REQUIREMENTS"


  # ---------------------------------------------------------------------------
  # Prueba mínima.
  # ---------------------------------------------------------------------------

  if ! "${MONITOR_VENV}/bin/python" \
    -c "import tkinter, requests" \
    >/dev/null 2>&1
  then
    fail "Marcha Monitor fue actualizado pero su entorno Python no es valido."
  fi


  success "Dependencias de Marcha Monitor actualizadas"
}


# -----------------------------------------------------------------------------
# Crear / actualizar autostart de Marcha Monitor.
# -----------------------------------------------------------------------------

install_monitor_autostart() {

  if [ ! -x "${MONITOR_VENV}/bin/python" ]; then
    warn "Marcha Monitor no tiene un entorno virtual valido; omito autostart."
    return 0
  fi


  local target_user
  local target_group
  local home_dir
  local autostart_dir
  local autostart_file


  target_user="$(
    get_desktop_user
  )"


  if [ -z "$target_user" ] \
    || [ "$target_user" = "root" ]
  then
    warn "No pude detectar el usuario grafico; omito autostart de Marcha Monitor."
    return 0
  fi


  target_group="$(
    id -gn "$target_user" 2>/dev/null || true
  )"


  if [ -z "$target_group" ]; then
    warn "No pude detectar el grupo de ${target_user}; omito autostart de Marcha Monitor."
    return 0
  fi


  home_dir="$(
    getent passwd "$target_user" \
      | cut -d: -f6
  )"


  if [ -z "$home_dir" ]; then
    warn "No pude detectar HOME de ${target_user}; omito autostart de Marcha Monitor."
    return 0
  fi


  autostart_dir="${home_dir}/.config/autostart"
  autostart_file="${autostart_dir}/marcha-monitor.desktop"


  run_privileged \
    install \
    -d \
    -m 0755 \
    -o "$target_user" \
    -g "$target_group" \
    "$autostart_dir"


  run_privileged \
    tee "$autostart_file" \
    >/dev/null << EOF
[Desktop Entry]
Type=Application
Name=Marcha Monitor
Comment=Monitor de estado del servidor Marcha
Exec=${MONITOR_VENV}/bin/python ${MONITOR_DIR}/marcha_monitor.py
Terminal=false
X-GNOME-Autostart-enabled=true
Categories=Utility;
EOF


  run_privileged \
    chown \
    "$target_user:$target_group" \
    "$autostart_file"


  run_privileged \
    chmod \
    0644 \
    "$autostart_file"


  success "Autostart de Marcha Monitor configurado para ${target_user}"
}


# -----------------------------------------------------------------------------
# Esperar backend
# -----------------------------------------------------------------------------

wait_for_backend() {
  local ready=0

  for _ in {1..45}; do

    if compose exec -T backend \
      python -c \
      "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" \
      >/dev/null 2>&1
    then
      ready=1
      break
    fi

    sleep 2
  done

  [ "$ready" -eq 1 ] \
    || fail "El backend no quedo listo despues de actualizar. Revisa: docker compose -f ${COMPOSE_FILE} logs backend"
}


# -----------------------------------------------------------------------------
# Esperar frontend
# -----------------------------------------------------------------------------

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

  [ "$ready" -eq 1 ] \
    || fail "El frontend no quedo listo despues de actualizar. Revisa: docker compose -f ${COMPOSE_FILE} logs frontend"
}


# -----------------------------------------------------------------------------
# Backup previo a actualización
# -----------------------------------------------------------------------------

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


# -----------------------------------------------------------------------------
# Mantener únicamente los últimos backups previos a actualización
# -----------------------------------------------------------------------------

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


# =============================================================================
# INICIO
# =============================================================================

printf "%sPOS Restaurant - actualizador%s\n" \
  "$BOLD" "$RESET"


cd "$APP_DIR"


# -----------------------------------------------------------------------------
# Validaciones iniciales
# -----------------------------------------------------------------------------

command -v git >/dev/null 2>&1 \
  || fail "git no esta instalado."

command -v docker >/dev/null 2>&1 \
  || fail "Docker no esta instalado."

docker compose version >/dev/null 2>&1 \
  || fail "Docker Compose no esta disponible."

[ -d "${APP_DIR}/.git" ] \
  || fail "Este directorio no parece ser un repositorio git: ${APP_DIR}"

[ -f "${APP_DIR}/${COMPOSE_FILE}" ] \
  || fail "No encontre ${COMPOSE_FILE}"


# -----------------------------------------------------------------------------
# Verificar Docker
# -----------------------------------------------------------------------------

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


docker info >/dev/null 2>&1 \
  || fail "Docker no respondio despues de 30 segundos."


success "Docker esta listo"


# -----------------------------------------------------------------------------
# Estado local Git
# -----------------------------------------------------------------------------

section "Revisando estado local"


if [ -n "$(git status --porcelain)" ]; then
  fail "Hay cambios locales sin confirmar. Guarda esos cambios antes de actualizar para no pisar trabajo."
fi


CURRENT_BRANCH="$(
  git rev-parse --abbrev-ref HEAD
)"

CURRENT_COMMIT="$(
  git rev-parse --short HEAD
)"


success "Repositorio limpio en rama ${CURRENT_BRANCH} (${CURRENT_COMMIT})"


# -----------------------------------------------------------------------------
# Backup previo
# -----------------------------------------------------------------------------

section "Preparando backup"

make_database_backup


# -----------------------------------------------------------------------------
# Descargar cambios
# -----------------------------------------------------------------------------

section "Descargando cambios"


git fetch \
  origin \
  "$CURRENT_BRANCH"


git pull \
  --ff-only \
  origin \
  "$CURRENT_BRANCH"


NEW_COMMIT="$(
  git rev-parse --short HEAD
)"


success "Codigo actualizado: ${CURRENT_COMMIT} -> ${NEW_COMMIT}"


# -----------------------------------------------------------------------------
# Actualizar Marcha Monitor
#
# Se hace antes de detener Marcha.
# Si debemos instalar dependencias del monitor, el POS continúa funcionando
# durante esta parte.
# -----------------------------------------------------------------------------

section "Actualizando Marcha Monitor"

update_monitor

install_monitor_autostart


# -----------------------------------------------------------------------------
# Detener servicios
# -----------------------------------------------------------------------------

section "Deteniendo servicios"


if service_exists "$ZEROCONF_SERVICE"; then
  run_privileged systemctl stop "$ZEROCONF_SERVICE" || true
fi


if service_exists "$SERVICE_NAME"; then
  run_privileged systemctl stop "$SERVICE_NAME" || true
fi


compose down --remove-orphans


success "Servicios detenidos"


# -----------------------------------------------------------------------------
# Reconstruir contenedores
# -----------------------------------------------------------------------------

section "Reconstruyendo contenedores"


compose build


success "Imagenes reconstruidas"


# -----------------------------------------------------------------------------
# Iniciar servicios
# -----------------------------------------------------------------------------

section "Iniciando servicios"


if service_exists "$SERVICE_NAME"; then

  run_privileged \
    systemctl start \
    "$SERVICE_NAME"

else

  compose up -d

fi


if service_exists "$ZEROCONF_SERVICE"; then

  run_privileged \
    systemctl start \
    "$ZEROCONF_SERVICE"

fi


success "Servicios iniciados"


# -----------------------------------------------------------------------------
# Verificar servicios
# -----------------------------------------------------------------------------

section "Verificando servicios"


wait_for_backend

success "Backend responde en /health"


wait_for_frontend

success "Frontend responde en puerto 80"


# -----------------------------------------------------------------------------
# Marcha Monitor
# -----------------------------------------------------------------------------

if pgrep -f "${MONITOR_DIR}/marcha_monitor.py" >/dev/null 2>&1; then

  printf "\n"

  warn "Marcha Monitor estaba abierto durante la actualizacion."

  printf "Cierra y vuelve a abrir el monitor para cargar cualquier cambio nuevo.\n"

else

  success "Marcha Monitor quedara disponible en el proximo inicio de sesion grafico"

fi


# -----------------------------------------------------------------------------
# Información final
# -----------------------------------------------------------------------------

printf "\n%sActualizacion completada.%s\n" \
  "$GREEN" "$RESET"

printf "Version instalada: %s\n" \
  "$NEW_COMMIT"

printf "Acceso local: http://pos.local\n"

printf "Monitor: %s/bin/python %s/marcha_monitor.py\n" \
  "$MONITOR_VENV" \
  "$MONITOR_DIR"


if [ -t 0 ]; then

  printf "Presiona Enter para cerrar esta ventana."

  read -r _

fi