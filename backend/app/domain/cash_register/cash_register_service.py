from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal

from app.models.cash_register import CashRegister
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentMethod
from app.models.cash_movement import CashMovementType
from app.domain.cash_register.cash_movement_service import CashMovement
from app.domain.errors import CashRegisterDomainError


class CashRegisterService:

    def open_cash_register(
        self,
        db: Session,
        restaurant_id: int,
        user_id: int,
        opening_amount: Decimal
    ):
        existing = db.query(CashRegister).filter(
            CashRegister.restaurant_id == restaurant_id,
            CashRegister.is_open == True
        ).first()

        if existing:
            raise CashRegisterDomainError("Ya hay una caja abierta", 
                code="cash_register_already_open")

        cash_register = CashRegister(
            restaurant_id=restaurant_id,
            opened_by_id=user_id,
            opening_amount=opening_amount,
            is_open=True
        )

        db.add(cash_register)
        db.commit()
        db.refresh(cash_register)

        return cash_register


    def close_cash_register(
        self,
        db: Session,
        restaurant_id: int,
        user_id: int,
        counted_cash: Decimal
    ):

        cash_register = db.query(CashRegister).filter(
            CashRegister.restaurant_id == restaurant_id,
            CashRegister.is_open == True
        ).with_for_update().first()

        if not cash_register:
            raise CashRegisterDomainError("No hay caja abierta",
                code="not_cash_register_open")
        
        if not cash_register.is_open:
            raise CashRegisterDomainError("La caja ya está cerrada")

        # 🚨 verificar órdenes abiertas
        open_orders = db.query(Order).filter(
            Order.restaurant_id == restaurant_id,
            Order.status.notin_([OrderStatus.CLOSED, OrderStatus.CANCELLED])
        ).count()

        if open_orders > 0:
            raise CashRegisterDomainError(
                "No se puede cerrar caja: hay órdenes abiertas",
                code="cant_close_cash_register_orders_already_open"
            )

        if counted_cash < 0:
            raise CashRegisterDomainError("El monto contado es inválido")

        total_sales = db.query(
            func.coalesce(func.sum(Payment.amount), 0)
        ).filter(
            Payment.cash_register_id == cash_register.id
        ).scalar()

        transactions_count = db.query(
            func.count(Payment.id)
        ).filter(
            Payment.cash_register_id == cash_register.id
        ).scalar()

        payments = db.query(
            Payment.method,
            func.sum(Payment.amount)
        ).filter(
            Payment.cash_register_id == cash_register.id
        ).group_by(
            Payment.method
        ).all()

        payment_breakdown = {
            method.value if hasattr(method, "value") else method: float(total)
            for method, total in payments
        }

        cash_sales = payment_breakdown.get(PaymentMethod.CASH.value, 0)
        cash_sales = Decimal(str(cash_sales))

        # movimientos de caja
        movements = db.query(
            CashMovement.type,
            func.sum(CashMovement.amount)
        ).filter(
            CashMovement.cash_register_id == cash_register.id
        ).group_by(
            CashMovement.type
        ).all()

        cash_in = Decimal("0")
        cash_out = Decimal("0")

        for mtype, total in movements:
            if mtype == CashMovementType.CASH_IN:
                cash_in = total or Decimal("0")
            else:
                cash_out = total or Decimal("0")

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
        cash_register.payments_snapshot = payment_breakdown

        db.commit()

        return {
            "message": "Caja cerrada",
            "total_sales": float(total_sales),
            "transactions_count": transactions_count,
            "by_method": payment_breakdown,
            "opening_amount": float(cash_register.opening_amount),
            "cash_in": float(cash_in),
            "cash_out": float(cash_out),
            "expected_cash": float(expected_cash),
            "counted_cash": float(counted_cash),
            "difference": float(difference)
        }


    def get_current_cash_register(
        self,
        db: Session,
        restaurant_id: int
    ):
        cash_register = db.query(CashRegister).filter(
            CashRegister.is_open == True,
            CashRegister.restaurant_id == restaurant_id
        ).first()

        if not cash_register:
            return None

        total_sales = db.query(
            func.coalesce(func.sum(Payment.amount), 0)
        ).filter(
            Payment.cash_register_id == cash_register.id
        ).scalar()

        orders_count = db.query(
            func.count(func.distinct(Payment.order_id))
        ).filter(
            Payment.cash_register_id == cash_register.id
        ).scalar()

        average_ticket = (
            total_sales / orders_count
            if orders_count > 0
            else Decimal("0")
        )

        rows = db.query(
            Payment.method,
            func.sum(Payment.amount)
        ).filter(
            Payment.cash_register_id == cash_register.id
        ).group_by(
            Payment.method
        ).all()

        return {
            "cash_register_id": cash_register.id,
            "opened_at": cash_register.opened_at,
            "total_sales": float(total_sales),
            "orders_count": orders_count,
            "average_ticket": float(average_ticket),
            "by_method": {
                method.value: float(amount)
                for method, amount in rows
            }
        }


    def require_open_cash_register(self, db: Session, restaurant_id: int):
        cash_register = db.query(CashRegister).filter(
            CashRegister.restaurant_id == restaurant_id,
            CashRegister.is_open == True
        ).first()

        if not cash_register:
            raise CashRegisterDomainError("No hay caja abierta")

        return cash_register


    def get_dashboard(
        self,
        db: Session,
        restaurant_id: int
    ):
        cash_register = db.query(CashRegister).filter(
            CashRegister.restaurant_id == restaurant_id,
            CashRegister.is_open == True
        ).first()

        if not cash_register:
            return None

        total_sales = db.query(
            func.coalesce(func.sum(Payment.amount), 0)
        ).filter(
            Payment.cash_register_id == cash_register.id
        ).scalar()

        orders_count = db.query(
            func.count(func.distinct(Payment.order_id))
        ).filter(
            Payment.cash_register_id == cash_register.id
        ).scalar()

        average_ticket = (
            total_sales / orders_count
            if orders_count
            else Decimal("0")
        )

        rows = db.query(
            Payment.method,
            func.sum(Payment.amount)
        ).filter(
            Payment.cash_register_id == cash_register.id
        ).group_by(
            Payment.method
        ).all()

        by_method = {
            method.value: float(amount)
            for method, amount in rows
        }

        movements = db.query(CashMovement).filter(
            CashMovement.cash_register_id == cash_register.id
        ).order_by(
            CashMovement.created_at.desc()
        ).all()

        movements_list = [
            {
                "id": m.id,
                "type": m.type,
                "amount": float(m.amount),
                "reason": m.reason,
                "created_at": m.created_at
            }
            for m in movements
        ]

        cash_sales = Decimal(by_method.get("CASH", 0))

        cash_in = Decimal(db.query(
            func.coalesce(func.sum(CashMovement.amount), 0)
        ).filter(
            CashMovement.cash_register_id == cash_register.id,
            CashMovement.type == "cash_in"
        ).scalar())

        cash_out = Decimal(db.query(
            func.coalesce(func.sum(CashMovement.amount), 0)
        ).filter(
            CashMovement.cash_register_id == cash_register.id,
            CashMovement.type == "cash_out"
        ).scalar())

        expected_cash = (
            cash_register.opening_amount
            + cash_sales
            + cash_in
            - cash_out
        )

        return {
            "cash_register_id": cash_register.id,
            "opened_at": cash_register.opened_at,
            "opening_amount": Decimal(cash_register.opening_amount),
            "total_sales": Decimal(total_sales),
            "orders_count": orders_count,
            "average_ticket": Decimal(average_ticket),
            "by_method": by_method,
            "cash_movements": movements_list,
            "expected_cash": Decimal(expected_cash)
        }