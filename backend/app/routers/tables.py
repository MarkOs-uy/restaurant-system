from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload  # 🟢 AGREGADO

from app.db.session import get_db
from app.models import Table
from app.models.order import Order, OrderStatus

router = APIRouter(prefix="/tables", tags=["tables"])


@router.post("/{table_id}/touch")
def touch_table(table_id: int, db: Session = Depends(get_db)):

    table = db.query(Table).filter(
        Table.id == table_id,
        Table.active == True
    ).first()

    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    # 🔴 MODIFICADO → ahora también excluye CANCELLED
    order = db.query(Order).filter(
        Order.table_id == table_id,
        Order.status.notin_([
            OrderStatus.CLOSED,
            OrderStatus.CANCELLED
        ])
    ).first()

    # si no existe → crearlo
    if not order:
        order = Order(
            table_id=table_id,
            restaurant_id=table.restaurant_id,
            status=OrderStatus.OPEN  # 🟢 AGREGADO explícito
        )
        db.add(order)
        db.commit()
        db.refresh(order)

    return {
        "order_id": order.id,
        "table_number": table.number,
        "status": order.status
    }


# 🔥 ESTE ES EL ENDPOINT IMPORTANTE
@router.get("/")
def list_tables(db: Session = Depends(get_db)):

    tables = (
        db.query(Table)
        .options(joinedload(Table.orders))
        .filter(Table.active == True)
        .order_by(Table.number)
        .all()
    )
    result = []

    for table in tables:

        # buscar orden activa
        active_order = next(
            (
                order for order in table.orders
                if order.status not in [
                    OrderStatus.CLOSED,
                    OrderStatus.CANCELLED
                ]
            ),
            None
        )

        if active_order:
            result.append({
                "id": table.id,
                "number": table.number,
                "status": "ocupada",
                "order_id": active_order.id,
                "order_status": active_order.status.value
            })
        else:
            result.append({
                "id": table.id,
                "number": table.number,
                "status": "libre",
                "order_id": None,
                "order_status": None
            })

    return result
