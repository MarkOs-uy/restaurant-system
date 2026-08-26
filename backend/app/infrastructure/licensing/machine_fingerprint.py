import hashlib
from pathlib import Path


HOST_MACHINE_ID_PATH = Path(
    "/host/etc/machine-id"
)

HOST_PRODUCT_UUID_PATH = Path(
    "/host/product_uuid"
)


class MachineFingerprintError(RuntimeError):
    pass


def _read_identifier(
    path: Path
) -> str:

    if not path.exists():
        return ""

    return (
        path.read_text(
            encoding="utf-8"
        )
        .strip()
        .lower()
    )


def generate_machine_fingerprint() -> str:

    machine_id = _read_identifier(
        HOST_MACHINE_ID_PATH
    )

    product_uuid = _read_identifier(
        HOST_PRODUCT_UUID_PATH
    )

    if not machine_id and not product_uuid:
        raise MachineFingerprintError(
            "No se pudo obtener una identidad estable "
            "de la maquina host."
        )

    source = (
        f"{machine_id}|{product_uuid}"
    )

    return hashlib.sha256(
        source.encode("utf-8")
    ).hexdigest()