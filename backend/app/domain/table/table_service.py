from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models import Table
from app.models.order import Order
from app.schemas.table import TablePositionUpdate

from app.domain.order.constants import ACTIVE_ORDER_STATUSES

from app.domain.errors.base import DomainError
from app.domain.errors.error_codes import ErrorCode

import logging

logger = logging.getLogger("app.domain.table")


class TableService:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Listar mesas
    # -------------------------

    def list_tables(self, restaurant_id: int, active: bool | None = True):
        query = self.db.query(Table).filter(
            Table.restaurant_id == restaurant_id
        )

        if active is not None:
            query = query.filter(Table.active == active)
        return query.order_by(Table.number).all()


    # -------------------------
    # Listar status de las mesas
    # -------------------------

    def list_tables_status(self, restaurant_id: int):

        active_order_subquery = (
            self.db.query(
                Order.table_id,
                func.max(Order.id).label("order_id")
            )
            .filter(
                Order.restaurant_id == restaurant_id,
                Order.status.in_(ACTIVE_ORDER_STATUSES)
            )
            .group_by(Order.table_id)
            .subquery()
        )
        rows = (
            self.db.query(
                Table.id,
                Table.number,
                Table.x,
                Table.y,
                Table.capacity,
                Table.shape,
                Table.active,
                Order.id.label("order_id"),
                Order.status.label("order_status")
            )
            .outerjoin(
                active_order_subquery,
                Table.id == active_order_subquery.c.table_id
            )
            .outerjoin(
                Order,
                Order.id == active_order_subquery.c.order_id
            )
            .filter(
                Table.restaurant_id == restaurant_id,
                Table.active.is_(True)
            )
            .order_by(Table.number)
            .all()
        )
        return [
            {
                "id": row.id,
                "number": row.number,
                "x": row.x,
                "y": row.y,
                "capacity": row.capacity,
                "shape": row.shape,
                "active": row.active,
                "status": "ocupada" if row.order_id else "libre",
                "order_id": row.order_id,
                "order_status": row.order_status
            }
            for row in rows
        ]

    # -------------------------
    # Devolver mesa
    # -------------------------        

    def _get_table(self, restaurant_id: int, table_id: int, active_only=False) -> Table:
        query = self.db.query(Table).filter(
            Table.id == table_id,
            Table.restaurant_id == restaurant_id
        )
        if active_only:
            query = query.filter(Table.active.is_(True))
        table = query.first()
        if not table:
            raise DomainError(
                "Table not found",
                code=ErrorCode.TABLE_NOT_FOUND,
                context={"table_id": table_id}
            )
        return table

    # -------------------------
    # Crear mesa
    # -------------------------

    def create_table(self, restaurant_id, table_in):
        new_number = table_in.number

        if new_number is None:
            max_number = self.db.query(func.max(Table.number)).filter(
                Table.restaurant_id == restaurant_id
            ).scalar()
            new_number = (max_number or 0) + 1

        if new_number <= 0:
            raise DomainError(
                "Table number must be greater than zero",
                code=ErrorCode.INVALID_OPERATION,
                context={"number": new_number}
            )

        existing = self.db.query(Table).filter(
            Table.restaurant_id == restaurant_id,
            Table.number == new_number
        ).first()
        if existing:
            raise DomainError(
                "Table number already exists",
                code=ErrorCode.TABLE_NUMBER_ALREADY_EXISTS,
                context={
                    "number": new_number,
                    "active": existing.active
                }
            )
        logger.info("Mesa creada r=%s number=%s", restaurant_id, new_number)
        table = Table(
            restaurant_id=restaurant_id,
            number=new_number,
            x=table_in.x,
            y=table_in.y,
            capacity=table_in.capacity,
            shape=table_in.shape
        )
        self.db.add(table)
        self.db.commit()
        self.db.refresh(table)
        return table

    # -------------------------
    # Actualizar mesa
    # -------------------------

    def update_table(self, restaurant_id, table_id, table_in):
        table = self._get_table(restaurant_id, table_id)
        update_data = table_in.model_dump(exclude_unset=True)

        new_number = update_data.get("number")
        if new_number is not None:
            if new_number <= 0:
                raise DomainError(
                    "Table number must be greater than zero",
                    code=ErrorCode.INVALID_OPERATION,
                    context={"number": new_number}
                )
            existing = self.db.query(Table).filter(
                Table.restaurant_id == restaurant_id,
                Table.number == new_number,
                Table.id != table_id
            ).first()
            if existing:
                raise DomainError(
                    "Table number already exists",
                    code=ErrorCode.TABLE_NUMBER_ALREADY_EXISTS,
                    context={
                        "number": new_number,
                        "active": existing.active
                    }
                )

        for field, value in update_data.items():
            setattr(table, field, value)
        self.db.commit()
        self.db.refresh(table)
        return table

    # -------------------------
    # Actualizar posición de la mesa
    # -------------------------

    def update_position(
        self,
        restaurant_id: int,
        table_id: int,
        data: TablePositionUpdate
    ) -> Table:
        table = self._get_table(restaurant_id, table_id, active_only=True)

        table.x = data.x
        table.y = data.y

        self.db.commit()
        self.db.refresh(table)
        return table

    # -------------------------
    # Desactivar mesa
    # -------------------------

    def deactivate_table(self, restaurant_id, table_id):
        table = self._get_table(restaurant_id, table_id, active_only=True)
        logger.info("Mesa desactivada r=%s table_id=%s", restaurant_id, table_id)
        table.active = False
        self.db.commit()
        return {"message": "Table deactivated"}

    # -------------------------
    # Activar mesa
    # -------------------------

    def activate_table(self, restaurant_id, table_id):
        table = self._get_table(restaurant_id, table_id)
        logger.info("Mesa activada r=%s table_id=%s", restaurant_id, table_id)
        table.active = True
        self.db.commit()
        return {"message": "Table activated"}    
    
    # -------------------------
    # Tocar mesa
    # -------------------------

    def touch_table(self, restaurant_id: int, table_id: int):
        table = self._get_table(restaurant_id, table_id, active_only=True)
        order = self.db.query(Order).filter(
            Order.table_id == table_id,
            Order.restaurant_id == restaurant_id,
            Order.status.in_(ACTIVE_ORDER_STATUSES)
        ).first()
        return {
            "table_id": table.id,
            "table_number": table.number,
            "order_id": order.id if order else None
        }
