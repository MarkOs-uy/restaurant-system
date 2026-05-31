#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="docker-compose.prod.yml"
SERVICE_NAME="pos-restaurant"
ZEROCONF_SERVICE="pos-zeroconf"
HOSTNAME_LOCAL="pos"

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

if [ "$EUID" -ne 0 ]; then
  printf "%s[ERROR]%s Ejecuta el desinstalador como root: sudo bash uninstall.sh\n" "$RED" "$RESET" >&2
  exit 1
fi

compose() {
  docker compose -f "$COMPOSE_FILE" "$@"
}

desktop_dir_for_user() {
  local username="$1"
  local home_dir

  home_dir="$(getent passwd "$username" | cut -d: -f6)"
  [ -n "$home_dir" ] || return 1

  if [ -d "${home_dir}/Desktop" ]; then
    printf "%s/Desktop" "$home_dir"
  elif [ -d "${home_dir}/Escritorio" ]; then
    printf "%s/Escritorio" "$home_dir"
  else
    printf "%s/Desktop" "$home_dir"
  fi
}

TARGET_USER="${SUDO_USER:-}"
if [ -z "$TARGET_USER" ] || [ "$TARGET_USER" = "root" ]; then
  TARGET_USER="$(logname 2>/dev/null || true)"
fi

printf "%sPOS Restaurant - desinstalador%s\n" "$BOLD" "$RESET"

section "Deteniendo servicios"
if command -v systemctl >/dev/null 2>&1; then
  systemctl stop "$ZEROCONF_SERVICE" >/dev/null 2>&1 || true
  systemctl stop "$SERVICE_NAME" >/dev/null 2>&1 || true
  systemctl disable "$ZEROCONF_SERVICE" >/dev/null 2>&1 || true
  systemctl disable "$SERVICE_NAME" >/dev/null 2>&1 || true
fi

if command -v docker >/dev/null 2>&1 && [ -f "${APP_DIR}/${COMPOSE_FILE}" ]; then
  cd "$APP_DIR"
  compose down || true
fi
success "Servicios detenidos"

section "Quitando servicios systemd"
rm -f "/etc/systemd/system/${ZEROCONF_SERVICE}.service"
rm -f "/etc/systemd/system/${SERVICE_NAME}.service"
systemctl daemon-reload >/dev/null 2>&1 || true
success "Servicios systemd quitados"

section "Quitando accesos directos"
if [ -n "$TARGET_USER" ]; then
  DESKTOP_DIR="$(desktop_dir_for_user "$TARGET_USER" || true)"
  if [ -n "${DESKTOP_DIR:-}" ]; then
    rm -f "${DESKTOP_DIR}/POS Restaurant - Iniciar.desktop"
    rm -f "${DESKTOP_DIR}/POS Restaurant - Detener.desktop"
    rm -f "${DESKTOP_DIR}/POS Restaurant - Actualizar.desktop"
    success "Accesos directos quitados de ${DESKTOP_DIR}"
  else
    warn "No pude detectar el escritorio del usuario"
  fi
else
  warn "No pude detectar el usuario de escritorio"
fi

section "Datos"
warn "No se borraron la base de datos, backups, backend/.env ni imagenes de Docker."
printf "Para borrar tambien volumenes de Docker, ejecuta manualmente:\n"
printf "  cd %s && docker compose -f %s down -v\n" "$APP_DIR" "$COMPOSE_FILE"

printf "\n%sDesinstalacion completada.%s\n" "$GREEN" "$RESET"
printf "El codigo de la aplicacion sigue en: %s\n" "$APP_DIR"
printf "Hostname mDNS usado por la instalacion: %s.local\n" "$HOSTNAME_LOCAL"
