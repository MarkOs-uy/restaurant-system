# checks.py
import platform
import shutil
import socket
import subprocess
import requests
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone



from config import (
    DISK_CRITICAL_PERCENT,
    DISK_WARNING_PERCENT,
    FRONTEND_URL,
    HEALTH_URL,
    MARCHA_HOST,
    SYSTEMD_SERVICE,
)

@dataclass
class CheckResult:
    ok: bool
    status: str
    detail: str = ""
    warning: bool = False
    applicable: bool = True

@dataclass
class HealthResult:
    backend: CheckResult
    database: CheckResult
    redis: CheckResult
    backup: CheckResult
    version: str


def _parse_backup_status(data: dict) -> CheckResult:
    backup_data = data.get(
        "backup",
        {},
    )

    backup_status = backup_data.get("status")
    last_backup_at = backup_data.get("last_backup_at")

    if backup_status == "missing":
        return CheckResult(
            ok=True,
            warning=True,
            status="No hay backups",
        )

    if backup_status != "ok" or not last_backup_at:
        return CheckResult(
            ok=True,
            warning=True,
            status="Estado desconocido",
        )

    try:
        backup_datetime = datetime.fromisoformat(
            last_backup_at.replace(
                "Z",
                "+00:00",
            )
        )

        now = datetime.now(timezone.utc)

        age = now - backup_datetime.astimezone(
            timezone.utc
        )

        age_hours = age.total_seconds() / 3600

        local_backup_time = backup_datetime.astimezone()

        formatted = local_backup_time.strftime(
            "%d/%m/%Y %H:%M"
        )

        if age_hours > 36:
            return CheckResult(
                ok=True,
                warning=True,
                status=f"{formatted} - antiguo",
            )

        return CheckResult(
            ok=True,
            status=formatted,
        )

    except (ValueError, TypeError):
        return CheckResult(
            ok=True,
            warning=True,
            status="Fecha inválida",
        )


def is_local_monitoring() -> bool:
    return MARCHA_HOST.lower() in {
        "localhost",
        "127.0.0.1",
        "::1",
    }

def check_systemd() -> CheckResult:
    if (
        platform.system() != "Linux"
        or not is_local_monitoring()
    ):
        return CheckResult(
            ok=True,
            status="Solo disponible localmente",
            detail="systemd solo se comprueba en el servidor Marcha",
            applicable=False,
        )

    try:
        result = subprocess.run(
            ["systemctl", "is-active", SYSTEMD_SERVICE],
            capture_output=True,
            text=True,
            timeout=3,
        )

        status = result.stdout.strip()

        if result.returncode == 0 and status == "active":
            return CheckResult(
                ok=True,
                status="Activo",
            )

        return CheckResult(
            ok=False,
            status=status or "Inactivo",
        )

    except Exception as exc:
        return CheckResult(
            ok=False,
            status="Error",
            detail=str(exc),
        )


def check_health() -> HealthResult:
    try:
        response = requests.get(
            HEALTH_URL,
            timeout=3,
        )

        data = response.json()

        backup = _parse_backup_status(data)

        database_status = (
            data.get("database", {})
            .get("status")
        )

        redis_status = (
            data.get("redis", {})
            .get("status")
        )

        version = data.get(
            "version",
            "Desconocida",
        )

        backend = CheckResult(
            ok=response.status_code == 200,
            status=(
                "Saludable"
                if response.status_code == 200
                else f"HTTP {response.status_code}"
            ),
        )

        database = CheckResult(
            ok=database_status == "ok",
            status=(
                "Disponible"
                if database_status == "ok"
                else "No disponible"
            ),
        )

        redis_result = CheckResult(
            ok=redis_status == "ok",
            status=(
                "Disponible"
                if redis_status == "ok"
                else "No disponible"
            ),
        )

        return HealthResult(
            backend=backend,
            database=database,
            redis=redis_result,
            backup=backup,
            version=version,
        )

    except requests.RequestException as exc:
        unavailable = CheckResult(
            ok=False,
            status="No responde",
            detail=str(exc),
        )

        return HealthResult(
            backend=unavailable,
            database=CheckResult(
                ok=False,
                status="Desconocido",
            ),
            redis=CheckResult(
                ok=False,
                status="Desconocido",
            ),
            backup=CheckResult(
                ok=True,
                warning=True,
                status="Desconocido",
            ),
            version="Desconocida",
        )

    except ValueError as exc:
        return HealthResult(
            backend=CheckResult(
                ok=False,
                status="Respuesta inválida",
                detail=str(exc),
            ),
            database=CheckResult(
                ok=False,
                status="Desconocido",
            ),
            redis=CheckResult(
                ok=False,
                status="Desconocido",
            ),
            backup=CheckResult(
                ok=True,
                warning=True,
                status="Desconocido",
            ),
            version="Desconocida",
        )


def check_frontend() -> CheckResult:
    try:
        response = requests.get(
            FRONTEND_URL,
            timeout=3,
        )

        if response.status_code == 200:
            return CheckResult(
                ok=True,
                status="Disponible",
            )

        return CheckResult(
            ok=False,
            status=f"HTTP {response.status_code}",
        )

    except requests.RequestException as exc:
        return CheckResult(
            ok=False,
            status="No responde",
            detail=str(exc),
        )


def check_disk() -> CheckResult:
    if not is_local_monitoring():
        return CheckResult(
            ok=True,
            status="Solo disponible localmente",
            detail="El disco solo se comprueba en el servidor Marcha",
            applicable=False,
        )

    try:
        if platform.system() == "Windows":
            disk_path = Path.home().anchor
        else:
            disk_path = "/"

        usage = shutil.disk_usage(disk_path)

        used_percent = (
            usage.used / usage.total
        ) * 100

        free_percent = 100 - used_percent

        if used_percent >= DISK_CRITICAL_PERCENT:
            return CheckResult(
                ok=False,
                status=f"{free_percent:.0f}% libre",
                detail="Espacio en disco crítico",
            )

        if used_percent >= DISK_WARNING_PERCENT:
            return CheckResult(
                ok=True,
                warning=True,
                status=f"{free_percent:.0f}% libre",
                detail="Espacio en disco bajo",
            )

        return CheckResult(
            ok=True,
            status=f"{free_percent:.0f}% libre",
        )

    except Exception as exc:
        return CheckResult(
            ok=False,
            status="Error",
            detail=str(exc),
        )


def get_server_address() -> str:
    if is_local_monitoring():
        return get_local_ip()

    return MARCHA_HOST


def get_local_ip() -> str:
    try:
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
        )

        sock.connect(("8.8.8.8", 80))

        ip = sock.getsockname()[0]

        sock.close()

        return ip

    except OSError:
        return "No disponible"