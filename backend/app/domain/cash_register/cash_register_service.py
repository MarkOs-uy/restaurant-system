from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.cash_register import CashRegister
from app.models.payment import Payment
from app.models.cash_movement import CashMovement
from app.models.order import Order, OrderStatus
from app.models.payment import PaymentMethod
from app.models.cash_movement import CashMovementType

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode
from app.core.serialization import decimal_dict_to_float


class CashRegisterService:

    def __init__(self, db: Session):
        self.db = db


    def _get_open_cash_register(
        self,
        restaurant_id: int,
        for_update: bool = False
    ):

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


    def _calculate_sales(self, cash_register_id: int):
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


    def _calculate_payment_breakdown(self, cash_register_id: int):
        rows = self.db.query(
            Payment.method,
            func.sum(Payment.amount)
        ).filter(
            Payment.cash_register_id == cash_register_id
        ).group_by(
            Payment.method
        ).all()
        return {
            method.value: total or Decimal("0")
            for method, total in rows
        }


    def _calculate_cash_movements(self, cash_register_id: int):
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


    def open_cash_register(
        self,
        restaurant_id: int,
        user_id: int,
        opening_amount: Decimal
    ):
        existing = self.db.query(CashRegister).filter(
            CashRegister.restaurant_id == restaurant_id,
            CashRegister.is_open == True
        ).first()
        if existing:
            raise DomainError(
                "Cash register already open", 
                ErrorCode.CASH_REGISTER_ALREADY_OPEN
                )
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


    def close_cash_register(
        self,
        restaurant_id: int,
        user_id: int,
        counted_cash: Decimal
    ):

        cash_register = self._get_open_cash_register(
            restaurant_id,
            for_update=True
        )

        open_orders = self.db.query(Order).filter(
            Order.restaurant_id == restaurant_id,
            Order.status.notin_([OrderStatus.CLOSED, OrderStatus.CANCELLED])
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

        difference = counted_cash - expected_cash

        cash_register.closed_at = func.now()
        cash_register.closed_by_id = user_id
        cash_register.is_open = False
        cash_register.total_sales = total_sales
        cash_register.expected_cash = expected_cash
        cash_register.counted_cash = counted_cash
        cash_register.difference = difference
        cash_register.payments_snapshot = decimal_dict_to_float(payment_breakdown)

        self.db.commit()

        return {
            "message": "Caja cerrada",
            "opening_amount": cash_register.opening_amount,
            "total_sales": total_sales,
            "orders_count": orders_count,
            "transactions_count": transactions_count,
            "average_ticket": average_ticket,
            "by_method": payment_breakdown,
            "cash_in": cash_in,
            "cash_out": cash_out,
            "expected_cash": expected_cash,
            "counted_cash": counted_cash,
            "difference": difference
        }


    def get_current_cash_register(self, restaurant_id: int):
        cash_register = self._get_open_cash_register(restaurant_id)
        total_sales, transactions_count, orders_count, average_ticket = self._calculate_sales(
            cash_register.id
        )
        by_method = self._calculate_payment_breakdown(
            cash_register.id
        )
        return {
            "cash_register_id": cash_register.id,
            "opened_at": cash_register.opened_at,
            "total_sales": total_sales,
            "orders_count": orders_count,
            "transactions_count": transactions_count,
            "average_ticket": average_ticket,
            "by_method": by_method
        }


    def require_open_cash_register(self, restaurant_id: int):
        return self._get_open_cash_register(restaurant_id)


    def get_dashboard(self, restaurant_id: int):

        cash_register = self._get_open_cash_register(restaurant_id)
        print("DEBUG cash_register:", cash_register.id)
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
        print("DEBUG dashboard:", {
            "opening_amount": cash_register.opening_amount,
            "total_sales": total_sales,
            "orders_count": orders_count
        })
        return {
            "cash_register_id": cash_register.id,
            "opened_at": cash_register.opened_at,
            "opening_amount": cash_register.opening_amount,
            "total_sales": total_sales,
            "orders_count": orders_count,
            "transactions_count": transactions_count,
            "average_ticket": average_ticket,
            "by_method": by_method,
            "cash_movements": movements_list,
            "expected_cash": expected_cash
        }