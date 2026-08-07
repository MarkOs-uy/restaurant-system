from pathlib import Path

from app.domain.backup.restore_executor import RestoreExecutor


# --------------------------------------------------------------------------------------
# Archivo utilizado para indicar que existe una restauración pendiente.
# --------------------------------------------------------------------------------------
PENDING = Path("/backups/restore.pending")


# --------------------------------------------------------------------------------------
# Si existe un archivo de restauración pendiente, ejecutar el restore antes de iniciar
# la aplicación y eliminar el archivo de control.
# --------------------------------------------------------------------------------------
if PENDING.exists():
    backup = Path(PENDING.read_text().strip())

    print(
        f"restore_pending. Restaurando base de datos desde backup: {backup}"
    )

    RestoreExecutor.restore(backup)

    PENDING.unlink()