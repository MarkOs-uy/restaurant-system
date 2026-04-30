class DomainError(Exception):

    def __init__(
        self,
        message: str,
        code: str = "domain_error",
        context: dict | None = None
    ):
        self.message = message
        self.code = code
        self.context = context or {}
        super().__init__(message)