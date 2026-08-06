from pathlib import Path

from app.domain.backup.restore_executor import RestoreExecutor

PENDING = Path("/backups/restore.pending")

if PENDING.exists():
    backup = Path(PENDING.read_text().strip())
    print(f"restore_pending. Restaurando base de datos desde backup: {backup}")
    RestoreExecutor.restore(backup)
    PENDING.unlink()