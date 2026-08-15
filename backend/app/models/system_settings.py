# app/models/system_settings.py

from datetime import time

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Time,
    Enum as SqlEnum,
)
from sqlalchemy.orm import relationship

from app.models.enums import BackupFrequency

from app.db.base_class import Base


class SystemSettings(Base):
    __tablename__ = "system_settings"

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        primary_key=True
    )

    # SMTP
    smtp_host = Column(
        String,
        nullable=True
    )

    smtp_port = Column(
        Integer,
        nullable=False,
        default=587
    )

    smtp_user = Column(
        String,
        nullable=True
    )

    smtp_password = Column(
        String,
        nullable=True
    )

    smtp_from = Column(
        String,
        nullable=True
    )

    smtp_use_tls = Column(
        Boolean,
        nullable=False,
        default=True
    )


    # Backups
    backup_email = Column(
        String,
        nullable=True
    )

    backup_frequency = Column(
        SqlEnum(
            BackupFrequency,
            values_callable=lambda enum: [
                item.value
                for item in enum
            ],
            native_enum=False,
            length=20
        ),
        nullable=False,
        default=BackupFrequency.MANUAL
    )

    backup_retention_daily = Column(
        Integer,
        nullable=False,
        default=30
    )

    backup_retention_weekly = Column(
        Integer,
        nullable=False,
        default=84
    )

    backup_retention_monthly = Column(
        Integer,
        nullable=False,
        default=365
    )

    backup_time = Column(
        Time,
        nullable=False,
        default=time(hour=3, minute=0)
    )

    backup_weekday = Column(
        Integer,
        nullable=True
    )

    backup_monthday = Column(
        Integer,
        nullable=True
    )

    backup_enabled = Column(
        Boolean,
        nullable=False,
        default=False
    )

    last_automatic_backup_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    next_automatic_backup_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    last_backup_result = Column(
        String,
        nullable=True
    )

    backup_keep_local = Column(
        Boolean,
        nullable=False,
        default=True
    )

    backup_send_email = Column(
        Boolean,
        nullable=False,
        default=False
    )

    backup_timezone = Column(
        String,
        nullable=False,
        default="America/Montevideo"
    )

    restaurant = relationship(
        "Restaurant",
        back_populates="settings"
    )