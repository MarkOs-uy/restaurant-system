import logging

from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.core.serialization import decimal_dict_to_float

from app.utils.money import money

from app.models.cash_register import CashRegister
from app.models.payment import Payment
from app.models.cash_movement import CashMovement
from app.models.order import Order, OrderStatus
from app.models.payment import PaymentMethod
from app.models.cash_movement import CashMovementType

from app.schemas.cash_register import (
    CashRegisterClose,
    CashRegisterCloseOut,
    CashRegisterSummary,
    CashRegisterDashboard
)

logger = logging.getLogger("app.domain.cash_register")

class CashRegisterService:

    """
    Servicio encargado de la lógica de negocio relacionada con la caja registradora.

    Responsabilidades:
    - Gestionar la lógica de negocio de la caja registradora.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # --------------------------------------------------------------------------------
    # Método de cálculo de ventas realizadas por caja registradora
    # --------------------------------------------------------------------------------
    def _calculate_sales(self, cash_register_id: int) -> tuple[
        Decimal,
        int,
        int,
        Decimal
    ]:
        total_sales = self.db.query(
            func.coalesce(func.sum(Payment.amount), 0)
        ).filter(
            Payment.cash_register_id == cash_register_id
        ).scalar()
        transactions_count = self.db.query(
            func.count(Payment.id)
        ).filter(
            Payment.cash_register_id == cash_register_id
        ).scalar()
        orders_count = self.db.query(
            func.count(func.distinct(Payment.order_id))
        ).filter(
            Payment.cash_register_id == cash_register_id
        ).scalar()
        average_ticket = (
            total_sales / orders_count
            if orders_count
            else Decimal("0")
        )
        return total_sales, transactions_count, orders_count, average_ticket

    # --------------------------------------------------------------------------------
    # Sumar pagos por método de pago
    # --------------------------------------------------------------------------------
    def _calculate_payment_breakdown(self, cash_register_id: int) -> dict[str, Decimal]:
        breakdown = {
            method.value: Decimal("0")
            for method in PaymentMethod
        }
        rows = self.db.query(
            Payment.method,
            func.sum(Payment.amount)
        ).filter(
            Payment.cash_register_id == cash_register_id
        ).group_by(
            Payment.method
        ).all()
        for method, total in rows:
            breakdown[method.value] = total or Decimal("0")
        return breakdown

    # --------------------------------------------------------------------------------
    # Calcular movimientos de caja agrupados por entradas y salidas
    # --------------------------------------------------------------------------------
    def _calculate_cash_movements(self, cash_register_id: int) -> tuple[Decimal, Decimal]:
        rows = self.db.query(
            CashMovement.type,
            func.sum(CashMovement.amount)
        ).filter(
            CashMovement.cash_register_id == cash_register_id
        ).group_by(
            CashMovement.type
        ).all()
        cash_in = Decimal("0")
        cash_out = Decimal("0")
        for mtype, total in rows:
            if mtype == CashMovementType.CASH_IN:
                cash_in += total or Decimal("0")
            elif mtype == CashMovementType.CASH_OUT:
                cash_out += total or Decimal("0")
        return cash_in, cash_out

    # --------------------------------------------------------------------------------
    # Abrir Caja
    # --------------------------------------------------------------------------------
    def open_cash_register(
        self,
        restaurant_id: int,
        user_id: int,
        opening_amount: Decimal
    ) -> CashRegister:
        if opening_amount < Decimal("0"):
            raise DomainError(
                "opening amount must be greater than or equal to zero",
                ErrorCode.INVALID_OPERATION,
                context={"opening_amount": money(opening_amount)}
            )
        existing = self.db.query(CashRegister).filter(
            CashRegister.restaurant_id == restaurant_id,
            CashRegister.is_open == True
        ).first()
        if existing:
            raise DomainError(
                "Cash register already open", 
                ErrorCode.CASH_REGISTER_ALREADY_OPEN
                )
        logger.info("Caja abierta r=%s user=%s amount=%s", restaurant_id, user_id, opening_amount)
        cash_register = CashRegister(
            restaurant_id=restaurant_id,
            opened_by_id=user_id,
            opening_amount=opening_amount,
            is_open=True
        )
        self.db.add(cash_register)
        self.db.commit()
        self.db.refresh(cash_register)
        return cash_register

    # --------------------------------------------------------------------------------
    # Obtener una caja registradora abierta o lanzar DomainError si no existe
    # --------------------------------------------------------------------------------
    def get_open_cash_register(
        self,
        restaurant_id: int,
        for_update: bool = False
    ) -> CashRegister:
        query = self.db.query(CashRegister).filter(
            CashRegister.restaurant_id == restaurant_id,
            CashRegister.is_open == True
        )
        if for_update:
            query = query.with_for_update()
        cash_register = query.first()
        if not cash_register:
            raise DomainError(
                "cash register not open",
                ErrorCode.CASH_REGISTER_NOT_OPEN
            )
        return cash_register
    
    # --------------------------------------------------------------------------------
    # Cerrar caja
    # --------------------------------------------------------------------------------
    def close_cash_register(
        self,
        restaurant_id: int,
        user_id: int,
        data: CashRegisterClose
    ) -> CashRegisterCloseOut:
        if data.counted_cash < Decimal("0"):
            raise DomainError(
                "counted cash must be greater than or equal to zero",
                ErrorCode.CASH_REGISTER_INVALID_COUNT,
                context={"counted_cash": money(data.counted_cash)}
            )
        cash_register = self.get_open_cash_register(
            restaurant_id,
            for_update=True
        )
        open_orders = self.db.query(Order).filter(
            Order.restaurant_id == restaurant_id,
            Order.status.notin_([OrderStatus.CLOSED, OrderStatus.CANCELLED, OrderStatus.DRAFT])
        ).count()
        if open_orders > 0:
            raise DomainError(
                "cannot close cash register: there are open orders",
                ErrorCode.CASH_REGISTER_PENDING_ORDERS
            )
        total_sales, transactions_count, orders_count, average_ticket = self._calculate_sales(
            cash_register.id
        )
        payment_breakdown = self._calculate_payment_breakdown(
            cash_register.id
        )
        cash_sales = payment_breakdown.get(
            PaymentMethod.CASH.value,
            Decimal("0")
        )
        cash_in, cash_out = self._calculate_cash_movements(
            cash_register.id
        )
        expected_cash = (
            cash_register.opening_amount
            + cash_sales
            + cash_in
            - cash_out
        )
        closing_amount = (
            cash_register.opening_amount
            + total_sales
            + cash_in
            - cash_out
        )

        difference = data.counted_cash - expected_cash

        cash_register.closed_at = func.now()
        cash_register.closed_by_id = user_id
        cash_register.is_open = False
        cash_register.total_sales = total_sales
        cash_register.closing_amount = closing_amount
        cash_register.expected_cash = expected_cash
        cash_register.counted_cash = data.counted_cash
        cash_register.difference = difference
        cash_register.payments_snapshot = decimal_dict_to_float(payment_breakdown)
        logger.info("Caja cerrada r=%s user=%s difference=%s", restaurant_id, user_id, difference)
        self.db.commit()
        return CashRegisterCloseOut(
            message="Caja cerrada",
            opening_amount=cash_register.opening_amount,
            closing_amount=cash_register.closing_amount,
            total_sales=total_sales,
            orders_count=orders_count,
            transactions_count=transactions_count,
            average_ticket=average_ticket,
            by_method=payment_breakdown,
            cash_in=cash_in,
            cash_out=cash_out,
            expected_cash=expected_cash,
            counted_cash=data.counted_cash,
            difference=difference
        )

    # --------------------------------------------------------------------------------
    # Devolver caja registradora actual
    # --------------------------------------------------------------------------------
    def get_current_cash_register(self, restaurant_id: int) -> CashRegisterSummary:
        cash_register = self.get_open_cash_register(restaurant_id)
        total_sales, transactions_count, orders_count, average_ticket = self._calculate_sales(
            cash_register.id
        )
        by_method = self._calculate_payment_breakdown(
            cash_register.id
        )
        return CashRegisterSummary(
            cash_register_id=cash_register.id,
            opened_at=cash_register.opened_at,
            total_sales=total_sales,
            orders_count=orders_count,
            transactions_count=transactions_count,
            average_ticket=average_ticket,
            by_method=by_method
        )

    # --------------------------------------------------------------------------------
    # Devolver dashboard
    # --------------------------------------------------------------------------------
    def get_dashboard(self, restaurant_id: int) -> CashRegisterDashboard:
        cash_register = self.get_open_cash_register(restaurant_id)
        logger.debug("get_dashboard cash_register_id=%s", cash_register.id)
        total_sales, transactions_count, orders_count, average_ticket = self._calculate_sales(
            cash_register.id
        )
        by_method = self._calculate_payment_breakdown(
            cash_register.id
        )
        cash_in, cash_out = self._calculate_cash_movements(
            cash_register.id
        )
        cash_sales = by_method.get(
            PaymentMethod.CASH.value,
            Decimal("0")
        )
        expected_cash = (
            cash_register.opening_amount
            + cash_sales
            + cash_in
            - cash_out
        )
        movements = self.db.query(CashMovement).filter(
            CashMovement.cash_register_id == cash_register.id
        ).order_by(
            CashMovement.created_at.desc()
        ).all()
        movements_list = [
            {
                "id": m.id,
                "type": m.type,
                "amount": m.amount,
                "reason": m.reason,
                "created_at": m.created_at
            }
            for m in movements
        ]
        logger.debug(
            "get_dashboard r=%s opening=%s sales=%s orders=%s",
            cash_register.restaurant_id,
            cash_register.opening_amount,
            total_sales,
            orders_count
        )
        return CashRegisterDashboard(
            cash_register_id=cash_register.id,
            opened_at=cash_register.opened_at,
            opening_amount=cash_register.opening_amount,
            total_sales=total_sales,
            orders_count=orders_count,
            transactions_count=transactions_count,
            average_ticket=average_ticket,
            by_method=by_method,
            cash_movements=movements_list,
            expected_cash=expected_cash
        )