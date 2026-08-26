import os
import shutil
import smtplib
import socket
import subprocess
import logging
from datetime import (
    datetime,
    timedelta,
    timezone,
    time
)
import calendar
from zoneinfo import ZoneInfo
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import unquote, urlparse

from fastapi.responses import FileResponse

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.db.session import DATABASE_URL

from app.infrastructure.restart.restart_manager import RestartManager

from app.models.system_settings import SystemSettings

from app.schemas.backup import (
    BackupStatusOut,
    BackupInfoOut,
    BackupFileOut,
    BackupEmailOut,
    BackupDeleteOut,
    BackupRestoreOut
)

BEFORE_RESTORE_MAX = 10
logger = logging.getLogger("app.domain.backup")

class BackupService:

    """
    Servicio encargado de la lógica de negocio relacionada con los backups.

    Responsabilidades:
    - Gestionar la lógica de negocio de los backups.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db) -> None:
        self.db = db
        self.backup_dir = self._resolve_backup_dir()

#-------------------------------------------------------------------
# DEVOLVER CONFIGURACIÓN DEL RESTAURANTE
#-------------------------------------------------------------------
    def _get_settings(self,restaurant_id: int) -> SystemSettings | None:
        return (
            self.db.query(SystemSettings)
            .filter(
                SystemSettings.restaurant_id
                == restaurant_id
            )
            .first()
        )

#-------------------------------------------------------------------
# CREAR BACKUP (MANUAL, AUTOMÁTICO O ANTES DE RESTAURAR)
#-------------------------------------------------------------------
    def _create_backup(self, restaurant_id: int, backup_type: str) -> BackupInfoOut:
        backup_path = self._build_backup_path(
            restaurant_id,
            backup_type,
            datetime.now(timezone.utc)
        )
        self._backup_database(backup_path)
        return self._backup_info(backup_path, backup_type)

#-------------------------------------------------------------------
# CREAR BACKUP ANTES DE RESTAURAR
#-------------------------------------------------------------------
    def _backup_before_restore(self, restaurant_id) -> None:
        self._create_backup(
            restaurant_id,
            "before_restore"
        )
        self._cleanup_before_restore(restaurant_id)

#-------------------------------------------------------------------
# MANTENER SOLO LOS ÚLTIMOS BACKUPS ANTES DE RESTAURAR
#-------------------------------------------------------------------
    def _cleanup_before_restore(self, restaurant_id: int):
        directory = (
            self._restaurant_backup_directory(restaurant_id)
            / "before_restore"
        )

        if not directory.exists():
            return

        backups = sorted(
            (
                path
                for path in directory.iterdir()
                if path.is_file()
            ),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        for backup in backups[BEFORE_RESTORE_MAX:]:
            backup.unlink()

#-------------------------------------------------------------------
# DEVOLVER INFORMACIÓN DEL BACKUP
#-------------------------------------------------------------------
    def _backup_info(self, backup_path: Path, backup_type: str) -> BackupInfoOut:

        stat = backup_path.stat()

        return BackupInfoOut(
            last_backup_at=datetime.fromtimestamp(
                stat.st_mtime,
                tz=timezone.utc
            ),
            last_backup_file=str(backup_path.relative_to(self.backup_dir)),
            last_backup_size=stat.st_size,
            type=backup_type
        )

#-------------------------------------------------------------------
# DEVOLVER EL PATH DEL BACKUP SI EXISTE, O LANZAR ERROR SI NO EXISTE
#-------------------------------------------------------------------
    def _find_backup(
        self,
        restaurant_id: int,
        filename: str
    ) -> Path:
        restaurant_dir = self._restaurant_backup_directory(
            restaurant_id
        )
        path = (restaurant_dir / filename).resolve()
        if not path.exists() or not path.is_file():
            raise DomainError(
                "Backup not found",
                ErrorCode.BACKUP_NOT_FOUND,
                context={"filename": filename})
        # Evita que intenten acceder fuera del directorio
        if restaurant_dir.resolve() not in path.parents:
            raise DomainError(
                "Invalid backup path",
                ErrorCode.BACKUP_INVALID_PATH,
                context={"filename": filename}
            )
        return path

#-------------------------------------------------------------------
# CONSTRUIR EL PATH DEL BACKUP
#-------------------------------------------------------------------
    def _build_backup_path(
        self,
        restaurant_id: int,
        backup_type: str,
        created_at: datetime,
    ) -> Path:

        suffix = (
            ".sqlite3"
            if DATABASE_URL.startswith("sqlite")
            else ".dump"
        )

        restaurant_dir = (
            self._restaurant_backup_directory(
                restaurant_id
            )
        )

        if backup_type == "manual":
            directory = restaurant_dir
        else:
            directory = (
                restaurant_dir /
                backup_type
            )

            directory.mkdir(
                parents=True,
                exist_ok=True
            )

        return (
            directory /
            f"backup-{created_at:%Y%m%d-%H%M%S}{suffix}"
        )

#-------------------------------------------------------------------
# BACKUP BASE DE DATOS DE ACUERDO AL MOTOR DE BASE DE DATOS
#-------------------------------------------------------------------
    def _backup_database(self, backup_path: Path):
        if DATABASE_URL.startswith("sqlite"):
            self._backup_sqlite(backup_path)

        elif DATABASE_URL.startswith("postgresql"):
            self._backup_postgres(backup_path)

        else:
            raise DomainError(
                "Not supported database engine for backup",
                ErrorCode.BACKUP_ENGINE_NOT_SUPPORTED
            )

#-------------------------------------------------------------------
# BACKUP EN SQLITE
#-------------------------------------------------------------------
    def _backup_sqlite(self, backup_path: Path):
        parsed = urlparse(DATABASE_URL)
        database_path = unquote(parsed.path)
        if os.name == "nt" and database_path.startswith("/"):
            database_path = database_path[1:]
        source = Path(database_path)
        if not source.exists():
            raise DomainError(
                "Database file not found for backup",
                ErrorCode.BACKUP_DATABASE_NOT_FOUND
            )
        shutil.copy2(source, backup_path)

#-------------------------------------------------------------------
# BACKUP EN POSTGRES
#-------------------------------------------------------------------
    def _backup_postgres(self, backup_path: Path):
        parsed = urlparse(
            DATABASE_URL.replace(
                "postgresql+psycopg2://",
                "postgresql://"
            )
        )
        env = os.environ.copy()
        env["PGPASSWORD"] = parsed.password
        command = [
            "pg_dump",
            "-h", parsed.hostname,
            "-p", str(parsed.port or 5432),
            "-U", parsed.username,
            "-d", parsed.path.lstrip("/"),

            "--format=custom",
            "--clean",
            "--if-exists",
            "--no-owner",
            
            "--file", str(backup_path)
        ]
        result = subprocess.run(command, capture_output=True, text=True, env=env)
        if result.returncode != 0:
            detail = result.stderr.strip() or "No se pudo ejecutar pg_dump"
            raise DomainError(
                "Error creating backup with pg_dump",
                ErrorCode.BACKUP_FAILED,
                context={"detail": detail}
            )

#-------------------------------------------------------------------
# ENVIAR BACKUP POR EMAIL
#-------------------------------------------------------------------
    def _send_backup_email(self, recipient_email: str, backup_path: Path, created_at: datetime, restaurant_id: int) -> None:
        settings = self._get_settings(
            restaurant_id
        )
        if not settings:
            raise DomainError(
                code=ErrorCode.SMTP_NOT_CONFIGURED,
                detail="SMTP does not configured for this restaurant"
            )
        smtp_host = settings.smtp_host
        smtp_port = settings.smtp_port or 587
        smtp_user = settings.smtp_user or ""
        smtp_password = settings.smtp_password or ""
        smtp_from = (
            settings.smtp_from
            or smtp_user
        )
        smtp_use_tls = settings.smtp_use_tls
        message = EmailMessage()
        message["Subject"] = "Backup del sistema restaurant"
        message["From"] = smtp_from
        message["To"] = recipient_email
        message.set_content(
            "Adjunto backup generado el "
            f"{created_at:%Y-%m-%d %H:%M:%S UTC}.\n\n"
            "Este correo fue generado automaticamente "
            "por el sistema."
        )
        message.add_attachment(
            backup_path.read_bytes(),
            maintype="application",
            subtype="octet-stream",
            filename=backup_path.name
        )
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as smtp:
            if smtp_use_tls:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
            if smtp_user:
                smtp.login(smtp_user, smtp_password)
            smtp.send_message(message)

#-------------------------------------------------------------------
# DEVOLVER TRUE o FALSE SI EL EMAIL ESTA CONFIGURADO PARA ESTE RESTAURANTE
#-------------------------------------------------------------------
    def _email_enabled(self, restaurant_id: int):
        settings = self._get_settings(restaurant_id)
        if not settings:
            return False
        return bool(
            settings.smtp_host
            and (
                settings.smtp_from
                or settings.smtp_user
            )
        )

#-------------------------------------------------------------------
# DEVOLVER EL DIRECTORIO DE BACKUPS
#-------------------------------------------------------------------
    def _resolve_backup_dir(self):
        configured_dir = os.getenv("BACKUP_DIR")
        if configured_dir:
            return Path(configured_dir)
        mounted_dir = Path("/backups")
        if mounted_dir.exists():
            return mounted_dir
        return Path("backups")

#-------------------------------------------------------------------
# OBTENER ÚLTIMO BACKUP
#-------------------------------------------------------------------
    def _latest_backup_file(self, restaurant_id: int):
        restaurant_dir = self._restaurant_backup_directory(restaurant_id)
        if not restaurant_dir.exists():
            return None
        candidates = [
            path
            for path in restaurant_dir.rglob("*")
            if path.is_file()
            and path.stat().st_size > 0
        ]
        if not candidates:
            return None
        latest = max(candidates, key=lambda path: path.stat().st_mtime)
        stats = latest.stat()

        return {
            "name": str(latest.relative_to(self.backup_dir)),
            "modified_at": datetime.fromtimestamp(stats.st_mtime,tz=timezone.utc).isoformat(),
            "size": stats.st_size,
            "type": latest.parent.name
        }

#-------------------------------------------------------------------
# Devolver el directorio de backups del restaurante
#-------------------------------------------------------------------    
    def _restaurant_backup_directory(
        self,
        restaurant_id: int
    ) -> Path:
        directory = (
            self.backup_dir /
            f"restaurant_{restaurant_id}"
        )
        directory.mkdir(
            parents=True,
            exist_ok=True
        )
        return directory

#-------------------------------------------------------------------
# APLICAR POLÍTICA DE RETENCIÓN
#-------------------------------------------------------------------
    def _apply_retention_policy(self, settings: SystemSettings):
        restaurant_dir = (
            self.backup_dir /
            f"restaurant_{settings.restaurant_id}"
        )

        if not restaurant_dir.exists():
            return

        now = datetime.now(timezone.utc)

        retention = {
            "daily": settings.backup_retention_daily,
            "weekly": settings.backup_retention_weekly,
            "monthly": settings.backup_retention_monthly,
        }

        for backup_type, days in retention.items():

            if not days:
                continue

            directory = restaurant_dir / backup_type

            if not directory.exists():
                continue

            limit = now - timedelta(days=days)

            for backup in directory.rglob("*"):

                if not backup.is_file():
                    continue

                modified = datetime.fromtimestamp(
                    backup.stat().st_mtime,
                    tz=timezone.utc
                )

                if modified < limit:
                    backup.unlink()

#-------------------------------------------------------------------
# CALCULAR PRÓXIMO BACKUP PROGRAMADO
#-------------------------------------------------------------------
    def _calculate_next_run(
        self,
        settings: SystemSettings
    ):
        tz = ZoneInfo(settings.backup_timezone)
        now = datetime.now(tz)
        backup_time = settings.backup_time or time(3, 0)
        candidate = now.replace(
            hour=backup_time.hour,
            minute=backup_time.minute,
            second=0,
            microsecond=0
        )
        frequency = settings.backup_frequency.value
        if frequency == "daily":
            if candidate <= now:
                candidate += timedelta(days=1)
            return candidate
        if frequency == "weekly":
            weekday = settings.backup_weekday or 0
            days = weekday - candidate.weekday()
            if days < 0:
                days += 7
            candidate += timedelta(days=days)
            if candidate <= now:
                candidate += timedelta(days=7)
            return candidate
        if frequency == "monthly":
            monthday = settings.backup_monthday or 1
            year = now.year
            month = now.month
            last_day = calendar.monthrange(year, month)[1]
            day = min(monthday, last_day)
            candidate = candidate.replace(day=day)
            if candidate <= now:
                if month == 12:
                    year += 1
                    month = 1
                else:
                    month += 1
                last_day = calendar.monthrange(year, month)[1]
                day = min(monthday, last_day)
                candidate = candidate.replace(
                    year=year,
                    month=month,
                    day=day
                )
            return candidate.astimezone(timezone.utc)
        return None

#-------------------------------------------------------------------------------
# Crear archivo restore.pending para indicar que se debe restaurar un backup
#-------------------------------------------------------------------------------
    def _create_restore_pending(self, backup: Path):
        pending = Path(os.getenv("BACKUP_DIR", "/backups")) / "restore.pending"
        pending.write_text(str(backup), encoding="utf-8")

#-------------------------------------------------------------------
# DEVOLVER EL ESTADO DEL BACKUP
#-------------------------------------------------------------------
    def status(self, restaurant_id: int) -> BackupStatusOut:
        settings = self._get_settings(restaurant_id)
        self.backup_dir.mkdir(
            parents=True,
            exist_ok=True
        )
        latest = self._latest_backup_file(restaurant_id)
        return BackupStatusOut(
            last_backup_at=latest["modified_at"] if latest else None,
            last_backup_file=latest["name"] if latest else None,
            last_backup_size=latest["size"] if latest else None,
            last_backup_source=latest["type"] if latest else None,
            email_enabled=self._email_enabled(restaurant_id),
            email_from=settings.smtp_from if settings else None,
            last_automatic_backup_at=settings.last_automatic_backup_at
            if settings and settings.last_automatic_backup_at
            else None,
            next_automatic_backup_at=settings.next_automatic_backup_at
                if settings and settings.next_automatic_backup_at
                else None,
            last_backup_result=settings.last_backup_result
                if settings else None
        )

#-------------------------------------------------------------------
# CREAR BACKUP
#-------------------------------------------------------------------
    def create_backup(self, restaurant_id) -> BackupInfoOut:
        return self._create_backup(
            restaurant_id,
            "manual"
        )

#-------------------------------------------------------------------
# CREAR BACKUP AUTOMÁTICO
#-------------------------------------------------------------------
    def create_automatic_backup(self, restaurant_id: int, frequency: str) -> BackupInfoOut:
        return self._create_backup(restaurant_id, frequency)

#-------------------------------------------------------------------
# CREAR BACKUP Y ENVIAR POR EMAIL
#-------------------------------------------------------------------
    def create_and_email_backup(self, recipient_email: str, restaurant_id: int) -> BackupEmailOut:
        if not self._email_enabled(restaurant_id):
            raise DomainError(
                code=ErrorCode.SMTP_NOT_CONFIGURED,
                detail="SMTP is not configured for this restaurant"
            )
        backup = self.create_backup(restaurant_id)
        backup_path = self.backup_dir / backup.last_backup_file
        try:
            self._send_backup_email(
                recipient_email=recipient_email,
                backup_path=backup_path,
                created_at=backup.last_backup_at,
                restaurant_id=restaurant_id
            )

        except (
            smtplib.SMTPException,
            ConnectionError,
            TimeoutError,
            socket.timeout,
            OSError
        ) as ex:
            raise DomainError(
                "Error sending backup email",
                ErrorCode.EMAIL_SEND_FAILURE,
                context={
                    "recipient": recipient_email,
                    "detail": str(ex)
                }
            ) from ex

        return BackupEmailOut(
            **backup.model_dump(),
            sent_to=recipient_email
        )

#-------------------------------------------------------------------
# DESCARGAR BACKUP
#-------------------------------------------------------------------
    def download_backup(self, restaurant_id: int, filename: str ):
        path = self._find_backup(
            restaurant_id,
            filename
        )
        return FileResponse(
            path=path,
            filename=path.name,
            media_type="application/octet-stream"
        )

#-------------------------------------------------------------------
# LISTAR BACKUPS
#-------------------------------------------------------------------
    def list_backups(self, restaurant_id: int) -> list[BackupFileOut]:
        directory = self._restaurant_backup_directory(
            restaurant_id
        )
        files = [
            path
            for path in directory.rglob("*")
            if path.is_file()
        ]
        files.sort(
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        return [
            BackupFileOut(
                filename=str(path.relative_to(directory)),
                created_at=datetime.fromtimestamp(
                    path.stat().st_mtime,
                    tz=timezone.utc
                ),
                size=path.stat().st_size,
                type=(
                    "manual"
                    if path.parent == directory
                    else path.parent.name
                )
            )
            for path in files
        ]

#-------------------------------------------------------------------
# ELIMINAR BACKUP
#-------------------------------------------------------------------    
    def delete_backup(self, restaurant_id: int, filename: str) -> BackupDeleteOut:
        path = self._find_backup(
            restaurant_id,
            filename
        )
        path.unlink()
        return BackupDeleteOut(success=True)

#-------------------------------------------------------------------
# RESTORE BACKUP
#-------------------------------------------------------------------
    def restore_backup(self, restaurant_id: int, filename: str) -> BackupRestoreOut:
        backup = self._find_backup(restaurant_id, filename)
        self._backup_before_restore(restaurant_id)
        self._create_restore_pending(backup)
        RestartManager.request_restart()
        return BackupRestoreOut(
            success=True,
            restart_required=True
        )

#-------------------------------------------------------------------
# CORRER BACKUPS PENDIENTES
#-------------------------------------------------------------------
    def run_pending_backups(self):
        now = datetime.now(timezone.utc)
        restaurants = (
            self.db.query(SystemSettings)
            .filter(
                SystemSettings.backup_enabled.is_(True),
                SystemSettings.next_automatic_backup_at <= now
            )
            .all()
        )
        for settings in restaurants:
            try:
                self.run_scheduled_backup(
                    settings.restaurant_id
                )
            except Exception:
                logger.exception(
                    f"Error running scheduled backup for restaurant {settings.restaurant_id}"
                )
                self.db.rollback()

#-------------------------------------------------------------------
# CORRER BACKUP PROGRAMADO
#-------------------------------------------------------------------
    def run_scheduled_backup(self, restaurant_id: int):
        settings = self._get_settings(restaurant_id)
        if not settings:
            raise DomainError(
                "Backup settings not found",
                ErrorCode.NOT_FOUND
            )

        try:
            backup = self.create_automatic_backup(
                restaurant_id,
                settings.backup_frequency.value
            )

            self._apply_retention_policy(settings)
            
            if settings.backup_send_email and settings.backup_email:
                backup_path = (
                    self.backup_dir /
                    backup.last_backup_file
                )
                self._send_backup_email(
                    settings.backup_email,
                    backup_path,
                    backup.last_backup_at,
                    restaurant_id
                )
            settings.last_backup_result = "OK"
        except Exception as ex:
            logger.exception(
                f"Error running scheduled backup for restaurant {settings.restaurant_id}"
            )
            settings.last_backup_result = str(ex)
        settings.last_automatic_backup_at = datetime.now(timezone.utc)
        settings.next_automatic_backup_at = self._calculate_next_run(settings)
        self.db.commit()