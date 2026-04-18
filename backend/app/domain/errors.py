class DomainError(Exception):

    def __init__(self, message: str, code: str = "domain_error", context: dict | None = None):
        self.message = message
        self.code = code
        self.context = context or {}
        super().__init__(message)


class CashRegisterDomainError(DomainError):
    pass


class PaymentDomainError(DomainError):
    pass


class OrderDomainError(DomainError):
    pass


class OrderItemDomainError(DomainError):
    pass


class ProductDomainError(DomainError):
    pass


class TableDomainError(DomainError):
    pass


class UserDomainError(DomainError):
    pass