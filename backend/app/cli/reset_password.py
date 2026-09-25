"""
Restablecimiento de contraseña de usuarios desde línea de comandos.

Uso:

    python -m app.cli.reset_password \
        --restaurant-id 1 \
        --username admin

Los argumentos son opcionales. Si alguno no se proporciona,
el comando lo solicita interactivamente.

Este comando está pensado para recuperación administrativa local.

No expone ningún endpoint HTTP y debe ejecutarse únicamente
desde un entorno con acceso administrativo al backend.
"""

import argparse
import getpass
import sys

from sqlalchemy.exc import SQLAlchemyError

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.user import User


EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_INVALID_INPUT = 2
EXIT_CANCELLED = 3


def parse_args() -> argparse.Namespace:
    """
    Lee los argumentos opcionales de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description="Restablecer la contraseña de un usuario de Marcha."
    )

    parser.add_argument(
        "--restaurant-id",
        type=int,
        help="ID del restaurante al que pertenece el usuario.",
    )

    parser.add_argument(
        "--username",
        type=str,
        help="Nombre del usuario cuya contraseña se desea restablecer.",
    )

    return parser.parse_args()


def ask_restaurant_id(value: int | None) -> int:
    """
    Devuelve el restaurant_id recibido por argumento o lo solicita
    interactivamente si no fue proporcionado.
    """
    if value is not None:
        if value <= 0:
            raise ValueError("restaurant-id debe ser mayor que cero.")

        return value

    while True:
        raw_value = input("ID del restaurante: ").strip()

        try:
            restaurant_id = int(raw_value)

            if restaurant_id <= 0:
                raise ValueError

            return restaurant_id

        except ValueError:
            print(
                "El ID del restaurante debe ser un número entero mayor que cero."
            )


def ask_username(value: str | None) -> str:
    """
    Devuelve el username recibido por argumento o lo solicita
    interactivamente si no fue proporcionado.
    """
    if value is not None:
        username = value.strip()

        if not username:
            raise ValueError("El nombre de usuario no puede estar vacío.")

        return username

    while True:
        username = input("Usuario: ").strip()

        if username:
            return username

        print("El nombre de usuario no puede estar vacío.")


def find_user(
    db,
    restaurant_id: int,
    username: str,
) -> User | None:
    """
    Busca al usuario dentro del restaurante indicado.

    Es importante filtrar simultáneamente por restaurant_id y username
    para respetar el aislamiento multi-tenant.
    """
    return (
        db.query(User)
        .filter(
            User.restaurant_id == restaurant_id,
            User.username == username,
        )
        .first()
    )


def print_user_summary(user: User) -> None:
    """
    Muestra información suficiente para que el operador confirme
    que está modificando al usuario correcto.
    """
    print()
    print("Usuario encontrado:")
    print(f"  ID:          {user.id}")
    print(f"  Usuario:     {user.username}")
    print(f"  Restaurante: {user.restaurant_id}")
    print(f"  Rol:         {user.role.value}")

    if hasattr(user, "active") and not user.active:
        print()
        print("ADVERTENCIA:")
        print("  Este usuario está desactivado.")
        print("  La contraseña puede modificarse, pero el usuario")
        print("  continuará sin poder iniciar sesión mientras siga inactivo.")


def confirm_reset() -> bool:
    """
    Solicita confirmación explícita antes de modificar la contraseña.

    Por seguridad, cualquier respuesta distinta de 's' o 'si'
    se interpreta como cancelación.
    """
    print()

    answer = input(
        "¿Desea restablecer la contraseña de este usuario? [s/N]: "
    ).strip().lower()

    return answer in {"s", "si", "sí"}


def ask_new_password() -> str:
    """
    Solicita la nueva contraseña dos veces sin mostrarla en pantalla.
    """
    while True:
        password = getpass.getpass("Nueva contraseña: ")

        if not password:
            print("La contraseña no puede estar vacía.")
            continue

        confirmation = getpass.getpass("Confirmar contraseña: ")

        if password != confirmation:
            print("Las contraseñas no coinciden.")
            print("Intente nuevamente.")
            print()
            continue

        return password


def reset_user_password(
    db,
    user: User,
    new_password: str,
) -> None:
    """
    Actualiza únicamente el hash de contraseña del usuario.

    No modifica:
    - role
    - restaurant_id
    - active
    - ningún otro atributo del usuario
    """
    user.password_hash = get_password_hash(new_password)

    db.commit()
    db.refresh(user)


def main() -> None:
    args = parse_args()

    try:
        restaurant_id = ask_restaurant_id(args.restaurant_id)
        username = ask_username(args.username)

    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(EXIT_INVALID_INPUT)

    db = SessionLocal()

    try:
        user = find_user(
            db=db,
            restaurant_id=restaurant_id,
            username=username,
        )

        if user is None:
            print()
            print(
                f'ERROR: no existe el usuario "{username}" '
                f"en el restaurante {restaurant_id}.",
                file=sys.stderr,
            )
            sys.exit(EXIT_INVALID_INPUT)

        print_user_summary(user)

        if not confirm_reset():
            print()
            print("Operación cancelada. No se realizaron cambios.")
            sys.exit(EXIT_CANCELLED)

        print()

        new_password = ask_new_password()

        reset_user_password(
            db=db,
            user=user,
            new_password=new_password,
        )

        print()
        print("Contraseña restablecida correctamente.")
        print()
        print("El usuario puede iniciar sesión con la nueva contraseña.")

        if hasattr(user, "active") and not user.active:
            print()
            print(
                "IMPORTANTE: el usuario continúa desactivado "
                "y no podrá iniciar sesión hasta ser reactivado."
            )

        sys.exit(EXIT_SUCCESS)

    except SQLAlchemyError as exc:
        db.rollback()

        print()
        print(
            "ERROR: no se pudo actualizar la contraseña.",
            file=sys.stderr,
        )
        print(
            f"Detalle técnico: {exc}",
            file=sys.stderr,
        )

        sys.exit(EXIT_ERROR)

    finally:
        db.close()


if __name__ == "__main__":
    main()