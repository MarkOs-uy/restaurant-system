from datetime import date

from app.schemas.base import BaseSchema


class LicenseData(BaseSchema):
    product: str
    license_id: str
    customer: str
    machine_id: str
    issued_at: date
    expires_at: date | None = None
    signature: str