from typing import Any

class DomainError(Exception):

    message: str
    code: str
    context: dict[str, Any]

    def __init__(
        self,
        message: str,
        code: str = "domain_error",
        *,
        context: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.context = context or {}
        super().__init__(message)