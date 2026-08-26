import os

from app.infrastructure.licensing.license_service import (
    LicenseService
)


def main() -> None:

    environment = os.getenv(
        "ENVIRONMENT",
        "production"
    ).lower()

    if environment == "development":
        print(
            "Entorno de desarrollo: "
            "validacion de licencia omitida"
        )
        return

    LicenseService.validate()

    print("Licencia valida")


if __name__ == "__main__":
    main()