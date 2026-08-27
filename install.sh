#!/usr/bin/env bash
set -euo pipefail


APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ENV_FILE="${APP_DIR}/backend/.env"
COMPOSE_FILE="docker-compose.prod.yml"

HOSTNAME_LOCAL="pos"
FRONTEND_PORT="80"
BACKEND_PORT="8000"

INSTALL_STATE_DIR="/var/lib/pos-restaurant"
INSTALL_STATE_FILE="${INSTALL_STATE_DIR}/install.conf"

LICENSE_DIR="/var/lib/pos-restaurant"
LICENSE_FILE="${LICENSE_DIR}/license.json"


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
# Docker Compose
# -----------------------------------------------------------------------------

compose() {
  docker compose -f "$COMPOSE_FILE" "$@"
}


# -----------------------------------------------------------------------------
# Obtener IP local
# -----------------------------------------------------------------------------

get_local_ip() {
  ip route get 1.1.1.1 2>/dev/null \
    | awk '{
        for (i=1; i<=NF; i++) {
          if ($i == "src") {
            print $(i + 1)
            exit
          }
        }
      }'
}


# -----------------------------------------------------------------------------
# Leer valor desde backend/.env
# -----------------------------------------------------------------------------

env_value() {
  awk -F= -v key="$1" '
    $1 == key {
      sub(/\r$/, "")
      print substr($0, index($0, "=") + 1)
      exit
    }
  ' "$ENV_FILE"
}


# -----------------------------------------------------------------------------
# Generar fingerprint estable de esta máquina.
#
# IMPORTANTE:
# - No se guarda como fuente de verdad.
# - Backend vuelve a calcularlo desde el host.
# -----------------------------------------------------------------------------

generate_machine_fingerprint() {
  local system_id=""
  local product_uuid=""

  if [ -f /etc/machine-id ]; then
    system_id="$(
      tr -d '\n' < /etc/machine-id \
        | tr '[:upper:]' '[:lower:]'
    )"
  fi

  if [ -f /sys/class/dmi/id/product_uuid ]; then
    product_uuid="$(
      tr -d '\n' < /sys/class/dmi/id/product_uuid \
        | tr '[:upper:]' '[:lower:]'
    )"
  fi

  if [ -z "$system_id" ] && [ -z "$product_uuid" ]; then
    fail "No pude obtener una identidad estable de esta maquina."
  fi

  printf '%s|%s' \
    "$system_id" \
    "$product_uuid" \
    | sha256sum \
    | awk '{print $1}'
}


# -----------------------------------------------------------------------------
# Mostrar fingerprint de forma legible
# -----------------------------------------------------------------------------

print_machine_fingerprint() {
  local fingerprint="$1"

  printf "%s-%s-%s-%s-%s-%s-%s-%s\n" \
    "${fingerprint:0:8}" \
    "${fingerprint:8:8}" \
    "${fingerprint:16:8}" \
    "${fingerprint:24:8}" \
    "${fingerprint:32:8}" \
    "${fingerprint:40:8}" \
    "${fingerprint:48:8}" \
    "${fingerprint:56:8}"
}


# -----------------------------------------------------------------------------
# Detectar escritorio del usuario
# -----------------------------------------------------------------------------

desktop_dir_for_user() {
  local username="$1"
  local home_dir

  home_dir="$(
    getent passwd "$username" \
      | cut -d: -f6
  )"

  [ -n "$home_dir" ] || return 1

  if [ -d "${home_dir}/Desktop" ]; then
    printf "%s/Desktop" "$home_dir"

  elif [ -d "${home_dir}/Escritorio" ]; then
    printf "%s/Escritorio" "$home_dir"

  else
    printf "%s/Desktop" "$home_dir"
  fi
}


# -----------------------------------------------------------------------------
# Crear accesos directos
# -----------------------------------------------------------------------------

install_desktop_shortcuts() {
  local target_user="${SUDO_USER:-}"
  local desktop_dir
  local target_group

  if [ -z "$target_user" ] || [ "$target_user" = "root" ]; then
    target_user="$(
      logname 2>/dev/null || true
    )"
  fi

  if [ -z "$target_user" ]; then
    warn "No pude detectar el usuario de escritorio; omito accesos directos."
    return
  fi

  target_group="$(
    id -gn "$target_user" 2>/dev/null || true
  )"

  if [ -z "$target_group" ]; then
    warn "No pude detectar el grupo de ${target_user}; omito accesos directos."
    return
  fi

  desktop_dir="$(
    desktop_dir_for_user "$target_user" || true
  )"

  if [ -z "$desktop_dir" ]; then
    warn "No pude detectar el escritorio de ${target_user}; omito accesos directos."
    return
  fi

  install \
    -d \
    -m 0755 \
    -o "$target_user" \
    -g "$target_group" \
    "$desktop_dir"


  cat > "${desktop_dir}/POS Restaurant - Iniciar.desktop" << EOF
[Desktop Entry]
Type=Application
Name=POS Restaurant - Iniciar
Comment=Iniciar el servidor POS Restaurant
Exec=/usr/bin/env bash "${APP_DIR}/start_server.sh"
Icon=utilities-terminal
Terminal=true
Categories=Utility;
EOF


  cat > "${desktop_dir}/POS Restaurant - Detener.desktop" << EOF
[Desktop Entry]
Type=Application
Name=POS Restaurant - Detener
Comment=Detener el servidor POS Restaurant
Exec=/usr/bin/env bash "${APP_DIR}/stop_server.sh"
Icon=process-stop
Terminal=true
Categories=Utility;
EOF


  cat > "${desktop_dir}/POS Restaurant - Actualizar.desktop" << EOF
[Desktop Entry]
Type=Application
Name=POS Restaurant - Actualizar
Comment=Actualizar POS Restaurant desde el repositorio
Exec=/usr/bin/env bash "${APP_DIR}/update.sh"
Icon=software-update-available
Terminal=true
Categories=Utility;
EOF


  chown "$target_user:$target_group" \
    "${desktop_dir}/POS Restaurant - Iniciar.desktop" \
    "${desktop_dir}/POS Restaurant - Detener.desktop" \
    "${desktop_dir}/POS Restaurant - Actualizar.desktop"


  chmod +x \
    "${desktop_dir}/POS Restaurant - Iniciar.desktop" \
    "${desktop_dir}/POS Restaurant - Detener.desktop" \
    "${desktop_dir}/POS Restaurant - Actualizar.desktop"


  if command -v gio >/dev/null 2>&1; then

    sudo -u "$target_user" \
      gio set \
      "${desktop_dir}/POS Restaurant - Iniciar.desktop" \
      metadata::trusted true \
      >/dev/null 2>&1 || true

    sudo -u "$target_user" \
      gio set \
      "${desktop_dir}/POS Restaurant - Detener.desktop" \
      metadata::trusted true \
      >/dev/null 2>&1 || true

    sudo -u "$target_user" \
      gio set \
      "${desktop_dir}/POS Restaurant - Actualizar.desktop" \
      metadata::trusted true \
      >/dev/null 2>&1 || true
  fi

  success "Accesos directos creados en ${desktop_dir}"
}


# -----------------------------------------------------------------------------
# Esperar PostgreSQL
# -----------------------------------------------------------------------------

wait_for_postgres() {
  local ready=0

  for _ in {1..30}; do

    if compose exec -T db \
      pg_isready \
      -U "${POSTGRES_USER_VALUE:-pos_user}" \
      -d "${POSTGRES_DB_VALUE:-restaurant}" \
      >/dev/null 2>&1
    then
      ready=1
      break
    fi

    sleep 2
  done

  [ "$ready" -eq 1 ]
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

  [ "$ready" -eq 1 ]
}


# =============================================================================
# INICIO
# =============================================================================

printf "%sPOS Restaurant - instalador de produccion%s\n" \
  "$BOLD" "$RESET"


# -----------------------------------------------------------------------------
# Validaciones iniciales
# -----------------------------------------------------------------------------

if ! command -v apt-get >/dev/null 2>&1; then
  fail "Este instalador esta pensado para Linux Debian/Ubuntu."
fi


if [ "$EUID" -ne 0 ]; then
  fail "Ejecuta el instalador como root: sudo bash install.sh"
fi


cd "$APP_DIR"


# -----------------------------------------------------------------------------
# LICENCIA
#
# Esto ocurre ANTES de modificar/configurar la máquina.
# Si no existe licencia, solamente mostramos el fingerprint y terminamos.
# -----------------------------------------------------------------------------

section "Verificando licencia"

install -d \
  -m 0700 \
  "$LICENSE_DIR"


MACHINE_FINGERPRINT="$(
  generate_machine_fingerprint
)"


if [ ! -f "$LICENSE_FILE" ]; then

  printf "\n%sEsta instalacion requiere una licencia.%s\n" \
    "$YELLOW" "$RESET"

  printf "\nCodigo de instalacion:\n"
  printf "  %s\n" "$MACHINE_FINGERPRINT"

  printf "\nFormato legible:\n"
  printf "  "

  print_machine_fingerprint \
    "$MACHINE_FINGERPRINT"

  printf "\nGenera una licencia para este equipo y copiala en:\n"
  printf "  %s\n" "$LICENSE_FILE"

  printf "\nLuego vuelve a ejecutar:\n"
  printf "  sudo bash %s/install.sh\n" "$APP_DIR"

  printf "\n"

  exit 2
fi


chmod 600 "$LICENSE_FILE"

success "Archivo de licencia encontrado"


# -----------------------------------------------------------------------------
# Preparar scripts
# -----------------------------------------------------------------------------

section "Preparando scripts de control"

chmod +x \
  "${APP_DIR}/start_server.sh" \
  "${APP_DIR}/stop_server.sh" \
  "${APP_DIR}/update.sh" \
  "${APP_DIR}/uninstall.sh" \
  "${APP_DIR}/scripts/start_stack.sh"

success "Scripts de inicio, cierre, actualizacion y desinstalacion listos"


# -----------------------------------------------------------------------------
# Dependencias del sistema
# -----------------------------------------------------------------------------

section "Instalando dependencias del sistema"

apt-get update -qq

apt-get install -y \
  avahi-daemon \
  ca-certificates \
  curl \
  git \
  gnupg \
  iproute2 \
  libnss-mdns \
  python3 \
  python3-zeroconf

success "Dependencias base instaladas"


# -----------------------------------------------------------------------------
# Docker
# -----------------------------------------------------------------------------

section "Instalando Docker"

if command -v docker >/dev/null 2>&1 \
  && docker compose version >/dev/null 2>&1
then

  warn "Docker ya instalado - omitiendo"

else

  . /etc/os-release

  if [ "$ID" != "ubuntu" ] && [ "$ID" != "debian" ]; then
    fail "Sistema no soportado: ${ID}. Se requiere Ubuntu o Debian."
  fi

  printf "Sistema detectado: %s %s\n" \
    "$ID" "$VERSION_CODENAME"


  apt-get remove -y \
    docker \
    docker-engine \
    docker.io \
    containerd \
    runc \
    2>/dev/null || true


  install \
    -m 0755 \
    -d \
    /etc/apt/keyrings


  curl -fsSL \
    "https://download.docker.com/linux/${ID}/gpg" \
    -o /etc/apt/keyrings/docker.asc


  chmod a+r \
    /etc/apt/keyrings/docker.asc


  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/${ID} ${VERSION_CODENAME} stable" \
    | tee /etc/apt/sources.list.d/docker.list \
    >/dev/null


  apt-get update -qq


  apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin


  success "Docker instalado"
fi


# -----------------------------------------------------------------------------
# Configuración mDNS / hostname
# -----------------------------------------------------------------------------

section "Configurando mDNS: ${HOSTNAME_LOCAL}.local"

AVAHI_CONF="/etc/avahi/avahi-daemon.conf"

AVAHI_BACKUP="/etc/avahi/avahi-daemon.conf.pos-backup.$(
  date +%Y%m%d%H%M%S
)"


install \
  -d \
  -m 0700 \
  "$INSTALL_STATE_DIR"


# Guardamos la configuración original una única vez.
if [ ! -f "$INSTALL_STATE_FILE" ]; then

  ORIGINAL_HOSTNAME="$(
    hostnamectl --static
  )"

  cp \
    "$AVAHI_CONF" \
    "$AVAHI_BACKUP"


  cat > "$INSTALL_STATE_FILE" << EOF
ORIGINAL_HOSTNAME=${ORIGINAL_HOSTNAME}
AVAHI_BACKUP=${AVAHI_BACKUP}
EOF


  chmod 600 \
    "$INSTALL_STATE_FILE"

else

  warn "El estado original de red ya estaba registrado; se conserva."

fi


if grep -q "^#\?host-name=" "$AVAHI_CONF"; then

  sed -i \
    "s/^#\?host-name=.*/host-name=${HOSTNAME_LOCAL}/" \
    "$AVAHI_CONF"

else

  sed -i \
    "/^\[server\]/a host-name=${HOSTNAME_LOCAL}" \
    "$AVAHI_CONF"

fi


systemctl enable \
  avahi-daemon \
  >/dev/null


hostnamectl set-hostname \
  "$HOSTNAME_LOCAL"


systemctl restart \
  avahi-daemon


success "mDNS activo como ${HOSTNAME_LOCAL}.local"


# -----------------------------------------------------------------------------
# Configuración de Marcha
# -----------------------------------------------------------------------------

section "Generando configuracion"

ENV_CREATED=0
ADMIN_PASSWORD=""


LOCAL_IP="$(
  get_local_ip
)"


if [ -z "$LOCAL_IP" ]; then
  LOCAL_IP="$(
    hostname -I 2>/dev/null \
      | awk '{print $1}'
  )"
fi


[ -n "$LOCAL_IP" ] || \
  fail "No pude detectar la IP local del servidor."


if [ ! -f "$ENV_FILE" ]; then

  POSTGRES_PASSWORD="$(
    python3 -c \
      "import secrets; print(secrets.token_hex(16))"
  )"


  SECRET_KEY="$(
    python3 -c \
      "import secrets; print(secrets.token_hex(32))"
  )"


  ENCRYPTION_KEY="$(
    python3 -c \
      "import os, base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"
  )"


  ADMIN_PASSWORD="$(
    python3 -c \
      "import secrets; print(secrets.token_urlsafe(12))"
  )"


  cat > "$ENV_FILE" << EOF
POSTGRES_USER=pos_user
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=restaurant
DATABASE_URL=postgresql://pos_user:${POSTGRES_PASSWORD}@db:5432/restaurant

SECRET_KEY=${SECRET_KEY}
ENCRYPTION_KEY=${ENCRYPTION_KEY}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

CORS_ORIGINS=http://localhost,http://${LOCAL_IP},http://${HOSTNAME_LOCAL}.local

REDIS_HOST=redis
REDIS_PORT=6379

ADMIN_SEED_PASSWORD=${ADMIN_PASSWORD}

ENVIRONMENT=production
LOG_LEVEL=INFO
EOF


  chmod 600 \
    "$ENV_FILE"


  ENV_CREATED=1


  success "Configuracion creada en backend/.env"

else

  warn "backend/.env ya existe; no se sobreescribe."

fi


POSTGRES_USER_VALUE="$(
  env_value POSTGRES_USER
)"

POSTGRES_DB_VALUE="$(
  env_value POSTGRES_DB
)"


# -----------------------------------------------------------------------------
# Iniciar Docker
# -----------------------------------------------------------------------------

section "Iniciando Docker"

systemctl enable \
  docker \
  >/dev/null


systemctl start \
  docker


until docker info >/dev/null 2>&1; do
  sleep 1
done


success "Docker esta listo"


# -----------------------------------------------------------------------------
# Construir / iniciar contenedores
# -----------------------------------------------------------------------------

section "Construyendo e iniciando contenedores"

compose up \
  -d \
  --build


success "Contenedores iniciados"


# -----------------------------------------------------------------------------
# Verificar servicios
# -----------------------------------------------------------------------------

section "Verificando servicios"

printf "Esperando base de datos...\n"


if ! wait_for_postgres; then

  compose down || true

  fail "Postgres no respondio despues de 60 segundos. Revisa: docker compose -f ${COMPOSE_FILE} logs db"

fi


success "Postgres responde"


printf "Esperando backend...\n"


if ! wait_for_backend; then

  printf "\n"

  compose logs \
    --tail=40 \
    backend \
    >&2 || true

  compose down || true

  fail "El backend no quedo listo. Revisa la licencia, migraciones y logs del backend."

fi


success "Backend responde en /health"


# -----------------------------------------------------------------------------
# Registrar servicios systemd
# -----------------------------------------------------------------------------

section "Registrando servicios del sistema"


tee \
  /etc/systemd/system/pos-zeroconf.service \
  >/dev/null << EOF
[Unit]
Description=POS Zeroconf Announcer
After=network-online.target avahi-daemon.service docker.service
Wants=network-online.target
Requires=avahi-daemon.service docker.service

[Service]
Type=simple
WorkingDirectory=${APP_DIR}
Environment=POS_HOSTNAME=${HOSTNAME_LOCAL}.local
Environment=POS_FRONTEND_PORT=${FRONTEND_PORT}
Environment=POS_BACKEND_PORT=${BACKEND_PORT}
ExecStart=/usr/bin/python3 ${APP_DIR}/scripts/announce_service.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF


tee \
  /etc/systemd/system/pos-restaurant.service \
  >/dev/null << EOF
[Unit]
Description=POS Restaurant
After=network.target docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/scripts/start_stack.sh
ExecStop=/usr/bin/docker compose -f ${COMPOSE_FILE} down
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
EOF


systemctl daemon-reload


systemctl enable \
  pos-restaurant \
  >/dev/null


systemctl enable \
  pos-zeroconf \
  >/dev/null


# Los contenedores ya están arriba por la instalación,
# pero necesitamos que systemd adopte correctamente su estado.
if ! systemctl start pos-restaurant; then

  compose down || true

  fail "No se pudo registrar correctamente el servicio POS Restaurant."

fi


systemctl restart \
  pos-zeroconf


success "Servicios systemd registrados"


# -----------------------------------------------------------------------------
# Accesos directos
# -----------------------------------------------------------------------------

section "Creando accesos directos"

install_desktop_shortcuts


# -----------------------------------------------------------------------------
# Información final
# -----------------------------------------------------------------------------

LOCAL_IP="$(
  get_local_ip
)"


if [ -z "$LOCAL_IP" ]; then
  LOCAL_IP="$(
    hostname -I 2>/dev/null \
      | awk '{print $1}'
  )"
fi


printf "\n%s+--------------------------------------------------+%s\n" \
  "$GREEN" "$RESET"

printf "%s|       POS Restaurant instalado con exito         |%s\n" \
  "$GREEN" "$RESET"

printf "%s+--------------------------------------------------+%s\n" \
  "$GREEN" "$RESET"


printf "\n%sAcceso en la red local:%s\n" \
  "$BOLD" "$RESET"

printf "  %shttp://%s.local%s\n" \
  "$BLUE" "$HOSTNAME_LOCAL" "$RESET"

printf "  %shttp://%s%s\n" \
  "$BLUE" "$LOCAL_IP" "$RESET"


printf "\n%sCredenciales iniciales:%s\n" \
  "$BOLD" "$RESET"

printf "  Usuario:    admin\n"


if [ "$ENV_CREATED" -eq 1 ]; then

  printf "  Contrasena: %s\n" \
    "$ADMIN_PASSWORD"

  printf "\n%sGuarda esta contrasena ahora; no se volvera a mostrar en pantalla.%s\n" \
    "$YELLOW" "$RESET"

else

  printf "  Contrasena: ya configurada anteriormente en backend/.env\n"

fi


printf "\n%sLicencia:%s\n" \
  "$BOLD" "$RESET"

printf "  Codigo del equipo:\n"
printf "  %s\n" \
  "$MACHINE_FINGERPRINT"


printf "\n%sComandos utiles:%s\n" \
  "$BOLD" "$RESET"

printf "  Logs:        cd %s && docker compose -f %s logs -f\n" \
  "$APP_DIR" "$COMPOSE_FILE"

printf "  Iniciar:     %s/start_server.sh\n" \
  "$APP_DIR"

printf "  Detener:     %s/stop_server.sh\n" \
  "$APP_DIR"

printf "  Actualizar:  %s/update.sh\n" \
  "$APP_DIR"

printf "  Reiniciar:   systemctl restart pos-restaurant\n"

printf "  Estado:      systemctl status pos-restaurant\n"

printf "  Desinstalar: sudo bash %s/uninstall.sh\n" \
  "$APP_DIR"

printf "  Backup:      ls -lh %s/backups\n" \
  "$APP_DIR"

printf "\n"