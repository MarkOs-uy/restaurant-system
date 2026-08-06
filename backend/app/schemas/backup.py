from datetime import datetime

from .base import BaseSchema
from pydantic import EmailStr


# -------------------------------------------------------------------
# Request
# -------------------------------------------------------------------
class BackupEmailRequest(BaseSchema):
    email: EmailStr

# -------------------------------------------------------------------
# Reusable
# -------------------------------------------------------------------
class BackupInfoOut(BaseSchema):
    last_backup_at: datetime
    last_backup_file: str
    last_backup_size: int
    type: str


class BackupFileOut(BaseSchema):
    filename: str
    created_at: datetime
    size: int
    type: str

# -------------------------------------------------------------------
# Status
# -------------------------------------------------------------------
class BackupStatusOut(BaseSchema):
    last_backup_at: datetime | None
    last_backup_file: str | None
    last_backup_size: int | None
    last_backup_source: str | None

    email_enabled: bool
    email_from: str | None

    last_automatic_backup_at: datetime | None
    next_automatic_backup_at: datetime | None

    last_backup_result: str | None

# -------------------------------------------------------------------
# Responses
# -------------------------------------------------------------------
class BackupEmailOut(BackupInfoOut):
    sent_to: EmailStr


class BackupDeleteOut(BaseSchema):
    success: bool


class BackupRestoreOut(BaseSchema):
    success: bool
    restart_required: bool