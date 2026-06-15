import json
import os
import shutil
import smtplib
import subprocess
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import unquote, urlparse

from app.db.session import DATABASE_URL


class BackupService:
    def __init__(self):
        self.backup_dir = self._resolve_backup_dir()
        self.metadata_path = self.backup_dir / "metadata.json"

    def status(self):
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        metadata = self._read_metadata()
        latest_backup = self._latest_backup_file()

        return {
            "last_backup_at": latest_backup["modified_at"] if latest_backup else metadata.get("last_backup_at"),
            "last_backup_file": latest_backup["name"] if latest_backup else metadata.get("last_backup_file"),
            "last_backup_size": latest_backup["size"] if latest_backup else metadata.get("last_backup_size"),
            "last_backup_source": latest_backup["source"] if latest_backup else "manual",
            "email_enabled": self._email_enabled(),
            "email_from": os.getenv("SMTP_FROM", os.getenv("SMTP_USER", "")) or None
        }

    def create_backup(self):
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        created_at = datetime.now()
        backup_path = self._backup_path(created_at)

        if DATABASE_URL.startswith("sqlite"):
            self._backup_sqlite(backup_path)
        elif DATABASE_URL.startswith("postgresql"):
            self._backup_postgres(backup_path)
        else:
            raise RuntimeError("Motor de base de datos no soportado para backup")

        metadata = {
            "last_backup_at": created_at.isoformat(),
            "last_backup_file": backup_path.name,
            "last_backup_size": backup_path.stat().st_size
        }
        self._write_metadata(metadata)

        return metadata

    def create_and_email_backup(self, recipient_email: str):
        if not self._email_enabled():
            raise RuntimeError("SMTP no esta configurado")

        backup = self.create_backup()
        backup_path = self.backup_dir / backup["last_backup_file"]
        self._send_backup_email(recipient_email, backup_path, backup["last_backup_at"])

        return {
            **backup,
            "sent_to": recipient_email
        }

    def _backup_path(self, created_at: datetime):
        suffix = ".sqlite3" if DATABASE_URL.startswith("sqlite") else ".dump"
        manual_dir = self.backup_dir / "manual"
        manual_dir.mkdir(parents=True, exist_ok=True)
        return manual_dir / f"backup-{created_at.strftime('%Y%m%d-%H%M%S')}{suffix}"

    def _backup_sqlite(self, backup_path: Path):
        parsed = urlparse(DATABASE_URL)
        database_path = unquote(parsed.path)

        if os.name == "nt" and database_path.startswith("/"):
            database_path = database_path[1:]

        source = Path(database_path)
        if not source.exists():
            raise RuntimeError("No se encontro el archivo de base de datos SQLite")

        shutil.copy2(source, backup_path)

    def _backup_postgres(self, backup_path: Path):
        command = ["pg_dump", "--format=custom", "--file", str(backup_path), DATABASE_URL]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            detail = result.stderr.strip() or "No se pudo ejecutar pg_dump"
            raise RuntimeError(detail)

    def _send_backup_email(self, recipient_email: str, backup_path: Path, created_at: str):
        smtp_host = os.getenv("SMTP_HOST", "")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        smtp_from = os.getenv("SMTP_FROM", smtp_user)
        smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes", "on")

        message = EmailMessage()
        message["Subject"] = "Backup del sistema restaurant"
        message["From"] = smtp_from
        message["To"] = recipient_email
        message.set_content(
            f"Adjunto backup generado el {created_at}.\n\n"
            "Este correo fue generado automaticamente por el sistema."
        )

        message.add_attachment(
            backup_path.read_bytes(),
            maintype="application",
            subtype="octet-stream",
            filename=backup_path.name
        )

        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as smtp:
            if smtp_use_tls:
                smtp.starttls()
            if smtp_user:
                smtp.login(smtp_user, smtp_password)
            smtp.send_message(message)

    def _email_enabled(self):
        return bool(
            os.getenv("SMTP_HOST")
            and os.getenv("SMTP_FROM", os.getenv("SMTP_USER", ""))
        )

    def _read_metadata(self):
        if not self.metadata_path.exists():
            return {}

        try:
            return json.loads(self.metadata_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _write_metadata(self, metadata: dict):
        self.metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    def _resolve_backup_dir(self):
        configured_dir = os.getenv("BACKUP_DIR")
        if configured_dir:
            return Path(configured_dir)

        mounted_dir = Path("/backups")
        if mounted_dir.exists():
            return mounted_dir

        return Path("backups")

    def _latest_backup_file(self):
        if not self.backup_dir.exists():
            return None

        candidates = [
            path
            for path in self.backup_dir.rglob("*")
            if path.is_file()
            and path.name != "metadata.json"
            and path.stat().st_size > 0
        ]

        if not candidates:
            return None

        latest = max(candidates, key=lambda path: path.stat().st_mtime)
        stats = latest.stat()

        return {
            "name": str(latest.relative_to(self.backup_dir)),
            "modified_at": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "size": stats.st_size,
            "source": "automatic" if latest.parts[-2] in ("daily", "weekly", "monthly", "last") else "manual"
        }
