import os
import shutil
import subprocess
from pathlib import Path

from urllib.parse import unquote, urlparse

from app.db.session import DATABASE_URL

class RestoreExecutor:

#--------------------------------------------------------------------------------------
# RESTAURA LA BASE DE DATOS DE ACUERDO AL MOTOR DE BASE DE DATOS
#--------------------------------------------------------------------------------------
    @staticmethod
    def restore(backup: Path) -> None:
        if DATABASE_URL.startswith("sqlite"):
            RestoreExecutor._restore_sqlite(backup)
        elif DATABASE_URL.startswith("postgresql"):
            RestoreExecutor._restore_postgres(backup)
        else:
            raise RuntimeError(
                f"Unsupported database engine: {DATABASE_URL}"
            )

#-------------------------------------------------------------------
# RESTORE SQLITE
#-------------------------------------------------------------------
    @staticmethod
    def _restore_sqlite(backup: Path) -> None:
        parsed = urlparse(DATABASE_URL)
        database_path = unquote(parsed.path)
        if os.name == "nt" and database_path.startswith("/"):
            database_path = database_path[1:]
        destination = Path(database_path)
        shutil.copy2(backup, destination)

#-------------------------------------------------------------------
# RESTORE POSTGRES
#-------------------------------------------------------------------
    @staticmethod
    def _restore_postgres(backup: Path) -> None:
        parsed = urlparse(
            DATABASE_URL.replace(
                "postgresql+psycopg2://",
                "postgresql://"
            )
        )
        env = os.environ.copy()
        env["PGPASSWORD"] = parsed.password
        command = [
            "pg_restore",
            "-h", parsed.hostname,
            "-p", str(parsed.port or 5432),
            "-U", parsed.username,
            "-d", parsed.path.lstrip("/"),
            "--clean",
            "--if-exists",
            "--no-owner",
            "--exit-on-error",
            "--verbose",
            str(backup)
        ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            env=env
        )
        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip()
            )