from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException

from app.models import Table
from app.models.order import Order, OrderStatus
from app.schemas.table import TableStatus


class TableService:

    def __init__(self, db: Session):
        self.db = db


def list_tables(self, restaurant_id: int, active: bool | None = True):

    query = self.db.query(Table).filter(
        Table.restaurant_id == restaurant_id
    )

    if active is not None:
        query = query.filter(Table.active == active)

    return query.order_by(Table.number).all()


def list_tables_status(self, restaurant_id: int):

    active_status = [
        OrderStatus.DRAFT,
        OrderStatus.OPEN,
        OrderStatus.SENT,
        OrderStatus.IN_PROGRESS,
        OrderStatus.READY
    ]

    # 🔹 Subquery: una sola orden activa por mesa
    active_order_subquery = (
        self.db.query(
            Order.table_id,
            func.max(Order.id).label("order_id")
        )
        .filter(
            Order.restaurant_id == restaurant_id,
            Order.status.in_(active_status)
        )
        .group_by(Order.table_id)
    ).subquery()

    rows = (
        self.db.query(
            Table.id,
            Table.number,
            Table.x,
            Table.y,
            Table.capacity,
            Table.shape,
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
            Table.active == True
        )
        .order_by(Table.number)
        .all()
    )

    result = []

    for row in rows:
        result.append({
            "id": row.id,
            "number": row.number,
            "x": row.x,
            "y": row.y,
            "capacity": row.capacity,
            "shape": row.shape,
            "status": "occupied" if row.order_id else "free",
            "order_id": row.order_id,
            "order_status": row.order_status
        })

    return result
    
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from app.models.table import Table


class TableService:

    def __init__(self, db: Session):
        self.db = db


    def _get_table(self, restaurant_id: int, table_id: int, active_only=False) -> Table:

        query = self.db.query(Table).filter(
            Table.id == table_id,
            Table.restaurant_id == restaurant_id
        )

        if active_only:
            query = query.filter(Table.active == True)

        table = query.first()

        if not table:
            raise HTTPException(404, "Table not found")

        return table


    def create_table(self, restaurant_id, table_in):

        max_number = self.db.query(func.max(Table.number)).filter(
            Table.restaurant_id == restaurant_id
        ).scalar()

        new_number = (max_number or 0) + 1

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


    def update_table(self, restaurant_id, table_id, table_in):

        table = self._get_table(restaurant_id, table_id, active_only=True)

        update_data = table_in.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(table, field, value)

        self.db.commit()
        self.db.refresh(table)

        return table


    def update_position(self, restaurant_id, table_id, x, y):

        table = self._get_table(restaurant_id, table_id, active_only=True)

        table.x = x
        table.y = y

        self.db.commit()

        return {"success": True}


    def deactivate_table(self, restaurant_id, table_id):

        table = self._get_table(restaurant_id, table_id, active_only=True)

        table.active = False

        self.db.commit()

        return {"message": "Mesa desactivada"}


    def activate_table(self, restaurant_id, table_id):

        table = self._get_table(restaurant_id, table_id, active_only=True)

        table.active = True

        self.db.commit()

        return {"message": "Mesa activada"}    