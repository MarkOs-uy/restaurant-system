import re

from pydantic import SecretStr, ConfigDict, field_validator

from .base import BaseSchema
from app.models.user import UserRole

USERNAME_RE = re.compile(r"^[a-z0-9_.-]+$")

class UserCreate(BaseSchema):
    username: str
    password: SecretStr
    role: UserRole

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.lower()
        if not USERNAME_RE.fullmatch(value):
            raise ValueError(
                "Username may only contain lowercase letters, numbers, '.', '-' and '_'."
            )
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        password = value.get_secret_value()
        if len(password) < 4:
            raise ValueError("Password must contain at least 4 characters.")
        return value


class UserUpdate(BaseSchema):
    username: str | None = None
    password: SecretStr | None = None
    role: UserRole | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.lower()
        if not USERNAME_RE.fullmatch(value):
            raise ValueError(
                "Username may only contain lowercase letters, numbers, '.', '-' and '_'."
            )
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr | None) -> SecretStr | None:
        if value is None:
            return None
        password = value.get_secret_value()
        if len(password) < 4:
            raise ValueError("Password must contain at least 4 characters.")
        return value

class UserOut(BaseSchema):
    id: int
    username: str
    role: UserRole
    active: bool