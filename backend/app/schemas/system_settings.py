from pydantic import Field, EmailStr

from .base import BaseSchema
from datetime import datetime, time
from app.models.enums import BackupFrequency

class SettingsUpdateRequest(BaseSchema):
    smtp_host: str | None = None
    smtp_port: int | None = Field(ge=1, le=65535)
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: EmailStr | None = None
    smtp_use_tls: bool = True

    backup_email: EmailStr | None = None

    backup_enabled: bool = False
    backup_frequency: BackupFrequency = BackupFrequency.MANUAL

    backup_time: time | None = None
    backup_weekday: int | None = Field(default=None, ge=0, le=6)
    backup_monthday: int | None = Field(default=None, ge=1, le=31)

    backup_retention_daily: int = Field(default=30, ge=1)
    backup_retention_weekly: int = Field(default=12, ge=1)
    backup_retention_monthly: int = Field(default=24, ge=1)
    backup_keep_local: bool = True
    backup_send_email: bool = True

    backup_timezone: str = "America/Montevideo"


class SettingsResponse(BaseSchema):

    smtp_host: str | None
    smtp_port: int | None
    smtp_user: str | None

    smtp_from: EmailStr | None
    smtp_use_tls: bool

    smtp_password_configured: bool

    backup_email: EmailStr | None

    backup_enabled: bool
    backup_frequency: BackupFrequency

    backup_time: time | None
    backup_weekday: int | None
    backup_monthday: int | None

    backup_retention_daily: int
    backup_retention_weekly: int
    backup_retention_monthly: int

    backup_keep_local: bool
    backup_send_email: bool

    backup_timezone: str

    last_automatic_backup_at: datetime | None
    next_automatic_backup_at: datetime | None
    last_backup_result: str | None

class EmailTestResponse(BaseSchema):
    success: bool
    sent_to: str