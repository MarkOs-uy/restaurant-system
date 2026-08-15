from sqlalchemy.orm import Session

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

from app.domain.cash_register.cash_register_service import CashRegisterService
from app.domain.events.websocket import WSEvent
from app.services.event_service import EventService

from app.utils.money import money

from app.models.cash_movement import CashMovement
from app.models.cash_register import CashRegister
from app.models.user import UserRole
from app.schemas.cash_register import CashMovementCreate


class CashMovementService:

    """
    Servicio encargado de la lógica de negocio relacionada con los movimientos de la caja registradora.

    Responsabilidades:
    - Gestionar la lógica de negocio de los movimientos de la caja registradora.
    - Validar las reglas de negocio.
    - Acceder a la base de datos mediante SQLAlchemy.
    - Lanzar DomainError cuando una operación no pueda completarse.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.events = EventService(db)

    # --------------------------------------------------------
    # Obtener movimiento de caja
    # --------------------------------------------------------
    def _get_cash_movement(
        self,
        restaurant_id: int,
        movement_id: int
    ) -> CashMovement:
        movement = (
            self.db.query(CashMovement)
            .join(
                CashRegister,
                CashMovement.cash_register_id == CashRegister.id
            )
            .filter(
                CashMovement.id == movement_id,
                CashRegister.restaurant_id == restaurant_id
            )
            .first()
        )
        if not movement:
            raise DomainError(
                "Movement not found",
                ErrorCode.CASH_MOVEMENT_NOT_FOUND
            )
        return movement

    # -------------------------
    # Crear movimiento de caja
    # -------------------------
    def create_cash_movement(
        self,
        restaurant_id: int,
        user_id: int,
        data: CashMovementCreate
    ) -> CashMovement:
        cash_register = CashRegisterService(self.db).get_open_cash_register(
            restaurant_id,
            for_update=True
        )
        movement = CashMovement(
            cash_register_id=cash_register.id,
            user_id=user_id,
            type=data.type,
            amount=data.amount,
            reason=data.reason
        )
        self.db.add(movement)
        self.db.flush()
        self.db.refresh(movement)
        self.events.emit(
            restaurant_id=restaurant_id,
            event_type=WSEvent.CASH_MOVEMENT_ADDED,
            payload={
                "movement": {
                    "id": movement.id,
                    "type": movement.type.value,
                    "amount": money(movement.amount),
                    "reason": movement.reason,
                    "created_at": movement.created_at.isoformat()
                }
            },
            target="role",
            target_id=UserRole.CASHIER.value
        )
        self.db.commit()
        return movement

    # ---------------------------------------------------------
    # Eliminar movimiento de caja
    # ---------------------------------------------------------
    def delete_cash_movement(
        self,
        restaurant_id: int,
        movement_id: int
    ) -> None:
        movement = self._get_cash_movement(restaurant_id, movement_id)
        amount = movement.amount
        movement_type = movement.type
        payload={
            "movement_id": movement_id,
            "amount": money(amount),
            "movement_type": movement_type.value
        }
        self.db.delete(movement)
        self.events.emit(
            restaurant_id=restaurant_id,
            event_type=WSEvent.CASH_MOVEMENT_DELETED,
            payload=payload,
            target="role",
            target_id=UserRole.CASHIER.value
        )
        self.db.commit()