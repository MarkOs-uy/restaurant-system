import calendar

from datetime import datetime, time, timedelta, timezone, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.models.system_settings import SystemSettings
from app.models.enums import BackupFrequency

#----------------------------------------------------------------------------------
# Resuelve la zona horaria a partir del nombre de la zona horaria.
# Si la zona horaria no es válida, se devuelve UTC.
#----------------------------------------------------------------------------------
def _resolve_timezone(timezone_name: str) -> tzinfo:
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        if timezone_name == "America/Montevideo":
            return timezone(timedelta(hours=-3))
        return timezone.utc

#------------------------------------------------------------------------------------------
# Devuelve el próximo instante programado en UTC según la configuración del restaurante.
#------------------------------------------------------------------------------------------
def calculate_next_backup(
    settings: SystemSettings,
    reference: datetime | None = None,
) -> datetime | None:
    if reference is None:
        reference = datetime.now(timezone.utc)

    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)

    tz = _resolve_timezone(settings.backup_timezone or "UTC")
    now = reference.astimezone(tz)
    backup_time = settings.backup_time or time(3, 0)

    candidate = now.replace(
        hour=backup_time.hour,
        minute=backup_time.minute,
        second=0,
        microsecond=0
    )

    frequency = settings.backup_frequency

    if frequency == BackupFrequency.DAILY:
        if candidate <= now:
            candidate += timedelta(days=1)
        return candidate.astimezone(timezone.utc)

    if frequency == BackupFrequency.WEEKLY:
        weekday = settings.backup_weekday or 0
        days = weekday - candidate.weekday()
        days = (weekday - candidate.weekday()) % 7
        candidate += timedelta(days=days)
        if candidate <= now:
            candidate += timedelta(days=7)
        return candidate.astimezone(timezone.utc)

    if frequency == BackupFrequency.MONTHLY:
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