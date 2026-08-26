import base64
import json

from datetime import date
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization

from app.infrastructure.licensing.machine_fingerprint import (
    generate_machine_fingerprint
)


LICENSE_FILE = Path("/license/license.json")

PUBLIC_KEY_FILE = (
    Path(__file__).resolve().parent
    / "public_key.pem"
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
    def _serialize_payload(
        license_data: dict
    ) -> bytes:

        payload = {
            key: value
            for key, value in license_data.items()
            if key != "signature"
        }

        return json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False
        ).encode("utf-8")


    @classmethod
    def validate(cls) -> None:

        if not LICENSE_FILE.exists():
            raise LicenseError(
                "License file not found"
            )

        try:
            license_data = json.loads(
                LICENSE_FILE.read_text(
                    encoding="utf-8"
                )
            )

        except (
            OSError,
            json.JSONDecodeError
        ) as ex:
            raise LicenseError(
                "Invalid license file"
            ) from ex


        if license_data.get("product") != "marcha":
            raise LicenseError(
                "Invalid product license"
            )


        expected_machine_id = (
            generate_machine_fingerprint()
        )

        license_machine_id = (
            str(
                license_data.get(
                    "machine_id",
                    ""
                )
            )
            .strip()
            .lower()
        )


        if license_machine_id != expected_machine_id:
            raise LicenseError(
                "License belongs to another machine"
            )


        expires_at = license_data.get(
            "expires_at"
        )

        if expires_at:

            try:
                expiration_date = (
                    date.fromisoformat(
                        expires_at
                    )
                )

            except ValueError as ex:
                raise LicenseError(
                    "Invalid license expiration date"
                ) from ex

            if expiration_date < date.today():
                raise LicenseError(
                    "License expired"
                )


        signature_value = license_data.get(
            "signature"
        )

        if not isinstance(
            signature_value,
            str
        ):
            raise LicenseError(
                "License signature not found"
            )


        try:
            signature = base64.b64decode(
                signature_value,
                validate=True
            )

        except ValueError as ex:
            raise LicenseError(
                "Invalid license signature encoding"
            ) from ex


        public_key = (
            cls._load_public_key()
        )


        try:
            public_key.verify(
                signature,
                cls._serialize_payload(
                    license_data
                )
            )

        except InvalidSignature as ex:
            raise LicenseError(
                "Invalid license signature"
            ) from ex