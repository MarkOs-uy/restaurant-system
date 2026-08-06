import smtplib
from email.message import EmailMessage
from sqlalchemy.orm import Session

from app.domain.backup.schedule_utils import calculate_next_backup
from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.models.enums import BackupFrequency
from app.models.system_settings import SystemSettings

from app.schemas.system_settings import (
    SettingsUpdateRequest,
    SettingsResponse
)

class SettingsService:

    def __init__(self, db: Session) -> None:
        self.db = db

    '''
    Servicio encargado de la lógica de negocio relacionada con la configuración del sistema.

    Responsabilidades:
    - Gestionar la lógica de negocio de la configuración del sistema.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    '''

    # --------------------------------------------------------------------------------------
    # Obtener configuración del sistema para un restaurante
    # --------------------------------------------------------------------------------------
    def get_settings(
        self,
        restaurant_id: int
    ) -> SystemSettings:
        settings = (
            self.db.query(SystemSettings)
            .filter(
                SystemSettings.restaurant_id == restaurant_id
            )
            .first()
        )
        if not settings:
            settings = SystemSettings(
                restaurant_id=restaurant_id,
                smtp_use_tls=True,
                backup_timezone="America/Montevideo"
            )
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        return settings

    # --------------------------------------------------------------------------------------
    # Serializar configuración del sistema para respuesta de API
    # --------------------------------------------------------------------------------------
    def to_response(
        self,
        settings: SystemSettings
    ) -> SettingsResponse:

        return SettingsResponse(
            smtp_host=settings.smtp_host,
            smtp_port=settings.smtp_port,
            smtp_user=settings.smtp_user,
            smtp_from=settings.smtp_from,
            smtp_use_tls=settings.smtp_use_tls,

            smtp_password_configured=bool(settings.smtp_password),

            backup_email=settings.backup_email,
            backup_enabled=settings.backup_enabled,
            backup_frequency=settings.backup_frequency,

            backup_time=settings.backup_time,
            backup_weekday=settings.backup_weekday,
            backup_monthday=settings.backup_monthday,

            backup_retention_daily=settings.backup_retention_daily,
            backup_retention_weekly=settings.backup_retention_weekly,
            backup_retention_monthly=settings.backup_retention_monthly,

            backup_keep_local=settings.backup_keep_local,
            backup_send_email=settings.backup_send_email,
            backup_timezone=settings.backup_timezone,

            last_automatic_backup_at=settings.last_automatic_backup_at,
            next_automatic_backup_at=settings.next_automatic_backup_at,
            last_backup_result=settings.last_backup_result,
        )

    # --------------------------------------------------------------------------------------
    # Actualizar configuración del sistema para un restaurante
    # --------------------------------------------------------------------------------------
    def update_settings(
        self,
        restaurant_id: int,
        data: SettingsUpdateRequest
    ) -> SystemSettings:
        settings = self.get_settings(restaurant_id)
        if (
            data.backup_enabled
            and not data.backup_keep_local
            and not data.backup_send_email
        ):
            raise DomainError(
                "Debe conservar el backup localmente o enviarlo por correo.",
                ErrorCode.BACKUP_DESTINATION_REQUIRED
            )
        if (
            data.backup_frequency == BackupFrequency.WEEKLY
            and data.backup_weekday is None
        ):
            raise DomainError(
                "Debe indicar el dia de la semana.",
                ErrorCode.BACKUP_WEEKDAY_REQUIRED
            )
        if (
            data.backup_frequency == BackupFrequency.MONTHLY
            and data.backup_monthday is None
        ):
            raise DomainError(
                "Debe indicar el dia del mes.",
                ErrorCode.BACKUP_MONTHDAY_REQUIRED
            )
        if data.backup_send_email:
            if not data.smtp_host:
                raise DomainError(
                    "SMTP Host no configurado",
                    ErrorCode.SMTP_HOST_NOT_CONFIGURED
                )
            if not data.backup_email:
                raise DomainError(
                    "Correo de backup no configurado",
                    ErrorCode.BACKUP_EMAIL_NOT_CONFIGURED
                )
        settings.smtp_host = data.smtp_host
        settings.smtp_port = data.smtp_port
        settings.smtp_user = data.smtp_user
        settings.smtp_from = data.smtp_from
        settings.smtp_use_tls = data.smtp_use_tls

        settings.backup_email = data.backup_email
        settings.backup_enabled = data.backup_enabled
        settings.backup_frequency = data.backup_frequency
        settings.backup_time = data.backup_time
        settings.backup_weekday = data.backup_weekday
        settings.backup_monthday = data.backup_monthday
        settings.backup_retention_daily = data.backup_retention_daily
        settings.backup_retention_weekly = data.backup_retention_weekly
        settings.backup_retention_monthly = data.backup_retention_monthly
        settings.backup_keep_local = data.backup_keep_local
        settings.backup_send_email = data.backup_send_email
        settings.backup_timezone = data.backup_timezone
        settings.next_automatic_backup_at = (
            calculate_next_backup(settings)
            if settings.backup_enabled
            else None
        )
        if data.smtp_password:
            settings.smtp_password = data.smtp_password
        self.db.commit()
        self.db.refresh(settings)
        return settings

    # --------------------------------------------------------------------------------------
    # Enviar correo de prueba para verificar configuración SMTP
    # --------------------------------------------------------------------------------------
    def send_test_email(
        self,
        restaurant_id: int
    ):
        settings = self.get_settings(restaurant_id)
        if not settings.smtp_host:
            raise DomainError(
                "SMTP Host no configurado",
                ErrorCode.SMTP_HOST_NOT_CONFIGURED
            )
        if not settings.backup_email:
            raise DomainError(
                "Correo de backup no configurado",
                ErrorCode.BACKUP_EMAIL_NOT_CONFIGURED
            )
        smtp_host = settings.smtp_host
        smtp_port = settings.smtp_port or 587
        smtp_user = settings.smtp_user or ""
        smtp_password = settings.smtp_password or ""
        smtp_from = settings.smtp_from or smtp_user
        smtp_use_tls = settings.smtp_use_tls

        message = EmailMessage()

        message["Subject"] = "Prueba de correo"
        message["From"] = smtp_from
        message["To"] = settings.backup_email

        message.set_content(
            "La configuracion SMTP del sistema funciona correctamente."
        )
        try:
            with smtplib.SMTP(
                smtp_host,
                smtp_port,
                timeout=30
            ) as smtp:
                if smtp_use_tls:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.ehlo()
                if smtp_user:
                    smtp.login(
                        smtp_user,
                        smtp_password
                    )
                smtp.send_message(message)
        except (
            smtplib.SMTPException,
            TimeoutError,
            ConnectionError,
            OSError
        ) as ex:
            raise DomainError(
                "No fue posible enviar el correo de prueba.",
                ErrorCode.EMAIL_SEND_FAILURE,
                context={"detail": str(ex)}
            ) from ex
        return {
            "success": True,
            "sent_to": settings.backup_email
        }