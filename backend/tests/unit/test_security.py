"""
tests/unit/test_security.py

Fase 3 (P1) del plan de testing: funciones puras de app/core/security.py.
No necesitan `db` -- son funciones sin estado, ideales para arrancar rápido.

Correr con: docker compose exec backend pytest tests/unit/test_security.py -v
"""

from datetime import datetime, timedelta, timezone

from jose import jwt as jose_jwt
import pytest

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.core.config import SECRET_KEY, ALGORITHM


# --------------------------------------------------------------------------------
# Hashing de contraseñas
# --------------------------------------------------------------------------------

def test_password_hash_verifica_correctamente():
    hash_ = get_password_hash("mi_password_segura")

    assert verify_password("mi_password_segura", hash_) is True


def test_password_hash_rechaza_password_incorrecto():
    hash_ = get_password_hash("mi_password_segura")

    assert verify_password("password_equivocado", hash_) is False


def test_password_hash_nunca_es_igual_al_texto_plano():
    """
    Chequeo básico pero importante: confirma que efectivamente se
    está hasheando y no guardando en texto plano por error.
    """
    hash_ = get_password_hash("mi_password_segura")

    assert hash_ != "mi_password_segura"


# --------------------------------------------------------------------------------
# create_access_token / decode_access_token
# --------------------------------------------------------------------------------

def test_create_access_token_incluye_los_claims_esperados():
    token = create_access_token({
        "sub": "1",
        "restaurant_id": "1",
        "role": "ADMIN",
    })

    payload = decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == "1"
    assert payload["restaurant_id"] == "1"
    assert payload["role"] == "ADMIN"
    assert "exp" in payload
    assert "iat" in payload
    assert "jti" in payload


def test_decode_access_token_con_token_invalido_devuelve_none():
    assert decode_access_token("esto-no-es-un-jwt-valido") is None


def test_decode_access_token_con_firma_incorrecta_devuelve_none():
    """
    Un token firmado con OTRA clave secreta -- simula un token
    falsificado o de otro entorno -- debe ser rechazado.
    """
    token_falso = jose_jwt.encode(
        {"sub": "1", "restaurant_id": "1", "role": "ADMIN",
         "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "clave-secreta-incorrecta",
        algorithm=ALGORITHM,
    )

    assert decode_access_token(token_falso) is None


def test_decode_access_token_expirado_devuelve_none():
    """
    Construye a mano un token ya vencido (exp en el pasado) para
    confirmar que decode_access_token lo rechaza en vez de aceptarlo.
    """
    token_vencido = jose_jwt.encode(
        {
            "sub": "1",
            "restaurant_id": "1",
            "role": "ADMIN",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    assert decode_access_token(token_vencido) is None
