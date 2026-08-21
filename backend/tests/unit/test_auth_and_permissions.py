"""
tests/unit/test_auth_and_permissions.py

Fase 3 (P1) del plan de testing: authenticate_token (dependencies/auth.py)
y require_roles (dependencies/permissions.py).

Estos tests protegen el activo más crítico de un sistema multi-tenant:
que un usuario nunca pueda autenticarse "cruzado" contra otro restaurante.

Correr con: docker compose exec backend pytest tests/unit/test_auth_and_permissions.py -v
"""

import pytest
from app.core.security import create_access_token
from app.dependencies.auth import authenticate_token
from app.dependencies.permissions import require_roles
from app.domain.errors.base import DomainError
from app.models.user import UserRole


# --------------------------------------------------------------------------------
# authenticate_token
# --------------------------------------------------------------------------------

def test_authenticate_token_rechaza_token_invalido(db):
    with pytest.raises(DomainError):
        authenticate_token(db=db, token="esto-no-es-un-token")


def test_authenticate_token_rechaza_payload_incompleto(db):
    """
    Token válido y bien firmado, pero le falta 'restaurant_id' --
    debe rechazarse en vez de reventar con un KeyError sin controlar.
    """
    token = create_access_token({"sub": "1", "role": "ADMIN"})

    with pytest.raises(DomainError):
        authenticate_token(db=db, token=token)


def test_authenticate_token_rechaza_usuario_inexistente(db, restaurant):
    token = create_access_token({
        "sub": "99999",  # no existe en la DB
        "restaurant_id": str(restaurant.id),
        "role": "ADMIN",
    })

    with pytest.raises(DomainError):
        authenticate_token(db=db, token=token)


def test_authenticate_token_rechaza_usuario_inactivo(db, restaurant, user):
    user.active = False
    db.commit()

    token = create_access_token({
        "sub": str(user.id),
        "restaurant_id": str(restaurant.id),
        "role": user.role.value,
    })

    with pytest.raises(DomainError):
        authenticate_token(db=db, token=token)


def test_authenticate_token_rechaza_rol_desactualizado(db, restaurant, user):
    """
    El token dice CASHIER (el rol que tenía al loguearse), pero en DB
    ahora el usuario es ADMIN (alguien le cambió el rol después). Debe
    rechazarse -- fuerza a repetir login en vez de operar con un rol
    que ya no es el real.
    """
    token = create_access_token({
        "sub": str(user.id),
        "restaurant_id": str(restaurant.id),
        "role": "CASHIER",  # rol viejo, embebido en el token
    })
    user.role = UserRole.ADMIN  # el rol real cambió en DB
    db.commit()

    with pytest.raises(DomainError):
        authenticate_token(db=db, token=token)


def test_authenticate_token_rechaza_restaurant_id_cruzado(db, restaurant, user):
    """
    CRÍTICO -- aislamiento multi-tenant.

    El token tiene el user_id correcto pero un restaurant_id de OTRO
    restaurante. La query de authenticate_token filtra por
    (User.id == user_id AND User.restaurant_id == restaurant_id), así
    que este intento de "cruzar" tenants debe fallar como si el
    usuario no existiera -- nunca debe devolver el User real.
    """
    token = create_access_token({
        "sub": str(user.id),
        "restaurant_id": "999999",  # restaurante que no es el suyo
        "role": user.role.value,
    })

    with pytest.raises(DomainError):
        authenticate_token(db=db, token=token)


def test_authenticate_token_devuelve_el_usuario_con_token_valido(db, restaurant, user):
    token = create_access_token({
        "sub": str(user.id),
        "restaurant_id": str(restaurant.id),
        "role": user.role.value,
    })

    resultado = authenticate_token(db=db, token=token)

    assert resultado.id == user.id
    assert resultado.restaurant_id == restaurant.id


# --------------------------------------------------------------------------------
# require_roles / role_checker
# --------------------------------------------------------------------------------

def test_require_roles_permite_rol_incluido(user):
    """
    role_checker es la función interna que devuelve require_roles().
    Se puede llamar directo pasándole el User -- FastAPI normalmente
    lo resuelve vía Depends(get_current_user), pero para testear la
    lógica de permisos no hace falta levantar ese mecanismo.
    """
    checker = require_roles(UserRole.CASHIER, UserRole.ADMIN)

    resultado = checker(user=user)

    assert resultado is user


def test_require_roles_rechaza_rol_no_incluido(user):
    checker = require_roles(UserRole.ADMIN)  # user (fixture) es CASHIER

    with pytest.raises(DomainError):
        checker(user=user)
