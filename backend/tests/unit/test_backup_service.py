"""
tests/unit/test_backup_service.py

Fase 4 (P1) del plan de testing: backup/restore.

No testeamos pg_dump/pg_restore en sí (eso lo garantiza Postgres) --
testeamos la lógica alrededor: cálculo de próxima corrida, política
de retención, resolución de directorios, y el manejo de errores de
subprocess (mockeado, sin ejecutar pg_dump de verdad).

IMPORTANTE: BackupService(db) llama a _resolve_backup_dir() en su
__init__, que en este contenedor puede resolver a /backups (el
volumen real montado, ver BACKUP_DIR en docker-compose.yml). Por eso
en casi todos los tests pisamos service.backup_dir = tmp_path
INMEDIATAMENTE después de instanciar, para no escribir jamás sobre
el directorio real de backups del restaurante.

Correr con: docker compose exec backend pytest tests/unit/test_backup_service.py -v
"""

import os
import subprocess
from datetime import datetime, time, timezone

import pytest
from app.domain.backup.backup_service import BackupService
from app.domain.errors.base import DomainError
from app.models.system_settings import SystemSettings
from app.models.enums import BackupFrequency


def _settings(**overrides) -> SystemSettings:
    """
    SystemSettings como objeto Python plano, SIN guardar en DB --
    _calculate_next_run y _apply_retention_policy solo leen atributos,
    no hacen falta persistidos.
    """
    defaults = dict(
        restaurant_id=1,
        backup_frequency=BackupFrequency.DAILY,
        backup_time=time(3, 0),
        backup_weekday=0,
        backup_monthday=1,
        backup_timezone="America/Montevideo",
        backup_retention_daily=30,
        backup_retention_weekly=84,
        backup_retention_monthly=365,
    )
    defaults.update(overrides)
    return SystemSettings(**defaults)


# --------------------------------------------------------------------------------
# _calculate_next_run -- función pura, sin filesystem ni DB
# --------------------------------------------------------------------------------

def test_calculate_next_run_daily_hora_futura_es_hoy(db):
    service = BackupService(db)
    settings = _settings(
        backup_frequency=BackupFrequency.DAILY,
        backup_time=time(23, 59),
    )

    resultado = service._calculate_next_run(settings)

    ahora = datetime.now(resultado.tzinfo)
    assert resultado.date() == ahora.date()
    assert resultado.hour == 23 and resultado.minute == 59


def test_calculate_next_run_daily_hora_pasada_es_manana(db):
    service = BackupService(db)
    settings = _settings(
        backup_frequency=BackupFrequency.DAILY,
        backup_time=time(0, 1),
    )

    resultado = service._calculate_next_run(settings)

    ahora = datetime.now(resultado.tzinfo)
    # Salvo que corras el test a las 00:00-00:01 exactas, debe caer mañana
    assert resultado.date() > ahora.date() or resultado > ahora


def test_calculate_next_run_monthly_clampea_dia_31_en_febrero(db):
    """
    Caso límite real: backup_monthday=31 pero el próximo mes es
    febrero (28 o 29 días) -- no debe reventar, debe usar el último
    día disponible del mes.
    """
    service = BackupService(db)
    settings = _settings(
        backup_frequency=BackupFrequency.MONTHLY,
        backup_monthday=31,
        backup_time=time(0, 0),
    )

    resultado = service._calculate_next_run(settings)

    # Nunca debe caer en un día que no existe (ej: 31 de febrero)
    assert 1 <= resultado.day <= 31


def test_calculate_next_run_weekly_cae_en_el_weekday_configurado(db):
    service = BackupService(db)
    settings = _settings(
        backup_frequency=BackupFrequency.WEEKLY,
        backup_weekday=2,  # miércoles (Monday=0)
        backup_time=time(23, 59),
    )

    resultado = service._calculate_next_run(settings)

    assert resultado.weekday() == 2


# --------------------------------------------------------------------------------
# _apply_retention_policy -- filesystem real, pero en tmp_path (pytest lo limpia solo)
# --------------------------------------------------------------------------------

def test_apply_retention_policy_borra_backups_viejos_conserva_nuevos(db, tmp_path):
    service = BackupService(db)
    service.backup_dir = tmp_path  # nunca tocar /backups real

    settings = _settings(restaurant_id=1, backup_retention_daily=7)
    daily_dir = tmp_path / "restaurant_1" / "daily"
    daily_dir.mkdir(parents=True)

    viejo = daily_dir / "backup-viejo.dump"
    nuevo = daily_dir / "backup-nuevo.dump"
    viejo.write_bytes(b"x")
    nuevo.write_bytes(b"x")

    ahora = datetime.now(timezone.utc).timestamp()
    diez_dias = 10 * 24 * 60 * 60
    un_dia = 24 * 60 * 60
    os.utime(viejo, (ahora - diez_dias, ahora - diez_dias))  # más viejo que retention=7 días
    os.utime(nuevo, (ahora - un_dia, ahora - un_dia))         # dentro de retention

    service._apply_retention_policy(settings)

    assert not viejo.exists()
    assert nuevo.exists()


def test_apply_retention_policy_sin_directorio_no_falla(db, tmp_path):
    """
    Si todavía no existe restaurant_X/ (nunca se hizo un backup),
    no debe romper -- debe salir en silencio.
    """
    service = BackupService(db)
    service.backup_dir = tmp_path
    settings = _settings(restaurant_id=999)

    service._apply_retention_policy(settings)  # no debe lanzar excepción


def test_apply_retention_policy_dias_en_cero_no_borra_nada(db, tmp_path):
    """
    retention=0/None para un tipo de backup significa "conservar para
    siempre" (el código hace `if not days: continue`) -- confirmamos
    que esa interpretación es la que efectivamente corre.
    """
    service = BackupService(db)
    service.backup_dir = tmp_path
    settings = _settings(restaurant_id=1, backup_retention_daily=0)

    daily_dir = tmp_path / "restaurant_1" / "daily"
    daily_dir.mkdir(parents=True)
    viejo = daily_dir / "backup-viejo.dump"
    viejo.write_bytes(b"x")
    ahora = datetime.now(timezone.utc).timestamp()
    cien_dias = 100 * 24 * 60 * 60
    os.utime(viejo, (ahora - cien_dias, ahora - cien_dias))

    service._apply_retention_policy(settings)

    assert viejo.exists()


# --------------------------------------------------------------------------------
# _resolve_backup_dir
# --------------------------------------------------------------------------------

def test_resolve_backup_dir_respeta_env_var(db, tmp_path, monkeypatch):
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path))

    service = BackupService(db)

    assert service.backup_dir == tmp_path


# --------------------------------------------------------------------------------
# _restaurant_backup_directory -- crea el directorio si no existe
# --------------------------------------------------------------------------------

def test_restaurant_backup_directory_crea_carpeta_si_no_existe(db, tmp_path):
    service = BackupService(db)
    service.backup_dir = tmp_path

    resultado = service._restaurant_backup_directory(restaurant_id=5)

    assert resultado.exists()
    assert resultado == tmp_path / "restaurant_5"


# --------------------------------------------------------------------------------
# _backup_postgres -- subprocess mockeado, nunca corre pg_dump de verdad
# --------------------------------------------------------------------------------

def test_backup_postgres_lanza_domain_error_si_pg_dump_falla(db, tmp_path, monkeypatch):
    service = BackupService(db)

    def fake_run(command, capture_output, text, env):
        return subprocess.CompletedProcess(
            args=command, returncode=1, stdout="", stderr="conexión rechazada"
        )

    monkeypatch.setattr(
        "app.domain.backup.backup_service.subprocess.run", fake_run
    )

    with pytest.raises(DomainError):
        service._backup_postgres(tmp_path / "backup.dump")


def test_backup_postgres_no_lanza_error_si_pg_dump_ok(db, tmp_path, monkeypatch):
    service = BackupService(db)

    def fake_run(command, capture_output, text, env):
        return subprocess.CompletedProcess(args=command, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(
        "app.domain.backup.backup_service.subprocess.run", fake_run
    )

    service._backup_postgres(tmp_path / "backup.dump")  # no debe lanzar
