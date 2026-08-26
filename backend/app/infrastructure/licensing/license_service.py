import base64
import json

from datetime import date
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization


LICENSE_DIR = Path("/license")
LICENSE_FILE = LICENSE_DIR / "license.json"
MACHINE_ID_FILE = LICENSE_DIR / "machine-id"

PUBLIC_KEY_FILE = (
    Path(__file__).parent /
    "public_key.pem"
)


class LicenseError(RuntimeError):
    pass


class LicenseService:

    @staticmethod
    def _load_public_key():

        return serialization.load_pem_public_key(
            PUBLIC_KEY_FILE.read_bytes()
        )


    @staticmethod
    def _payload(
        license_data: dict
    ) -> bytes:

        data = {
            key: value
            for key, value in license_data.items()
            if key != "signature"
        }

        return json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":")
        ).encode("utf-8")


    @classmethod
    def validate(cls) -> None:

        if not MACHINE_ID_FILE.exists():
            raise LicenseError(
                "Machine ID not found"
            )

        if not LICENSE_FILE.exists():
            raise LicenseError(
                "License not found"
            )

        machine_id = (
            MACHINE_ID_FILE
            .read_text()
            .strip()
        )

        license_data = json.loads(
            LICENSE_FILE.read_text(
                encoding="utf-8"
            )
        )

        if license_data.get("product") != "marcha":
            raise LicenseError(
                "Invalid product license"
            )

        if license_data.get("machine_id") != machine_id:
            raise LicenseError(
                "License belongs to another machine"
            )

        expires_at = license_data.get(
            "expires_at"
        )

        if expires_at:
            if date.fromisoformat(expires_at) < date.today():
                raise LicenseError(
                    "License expired"
                )

        signature = base64.b64decode(
            license_data["signature"]
        )

        public_key = cls._load_public_key()

        try:
            public_key.verify(
                signature,
                cls._payload(
                    license_data
                )
            )

        except InvalidSignature as ex:
            raise LicenseError(
                "Invalid license signature"
            ) from ex